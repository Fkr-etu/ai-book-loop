from book_loop.application.use_cases.consistency_coverage import PairDisposition, classify_pair
from book_loop.domain.epistemic import AssertionEpistemic, AuthorityLevel, EpistemicStatus
from book_loop.domain.models import Assertion
from book_loop.domain.predicate_semantics import PredicateSemanticsRegistry
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


class EpistemicStore:
    def __init__(self, values: dict[str, AssertionEpistemic]) -> None:
        self.values = values

    def get_epistemic(self, *, assertion_id: str) -> AssertionEpistemic | None:
        return self.values.get(assertion_id)


class TemporalStore:
    def __init__(self, values: dict[str, TemporalScope]) -> None:
        self.values = values

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self.values.get(assertion_id)


def assertion(identifier: str, value: str) -> Assertion:
    return Assertion(
        id=identifier,
        source_document_id="source",
        chunk_id="chunk",
        statement=f"Kael lives in {value}",
        subject="Kael",
        predicate="lives_in",
        object=value,
        confidence=1.0,
        evidence_id=f"evidence-{identifier}",
    )


def test_belief_against_canonical_is_deferred_instead_of_hard_conflict() -> None:
    left = assertion("left", "Citadel")
    right = assertion("right", "Bas-Fonds")
    epistemic = EpistemicStore(
        {
            "left": AssertionEpistemic(
                status=EpistemicStatus.BELIEVED,
                authority=AuthorityLevel.CHARACTER,
            ),
            "right": AssertionEpistemic(
                status=EpistemicStatus.CANONICAL,
                authority=AuthorityLevel.CANONICAL,
            ),
        }
    )
    temporal = TemporalStore(
        {
            "left": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
            "right": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        }
    )

    assert classify_pair(
        left,
        right,
        temporal_context_store=temporal,
        predicate_semantics=PredicateSemanticsRegistry(),
        epistemic_store=epistemic,
    ) is PairDisposition.EPISTEMIC_DEFERRED


def test_missing_epistemic_metadata_preserves_existing_candidate_behavior() -> None:
    left = assertion("left", "Citadel")
    right = assertion("right", "Bas-Fonds")
    temporal = TemporalStore(
        {
            "left": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
            "right": TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        }
    )

    assert classify_pair(
        left,
        right,
        temporal_context_store=temporal,
        predicate_semantics=PredicateSemanticsRegistry(),
        epistemic_store=EpistemicStore({}),
    ) is PairDisposition.CANDIDATE
