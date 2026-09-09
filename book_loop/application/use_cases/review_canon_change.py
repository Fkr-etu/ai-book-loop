from __future__ import annotations

import logging
from contextlib import nullcontext
from datetime import UTC, datetime
from uuid import uuid4

from book_loop.application.services.canonical_fact_embedding_indexer import CanonicalFactEmbeddingIndexer
from book_loop.domain.canon_change import (
    CanonChangeProposalStaleError,
    CanonChangeProposalStatus,
    CanonChangeReviewDecision,
    CanonChangeReviewDecisionType,
)
from book_loop.domain.models import CanonicalFact
from book_loop.domain.protocols import KnowledgeRepository

logger = logging.getLogger(__name__)


class ReviewCanonChange:
    """Apply an explicit review decision to an author Canon change proposal."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        embedding_indexer: CanonicalFactEmbeddingIndexer | None = None,
    ) -> None:
        self.repository = repository
        self.embedding_indexer = embedding_indexer

    def execute(self, *, book_id: str, proposal_id: str, decision: CanonChangeReviewDecisionType, reviewer_id: str | None = None, rationale: str = "") -> CanonChangeReviewDecision:
        transaction = getattr(self.repository, "transaction", None)
        context = transaction() if transaction is not None else nullcontext()
        with context:
            lock = getattr(self.repository, "lock_canon_change_proposal", None)
            if lock is not None:
                lock(proposal_id)
            review, fact = self._execute_in_transaction(book_id=book_id, proposal_id=proposal_id, decision=decision, reviewer_id=reviewer_id, rationale=rationale)

        if fact is not None and self.embedding_indexer is not None:
            try:
                self.embedding_indexer.index(fact)
            except Exception:
                logger.exception("Unable to index canonical fact %s", fact.id)
        return review

    def _execute_in_transaction(self, *, book_id: str, proposal_id: str, decision: CanonChangeReviewDecisionType, reviewer_id: str | None, rationale: str) -> tuple[CanonChangeReviewDecision, CanonicalFact | None]:
        proposal = self.repository.get_canon_change_proposal(proposal_id)
        if proposal.book_id != book_id:
            raise KeyError(f"Unknown Canon change proposal: {proposal_id}")
        if proposal.status is not CanonChangeProposalStatus.PROPOSED:
            raise ValueError(f"Canon change proposal {proposal_id} already has a terminal status")

        current_fact = None
        if decision is CanonChangeReviewDecisionType.ACCEPT:
            active_facts = self.repository.list_active_canonical_facts(book_id=book_id)
            current_fact = next((fact for fact in active_facts if fact.id == proposal.canonical_fact_id), None)
            if current_fact is None:
                raise CanonChangeProposalStaleError("Canon change proposal is stale: its source fact is no longer active")
            if (
                current_fact.subject.strip().casefold() != proposal.subject.strip().casefold()
                or current_fact.predicate.strip().casefold() != proposal.predicate.strip().casefold()
                or current_fact.object.strip().casefold() == proposal.object.strip().casefold()
            ):
                raise CanonChangeProposalStaleError("Canon change proposal is stale: its source fact has changed")

        review = CanonChangeReviewDecision(
            id=str(uuid4()), proposal_id=proposal.id, decision=decision, reviewer_id=reviewer_id,
            rationale=rationale.strip(), created_at=datetime.now(UTC).isoformat(),
        )
        self.repository.save_canon_change_review_decision(review)

        if decision is CanonChangeReviewDecisionType.REJECT:
            self.repository.set_canon_change_proposal_status(proposal.id, CanonChangeProposalStatus.REJECTED)
            return review, None

        assert current_fact is not None
        self.repository.deactivate_canonical_facts(book_id=book_id, subject=current_fact.subject, predicate=current_fact.predicate)
        next_fact = CanonicalFact(
            id=str(uuid4()), book_id=book_id, assertion_id=current_fact.assertion_id,
            statement=proposal.statement, subject=proposal.subject, predicate=proposal.predicate, object=proposal.object,
            decision_id=review.id,
            version=self.repository.next_canonical_version(book_id=book_id, subject=current_fact.subject, predicate=current_fact.predicate),
            active=True, previous_fact_id=current_fact.id,
        )
        self.repository.save_canonical_fact(next_fact)
        self.repository.set_canon_change_proposal_status(proposal.id, CanonChangeProposalStatus.ACCEPTED)
        return review, next_fact
