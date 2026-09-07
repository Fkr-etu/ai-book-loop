from book_loop.application.use_cases.inverse_relation_consistency_detector import (
    InverseRelationConsistencyDetector,
)
from book_loop.domain.models import Assertion, AssertionStatus, Evidence


class FakeKnowledgeRepository:
    def __init__(self, assertions: list[Assertion]) -> None:
        self.assertions = assertions
        self.evidence = [
            Evidence(
                id=f"e-{assertion.id}",
                assertion_id=assertion.id,
                source_document_id=assertion.source_document_id,
                chunk_id=assertion.chunk_id,
                start_offset=0,
                end_offset=len(assertion.statement),
                excerpt=assertion.statement,
            )
            for assertion in assertions
        ]

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return self.assertions

    def list_evidence(self, *, book_id: str) -> list[Evidence]:
        return self.evidence


def assertion(
    assertion_id: str,
    *,
    subject: str,
    predicate: str,
    object_: str,
    status: AssertionStatus = AssertionStatus.ACCEPTED,
) -> Assertion:
    return Assertion(
        id=assertion_id,
        source_document_id="doc-1",
        chunk_id="chunk-1",
        statement=f"{subject} {predicate} {object_}",
        subject=subject,
        predicate=predicate,
        object=object_,
        confidence=0.95,
        status=status,
        evidence_id=f"e-{assertion_id}",
    )


def test_inverse_relation_detector_reports_parent_child_role_conflict() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="alice", predicate="parent_of", object_="bob"),
            assertion("b", subject="alice", predicate="child_of", object_="bob"),
        ]
    )

    issues = InverseRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "relationship_continuity"
    assert issues[0].severity == "error"
    assert {issues[0].left_assertion_id, issues[0].right_assertion_id} == {"a", "b"}


def test_inverse_relation_detector_reports_older_younger_role_conflict() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="alice", predicate="older_than", object_="bob"),
            assertion("b", subject="alice", predicate="younger_than", object_="bob"),
        ]
    )

    issues = InverseRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].left_evidence == "alice older_than bob"
    assert issues[0].right_evidence == "alice younger_than bob"


def test_inverse_relation_detector_ignores_rejected_assertions() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="alice", predicate="parent_of", object_="bob"),
            assertion(
                "b",
                subject="alice",
                predicate="child_of",
                object_="bob",
                status=AssertionStatus.REJECTED,
            ),
        ]
    )

    assert InverseRelationConsistencyDetector(repository).detect(book_id="book-1") == []


def test_inverse_relation_detector_does_not_flag_correct_inverse_orientation() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="alice", predicate="parent_of", object_="bob"),
            assertion("b", subject="bob", predicate="child_of", object_="alice"),
        ]
    )

    assert InverseRelationConsistencyDetector(repository).detect(book_id="book-1") == []
