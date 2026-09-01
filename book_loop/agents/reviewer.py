from __future__ import annotations

import json

from pydantic import ValidationError

from book_loop.domain.models import SceneReview
from book_loop.domain.protocols import LLMProvider


class ReviewerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def review(self, *, context: str, draft: str) -> SceneReview:
        raw = self.llm.generate(
            system_prompt=(
                "Review the chapter for author-intent fidelity, continuity, coherence and writing quality. "
                "Return ONLY valid JSON with keys: score (0-10), approved (boolean), issues (array of strings), "
                "suggestions (array of strings)."
            ),
            user_prompt=f"CONTEXT:\n{context}\n\nDRAFT:\n{draft}",
        )
        try:
            return SceneReview.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ValueError("Reviewer returned invalid structured output") from exc
