from __future__ import annotations

import json

from book_loop.domain.models import Outline
from book_loop.domain.protocols import LLMProvider


class OutlineAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def generate(self, *, theme: str, author_idea: str, lore: str, constraints: list[str]) -> Outline:
        system_prompt = (
            "You are a developmental fiction editor. Create a concise global book outline "
            "that preserves the author's intent. Do not invent constraints that contradict it. "
            "Return valid JSON only, with this exact shape: "
            '{"chapters":[{"number":1,"title":"...","objective":"...","synopsis":"..."}]}.'
        )
        user_prompt = (
            f"THEME:\n{theme}\n\nAUTHOR IDEA:\n{author_idea}\n\nLORE:\n{lore}\n\n"
            f"CONSTRAINTS:\n{chr(10).join('- ' + c for c in constraints)}\n\n"
            "Create the chapter-by-chapter outline. Numbers must start at 1 and be consecutive."
        )
        raw = self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt).strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```").removeprefix("json").removesuffix("```").strip()
        try:
            return Outline.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError("The outline provider returned invalid structured JSON") from exc
