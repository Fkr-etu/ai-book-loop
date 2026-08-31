from __future__ import annotations

from book_loop.domain.protocols import LLMProvider


class SummarizerAgent:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    def summarize(self, *, context: str, chapter: str) -> str:
        return self.llm.generate(
            system_prompt=(
                "You are the canonical continuity editor. Summarize the chapter factually for future "
                "writers. Preserve characters, events, revelations, locations and unresolved threads."
            ),
            user_prompt=f"BOOK CONTEXT:\n{context}\n\nCHAPTER:\n{chapter}",
        )
