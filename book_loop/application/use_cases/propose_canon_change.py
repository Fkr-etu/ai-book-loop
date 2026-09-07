from __future__ import annotations

from uuid import uuid4

from book_loop.domain.models import Assertion, AssertionStatus, CanonicalFact
from book_loop.domain.protocols import KnowledgeRepository


class ProposeCanonChange:
    """Create a proposed assertion from an active Canon fact without mutating Canon."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        book_id: str,
        fact_id: str,
        statement: str,
        object: str,
        reviewer_id: str | None = None,
    ) -> Assertion:
        facts = self.repository.list_active_canonical_facts(book_id=book_id)
        fact = next((item for item in facts if item.id == fact_id), None)
        if fact is None:
            raise KeyError(f"Unknown active canonical fact: {fact_id}")
        if not statement.strip() or not object.strip():
            raise ValueError("statement and object must not be empty")

        source_id = f"canon-change:{fact.id}"
        assertion = Assertion(
            id=str(uuid4()),
            source_document_id=source_id,
            chunk_id=source_id,
            statement=statement.strip(),
            subject=fact.subject,
            predicate=fact.predicate,
            object=object.strip(),
            confidence=1.0,
            status=AssertionStatus.PROPOSED,
            evidence_id=source_id,
        )
        self.repository.save_assertion(assertion)
        return assertion
