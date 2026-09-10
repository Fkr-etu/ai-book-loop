from __future__ import annotations

from dataclasses import dataclass

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, Conflict
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind
from scripts.consistency_benchmark import GoldLabel, evaluate


@dataclass(frozen=True)
class ConsistencyCase:
    label: str
    left: tuple[str, str, str]
    right: tuple[str, str, str]
    left_scope: TemporalScope | None = None
    right_scope: TemporalScope | None = None
    expected_conflict: bool = False


CASES = (
    # True contradictions: the same state is asserted with incompatible values.
    ConsistencyCase(
        "contradiction",
        ("Elara", "porte", "Givre-Âme"),
        ("Elara", "porte", "Lame-Solaire"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=3),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=3),
        True,
    ),
    ConsistencyCase(
        "contradiction",
        ("Kael", "vit_a", "Fer-Noir"),
        ("Kael", "vit_a", "Port-Argent"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        True,
    ),
    ConsistencyCase(
        "contradiction",
        ("Myra", "travaille_pour", "Arbitre"),
        ("Myra", "travaille_pour", "Gardiens"),
        TemporalScope(kind=TemporalScopeKind.TIMELESS),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=6),
        True,
    ),

    # Legitimate evolution: the state changes between distinct story points.
    ConsistencyCase(
        "narrative_evolution",
        ("Elara", "est", "blessée"),
        ("Elara", "est", "guérie"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=1),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=4),
        False,
    ),
    ConsistencyCase(
        "narrative_evolution",
        ("Kael", "porte", "Cellule-de-Stase"),
        ("Kael", "porte", "Clé-de-Djinn"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=8),
        False,
    ),
    ConsistencyCase(
        "narrative_evolution",
        ("Elara", "est_a", "Port-Argent"),
        ("Elara", "est_a", "Palais-de-Verre"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=4),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=7),
        False,
    ),

    # Compatible restatements: the same fact is expressed again.
    ConsistencyCase(
        "compatible_restatement",
        ("Myra", "est", "mercenaire"),
        ("Myra", "est", "mercenaire"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=4),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=7),
        False,
    ),
    ConsistencyCase(
        "compatible_restatement",
        ("Kael", "possède", "Cellule-de-Stase"),
        ("Kael", "possède", "Cellule-de-Stase"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=5),
        False,
    ),
    ConsistencyCase(
        "compatible_restatement",
        ("Elara", "porte", "Givre-Âme"),
        ("Elara", "porte", "Givre-Âme"),
        TemporalScope(kind=TemporalScopeKind.TIMELESS),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=8),
        False,
    ),

    # Noise: unrelated assertions must never become conflicts.
    ConsistencyCase(
        "unrelated",
        ("Elara", "porte", "Givre-Âme"),
        ("Kael", "porte", "Surchargeuse"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=3),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=3),
        False,
    ),
    ConsistencyCase(
        "unrelated",
        ("Myra", "est", "mercenaire"),
        ("Myra", "possède", "Rose-des-Vents"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=5),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=5),
        False,
    ),
    ConsistencyCase(
        "unrelated",
        ("Kael", "vit_a", "Fer-Noir"),
        ("Elara", "vit_a", "Port-Argent"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=2),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=8),
        False,
    ),

    # Semantic predicate typing: possession is intentionally multi-valued.
    ConsistencyCase(
        "compatible_restatement",
        ("Kael", "owns", "Lentille"),
        ("Kael", "owns", "Analyseur-de-Flux"),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=5),
        TemporalScope(kind=TemporalScopeKind.STORY_POINT, position=5),
        False,
    ),
)


class BenchmarkRepository:
    def __init__(self, assertions: list[Assertion]) -> None:
        self.assertions = assertions
        self.conflicts: list[Conflict] = []

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return self.assertions

    def list_conflicts(self, *, book_id: str) -> list[Conflict]:
        return self.conflicts

    def save_conflict(self, conflict: Conflict) -> None:
        self.conflicts.append(conflict)


class BenchmarkTemporalStore:
    def __init__(self, scopes: dict[str, TemporalScope]) -> None:
        self.scopes = scopes

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self.scopes.get(assertion_id)

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        self.scopes[assertion_id] = scope


def assertion(case_id: str, claim: tuple[str, str, str]) -> Assertion:
    subject, predicate, object_ = claim
    return Assertion(
        id=case_id,
        source_document_id=f"source-{case_id}",
        chunk_id=f"chunk-{case_id}",
        statement=f"{subject} {predicate} {object_}",
        subject=subject,
        predicate=predicate,
        object=object_,
        confidence=1.0,
        evidence_id=f"evidence-{case_id}",
    )


def run_case(index: int, case: ConsistencyCase) -> bool:
    left = assertion(f"left-{index}", case.left)
    right = assertion(f"right-{index}", case.right)
    repository = BenchmarkRepository([left, right])
    scopes = {
        assertion_id: scope
        for assertion_id, scope in (
            (left.id, case.left_scope),
            (right.id, case.right_scope),
        )
        if scope is not None
    }
    temporal_store = BenchmarkTemporalStore(scopes)
    conflicts = DetectConflicts(
        repository,
        temporal_context_store=temporal_store,
    ).execute(book_id="benchmark")
    return bool(conflicts)


def test_consistency_benchmark_covers_four_distinct_case_types() -> None:
    assert {case.label for case in CASES} == {
        "contradiction",
        "narrative_evolution",
        "compatible_restatement",
        "unrelated",
    }
    assert all(sum(case.label == label for case in CASES) >= 3 for label in {
        "contradiction",
        "narrative_evolution",
        "compatible_restatement",
        "unrelated",
    })


def test_consistency_benchmark_matches_expected_labels() -> None:
    false_positives = []
    false_negatives = []

    for index, case in enumerate(CASES):
        detected = run_case(index, case)
        if detected and not case.expected_conflict:
            false_positives.append(case.label)
        if not detected and case.expected_conflict:
            false_negatives.append(case.label)

    assert false_positives == []
    assert false_negatives == []


def test_consistency_benchmark_reports_confusion_matrix() -> None:
    true_positives = sum(
        run_case(index, case) and case.expected_conflict
        for index, case in enumerate(CASES)
    )
    true_negatives = sum(
        not run_case(index, case) and not case.expected_conflict
        for index, case in enumerate(CASES)
    )
    false_positives = sum(
        run_case(index, case) and not case.expected_conflict
        for index, case in enumerate(CASES)
    )
    false_negatives = sum(
        not run_case(index, case) and case.expected_conflict
        for index, case in enumerate(CASES)
    )

    assert (true_positives, true_negatives, false_positives, false_negatives) == (
        3,
        10,
        0,
        0,
    )


def test_gold_metric_evaluator_matches_expected_classification() -> None:
    gold = {
        f"case-{index}": (
            GoldLabel.CONTRADICTION if case.expected_conflict else GoldLabel.EVOLUTION
        )
        for index, case in enumerate(CASES)
    }
    predicted = {
        f"case-{index}"
        for index, case in enumerate(CASES)
        if run_case(index, case)
    }

    metrics = evaluate(gold=gold, predicted_ids=predicted)

    assert metrics.true_positives == 3
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.fpr == 0.0
