from __future__ import annotations

from book_loop.domain.protocols import LLMProvider


class WriterAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def write(self, *, context: str) -> str:
        return self.llm.generate(
            system_prompt=(
                "You are the book's writer. Follow the author's intent and canonical context. "
                "Preserve continuity with established facts and characters. Write only the requested chapter."
            ),
            user_prompt=context,
        )
