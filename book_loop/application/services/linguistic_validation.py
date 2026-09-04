from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from book_loop.application.services.diagnostics import fuse_diagnostics
from book_loop.domain.models import Diagnostic, LinguisticCheckResult, LinguisticCheckStatus


class LinguisticChecker(Protocol):
    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult: ...


class LinguisticValidationService:
    """Run linguistic checkers and expose one provider-neutral result."""

    def __init__(self, checkers: Iterable[LinguisticChecker]) -> None:
        self.checkers = tuple(checkers)

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
        failures = [result for result in results if result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE]

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
