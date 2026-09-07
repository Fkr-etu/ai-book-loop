from __future__ import annotations

from book_loop.application.use_cases.narrative_consistency_support import (
    active_assertions,
    build_issue,
    evidence_map,
    normalize,
    normalize_key,
)
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.models import Assertion
from book_loop.domain.protocols import KnowledgeRepository


_INVERSE_RELATIONS = (
    ({"parent_of", "parent"}, {"child_of", "child"}),
    ({"older_than", "older"}, {"younger_than", "younger"}),
)


class InverseRelationConsistencyDetector:
    """Detect assertions that assign opposite roles to the same ordered pair."""

    rule_id = "RELATION_INVERSE_ROLE_CONTRADICTION"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))

        by_pair: dict[tuple[str, str], list[Assertion]] = {}
        for assertion in assertions:
            subject = normalize(assertion.subject)
            target = normalize(assertion.object)
            if not subject or not target:
                continue
            by_pair.setdefault((subject, target), []).append(assertion)

        issues: list[ConsistencyIssue] = []
        seen: set[tuple[str, str]] = set()

        for pair_assertions in by_pair.values():
            for left in pair_assertions:
                left_predicate = normalize_key(left.predicate)
                for right in pair_assertions:
                    if left.id >= right.id:
                        continue
                    right_predicate = normalize_key(right.predicate)
                    if not self._are_inverse(left_predicate, right_predicate):
                        continue

                    key = (left.id, right.id)
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="relationship_continuity",
                            severity="error",
                            message=(
                                "Deux assertions attribuent des rôles inverses incompatibles "
                                f"au même couple « {left.subject} » / « {left.object} »."
                            ),
                            left=left,
                            right=right,
                            evidence=evidence,
                        )
                    )

        return issues

    @staticmethod
    def _are_inverse(left: str, right: str) -> bool:
        return any(
            (left in positive and right in inverse)
            or (right in positive and left in inverse)
            for positive, inverse in _INVERSE_RELATIONS
        )
