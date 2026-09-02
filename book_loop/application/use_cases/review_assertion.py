from __future__ import annotations

from uuid import uuid4

from book_loop.domain.models import AssertionStatus, CanonicalFact, ReviewDecision, ReviewDecisionType
from book_loop.domain.protocols import KnowledgeRepository


class ReviewAssertion:
    """Apply an explicit review decision; only acceptance can create Canon."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(
        self,
        *,
        book_id: str,
        assertion_id: str,
        decision: ReviewDecisionType,
        reviewer_id: str | None = None,
        rationale: str = "",
    ) -> ReviewDecision:
        assertions = {item.id: item for item in self.repository.list_assertions(book_id=book_id)}
        assertion = assertions.get(assertion_id)
        if assertion is None:
            raise KeyError(f"Unknown assertion: {assertion_id}")
        if assertion.status in {AssertionStatus.ACCEPTED, AssertionStatus.REJECTED}:
            raise ValueError(f"Assertion {assertion_id} already has a terminal status")

        review = ReviewDecision(
            id=str(uuid4()),
            assertion_id=assertion_id,
            decision=decision,
            reviewer_id=reviewer_id,
            rationale=rationale,
        )
        self.repository.save_review_decision(review)

        if decision is ReviewDecisionType.REJECT:
            self.repository.set_assertion_status(assertion_id, AssertionStatus.REJECTED)
            return review
        if decision is ReviewDecisionType.DEFER:
            self.repository.set_assertion_status(assertion_id, AssertionStatus.DEFERRED)
            return review

        self.repository.set_assertion_status(assertion_id, AssertionStatus.ACCEPTED)
        for candidate in assertions.values():
            if not self._conflicts(assertion, candidate):
                continue
            if candidate.status in {AssertionStatus.PROPOSED, AssertionStatus.DEFERRED}:
                competing_review = ReviewDecision(
                    id=str(uuid4()),
                    assertion_id=candidate.id,
                    decision=ReviewDecisionType.REJECT,
                    reviewer_id=reviewer_id,
                    rationale=f"Superseded by accepted assertion {assertion_id}.",
                )
                self.repository.save_review_decision(competing_review)
                self.repository.set_assertion_status(candidate.id, AssertionStatus.REJECTED)
            self.repository.resolve_conflict(candidate.id, assertion_id, assertion_id)

        self.repository.deactivate_canonical_facts(
            book_id=book_id,
            subject=assertion.subject,
            predicate=assertion.predicate,
        )
        fact = CanonicalFact(
            id=str(uuid4()),
            book_id=book_id,
            assertion_id=assertion.id,
            statement=assertion.statement,
            subject=assertion.subject,
            predicate=assertion.predicate,
            object=assertion.object,
            decision_id=review.id,
            version=self.repository.next_canonical_version(
                book_id=book_id,
                subject=assertion.subject,
                predicate=assertion.predicate,
            ),
        )
        self.repository.save_canonical_fact(fact)
        return review

    @staticmethod
    def _conflicts(left, right) -> bool:
        return (
            left.id != right.id
            and left.subject.strip().casefold() == right.subject.strip().casefold()
            and left.predicate.strip().casefold() == right.predicate.strip().casefold()
            and left.object.strip().casefold() != right.object.strip().casefold()
        )
