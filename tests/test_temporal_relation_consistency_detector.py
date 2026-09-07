from book_loop.application.use_cases.temporal_relation_consistency_detector import (
    TemporalRelationConsistencyDetector,
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


def test_temporal_detector_reports_reverse_order() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="battle", predicate="before", object_="treaty"),
            assertion("b", subject="treaty", predicate="before", object_="battle"),
        ]
    )

    issues = TemporalRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "timeline"
    assert issues[0].severity == "error"
    assert {issues[0].left_assertion_id, issues[0].right_assertion_id} == {"a", "b"}


def test_temporal_detector_normalizes_after_into_before() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="battle", predicate="before", object_="treaty"),
            assertion("b", subject="treaty", predicate="after", object_="battle"),
        ]
    )

    assert TemporalRelationConsistencyDetector(repository).detect(book_id="book-1") == []


def test_temporal_detector_reports_explicit_negative_relation() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="battle", predicate="before", object_="treaty"),
            assertion("b", subject="battle", predicate="not_before", object_="treaty"),
        ]
    )

    issues = TemporalRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].left_evidence == "battle before treaty"
    assert issues[0].right_evidence == "battle not_before treaty"


def test_temporal_detector_ignores_rejected_assertions() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="battle", predicate="before", object_="treaty"),
            assertion(
                "b",
                subject="treaty",
                predicate="before",
                object_="battle",
                status=AssertionStatus.REJECTED,
            ),
        ]
    )

    assert TemporalRelationConsistencyDetector(repository).detect(book_id="book-1") == []
