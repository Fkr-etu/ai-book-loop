from __future__ import annotations

from book_loop.application.use_cases.narrative_consistency_support import (
    active_assertions,
    build_issue,
    evidence_map,
    normalize,
    normalize_key,
)
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.protocols import KnowledgeRepository


_NEGATION_PAIRS = {
    "contains": {"does_not_contain", "doesnt_contain", "not_contain"},
    "has": {"does_not_have", "doesnt_have", "not_have"},
    "includes": {"excludes", "does_not_include", "not_include"},
    "located_in": {"not_located_in", "does_not_locate_in"},
    "in": {"not_in", "outside"},
}


class WorldContinuityDetector:
    """Detect explicit positive/negative world-relation contradictions."""

    rule_id = "WORLD_POSITIVE_NEGATIVE_RELATION"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))
        grouped: dict[tuple[str, str], list] = {}
        for assertion in assertions:
            grouped.setdefault((assertion.subject.casefold(), normalize(assertion.object)), []).append(assertion)

        issues: list[ConsistencyIssue] = []
        for candidates in grouped.values():
            for index, left in enumerate(candidates):
                left_predicate = normalize_key(left.predicate)
                for right in candidates[index + 1 :]:
                    right_predicate = normalize_key(right.predicate)
                    contradictory = any(
                        (left_predicate == positive and right_predicate in negatives)
                        or (right_predicate == positive and left_predicate in negatives)
                        for positive, negatives in _NEGATION_PAIRS.items()
                    )
                    if contradictory:
                        issues.append(
                            build_issue(
                                rule_id=self.rule_id,
                                book_id=book_id,
                                category="world_continuity",
                                severity="warning",
                                message="Deux assertions décrivent des relations incompatibles pour la même entité.",
                                left=left,
                                right=right,
                                evidence=evidence,
                            )
                        )
        return issues
