from book_loop.application.use_cases.boolean_contradiction_consistency_detector import (
    BooleanContradictionConsistencyDetector,
)
from book_loop.domain.models import Assertion, AssertionStatus, Evidence


class FakeKnowledgeRepository:
    def __init__(self, assertions: list[Assertion]) -> None:
        self.assertions = assertions
        self.evidence = [
            Evidence(
                id=f"e-{a.id}",
                assertion_id=a.id,
                source_document_id=a.source_document_id,
                chunk_id=a.chunk_id,
                start_offset=0,
                end_offset=len(a.statement),
                excerpt=a.statement,
            )
            for a in assertions
        ]

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return self.assertions

    def list_evidence(self, *, book_id: str) -> list[Evidence]:
        return self.evidence


def make_assertion(i: str, subject: str, predicate: str, object_: str, status=AssertionStatus.ACCEPTED):
    return Assertion(
        id=i,
        source_document_id="doc-1",
        chunk_id="chunk-1",
        statement=f"{subject} {predicate} {object_}",
        subject=subject,
        predicate=predicate,
        object=object_,
        confidence=0.95,
        status=status,
        evidence_id=f"e-{i}",
    )


def test_detects_explicit_positive_negative_pair() -> None:
    repo = FakeKnowledgeRepository([
        make_assertion("a", "Alice", "is", "alive"),
        make_assertion("b", "Alice", "is_not", "alive"),
    ])
    issues = BooleanContradictionConsistencyDetector(repo).detect(book_id="book-1")
    assert len(issues) == 1
    assert {issues[0].left_assertion_id, issues[0].right_assertion_id} == {"a", "b"}


def test_does_not_flag_unrelated_predicates() -> None:
    repo = FakeKnowledgeRepository([
        make_assertion("a", "Alice", "is", "alive"),
        make_assertion("b", "Alice", "has", "alive"),
    ])
    assert BooleanContradictionConsistencyDetector(repo).detect(book_id="book-1") == []


def test_ignores_rejected_assertions() -> None:
    repo = FakeKnowledgeRepository([
        make_assertion("a", "Alice", "is", "alive"),
        make_assertion("b", "Alice", "is_not", "alive", AssertionStatus.REJECTED),
    ])
    assert BooleanContradictionConsistencyDetector(repo).detect(book_id="book-1") == []


def test_preserves_evidence() -> None:
    repo = FakeKnowledgeRepository([
        make_assertion("a", "Alice", "can", "swim"),
        make_assertion("b", "Alice", "cannot", "swim"),
    ])
    issue = BooleanContradictionConsistencyDetector(repo).detect(book_id="book-1")[0]
    assert issue.left_evidence
    assert issue.right_evidence
