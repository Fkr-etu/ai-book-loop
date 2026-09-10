from __future__ import annotations

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, AssertionStatus
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


class Repository:
    def __init__(self, assertions: list[Assertion]) -> None:
        self.assertions = assertions
        self.conflicts = []

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return self.assertions

    def list_conflicts(self, *, book_id: str):
        return self.conflicts

    def save_conflict(self, conflict) -> None:
        self.conflicts.append(conflict)


class TemporalStore:
    def __init__(self, scopes: dict[str, TemporalScope]) -> None:
        self.scopes = scopes

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self.scopes.get(assertion_id)


def assertion(assertion_id: str, value: str, predicate: str = "porte") -> Assertion:
    return Assertion(
        id=assertion_id,
        source_document_id="source",
        chunk_id=f"chunk-{assertion_id}",
        statement=f"Elara {predicate} {value}",
        subject="Elara",
        predicate=predicate,
        object=value,
        confidence=1.0,
        status=AssertionStatus.ACCEPTED,
        evidence_id=f"evidence-{assertion_id}",
    )


def test_different_story_points_are_narrative_evolution_not_conflict() -> None:
    left = assertion("a1", "Givre-Âme")
    right = assertion("a2", "Cuirasse de Givre")
    repository = Repository([left, right])
    store = TemporalStore({
        "a1": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=1),
        "a2": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
    })

    assert DetectConflicts(repository, temporal_context_store=store).execute(book_id="book") == []


def test_same_story_point_remains_a_conflict() -> None:
    left = assertion("a1", "Givre-Âme")
    right = assertion("a2", "Cuirasse de Givre")
    repository = Repository([left, right])
    store = TemporalStore({
        "a1": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        "a2": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
    })

    assert len(DetectConflicts(repository, temporal_context_store=store).execute(book_id="book")) == 1


def test_timeless_claim_still_conflicts_with_a_time_scoped_claim() -> None:
    left = assertion("a1", "Givre-Âme")
    right = assertion("a2", "Cuirasse de Givre")
    repository = Repository([left, right])
    store = TemporalStore({
        "a1": TemporalScope(),
        "a2": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
    })

    assert len(DetectConflicts(repository, temporal_context_store=store).execute(book_id="book")) == 1


def test_multi_valued_predicate_does_not_conflict() -> None:
    left = assertion("a1", "Lentille", predicate="owns")
    right = assertion("a2", "Analyseur de Flux", predicate="owns")
    repository = Repository([left, right])

    assert DetectConflicts(repository).execute(book_id="book") == []
