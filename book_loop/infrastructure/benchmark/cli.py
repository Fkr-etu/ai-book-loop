from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, RootModel

from book_loop.infrastructure.benchmark.runner import (
    BenchmarkCase,
    ModelPricing,
    run_case,
    skipped_result,
    write_results,
)
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.llm.gemini import GeminiProvider
from book_loop.infrastructure.llm.openai_compatible import OpenAICompatibleProvider


class Assertion(BaseModel):
    subject: str
    predicate: str
    object: str


class AssertionList(RootModel[list[Assertion]]):
    pass


PROVIDERS: dict[str, tuple[str, str, str]] = {
    "gemini": ("GEMINI_API_KEY", "gemini-3.6-flash", "gemini"),
    "kimi": ("KIMI_API_KEY", "kimi-k2.6", "kimi"),
    "minimax": ("MINIMAX_API_KEY", "MiniMax-M2.7", "minimax"),
    "deepseek": ("DEEPSEEK_API_KEY", "deepseek-v4-flash", "deepseek"),
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pricing(path: Path, model: str) -> ModelPricing:
    data = _load_json(path)
    try:
        value = data["models"][model]
    except KeyError as exc:
        raise ValueError(f"No pricing entry for benchmark model {model!r}") from exc
    return ModelPricing(input_per_million=value["input"], output_per_million=value["output"])


def _provider(settings: Settings, name: str, model: str):
    if name == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=model)
    keys_and_urls = {
        "kimi": (settings.kimi_api_key, settings.kimi_base_url),
        "minimax": (settings.minimax_api_key, settings.minimax_base_url),
        "deepseek": (settings.deepseek_api_key, settings.deepseek_base_url),
    }
    api_key, base_url = keys_and_urls[name]
    return OpenAICompatibleProvider(api_key=api_key, base_url=base_url, model=model)


def _cases(path: Path) -> tuple[str, list[BenchmarkCase]]:
    data = _load_json(path)
    cases = []
    for raw in data["cases"]:
        structured = raw["workload"] == "assertion_extraction"
        cases.append(
            BenchmarkCase(
                workload=raw["workload"],
                system_prompt=raw["system_prompt"],
                user_prompt=raw["user_prompt"],
                structured=structured,
                schema=AssertionList if structured else None,
            )
        )
    return data["benchmark_version"], cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="book-loop benchmark")
    parser.add_argument("--fixtures", type=Path, default=Path("book_loop/infrastructure/benchmark/fixtures.json"))
    parser.add_argument("--pricing", type=Path, default=Path("book_loop/infrastructure/benchmark/pricing.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/llm-benchmark.json"))
    parser.add_argument("--provider", action="append", choices=tuple(PROVIDERS), help="Run only selected provider(s)")
    return parser


def run(args: argparse.Namespace, settings: Settings) -> int:
    benchmark_version, cases = _cases(args.fixtures)
    pricing_data = _load_json(args.pricing)
    selected = args.provider or list(PROVIDERS)
    results = []

    for provider_name in selected:
        _, model, _ = PROVIDERS[provider_name]
        api_key = {
            "gemini": settings.gemini_api_key,
            "kimi": settings.kimi_api_key,
            "minimax": settings.minimax_api_key,
            "deepseek": settings.deepseek_api_key,
        }[provider_name]
        if not api_key.strip():
            reason = f"{PROVIDERS[provider_name][0]} is not configured"
            for case in cases:
                results.append(skipped_result(workload=case.workload, model=model, reason=reason))
            print(f"- {provider_name}: skipped ({reason})")
            continue

        provider = _provider(settings, provider_name, model)
        model_price = ModelPricing(
            input_per_million=pricing_data["models"][model]["input"],
            output_per_million=pricing_data["models"][model]["output"],
        )
        print(f"- {provider_name}: running {len(cases)} workloads")
        for case in cases:
            result = run_case(provider, case, model=model, pricing=model_price)
            results.append(result)
            print(f"  {case.workload}: {result.status} ({result.latency_ms:.0f} ms)")

    write_results(results, args.output, benchmark_version=benchmark_version)
    failed = sum(result.status == "failed" for result in results)
    skipped = sum(result.status == "skipped" for result in results)
    succeeded = sum(result.status == "success" for result in results)
    print(f"Results written to {args.output}: {succeeded} succeeded, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(run(args, Settings()))
