from __future__ import annotations

import ast
import json
import re

from pydantic import ValidationError

from book_loop.domain.models import SceneReview
from book_loop.domain.protocols import LLMProvider


class ReviewerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    @staticmethod
    def _parse_structured_output(raw: str) -> dict:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```").removeprefix("json").removesuffix("```").strip()

        normalized = re.sub(
            r"([,{]\s*)([A-Za-z_][A-Za-z0-9_-]*)(\s*:)",
            r'\1"\2"\3',
            cleaned,
        )
        try:
            parsed = json.loads(normalized)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(cleaned)
            except (SyntaxError, ValueError) as exc:
                raise ValueError("Reviewer returned invalid structured output") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Reviewer returned invalid structured output")
        return parsed

    def review(self, *, context: str, draft: str) -> SceneReview:
        raw = self.llm.generate(
            system_prompt=(
                "Review the chapter for author-intent fidelity, continuity, coherence and writing quality. "
                "Return ONLY valid JSON with keys: score (0-10), approved (boolean), issues (array of strings), "
                "suggestions (array of strings)."
            ),
            user_prompt=f"CONTEXT:\n{context}\n\nDRAFT:\n{draft}",
        ).strip()
        try:
            return SceneReview.model_validate(self._parse_structured_output(raw))
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            raise ValueError("Reviewer returned invalid structured output") from exc
