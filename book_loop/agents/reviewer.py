from __future__ import annotations

from book_loop.domain.models import Diagnostic, SceneReview
from book_loop.domain.protocols import LLMProvider


class ReviewerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def review(
        self,
        *,
        context: str,
        draft: str,
        diagnostics: list[Diagnostic] | None = None,
    ) -> SceneReview:
        diagnostic_context = self._render_diagnostics(diagnostics or [])
        try:
            return self.llm.generate_structured(
                system_prompt=(
                    "You are a deterministic chapter reviewer. Evaluate only the supplied chapter. "
                    "Assess author-intent fidelity, continuity, coherence and writing quality. "
                    "Treat supplied deterministic diagnostics as evidence to consider, not as facts to invent. "
                    "Do not rewrite the chapter, invent facts, modify canonical knowledge, or make decisions "
                    "outside the requested schema. Return only the structured review."
                ),
                user_prompt=(
                    f"CONTEXT:\n{context}\n\nDRAFT:\n{draft}"
                    f"{diagnostic_context}"
                ),
                schema=SceneReview,
                thinking_level="medium",
                max_output_tokens=2048,
            )
        except (ValueError, TypeError) as exc:
            raise ValueError("Reviewer returned invalid structured output") from exc

    @staticmethod
    def _render_diagnostics(diagnostics: list[Diagnostic]) -> str:
        if not diagnostics:
            return ""
        lines = ["\n\nDETERMINISTIC DIAGNOSTICS:"]
        for index, diagnostic in enumerate(diagnostics, start=1):
            lines.append(
                f"{index}. [{diagnostic.severity.value}] {diagnostic.category.value}: "
                f"{diagnostic.message}; excerpt={diagnostic.original_text!r}; "
                f"suggestions={diagnostic.suggestions!r}; rule_id={diagnostic.rule_id or 'none'}"
            )
        return "\n".join(lines)
