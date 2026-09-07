from __future__ import annotations

import pytest

from book_loop.application.use_cases.review_canon_change import ReviewCanonChange
from book_loop.domain.canon_change import (
    CanonChangeProposal,
    CanonChangeProposalStatus,
    CanonChangeReviewDecisionType,
)
from book_loop.domain.models import CanonicalFact


class FakeKnowledgeRepository:
    def __init__(self, proposal: CanonChangeProposal, fact: CanonicalFact) -> None:
        self.proposal = proposal
        self.facts = [fact]
        self.decisions = []
        self.statuses = []
        self.next_version_calls = 0

    def transaction(self):
        from contextlib import nullcontext
        return nullcontext()

    def lock_canon_change_proposal(self, proposal_id: str) -> None:
        assert proposal_id == self.proposal.id

    def get_canon_change_proposal(self, proposal_id: str):
        if proposal_id != self.proposal.id:
            raise KeyError(proposal_id)
        return self.proposal

    def list_active_canonical_facts(self, *, book_id: str):
        return [fact for fact in self.facts if fact.book_id == book_id and fact.active]

    def save_canon_change_review_decision(self, decision) -> None:
        self.decisions.append(decision)

    def set_canon_change_proposal_status(self, proposal_id, status) -> None:
        self.statuses.append((proposal_id, status))
        self.proposal.status = status

    def deactivate_canonical_facts(self, *, book_id: str, subject: str, predicate: str) -> None:
        for fact in self.facts:
            if fact.book_id == book_id and fact.subject == subject and fact.predicate == predicate:
                fact.active = False

    def next_canonical_version(self, *, book_id: str, subject: str, predicate: str) -> int:
        self.next_version_calls += 1
        return max((fact.version for fact in self.facts if fact.book_id == book_id and fact.subject == subject and fact.predicate == predicate), default=0) + 1

    def save_canonical_fact(self, fact: CanonicalFact) -> None:
        self.facts.append(fact)


def make_fixture() -> tuple[FakeKnowledgeRepository, CanonicalFact]:
    fact = CanonicalFact(id="fact-1", book_id="book-1", assertion_id="assertion-1", statement="Alice lives in Paris.", subject="Alice", predicate="lives_in", object="Paris", decision_id="decision-1")
    proposal = CanonChangeProposal(id="proposal-1", book_id="book-1", canonical_fact_id=fact.id, statement="Alice lives in Lyon.", subject="Alice", predicate="lives_in", object="Lyon")
    return FakeKnowledgeRepository(proposal, fact), fact


def test_accept_creates_new_active_version_and_preserves_history_link():
    repository, old_fact = make_fixture()
    review = ReviewCanonChange(repository).execute(book_id="book-1", proposal_id="proposal-1", decision=CanonChangeReviewDecisionType.ACCEPT, reviewer_id="user-1")
    new_fact = next(fact for fact in repository.facts if fact.id != old_fact.id)
    assert review.decision is CanonChangeReviewDecisionType.ACCEPT
    assert old_fact.active is False
    assert new_fact.active is True
    assert new_fact.object == "Lyon"
    assert new_fact.statement == "Alice lives in Lyon."
    assert new_fact.version == 2
    assert new_fact.previous_fact_id == old_fact.id
    assert new_fact.decision_id == review.id
    assert repository.proposal.status is CanonChangeProposalStatus.ACCEPTED


def test_reject_does_not_mutate_active_canon():
    repository, fact = make_fixture()
    review = ReviewCanonChange(repository).execute(book_id="book-1", proposal_id="proposal-1", decision=CanonChangeReviewDecisionType.REJECT, reviewer_id="user-1")
    assert review.decision is CanonChangeReviewDecisionType.REJECT
    assert fact.active is True
    assert fact.object == "Paris"
    assert len(repository.facts) == 1
    assert repository.proposal.status is CanonChangeProposalStatus.REJECTED


def test_deciding_terminal_proposal_fails():
    repository, _ = make_fixture()
    repository.proposal.status = CanonChangeProposalStatus.ACCEPTED
    with pytest.raises(ValueError, match="terminal status"):
        ReviewCanonChange(repository).execute(book_id="book-1", proposal_id="proposal-1", decision=CanonChangeReviewDecisionType.REJECT)


def test_accepting_stale_proposal_fails_without_mutation():
    repository, fact = make_fixture()
    fact.active = False
    with pytest.raises(ValueError, match="stale"):
        ReviewCanonChange(repository).execute(book_id="book-1", proposal_id="proposal-1", decision=CanonChangeReviewDecisionType.ACCEPT)
    assert repository.decisions == []
    assert repository.proposal.status is CanonChangeProposalStatus.PROPOSED
