from book_loop.application.use_cases.causal_relation_consistency_detector import (
    CausalRelationConsistencyDetector,
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


def test_causal_detector_reports_effect_before_cause() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="fire", predicate="causes", object_="alarm"),
            assertion("b", subject="alarm", predicate="before", object_="fire"),
        ]
    )

    issues = CausalRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "timeline"
    assert issues[0].severity == "error"
    assert {issues[0].left_assertion_id, issues[0].right_assertion_id} == {"a", "b"}


def test_causal_detector_reports_explicit_negative_causality() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="fire", predicate="causes", object_="alarm"),
            assertion("b", subject="fire", predicate="does_not_cause", object_="alarm"),
        ]
    )

    issues = CausalRelationConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "causality"
    assert issues[0].left_evidence == "fire causes alarm"
    assert issues[0].right_evidence == "fire does_not_cause alarm"


def test_causal_detector_ignores_rejected_assertions() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="fire", predicate="causes", object_="alarm"),
            assertion(
                "b",
                subject="alarm",
                predicate="before",
                object_="fire",
                status=AssertionStatus.REJECTED,
            ),
        ]
    )

    assert CausalRelationConsistencyDetector(repository).detect(book_id="book-1") == []


def test_causal_detector_does_not_flag_unrelated_temporal_facts() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("a", subject="fire", predicate="causes", object_="alarm"),
            assertion("b", subject="rain", predicate="before", object_="sunset"),
        ]
    )

    assert CausalRelationConsistencyDetector(repository).detect(book_id="book-1") == []
