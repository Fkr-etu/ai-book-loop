import json
from pathlib import Path

from book_loop.application.services.linguistic_evaluation import EvaluationCase, evaluate_checker
from book_loop.domain.models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
)


class FakeChecker:
    def __init__(self, mapping: dict[str, list[DiagnosticCategory]]) -> None:
        self.mapping = mapping

    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult:
        diagnostics = [
            Diagnostic(
                category=category,
                severity=DiagnosticSeverity.ERROR,
                source=DiagnosticSource.NLP,
                message=category.value,
                confidence=1.0,
            )
            for category in self.mapping.get(text, [])
        ]
        return LinguisticCheckResult(
            status=(
                LinguisticCheckStatus.ISSUES_FOUND
                if diagnostics
                else LinguisticCheckStatus.NO_ISSUES_FOUND
            ),
            diagnostics=diagnostics,
            checker="fake",
        )


def test_evaluation_reports_precision_recall_and_literary_false_positives() -> None:
    cases = [
        EvaluationCase(
            id="agreement",
            text="agreement",
            expected_categories=frozenset({DiagnosticCategory.AGREEMENT}),
        ),
        EvaluationCase(
            id="clean-literary",
            text="literary",
            expected_categories=frozenset(),
            literary=True,
        ),
    ]
    metrics = evaluate_checker(
        FakeChecker(
            {
                "agreement": [DiagnosticCategory.AGREEMENT],
                "literary": [DiagnosticCategory.SYNTAX],
            }
        ),
        cases,
    )

    assert metrics.cases == 2
    assert metrics.expected_findings == 1
    assert metrics.detected_findings == 2
    assert metrics.true_positives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0
    assert metrics.precision == 0.5
    assert metrics.recall == 1.0
    assert metrics.literary_false_positives == 1
    assert metrics.literary_false_positive_rate == 1.0


def test_evaluation_corpus_is_present_and_labelled() -> None:
    path = Path(__file__).parent / "fixtures" / "linguistic_corpus.json"
    corpus = json.loads(path.read_text(encoding="utf-8"))

    assert len(corpus) >= 5
    assert all(case["id"] for case in corpus)
    assert all("expected_categories" in case for case in corpus)
    assert any(case["literary"] for case in corpus)
