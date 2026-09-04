from book_loop.application.services.linguistic_context import (
    ContextualDiagnosticReview,
    DiagnosticDecision,
    GeminiDiagnosticContextualizer,
)
from book_loop.domain.models import (
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    DiagnosticSource,
)


class FakeLLM:
    def __init__(self, result: ContextualDiagnosticReview) -> None:
        self.result = result
        self.calls = []

    def generate_structured(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def diagnostic() -> Diagnostic:
    return Diagnostic(
        category=DiagnosticCategory.SYNTAX,
        severity=DiagnosticSeverity.ERROR,
        source=DiagnosticSource.NLP,
        message="Sentence may be a fragment",
        start_offset=0,
        end_offset=18,
        original_text="Le silence.",
        confidence=0.75,
        rule_id="SPACY_FR_NO_VERB",
    )


def test_downgrade_preserves_text_and_adds_provenance() -> None:
    llm = FakeLLM(
        ContextualDiagnosticReview(
            diagnostics=[
                {
                    "decision": "downgrade",
                    "severity": "suggestion",
                    "rationale": "Intentional literary fragment.",
                }
            ]
        )
    )
    result = GeminiDiagnosticContextualizer(llm=llm).review(
        chapter="Le silence. Marseille dormait.", diagnostics=[diagnostic()]
    )

    assert result[0].severity == DiagnosticSeverity.SUGGESTION
    assert result[0].original_text == "Le silence."
    assert result[0].metadata["llm_decision"] == "downgrade"
    assert "literary" in result[0].metadata["llm_rationale"]
    assert llm.calls[0]["thinking_level"] == "minimal"


def test_keep_leaves_deterministic_severity_unchanged() -> None:
    llm = FakeLLM(
        ContextualDiagnosticReview(
            diagnostics=[
                {
                    "decision": DiagnosticDecision.KEEP,
                    "rationale": "The agreement error is clear.",
                }
            ]
        )
    )
    result = GeminiDiagnosticContextualizer(llm=llm).review(chapter="Les veilleur avance.", diagnostics=[diagnostic()])
    assert result[0].severity == DiagnosticSeverity.ERROR
    assert result[0].metadata["llm_decision"] == "keep"


def test_empty_diagnostics_do_not_call_llm() -> None:
    llm = FakeLLM(ContextualDiagnosticReview())
    assert GeminiDiagnosticContextualizer(llm=llm).review(chapter="", diagnostics=[]) == []
    assert llm.calls == []


def test_invalid_diagnostic_count_is_rejected() -> None:
    llm = FakeLLM(ContextualDiagnosticReview(diagnostics=[]))
    try:
        GeminiDiagnosticContextualizer(llm=llm).review(chapter="texte", diagnostics=[diagnostic()])
    except ValueError as exc:
        assert "diagnostic count" in str(exc)
    else:
        raise AssertionError("Expected invalid diagnostic count to fail")
