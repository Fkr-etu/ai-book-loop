from __future__ import annotations

from book_loop.application.use_cases.narrative_consistency_support import (
    active_assertions,
    affirmative,
    build_issue,
    evidence_map,
    normalize_key,
)
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.protocols import KnowledgeRepository


_STATE_PAIRS = (
    ({"alive", "is_alive", "living"}, {"dead", "is_dead"}),
    ({"married", "is_married"}, {"single", "is_single", "unmarried"}),
)


class CharacterContinuityDetector:
    """Detect explicit mutually exclusive character states."""

    rule_id = "CHARACTER_MUTUALLY_EXCLUSIVE_STATE"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))
        by_subject: dict[str, list] = {}
        for assertion in assertions:
            by_subject.setdefault(assertion.subject.casefold(), []).append(assertion)

        issues: list[ConsistencyIssue] = []
        for subject_assertions in by_subject.values():
            for left in subject_assertions:
                left_predicate = normalize_key(left.predicate)
                if not affirmative(left.object):
                    continue
                for right in subject_assertions:
                    if left.id >= right.id or not affirmative(right.object):
                        continue
                    right_predicate = normalize_key(right.predicate)
                    if any(
                        (left_predicate in positive and right_predicate in negative)
                        or (right_predicate in positive and left_predicate in negative)
                        for positive, negative in _STATE_PAIRS
                    ):
                        issues.append(
                            build_issue(
                                rule_id=self.rule_id,
                                book_id=book_id,
                                category="character_continuity",
                                severity="error",
                                message="Deux assertions décrivent simultanément des états incompatibles pour le même personnage.",
                                left=left,
                                right=right,
                                evidence=evidence,
                            )
                        )
        return issues
