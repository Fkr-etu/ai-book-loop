from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from book_loop.domain.models import Diagnostic, DiagnosticSeverity
from book_loop.domain.protocols import LLMProvider


class DiagnosticDecision(StrEnum):
    KEEP = "keep"
    CONFIRM = "confirm"
    DOWNGRADE = "downgrade"


class ContextualDiagnostic(BaseModel):
    decision: DiagnosticDecision
    severity: DiagnosticSeverity | None = None
    rationale: str = Field(min_length=1)


class ContextualDiagnosticReview(BaseModel):
    diagnostics: list[ContextualDiagnostic] = Field(default_factory=list)


class GeminiDiagnosticContextualizer:
    """Uses Gemini only to contextualize deterministic findings, never rewrite text."""

    SYSTEM_PROMPT = (
        "Review deterministic French linguistic diagnostics against their local context. "
        "Decide KEEP when the finding is clearly valid, CONFIRM when it is plausible but "
        "needs contextual confirmation, and DOWNGRADE when literary usage makes it likely "
        "a false positive. Never rewrite the text. Preserve literary fragments, dialogue, "
        "stylistic choices and intentional non-standard forms unless clearly erroneous. "
        "Return one decision per supplied diagnostic, in the same order."
    )

    def __init__(self, *, llm: LLMProvider) -> None:
        self._llm = llm

    def review(self, *, chapter: str, diagnostics: list[Diagnostic]) -> list[Diagnostic]:
        if not diagnostics:
            return []
        user_prompt = self._build_prompt(chapter=chapter, diagnostics=diagnostics)
        result = self._llm.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=ContextualDiagnosticReview,
            thinking_level="minimal",
            max_output_tokens=2048,
        )
        if len(result.diagnostics) != len(diagnostics):
            raise ValueError("Gemini contextualizer returned an invalid diagnostic count")
        return [self._apply(diagnostic, decision) for diagnostic, decision in zip(diagnostics, result.diagnostics, strict=True)]

    @staticmethod
    def _build_prompt(*, chapter: str, diagnostics: list[Diagnostic]) -> str:
        lines = ["CHAPTER:\n" + chapter, "\nDIAGNOSTICS:"]
        for index, diagnostic in enumerate(diagnostics, start=1):
            lines.append(
                f"{index}. category={diagnostic.category.value}; severity={diagnostic.severity.value}; "
                f"rule_id={diagnostic.rule_id or 'none'}; excerpt={diagnostic.original_text!r}; "
                f"message={diagnostic.message!r}"
            )
        return "\n".join(lines)

    @staticmethod
    def _apply(diagnostic: Diagnostic, decision: ContextualDiagnostic) -> Diagnostic:
        updated = diagnostic.model_copy(deep=True)
        updated.metadata["llm_decision"] = decision.decision.value
        updated.metadata["llm_rationale"] = decision.rationale
        if decision.decision == DiagnosticDecision.DOWNGRADE:
            updated.severity = decision.severity or DiagnosticSeverity.SUGGESTION
        elif decision.decision == DiagnosticDecision.CONFIRM and decision.severity:
            updated.severity = decision.severity
        return updated
