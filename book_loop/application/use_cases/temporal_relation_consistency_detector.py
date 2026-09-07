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


_BEFORE_PREDICATES = {"before", "precedes", "preceded_by"}
_AFTER_PREDICATES = {"after", "follows", "followed_by"}
_NOT_BEFORE_PREDICATES = {"not_before", "does_not_precede", "doesnt_precede"}


class TemporalRelationConsistencyDetector:
    """Detect explicit contradictions between ordered temporal relations."""

    rule_id = "TIMELINE_CONTRADICTORY_ORDER"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))

        positive: dict[tuple[str, str], list[Assertion]] = {}
        negative: dict[tuple[str, str], list[Assertion]] = {}

        for assertion in assertions:
            predicate = normalize_key(assertion.predicate)
            subject = normalize(assertion.subject)
            target = normalize(assertion.object)
            if not subject or not target:
                continue

            if predicate in _BEFORE_PREDICATES:
                positive.setdefault((subject, target), []).append(assertion)
            elif predicate in _AFTER_PREDICATES:
                positive.setdefault((target, subject), []).append(assertion)
            elif predicate in _NOT_BEFORE_PREDICATES:
                negative.setdefault((subject, target), []).append(assertion)

        issues: list[ConsistencyIssue] = []
        seen: set[tuple[str, str]] = set()

        for pair, left_assertions in positive.items():
            reverse = (pair[1], pair[0])
            for left in left_assertions:
                for right in positive.get(reverse, []):
                    key = tuple(sorted((left.id, right.id)))
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="timeline",
                            severity="error",
                            message=(
                                "Deux assertions imposent des ordres temporels incompatibles "
                                f"entre « {left.subject} » et « {left.object} »."
                            ),
                            left=left,
                            right=right,
                            evidence=evidence,
                        )
                    )

            for left in left_assertions:
                for right in negative.get(pair, []):
                    key = tuple(sorted((left.id, right.id)))
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="timeline",
                            severity="error",
                            message=(
                                "Une assertion impose un ordre temporel qu'une autre assertion "
                                "nie explicitement."
                            ),
                            left=left,
                            right=right,
                            evidence=evidence,
                        )
                    )

        return issues
