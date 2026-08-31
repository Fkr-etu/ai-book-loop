from __future__ import annotations

from book_loop.domain.protocols import LLMProvider


class OutlineAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def generate(self, *, theme: str, author_idea: str, lore: str, constraints: list[str]) -> str:
        system_prompt = (
            "You are a developmental fiction editor. Create a concise global book outline "
            "that preserves the author's intent. Do not invent constraints that contradict it."
        )
        user_prompt = (
            f"THEME:\n{theme}\n\nAUTHOR IDEA:\n{author_idea}\n\nLORE:\n{lore}\n\n"
            f"CONSTRAINTS:\n{chr(10).join('- ' + c for c in constraints)}\n\n"
            "Return a chapter-by-chapter outline with each chapter's title and narrative objective."
        )
        return self.llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
