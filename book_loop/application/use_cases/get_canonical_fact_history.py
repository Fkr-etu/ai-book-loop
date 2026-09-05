from __future__ import annotations

from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import KnowledgeRepository


class GetCanonicalFactHistory:
    """Return the immutable version history for one Canon subject/predicate pair."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(self, *, book_id: str, subject: str, predicate: str) -> list[CanonicalFact]:
        return self.repository.list_canonical_fact_history(
            book_id=book_id,
            subject=subject,
            predicate=predicate,
        )
