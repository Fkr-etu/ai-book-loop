from __future__ import annotations

from dataclasses import dataclass

from book_loop.domain.models import BookState, Chapter
from book_loop.domain.value_objects import ChapterSummary


@dataclass(frozen=True)
class CanonicalContext:
    """Focused, structured context for generating one chapter."""

    author_idea: str
    theme: str
    lore: str
    outline: str
    constraints: tuple[str, ...]
    previous_summaries: tuple[ChapterSummary, ...]
    chapter_title: str
    chapter_objective: str

    def render(self) -> str:
        sections = (
            ("AUTHOR IDEA", self.author_idea),
            ("THEME", self.theme),
            ("LORE", self.lore),
            ("GLOBAL OUTLINE", self.outline),
            ("CONSTRAINTS", "\n".join(f"- {item}" for item in self.constraints)),
            ("PREVIOUS CHAPTER SUMMARIES", "\n".join(s.render() for s in self.previous_summaries)),
            ("CURRENT CHAPTER", self.chapter_title),
            ("CURRENT CHAPTER OBJECTIVE", self.chapter_objective),
        )
        return "\n\n".join(f"{name}:\n{value}" for name, value in sections if value)


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
                ChapterSummary(c.number, c.title, c.summary)
                for c in book.chapters
                if c.number < chapter_number and c.summary
            ),
            chapter_title=chapter.title,
            chapter_objective=chapter.objective,
        )
