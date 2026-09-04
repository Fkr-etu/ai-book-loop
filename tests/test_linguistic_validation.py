import json

import pytest

from book_loop.application.services.diagnostics import fuse_diagnostics
from book_loop.application.services.linguistic_validation import LinguisticValidationService
from book_loop.domain.models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
    LinguisticCheckResult,
    LinguisticCheckStatus,
)
from book_loop.infrastructure.linguistic.languagetool import LanguageToolChecker


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def diagnostic(
    message: str,
    *,
    source: DiagnosticSource = DiagnosticSource.LINGUISTIC_LINTER,
    severity: DiagnosticSeverity = DiagnosticSeverity.ERROR,
    category: DiagnosticCategory = DiagnosticCategory.AGREEMENT,
    start: int = 0,
    end: int = 4,
    confidence: float = 0.8,
    suggestions: list[str] | None = None,
) -> Diagnostic:
    return Diagnostic(
        category=category,
        severity=severity,
        source=source,
        message=message,
        start_offset=start,
        end_offset=end,
        original_text="test",
        suggestions=suggestions or [],
        confidence=confidence,
    )


def test_languagetool_maps_response_to_provider_neutral_diagnostic():
    captured = {}

    def opener(req, timeout):
        captured["body"] = req.data.decode("utf-8")
        captured["timeout"] = timeout
        return FakeResponse(
            {
                "matches": [
                    {
                        "offset": 4,
                        "length": 5,
                        "message": "Agreement issue",
                        "replacements": [{"value": "chevaliers"}],
                        "rule": {"id": "FR_AGREEMENT", "issueType": "grammar"},
                    }
                ]
            }
        )

    result = LanguageToolChecker(base_url="http://lt:8010", opener=opener).check(
        "Les chevalier avancent.", language="fr"
    )

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert result.checker == "languagetool"
    assert len(result.diagnostics) == 1
    issue = result.diagnostics[0]
    assert issue.category == DiagnosticCategory.GRAMMAR
    assert issue.severity == DiagnosticSeverity.ERROR
    assert issue.rule_id == "FR_AGREEMENT"
    assert issue.original_text == "cheva"
    assert issue.suggestions == ["chevaliers"]
    assert "language=fr" in captured["body"]
    assert captured["timeout"] == 10.0


def test_languagetool_maps_style_to_non_blocking_suggestion():
    def opener(req, timeout):
        return FakeResponse(
            {
                "matches": [
                    {
                        "offset": 0,
                        "length": 3,
                        "message": "Style suggestion",
                        "replacements": [],
                        "rule": {"id": "STYLE_X", "issueType": "style"},
                    }
                ]
            }
        )

    result = LanguageToolChecker(opener=opener).check("Une phrase.")

    assert result.diagnostics[0].category == DiagnosticCategory.STYLE
    assert result.diagnostics[0].severity == DiagnosticSeverity.SUGGESTION


def test_languagetool_returns_no_issues_for_empty_match_list():
    result = LanguageToolChecker(opener=lambda req, timeout: FakeResponse({"matches": []})).check("Bonjour.")

    assert result.status == LinguisticCheckStatus.NO_ISSUES_FOUND
    assert result.diagnostics == []


def test_languagetool_degrades_when_server_is_unavailable():
    def opener(req, timeout):
        raise OSError("connection refused")

    result = LanguageToolChecker(opener=opener).check("Bonjour.")

    assert result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE
    assert result.diagnostics == []
    assert "connection refused" in result.error


def test_languagetool_validates_configuration():
    with pytest.raises(ValueError):
        LanguageToolChecker(base_url="")
    with pytest.raises(ValueError):
        LanguageToolChecker(timeout=0)
    with pytest.raises(ValueError):
        LanguageToolChecker().check("Bonjour.", language="")


def test_fusion_merges_duplicate_findings_and_preserves_provenance():
    result = fuse_diagnostics(
        [
            diagnostic("Agreement", confidence=0.7, suggestions=["chevaliers"]),
            diagnostic(
                "Agreement",
                source=DiagnosticSource.NLP,
                confidence=0.95,
                suggestions=["chevaliers", "les chevaliers"],
            ),
        ]
    )

    assert len(result) == 1
    issue = result[0]
    assert issue.source == DiagnosticSource.FUSION
    assert issue.metadata["sources"] == "linguistic_linter,nlp"
    assert issue.confidence == 0.95
    assert issue.suggestions == ["chevaliers", "les chevaliers"]


def test_fusion_keeps_separate_spans_and_orders_deterministically():
    issues = [
        diagnostic("Later", start=10, end=12),
        diagnostic("Earlier", start=2, end=4),
    ]

    assert [item.message for item in fuse_diagnostics(issues)] == ["Earlier", "Later"]


def test_fusion_promotes_highest_severity():
    result = fuse_diagnostics(
        [
            diagnostic("same", severity=DiagnosticSeverity.SUGGESTION),
            diagnostic("same", severity=DiagnosticSeverity.ERROR),
        ]
    )

    assert result[0].severity == DiagnosticSeverity.ERROR


def test_validation_service_distinguishes_unavailable_from_clean():
    class CleanChecker:
        def check(self, text, *, language="fr"):
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.NO_ISSUES_FOUND,
                checker="clean",
            )

    class DownChecker:
        def check(self, text, *, language="fr"):
            raise OSError("down")

    assert (
        LinguisticValidationService([CleanChecker()]).validate("Bonjour.").status
        == LinguisticCheckStatus.NO_ISSUES_FOUND
    )
    result = LinguisticValidationService([DownChecker()]).validate("Bonjour.")
    assert result.status == LinguisticCheckStatus.CHECK_NOT_AVAILABLE
    assert "DownChecker" in result.error


def test_validation_service_keeps_available_diagnostics_when_another_checker_fails():
    class FindingChecker:
        def check(self, text, *, language="fr"):
            return LinguisticCheckResult(
                status=LinguisticCheckStatus.ISSUES_FOUND,
                checker="finding",
                diagnostics=[diagnostic("Found")],
            )

    class DownChecker:
        def check(self, text, *, language="fr"):
            raise OSError("down")

    result = LinguisticValidationService([FindingChecker(), DownChecker()]).validate("Bonjour.")

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert len(result.diagnostics) == 1
    assert "down" in result.error


def test_validation_service_rejects_empty_text_as_blocking_diagnostic():
    result = LinguisticValidationService([]).validate("   \n")

    assert result.status == LinguisticCheckStatus.ISSUES_FOUND
    assert result.diagnostics[0].severity == DiagnosticSeverity.ERROR
    assert result.diagnostics[0].rule_id == "BOOK_EMPTY_TEXT"
