from __future__ import annotations

from book_loop.domain.models import SceneReview
from book_loop.domain.protocols import LLMProvider


class CorrectorAgent:
    """Apply reviewer feedback to an existing draft without rewriting the workflow state."""

    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def correct(self, *, context: str, draft: str, review: SceneReview) -> str:
        feedback = "\n".join(
            [
                "ISSUES:",
                *(f"- {issue}" for issue in review.issues),
                "SUGGESTIONS:",
                *(f"- {suggestion}" for suggestion in review.suggestions),
            ]
        )
        return self.llm.generate(
            system_prompt=(
                "You are the book's editor. Apply the supplied editorial feedback to the existing chapter. "
                "Preserve valid material, author intent, continuity and canonical facts. "
                "Return only the corrected chapter."
            ),
            user_prompt=f"CONTEXT:\n{context}\n\nEDITORIAL FEEDBACK:\n{feedback}\n\nDRAFT:\n{draft}",
        )
