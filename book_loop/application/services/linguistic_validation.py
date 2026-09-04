from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from book_loop.application.services.diagnostics import fuse_diagnostics
from book_loop.application.services.linguistic_context import GeminiDiagnosticContextualizer
from book_loop.domain.models import Diagnostic, DiagnosticSeverity, LinguisticCheckResult, LinguisticCheckStatus


class LinguisticChecker(Protocol):
    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult: ...


class LinguisticValidationService:
    """Run deterministic checkers and optionally contextualize non-Canon findings."""

    def __init__(
        self,
        checkers: Iterable[LinguisticChecker],
        contextualizer: GeminiDiagnosticContextualizer | None = None,
    ) -> None:
        self.checkers = tuple(checkers)
        self.contextualizer = contextualizer

    def validate(self, text: str, *, language: str = "fr") -> LinguisticCheckResult:
        if not text.strip():
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.ISSUES_FOUND,
                diagnostics=[
                    Diagnostic(
                        category="grammar",
                        severity="error",
                        source="linguistic_linter",
                        message="Chapter text is empty",
                        confidence=1.0,
                        rule_id="BOOK_EMPTY_TEXT",
                    )
                ],
                checker="linguistic-validation",
            )

        results: list[LinguisticCheckResult] = []
        for checker in self.checkers:
            try:
                results.append(checker.check(text, language=language))
            except Exception as exc:
                results.append(
                    LinguisticCheckResult(
                        status=LinguisticCheckStatus.CHECK_NOT_AVAILABLE,
                        checker=checker.__class__.__name__,
                        error=str(exc),
                    )
                )

        diagnostics = fuse_diagnostics(
            diagnostic for result in results for diagnostic in result.diagnostics
        )
        failures = [
            result
            for result in results
            if result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE
        ]

        if self.contextualizer:
            contextualized = [
                diagnostic
                for diagnostic in diagnostics
                if diagnostic.category.value != "canon"
            ]
            if contextualized:
                try:
                    reviewed = self.contextualizer.review(
                        chapter=text,
                        diagnostics=contextualized,
                    )
                    by_rule = {id(item): item for item in contextualized}
                    for original, updated in zip(contextualized, reviewed, strict=True):
                        original.category = updated.category
                        original.severity = updated.severity
                        original.source = updated.source
                        original.message = updated.message
                        original.start_offset = updated.start_offset
                        original.end_offset = updated.end_offset
                        original.original_text = updated.original_text
                        original.suggestions = updated.suggestions
                        original.confidence = updated.confidence
                        original.rule_id = updated.rule_id
                        original.related_assertion_id = updated.related_assertion_id
                        original.metadata = updated.metadata
                except Exception as exc:
                    failures.append(
                        LinguisticCheckResult(
                            status=LinguisticCheckStatus.CHECK_NOT_AVAILABLE,
                            checker="gemini-contextualizer",
                            error=str(exc),
                        )
                    )

        if diagnostics:
            status = LinguisticCheckStatus.ISSUES_FOUND
        elif failures:
            status = LinguisticCheckStatus.CHECK_NOT_AVAILABLE
        else:
            status = LinguisticCheckStatus.NO_ISSUES_FOUND

        error = "; ".join(
            f"{result.checker}: {result.error}" for result in failures if result.error
        ) or None
        return LinguisticCheckResult(
            status=status,
            diagnostics=diagnostics,
            checker="linguistic-validation",
            error=error,
        )

    @staticmethod
    def blocking_diagnostics(result: LinguisticCheckResult) -> list[Diagnostic]:
        """Return diagnostics that are strong enough to trigger a bounded retry."""
        return [
            diagnostic
            for diagnostic in result.diagnostics
            if diagnostic.severity == DiagnosticSeverity.ERROR
        ]
