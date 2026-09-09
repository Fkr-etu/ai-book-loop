from __future__ import annotations

from dataclasses import dataclass

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, Conflict


@dataclass(frozen=True)
class ConsistencyCase:
    label: str
    left: tuple[str, str, str]
    right: tuple[str, str, str]


CASES = (
    ConsistencyCase("contradiction", ("Elara", "porte", "Givre-Âme"), ("Elara", "porte", "Lame-Solaire")),
    ConsistencyCase("contradiction", ("Kael", "vit_a", "Fer-Noir"), ("Kael", "vit_a", "Port-Argent")),
    ConsistencyCase("compatible_restatement", ("Myra", "est", "mercenaire"), ("Myra", "est", "mercenaire")),
    ConsistencyCase("unrelated", ("Elara", "porte", "Givre-Âme"), ("Kael", "porte", "Surchargeuse")),
    # The current Assertion model has no temporal scope, so this case is kept
    # explicit but is not scored by the structural detector yet.
    ConsistencyCase("narrative_evolution", ("Elara", "est", "blessée"), ("Elara", "est", "guérie")),
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


def test_structural_detector_matches_each_static_case() -> None:
    for index, case in enumerate(CASES):
        if case.label == "narrative_evolution":
            continue

        left = assertion(f"left-{index}", case.left)
        right = assertion(f"right-{index}", case.right)
        repository = BenchmarkRepository([left, right])
        conflicts = DetectConflicts(repository).execute(book_id="benchmark")

        assert bool(conflicts) is (case.label == "contradiction"), case.label
        if conflicts:
            assert {
                conflicts[0].left_assertion_id,
                conflicts[0].right_assertion_id,
            } == {left.id, right.id}


def test_narrative_evolution_is_explicitly_not_scored_without_temporal_context() -> None:
    evolution = next(case for case in CASES if case.label == "narrative_evolution")
    assert evolution.left[0] == evolution.right[0]
    assert evolution.left[1] == evolution.right[1]
    assert evolution.left[2] != evolution.right[2]
