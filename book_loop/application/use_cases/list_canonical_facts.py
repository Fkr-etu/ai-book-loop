from __future__ import annotations

from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import KnowledgeRepository


class ListCanonicalFacts:
    """Return only the currently active Canon facts for a book."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(self, *, book_id: str) -> list[CanonicalFact]:
        return self.repository.list_active_canonical_facts(book_id=book_id)
