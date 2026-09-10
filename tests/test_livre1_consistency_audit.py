from __future__ import annotations

from dataclasses import dataclass

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, Conflict
from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


@dataclass(frozen=True)
class CorpusAssertion:
    """A compact, source-grounded assertion from the real Livre I manuscript."""

    id: str
    chapter: int
    subject: str
    predicate: str
    object: str


# Diagnostic slice taken from Fkr-etu/M4ges Livre I chapters 1, 2, 4 and 8.
# The manuscript explicitly moves the characters through different locations;
# these are therefore useful real-corpus checks for temporal evolution.
# Source commits are the chapter blob SHAs at the time of this audit:
# c1=39f8ab1acfd26dac1857cdd6a8d02d62e6028645
# c2=333826e8c733f997fca4c32a48dbd7048fdfd306
# c4=bfc08a1f5ff138edfb662603fb79315fc0ba7aa5
# c8=d4660eff91a8e17dc72cf9150366d5e4e62f180e
CORPUS = (
    CorpusAssertion("elara-location-c1", 1, "Elara", "est_a", "Val-D'Or"),
    CorpusAssertion("elara-location-c4", 4, "Elara", "est_a", "Port-Argent"),
    CorpusAssertion("elara-location-c8", 8, "Elara", "est_a", "Marches Orientales"),
    CorpusAssertion("kael-location-c2", 2, "Kael", "est_a", "Fer-Noir"),
    CorpusAssertion("kael-location-c4", 4, "Kael", "est_a", "Port-Argent"),
    CorpusAssertion("kael-location-c8", 8, "Kael", "est_a", "Marches Orientales"),
)


class AuditRepository:
    def __init__(self, assertions: list[Assertion]) -> None:
        self.assertions = assertions
        self.conflicts: list[Conflict] = []

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        return self.assertions

    def list_conflicts(self, *, book_id: str) -> list[Conflict]:
        return self.conflicts

    def save_conflict(self, conflict: Conflict) -> None:
        self.conflicts.append(conflict)


class AuditTemporalStore:
    def __init__(self, scopes: dict[str, TemporalScope]) -> None:
        self.scopes = scopes

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return self.scopes.get(assertion_id)

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        self.scopes[assertion_id] = scope


def to_assertion(item: CorpusAssertion) -> Assertion:
    return Assertion(
        id=item.id,
        source_document_id=f"livre1-chapter-{item.chapter}",
        chunk_id=f"livre1-chapter-{item.chapter}",
        statement=f"{item.subject} {item.predicate} {item.object}",
        subject=item.subject,
        predicate=item.predicate,
        object=item.object,
        confidence=1.0,
        evidence_id=f"evidence-{item.id}",
    )


def test_livre1_location_evolution_is_not_reported_as_contradiction() -> None:
    assertions = [to_assertion(item) for item in CORPUS]
    scopes = {
        assertion.id: TemporalScope(
            kind=TemporalScopeKind.STORY_POINT,
            position=next(item.chapter for item in CORPUS if item.id == assertion.id),
        )
        for assertion in assertions
    }
    repository = AuditRepository(assertions)

    conflicts = DetectConflicts(
        repository,
        temporal_context_store=AuditTemporalStore(scopes),
    ).execute(book_id="livre-1")

    # There are six structurally comparable pairs (three Elara locations and
    # three Kael locations), but every pair spans distinct story points.
    assert len(assertions) == 6
    assert sum(
        left.subject == right.subject
        and left.predicate == right.predicate
        and left.object != right.object
        for index, left in enumerate(assertions)
        for right in assertions[index + 1 :]
    ) == 6
    assert conflicts == []


def test_livre1_audit_summary_exposes_the_signal_without_claiming_precision() -> None:
    assertions = [to_assertion(item) for item in CORPUS]
    candidate_pairs = [
        (left, right)
        for index, left in enumerate(assertions)
        for right in assertions[index + 1 :]
        if (
            left.subject.casefold() == right.subject.casefold()
            and left.predicate.casefold() == right.predicate.casefold()
            and left.object.casefold() != right.object.casefold()
        )
    ]

    summary = {
        "assertions": len(assertions),
        "candidate_pairs": len(candidate_pairs),
        "chapters": sorted({item.chapter for item in CORPUS}),
    }

    assert summary == {
        "assertions": 6,
        "candidate_pairs": 6,
        "chapters": [1, 2, 4, 8],
    }
