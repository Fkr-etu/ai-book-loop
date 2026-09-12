from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from book_loop.domain.protocols import LLMProvider


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: float
    output_per_million: float


@dataclass(frozen=True)
class BenchmarkCase:
    workload: str
    system_prompt: str
    user_prompt: str
    structured: bool = False
    schema: type[Any] | None = None
    max_output_tokens: int | None = None


@dataclass
class BenchmarkResult:
    workload: str
    model: str
    success: bool
    latency_ms: float
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost_usd: float | None
    structured_output_valid: bool | None
    error: str | None = None
    output: str | None = None
    quality_score: float | None = None


def estimate_cost(
    *,
    pricing: ModelPricing,
    input_tokens: int,
    output_tokens: int,
) -> float:
    return (
        input_tokens / 1_000_000 * pricing.input_per_million
        + output_tokens / 1_000_000 * pricing.output_per_million
    )


def run_case(
    provider: LLMProvider,
    case: BenchmarkCase,
    *,
    model: str,
    pricing: ModelPricing | None = None,
    token_counter: Callable[[str], int] | None = None,
) -> BenchmarkResult:
    started = time.perf_counter()
    try:
        if case.structured:
            if case.schema is None:
                raise ValueError("structured benchmark case requires a schema")
            value = provider.generate_structured(
                system_prompt=case.system_prompt,
                user_prompt=case.user_prompt,
                schema=case.schema,
                max_output_tokens=case.max_output_tokens,
            )
            output = value.model_dump_json()
            structured_valid = True
        else:
            output = provider.generate(
                system_prompt=case.system_prompt,
                user_prompt=case.user_prompt,
            )
            structured_valid = None

        elapsed_ms = (time.perf_counter() - started) * 1000
        input_tokens = token_counter(case.system_prompt + "\n" + case.user_prompt) if token_counter else None
        output_tokens = token_counter(output) if token_counter else None
        cost = (
            estimate_cost(
                pricing=pricing,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            if pricing and input_tokens is not None and output_tokens is not None
            else None
        )
        return BenchmarkResult(
            workload=case.workload,
            model=model,
            success=True,
            latency_ms=round(elapsed_ms, 2),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost,
            structured_output_valid=structured_valid,
            output=output,
        )
    except Exception as exc:  # benchmark failures must be explicit, not silently routed away
        return BenchmarkResult(
            workload=case.workload,
            model=model,
            success=False,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            input_tokens=None,
            output_tokens=None,
            estimated_cost_usd=None,
            structured_output_valid=False if case.structured else None,
            error=f"{type(exc).__name__}: {exc}",
        )


def write_results(
    results: list[BenchmarkResult],
    destination: Path,
    *,
    benchmark_version: str,
    timestamp: datetime | None = None,
) -> None:
    timestamp = timestamp or datetime.now(UTC)
    payload = {
        "benchmark_version": benchmark_version,
        "timestamp": timestamp.isoformat(),
        "results": [asdict(result) for result in results],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
