from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from book_loop.infrastructure.benchmark.runner import (
    BenchmarkCase,
    ModelPricing,
    estimate_cost,
    run_case,
    skipped_result,
    write_results,
)


class StructuredResult(BaseModel):
    answer: str


class FakeProvider:
    def generate(self, *, system_prompt: str, user_prompt: str, **_: object) -> str:
        return f"{system_prompt} | {user_prompt}"

    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema, **_: object):
        return schema(answer=f"{system_prompt} | {user_prompt}")


class FailingProvider(FakeProvider):
    def generate(self, *, system_prompt: str, user_prompt: str, **_: object) -> str:
        raise RuntimeError("provider unavailable")


def test_estimate_cost_uses_versioned_unit_prices() -> None:
    assert estimate_cost(
        pricing=ModelPricing(input_per_million=1.0, output_per_million=2.0),
        input_tokens=100_000,
        output_tokens=20_000,
    ) == 0.14


def test_run_case_records_success_and_cost() -> None:
    result = run_case(
        FakeProvider(),
        BenchmarkCase(workload="writer", system_prompt="system", user_prompt="user"),
        model="test-model",
        pricing=ModelPricing(input_per_million=1.0, output_per_million=2.0),
        token_counter=lambda value: len(value.split()),
    )

    assert result.success is True
    assert result.status == "success"
    assert result.workload == "writer"
    assert result.input_tokens == 2
    assert result.output_tokens == 3
    assert result.estimated_cost_usd == 0.000008


def test_run_case_never_hides_provider_failure() -> None:
    result = run_case(
        FailingProvider(),
        BenchmarkCase(workload="writer", system_prompt="system", user_prompt="user"),
        model="test-model",
    )

    assert result.success is False
    assert result.status == "failed"
    assert result.error == "RuntimeError: provider unavailable"


def test_missing_provider_key_is_explicitly_skipped() -> None:
    result = skipped_result(
        workload="writer",
        model="gemini-3.6-flash",
        reason="GEMINI_API_KEY is not configured",
    )

    assert result.success is False
    assert result.status == "skipped"
    assert result.error == "GEMINI_API_KEY is not configured"


def test_structured_case_records_validity() -> None:
    result = run_case(
        FakeProvider(),
        BenchmarkCase(
            workload="assertion_extraction",
            system_prompt="system",
            user_prompt="user",
            structured=True,
            schema=StructuredResult,
        ),
        model="test-model",
    )

    assert result.success is True
    assert result.structured_output_valid is True
    assert json.loads(result.output or "{}") == {"answer": "system | user"}


def test_write_results_is_reproducible_json(tmp_path: Path) -> None:
    destination = tmp_path / "results.json"
    write_results([], destination, benchmark_version="1")

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["benchmark_version"] == "1"
    assert payload["results"] == []
    assert "timestamp" in payload
