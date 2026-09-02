from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.domain.protocols import KnowledgeRepository


class ContextBuilder:
    """Build bounded prompt context from book state and active Canon."""

    def __init__(self, knowledge_repository: KnowledgeRepository | None = None) -> None:
        self.knowledge_repository = knowledge_repository

    def for_chapter(self, book: BookState, chapter_number: int) -> str:
        chapter = next(c for c in book.chapters if c.number == chapter_number)
        summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}"
            for c in book.chapters
            if c.number < chapter_number and c.summary
        )
        constraints = "\n".join(f"- {item}" for item in book.constraints)
        outline = book.outline.render() if book.outline else ""
        canonical = self._canonical_context(book.id)
        return "\n\n".join([
            f"AUTHOR IDEA:\n{book.author_idea}",
            f"THEME:\n{book.theme}",
            f"LORE:\n{book.lore}",
            f"CANONICAL KNOWLEDGE:\n{canonical}",
            f"GLOBAL OUTLINE:\n{outline}",
            f"CONSTRAINTS:\n{constraints}",
            f"PREVIOUS CHAPTER SUMMARIES:\n{summaries}",
            f"CURRENT CHAPTER OBJECTIVE:\n{chapter.objective}",
        ])

    def _canonical_context(self, book_id: str) -> str:
        if self.knowledge_repository is None:
            return "No canonical facts available."
        facts = self.knowledge_repository.list_active_canonical_facts(book_id=book_id)
        if not facts:
            return "No canonical facts available."
        return "\n".join(
            f"- {fact.statement} [canonical v{fact.version}; fact_id={fact.id}; assertion_id={fact.assertion_id}]"
            for fact in facts
        )
