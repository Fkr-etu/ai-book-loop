from __future__ import annotations

from uuid import uuid4

from book_loop.domain.canon_change import CanonChangeProposal
from book_loop.domain.protocols import KnowledgeRepository


class ProposeCanonChange:
    """Create an author-authored Canon change proposal without mutating Canon."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        book_id: str,
        fact_id: str,
        statement: str,
        object: str,
        proposer_id: str | None = None,
        rationale: str = "",
    ) -> CanonChangeProposal:
        facts = self.repository.list_active_canonical_facts(book_id=book_id)
        fact = next((item for item in facts if item.id == fact_id), None)
        if fact is None:
            raise KeyError(f"Unknown active canonical fact: {fact_id}")
        if not statement.strip() or not object.strip():
            raise ValueError("statement and object must not be empty")

        proposal = CanonChangeProposal(
            id=str(uuid4()),
            book_id=book_id,
            canonical_fact_id=fact.id,
            statement=statement.strip(),
            subject=fact.subject,
            predicate=fact.predicate,
            object=object.strip(),
            proposer_id=proposer_id,
            rationale=rationale.strip(),
        )
        self.repository.save_canon_change_proposal(proposal)
        return proposal
