from __future__ import annotations

from dataclasses import dataclass

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, Conflict


@dataclass(frozen=True)
class ConsistencyCase:
    label: str
    left: tuple[str, str, str]
    right: tuple[str, str, str]


# Small, source-independent benchmark used to protect the distinction between
# contradictions and harmless narrative changes. The corpus is deliberately
# compact: it exercises the structural detector, not linguistic extraction.
CASES = (
    ConsistencyCase(
        "contradiction",
        ("Elara", "porte", "Givre-Âme"),
        ("Elara", "porte", "Lame-Solaire"),
    ),
    ConsistencyCase(
        "contradiction",
        ("Kael", "vit_a", "Fer-Noir"),
        ("Kael", "vit_a", "Port-Argent"),
    ),
    ConsistencyCase(
        "compatible_restatement",
        ("Myra", "est", "mercenaire"),
        ("Myra", "est", "mercenaire"),
    ),
    ConsistencyCase(
        "unrelated",
        ("Elara", "porte", "Givre-Âme"),
        ("Kael", "porte", "Surchargeuse"),
    ),
    # A real narrative evolution must not automatically be treated as a
    # contradiction merely because the same subject changes state over time.
    # The current Assertion model has no temporal scope, so this case is kept
    # as an explicit benchmark label but is intentionally excluded from the
    # structural detector score until temporal context is modelled.
    ConsistencyCase(
        "narrative_evolution",
        ("Elara", "est", "blessée"),
        ("Elara", "est", "guérie"),
    ),
)


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


def test_consistency_benchmark_covers_distinct_case_types() -> None:
    assert {case.label for case in CASES} == {
        "contradiction",
        "compatible_restatement",
        "narrative_evolution",
        "unrelated",
    }


def test_structural_detector_identifies_only_gold_static_contradictions() -> None:
    contradiction_cases = [case for case in CASES if case.label == "contradiction"]
    compatible_cases = [
        case for case in CASES if case.label in {"compatible_restatement", "unrelated"}
    ]

    assertions = []
    for index, case in enumerate(contradiction_cases + compatible_cases):
        assertions.extend(
            [
                assertion(f"left-{index}", case.left),
                assertion(f"right-{index}", case.right),
            ]
        )

    repository = BenchmarkRepository(assertions)
    conflicts = DetectConflicts(repository).execute(book_id="benchmark")
    pairs = {
        frozenset((conflict.left_assertion_id, conflict.right_assertion_id))
        for conflict in conflicts
    }

    expected = {
        frozenset((f"left-{index}", f"right-{index}"))
        for index, case in enumerate(contradiction_cases)
    }
    assert pairs == expected


def test_narrative_evolution_is_explicitly_not_scored_without_temporal_context() -> None:
    evolution = next(case for case in CASES if case.label == "narrative_evolution")
    assert evolution.left[0] == evolution.right[0]
    assert evolution.left[1] == evolution.right[1]
    assert evolution.left[2] != evolution.right[2]
