from __future__ import annotations

from book_loop.domain.models import BookState


class ContextBuilder:
    """Build a bounded, explicit prompt context from canonical book state."""

    def for_chapter(self, book: BookState, chapter_number: int) -> str:
        chapter = next(c for c in book.chapters if c.number == chapter_number)
        summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}"
            for c in book.chapters
            if c.number < chapter_number and c.summary
        )
        constraints = "\n".join(f"- {item}" for item in book.constraints)
        return "\n\n".join(
            [
                f"AUTHOR IDEA:\n{book.author_idea}",
                f"THEME:\n{book.theme}",
                f"LORE:\n{book.lore}",
                f"GLOBAL OUTLINE:\n{book.outline or ''}",
                f"CONSTRAINTS:\n{constraints}",
                f"PREVIOUS CHAPTER SUMMARIES:\n{summaries}",
                f"CURRENT CHAPTER OBJECTIVE:\n{chapter.objective}",
            ]
        )
