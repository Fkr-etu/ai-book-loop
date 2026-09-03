from __future__ import annotations

from book_loop.application.services.retrieval import CanonicalRetriever
from book_loop.domain.models import BookState
from book_loop.domain.protocols import CanonicalKnowledgeRetriever, KnowledgeRepository


class ContextBuilder:
    """Build bounded prompt context from book state and relevant active Canon."""

    def __init__(
        self,
        knowledge_repository: KnowledgeRepository | None = None,
        retriever: CanonicalKnowledgeRetriever | None = None,
    ) -> None:
        self.knowledge_repository = knowledge_repository
        self.retriever = retriever or CanonicalRetriever()

    def for_chapter(self, book: BookState, chapter_number: int) -> str:
        chapter = next(c for c in book.chapters if c.number == chapter_number)
        summaries = "\n".join(
            f"Chapter {c.number} ({c.title}): {c.summary}"
            for c in book.chapters
            if c.number < chapter_number and c.summary
        )
        constraints = "\n".join(f"- {item}" for item in book.constraints)
        outline = book.outline.render() if book.outline else ""
        query = " ".join((chapter.title, chapter.objective, summaries))
        canonical = self._canonical_context(book.id, query=query)
        brief = self._creative_brief_context(book)
        return "\n\n".join([
            f"AUTHOR IDEA:\n{book.author_idea}",
            f"CREATIVE BRIEF:\n{brief}",
            f"THEME:\n{book.theme}",
            f"LORE:\n{book.lore}",
            f"CANONICAL KNOWLEDGE:\n{canonical}",
            f"GLOBAL OUTLINE:\n{outline}",
            f"CONSTRAINTS:\n{constraints}",
            f"PREVIOUS CHAPTER SUMMARIES:\n{summaries}",
            f"CURRENT CHAPTER OBJECTIVE:\n{chapter.objective}",
        ])

    @staticmethod
    def _creative_brief_context(book: BookState) -> str:
        if book.creative_brief is None:
            return "No structured creative brief provided."
        brief = book.creative_brief
        lines = [f"Premise: {brief.premise}"]
        if brief.audience:
            lines.append(f"Audience: {brief.audience}")
        if brief.tone:
            lines.append(f"Tone: {brief.tone}")
        if brief.themes:
            lines.append(f"Themes: {', '.join(brief.themes)}")
        if brief.must_include:
            lines.append(f"Must include: {', '.join(brief.must_include)}")
        if brief.must_avoid:
            lines.append(f"Must avoid: {', '.join(brief.must_avoid)}")
        return "\n".join(lines)

    def _canonical_context(self, book_id: str, *, query: str) -> str:
        if self.knowledge_repository is None:
            return "No canonical facts available."
        facts = self.knowledge_repository.list_active_canonical_facts(book_id=book_id)
        relevant = self.retriever.retrieve(facts, query=query)
        if not relevant:
            return "No relevant canonical facts available."
        return "\n".join(
            f"- {fact.statement} [canonical v{fact.version}; fact_id={fact.id}; assertion_id={fact.assertion_id}]"
            for fact in relevant
        )
