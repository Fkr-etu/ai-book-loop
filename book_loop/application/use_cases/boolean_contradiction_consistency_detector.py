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

_NEGATION_PAIRS = {
    "is": "is_not",
    "has": "does_not_have",
    "can": "cannot",
    "is_not": "is",
    "does_not_have": "has",
    "cannot": "can",
}


class BooleanContradictionConsistencyDetector:
    """Detect explicit positive/negative contradictions for boolean predicates."""

    rule_id = "ASSERTION_BOOLEAN_CONTRADICTION"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))
        indexed: dict[tuple[str, str, str], list[Assertion]] = {}
        for assertion in assertions:
            predicate = normalize_key(assertion.predicate)
            if predicate not in _NEGATION_PAIRS:
                continue
            indexed.setdefault(
                (normalize(assertion.subject), predicate, normalize(assertion.object)), []
            ).append(assertion)

        issues: list[ConsistencyIssue] = []
        seen: set[tuple[str, str]] = set()
        for (subject, predicate, target), left_assertions in indexed.items():
            opposite = _NEGATION_PAIRS[predicate]
            for left in left_assertions:
                for right in indexed.get((subject, opposite, target), []):
                    key = tuple(sorted((left.id, right.id)))
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="assertion",
                            severity="error",
                            message=(
                                "Deux assertions explicites sont incompatibles : "
                                f"« {left.subject} {left.predicate} {left.object} » et "
                                f"« {right.subject} {right.predicate} {right.object} »."
                            ),
                            left=left,
                            right=right,
                            evidence=evidence,
                        )
                    )
        return issues
