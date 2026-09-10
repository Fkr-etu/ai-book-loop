from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from book_loop.domain.models import Assertion
from book_loop.domain.predicate_semantics import (
    PredicateExclusivity,
    PredicateKind,
    PredicateSemanticsRegistry,
)
from book_loop.domain.temporal import AssertionTemporalContextStore, TemporalRelation


class PairDisposition(StrEnum):
    SUBJECT_MISMATCH = "subject_mismatch"
    PREDICATE_MISMATCH = "predicate_mismatch"
    SAME_OBJECT = "same_object"
    ACTION_EVENT = "action_event"
    MULTI_VALUED = "multi_valued"
    TEMPORAL_MISSING_SCOPE = "temporal_missing_scope"
    TEMPORAL_NON_OVERLAPPING = "temporal_non_overlapping"
    CANDIDATE = "candidate"


@dataclass(frozen=True)
class ConflictCoverage:
    total_assertions: int
    total_pairs: int
    subject_mismatch: int
    same_subject_pairs: int
    predicate_mismatch: int
    same_predicate_pairs: int
    same_object: int
    different_object_pairs: int
    action_event_excluded: int
    multi_valued_excluded: int
    temporal_missing_scope: int
    temporal_non_overlapping: int
    temporal_overlapping: int
    final_candidates: int


def classify_pair(
    left: Assertion,
    right: Assertion,
    *,
    temporal_context_store: AssertionTemporalContextStore | None,
    predicate_semantics: PredicateSemanticsRegistry,
) -> PairDisposition:
    if left.id == right.id:
        return PairDisposition.SUBJECT_MISMATCH
    if left.subject.strip().casefold() != right.subject.strip().casefold():
        return PairDisposition.SUBJECT_MISMATCH
    if left.predicate.strip().casefold() != right.predicate.strip().casefold():
        return PairDisposition.PREDICATE_MISMATCH
    if left.object.strip().casefold() == right.object.strip().casefold():
        return PairDisposition.SAME_OBJECT

    semantics = predicate_semantics.get(left.predicate)
    if semantics.kind in {PredicateKind.ACTION, PredicateKind.EVENT}:
        return PairDisposition.ACTION_EVENT
    if semantics.exclusivity is PredicateExclusivity.MULTI_VALUED:
        return PairDisposition.MULTI_VALUED

    if temporal_context_store is None:
        return PairDisposition.CANDIDATE
    left_scope = temporal_context_store.get_temporal_scope(assertion_id=left.id)
    right_scope = temporal_context_store.get_temporal_scope(assertion_id=right.id)
    if left_scope is None or right_scope is None:
        return PairDisposition.TEMPORAL_MISSING_SCOPE

    # The finer temporal model is now the source of truth for ordered scopes.
    # Only BEFORE/AFTER are ineligible; all other ordered relations remain
    # eligible for the semantic conflict detector.
    relation = left_scope.relation_to(right_scope)
    if relation in {TemporalRelation.BEFORE, TemporalRelation.AFTER}:
        return PairDisposition.TEMPORAL_NON_OVERLAPPING
    return PairDisposition.CANDIDATE


def measure_coverage(
    assertions: list[Assertion],
    *,
    temporal_context_store: AssertionTemporalContextStore | None,
    predicate_semantics: PredicateSemanticsRegistry | None = None,
) -> ConflictCoverage:
    registry = predicate_semantics or PredicateSemanticsRegistry()
    counts = {disposition: 0 for disposition in PairDisposition}
    total_pairs = 0

    for index, left in enumerate(assertions):
        for right in assertions[index + 1 :]:
            total_pairs += 1
            counts[classify_pair(
                left,
                right,
                temporal_context_store=temporal_context_store,
                predicate_semantics=registry,
            )] += 1

    same_subject = total_pairs - counts[PairDisposition.SUBJECT_MISMATCH]
    same_predicate = same_subject - counts[PairDisposition.PREDICATE_MISMATCH]
    different_object = same_predicate - counts[PairDisposition.SAME_OBJECT]

    return ConflictCoverage(
        total_assertions=len(assertions),
        total_pairs=total_pairs,
        subject_mismatch=counts[PairDisposition.SUBJECT_MISMATCH],
        same_subject_pairs=same_subject,
        predicate_mismatch=counts[PairDisposition.PREDICATE_MISMATCH],
        same_predicate_pairs=same_predicate,
        same_object=counts[PairDisposition.SAME_OBJECT],
        different_object_pairs=different_object,
        action_event_excluded=counts[PairDisposition.ACTION_EVENT],
        multi_valued_excluded=counts[PairDisposition.MULTI_VALUED],
        temporal_missing_scope=counts[PairDisposition.TEMPORAL_MISSING_SCOPE],
        temporal_non_overlapping=counts[PairDisposition.TEMPORAL_NON_OVERLAPPING],
        temporal_overlapping=counts[PairDisposition.CANDIDATE],
        final_candidates=counts[PairDisposition.CANDIDATE],
    )
