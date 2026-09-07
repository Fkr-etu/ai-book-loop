import pytest

from book_loop.application.use_cases.character_continuity_detector import CharacterContinuityDetector
from book_loop.application.use_cases.narrative_consistency_support import parse_year
from book_loop.application.use_cases.timeline_consistency_detector import TimelineConsistencyDetector
from book_loop.application.use_cases.world_continuity_detector import WorldContinuityDetector
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


def test_timeline_detector_reports_birth_after_death_with_evidence() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("birth", subject="Marie", predicate="birth_date", object_="1985"),
            assertion("death", subject="Marie", predicate="death_date", object_="1972"),
        ]
    )

    issues = TimelineConsistencyDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "timeline"
    assert issues[0].severity == "error"
    assert issues[0].left_evidence == "Marie birth_date 1985"
    assert issues[0].right_evidence == "Marie death_date 1972"


def test_timeline_detector_supports_normalized_date_expressions() -> None:
    pytest.importorskip("dateparser")
    assert parse_year("12 mars 1985") == 1985


def test_timeline_detector_ignores_relative_dates_without_reference_context() -> None:
    pytest.importorskip("dateparser")
    assert parse_year("demain") is None


def test_timeline_detector_is_idempotent_and_ignores_rejected_assertions() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("birth", subject="Marie", predicate="born", object_="1985"),
            assertion("death", subject="Marie", predicate="died", object_="1972"),
            assertion(
                "rejected",
                subject="Marie",
                predicate="death_date",
                object_="1960",
                status=AssertionStatus.REJECTED,
            ),
        ]
    )
    detector = TimelineConsistencyDetector(repository)

    first = detector.detect(book_id="book-1")
    second = detector.detect(book_id="book-1")

    assert [issue.id for issue in first] == [issue.id for issue in second]
    assert len(first) == 1


def test_character_detector_reports_explicit_incompatible_states() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("alive", subject="Paul", predicate="alive", object_="true"),
            assertion("dead", subject="Paul", predicate="dead", object_="true"),
        ]
    )

    issues = CharacterContinuityDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "character_continuity"
    assert issues[0].severity == "error"


def test_character_detector_does_not_flag_unrelated_states() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("alive", subject="Paul", predicate="alive", object_="true"),
            assertion("single", subject="Paul", predicate="single", object_="true"),
        ]
    )

    assert CharacterContinuityDetector(repository).detect(book_id="book-1") == []


def test_world_detector_reports_explicit_positive_negative_relation() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("contains", subject="Castle", predicate="contains", object_="secret room"),
            assertion(
                "not-contains",
                subject="Castle",
                predicate="does_not_contain",
                object_="secret room",
            ),
        ]
    )

    issues = WorldContinuityDetector(repository).detect(book_id="book-1")

    assert len(issues) == 1
    assert issues[0].category == "world_continuity"
    assert issues[0].left_assertion_id == "contains"
    assert issues[0].right_assertion_id == "not-contains"


def test_world_detector_requires_same_relation_target() -> None:
    repository = FakeKnowledgeRepository(
        [
            assertion("contains", subject="Castle", predicate="contains", object_="secret room"),
            assertion(
                "not-library",
                subject="Castle",
                predicate="does_not_contain",
                object_="library",
            ),
        ]
    )

    assert WorldContinuityDetector(repository).detect(book_id="book-1") == []
