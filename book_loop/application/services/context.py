from __future__ import annotations

from dataclasses import dataclass

from book_loop.domain.models import BookState, Chapter


@dataclass(frozen=True)
class CanonicalContext:
    """Focused, deterministic context for generating one chapter."""

    author_idea: str
    theme: str
    lore: str
    outline: str
    constraints: tuple[str, ...]
    previous_summaries: tuple[str, ...]
    chapter_title: str
    chapter_objective: str

    def render(self) -> str:
        constraints = "\n".join(f"- {item}" for item in self.constraints)
        summaries = "\n".join(self.previous_summaries)
        return "\n\n".join([
            f"AUTHOR IDEA:\n{self.author_idea}",
            f"THEME:\n{self.theme}",
            f"LORE:\n{self.lore}",
            f"GLOBAL OUTLINE:\n{self.outline}",
            f"CONSTRAINTS:\n{constraints}",
            f"PREVIOUS CHAPTER SUMMARIES:\n{summaries}",
            f"CURRENT CHAPTER:\n{self.chapter_title}",
            f"CURRENT CHAPTER OBJECTIVE:\n{self.chapter_objective}",
        ])


class ContextBuilder:
    """Build canonical chapter context without invoking an LLM."""

    def for_chapter(self, book: BookState, chapter_number: int) -> CanonicalContext:
        chapter = next(c for c in book.chapters if c.number == chapter_number)
        return CanonicalContext(
            author_idea=book.author_idea,
            theme=book.theme,
            lore=book.lore,
            outline=book.outline or "",
            constraints=tuple(book.constraints),
            previous_summaries=tuple(
                self._summary(c)
                for c in book.chapters
                if c.number < chapter_number and c.summary
            ),
            chapter_title=chapter.title,
            chapter_objective=chapter.objective,
        )

    @staticmethod
    def _summary(chapter: Chapter) -> str:
        return f"Chapter {chapter.number} ({chapter.title}): {chapter.summary}"
