from __future__ import annotations

import json
from collections.abc import Callable
from urllib import parse, request
from urllib.error import HTTPError, URLError

from book_loop.domain.models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
)


_CATEGORY_BY_ISSUE_TYPE = {
    "misspelling": DiagnosticCategory.SPELLING,
    "grammar": DiagnosticCategory.GRAMMAR,
    "typographical": DiagnosticCategory.TYPOGRAPHY,
    "style": DiagnosticCategory.STYLE,
}


class LanguageToolChecker:
    """HTTP adapter for a LanguageTool server; no provider types leak upward."""

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:8010",
        timeout: float = 10.0,
        opener: Callable[..., object] = request.urlopen,
    ) -> None:
        if not base_url.strip():
            raise ValueError("LanguageTool base URL is required")
        if timeout <= 0:
            raise ValueError("LanguageTool timeout must be positive")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.opener = opener

    def check(self, text: str, *, language: str = "fr") -> LinguisticCheckResult:
        if not language.strip():
            raise ValueError("LanguageTool language is required")

        payload = parse.urlencode({"text": text, "language": language}).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/v2/check",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with self.opener(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
            data = json.loads(body)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.CHECK_NOT_AVAILABLE,
                checker="languagetool",
                error=str(exc),
            )

        diagnostics = [self._diagnostic(match, text, language=language) for match in data.get("matches", [])]
        return LinguisticCheckResult(
            status=(
                LinguisticCheckStatus.ISSUES_FOUND
                if diagnostics
                else LinguisticCheckStatus.NO_ISSUES_FOUND
            ),
            diagnostics=diagnostics,
            checker="languagetool",
        )

    @staticmethod
    def _diagnostic(match: dict[str, object], text: str, *, language: str) -> Diagnostic:
        offset = int(match.get("offset", 0))
        length = int(match.get("length", 0))
        end = offset + length
        rule = match.get("rule") or {}
        if not isinstance(rule, dict):
            rule = {}
        issue_type = str(rule.get("issueType", "grammar"))
        category = _CATEGORY_BY_ISSUE_TYPE.get(issue_type, DiagnosticCategory.GRAMMAR)
        severity = (
            DiagnosticSeverity.SUGGESTION
            if issue_type == "style"
            else DiagnosticSeverity.ERROR
        )
        replacements = match.get("replacements") or []
        suggestions = [
            str(item.get("value", ""))
            for item in replacements
            if isinstance(item, dict) and item.get("value")
        ]
        return Diagnostic(
            category=category,
            severity=severity,
            source=DiagnosticSource.LINGUISTIC_LINTER,
            message=str(match.get("message", "LanguageTool diagnostic")),
            start_offset=offset,
            end_offset=end,
            original_text=text[offset:end] if 0 <= offset <= end <= len(text) else None,
            suggestions=suggestions,
            confidence=0.9 if severity == DiagnosticSeverity.ERROR else 0.7,
            rule_id=str(rule.get("id")) if rule.get("id") else None,
            metadata={"language": language},
        )
