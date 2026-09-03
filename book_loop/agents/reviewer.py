from __future__ import annotations

from book_loop.domain.models import SceneReview
from book_loop.domain.protocols import LLMProvider


class ReviewerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def review(self, *, context: str, draft: str) -> SceneReview:
        review = self.llm.generate_structured(
            system_prompt=(
                "You are a deterministic chapter reviewer. Evaluate only the supplied chapter. "
                "Assess author-intent fidelity, continuity, coherence and writing quality. "
                "Do not rewrite the chapter, invent facts, modify canonical knowledge, or make decisions "
                "outside the requested schema. Return only the structured review."
            ),
            user_prompt=f"CONTEXT:\n{context}\n\nDRAFT:\n{draft}",
            schema=SceneReview,
            thinking_level="medium",
            max_output_tokens=2048,
        )
        if not 0 <= review.score <= 10:
            raise ValueError("Reviewer score must be between 0 and 10")
        if review.approved != (review.score >= 7):
            raise ValueError("Reviewer approval must match the configured score threshold")
        return review
