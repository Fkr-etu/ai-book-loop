from __future__ import annotations

from book_loop.application.use_cases.consistency_coverage import measure_coverage
from book_loop.domain.models import Assertion, AssertionStatus
from book_loop.domain.predicate_semantics import PredicateExclusivity, PredicateKind, PredicateSemantics, PredicateSemanticsRegistry
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


class TemporalStore:
    def __init__(self, scopes: dict[str, TemporalScope]) -> None:
        self.scopes = scopes

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self.scopes.get(assertion_id)


class TestPredicateSemanticsRegistry(PredicateSemanticsRegistry):
    _SEMANTICS = {
        **PredicateSemanticsRegistry._SEMANTICS,
        "enters": PredicateSemantics(PredicateKind.EVENT, PredicateExclusivity.UNKNOWN),
    }


def assertion(assertion_id: str, subject: str, predicate: str, value: str, *, status: AssertionStatus = AssertionStatus.ACCEPTED) -> Assertion:
    return Assertion(id=assertion_id, source_document_id="source", chunk_id=f"chunk-{assertion_id}", statement=f"{subject} {predicate} {value}", subject=subject, predicate=predicate, object=value, confidence=1.0, status=status, evidence_id=f"evidence-{assertion_id}")


def test_coverage_exposes_each_detector_filter_without_changing_rules() -> None:
    assertions = [
        assertion("a", "Kael", "age", "20"),
        assertion("b", "Kael", "age", "21"),
        assertion("c", "Kael", "occupation", "ingénieur"),
        assertion("d", "Elara", "age", "30"),
        assertion("e", "Kael", "owns", "Lentille"),
        assertion("f", "Kael", "owns", "Analyseur"),
        assertion("g", "Kael", "enters", "Port"),
        assertion("h", "Kael", "enters", "Tour"),
        assertion("i", "Kael", "age", "20"),
        assertion("j", "Kael", "age", "22"),
        assertion("rejected", "Kael", "age", "99", status=AssertionStatus.REJECTED),
    ]
    scopes = {
        "a": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=1),
        "b": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        "j": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=1),
    }
    coverage = measure_coverage(
        assertions[:-1],
        temporal_context_store=TemporalStore(scopes),
        predicate_semantics=TestPredicateSemanticsRegistry(),
    )

    assert coverage.total_assertions == 10
    assert coverage.total_pairs == 45
    assert coverage.same_subject_pairs == 36
    assert coverage.same_predicate_pairs == 8
    assert coverage.different_object_pairs == 7
    assert coverage.action_event_excluded == 1
    assert coverage.multi_valued_excluded == 1
    assert coverage.temporal_missing_scope == 2
    assert coverage.temporal_non_overlapping == 2
    assert coverage.temporal_overlapping == 1
    assert coverage.final_candidates == 1


def test_coverage_accepts_only_the_assertions_given_to_it() -> None:
    rejected = assertion("r", "Kael", "age", "99", status=AssertionStatus.REJECTED)
    accepted = assertion("a", "Kael", "age", "20")
    coverage = measure_coverage([accepted], temporal_context_store=None)

    assert coverage.total_assertions == 1
    assert coverage.total_pairs == 0
    assert rejected.status is AssertionStatus.REJECTED