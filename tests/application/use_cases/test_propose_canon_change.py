from __future__ import annotations

from book_loop.application.use_cases.propose_canon_change import ProposeCanonChange
from book_loop.domain.models import AssertionStatus, CanonicalFact


class FakeKnowledgeRepository:
    def __init__(self, facts: list[CanonicalFact]) -> None:
        self.facts = facts
        self.saved = []

    def list_active_canonical_facts(self, *, book_id: str) -> list[CanonicalFact]:
        return [fact for fact in self.facts if fact.book_id == book_id and fact.active]

    def save_assertion(self, assertion) -> None:
        self.saved.append(assertion)


def canonical_fact() -> CanonicalFact:
    return CanonicalFact(
        id="fact-1",
        book_id="book-1",
        assertion_id="assertion-1",
        statement="Alice lives in Paris.",
        subject="Alice",
        predicate="lives_in",
        object="Paris",
        decision_id="decision-1",
    )


def test_propose_change_creates_proposed_assertion_without_mutating_canon():
    fact = canonical_fact()
    repository = FakeKnowledgeRepository([fact])

    proposal = ProposeCanonChange(repository).execute(
        book_id="book-1",
        fact_id="fact-1",
        statement="Alice lives in Lyon.",
        object="Lyon",
    )

    assert proposal.status is AssertionStatus.PROPOSED
    assert proposal.subject == fact.subject
    assert proposal.predicate == fact.predicate
    assert proposal.object == "Lyon"
    assert proposal.statement == "Alice lives in Lyon."
    assert proposal.source_document_id == "canon-change:fact-1"
    assert proposal.chunk_id == "canon-change:fact-1"
    assert proposal.evidence_id == "canon-change:fact-1"
    assert repository.saved == [proposal]
    assert fact.active is True
    assert fact.object == "Paris"


def test_propose_change_rejects_unknown_or_empty_input():
    repository = FakeKnowledgeRepository([canonical_fact()])
    use_case = ProposeCanonChange(repository)

    try:
        use_case.execute(
            book_id="book-1",
            fact_id="missing",
            statement="Alice lives in Lyon.",
            object="Lyon",
        )
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected unknown fact to fail")

    for statement, object_value in [("", "Lyon"), ("Alice lives in Lyon.", "")]:
        try:
            use_case.execute(
                book_id="book-1",
                fact_id="fact-1",
                statement=statement,
                object=object_value,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Expected empty proposal input to fail")
