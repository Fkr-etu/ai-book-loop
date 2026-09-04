from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from book_loop.domain.models import Diagnostic, DiagnosticCategory, LinguisticCheckResult


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    text: str
    expected_categories: frozenset[DiagnosticCategory]
    literary: bool = False


@dataclass(frozen=True)
class EvaluationMetrics:
    cases: int
    expected_findings: int
    detected_findings: int
    true_positives: int
    false_positives: int
    false_negatives: int
    literary_false_positives: int

    @property
    def precision(self) -> float:
        return self.true_positives / self.detected_findings if self.detected_findings else 0.0

    @property
    def recall(self) -> float:
        return self.true_positives / self.expected_findings if self.expected_findings else 0.0

    @property
    def literary_false_positive_rate(self) -> float:
        literary_cases = self._literary_cases
        return self.literary_false_positives / literary_cases if literary_cases else 0.0

    _literary_cases: int = 0


class Checkable(Protocol):
    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult: ...


def evaluate_checker(checker: Checkable, cases: list[EvaluationCase]) -> EvaluationMetrics:
    """Run a deterministic baseline evaluation over a small labelled corpus.

    A finding is a true positive when its category matches one of the expected
    categories for the case. This intentionally measures category-level recall;
    exact span evaluation belongs to the diagnostic contract tests.
    """
    expected = detected = true_positive = false_positive = false_negative = literary_fp = 0
    literary_cases = sum(case.literary for case in cases)

    for case in cases:
        result = checker.check(case.text, language="fr")
        categories = [diagnostic.category for diagnostic in result.diagnostics]
        expected += len(case.expected_categories)
        detected += len(categories)
        matched = sum(1 for category in case.expected_categories if category in categories)
        true_positive += matched
        false_negative += len(case.expected_categories) - matched
        false_positive += max(0, len(categories) - matched)
        if case.literary and categories:
            literary_fp += len(categories)

    return EvaluationMetrics(
        cases=len(cases),
        expected_findings=expected,
        detected_findings=detected,
        true_positives=true_positive,
        false_positives=false_positive,
        false_negatives=false_negative,
        literary_false_positives=literary_fp,
        _literary_cases=literary_cases,
    )


def diagnostic_categories(diagnostics: list[Diagnostic]) -> frozenset[DiagnosticCategory]:
    return frozenset(diagnostic.category for diagnostic in diagnostics)
