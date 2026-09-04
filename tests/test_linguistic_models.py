import pytest
from pydantic import ValidationError

from book_loop.domain.models import Diagnostic, DiagnosticCategory, DiagnosticSeverity, DiagnosticSource


def test_diagnostic_preserves_offsets_suggestions_and_provenance():
    issue = Diagnostic(
        category=DiagnosticCategory.SPELLING,
        severity=DiagnosticSeverity.ERROR,
        source=DiagnosticSource.LINGUISTIC_LINTER,
        message="Mot probablement mal orthographié",
        start_offset=12,
        end_offset=18,
        original_text="chevaal",
        suggestions=["cheval"],
        confidence=0.93,
        rule_id="MORFOLOGIK_RULE_FR_FR",
        metadata={"language": "fr"},
    )

    assert issue.start_offset == 12
    assert issue.end_offset == 18
    assert issue.suggestions == ["cheval"]
    assert issue.rule_id == "MORFOLOGIK_RULE_FR_FR"
    assert issue.metadata["language"] == "fr"


def test_diagnostic_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        Diagnostic(
            category=DiagnosticCategory.GRAMMAR,
            severity=DiagnosticSeverity.ERROR,
            source=DiagnosticSource.NLP,
            message="bad confidence",
            confidence=1.1,
        )


def test_diagnostic_rejects_negative_offsets():
    with pytest.raises(ValidationError):
        Diagnostic(
            category=DiagnosticCategory.GRAMMAR,
            severity=DiagnosticSeverity.ERROR,
            source=DiagnosticSource.NLP,
            message="bad offset",
            start_offset=-1,
            confidence=0.5,
        )
