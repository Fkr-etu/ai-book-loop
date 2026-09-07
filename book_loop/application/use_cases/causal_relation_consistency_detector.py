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

_CAUSES_PREDICATES = {"causes", "caused", "caused_by", "leads_to", "results_in"}
_BEFORE_PREDICATES = {"before", "precedes", "preceded_by"}
_NOT_CAUSES_PREDICATES = {"does_not_cause", "doesnt_cause", "not_cause"}


class CausalRelationConsistencyDetector:
    """Detect explicit causal relations that violate known temporal constraints."""

    rule_id = "CAUSAL_TEMPORAL_CONTRADICTION"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))

        causes: dict[tuple[str, str], list[Assertion]] = {}
        before: dict[tuple[str, str], list[Assertion]] = {}
        not_causes: dict[tuple[str, str], list[Assertion]] = {}

        for assertion in assertions:
            predicate = normalize_key(assertion.predicate)
            subject = normalize(assertion.subject)
            target = normalize(assertion.object)
            if not subject or not target:
                continue

            if predicate in _CAUSES_PREDICATES:
                pair = (subject, target)
                causes.setdefault(pair, []).append(assertion)
            elif predicate in _BEFORE_PREDICATES:
                pair = (subject, target)
                before.setdefault(pair, []).append(assertion)
            elif predicate in _NOT_CAUSES_PREDICATES:
                pair = (subject, target)
                not_causes.setdefault(pair, []).append(assertion)

        issues: list[ConsistencyIssue] = []
        seen: set[tuple[str, str]] = set()

        for pair, causal_assertions in causes.items():
            reverse = (pair[1], pair[0])

            # A cause cannot occur after its effect.
            for causal in causal_assertions:
                for temporal in before.get(reverse, []):
                    key = tuple(sorted((causal.id, temporal.id)))
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
                                "Une relation causale est incompatible avec l'ordre temporel "
                                f"explicite entre « {causal.subject} » et « {causal.object} »."
                            ),
                            left=causal,
                            right=temporal,
                            evidence=evidence,
                        )
                    )

                for negative in not_causes.get(pair, []):
                    key = tuple(sorted((causal.id, negative.id)))
                    if key in seen:
                        continue
                    seen.add(key)
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="causality",
                            severity="error",
                            message=(
                                "Une relation causale est explicitement contredite par une "
                                "assertion négative portant sur les mêmes éléments."
                            ),
                            left=causal,
                            right=negative,
                            evidence=evidence,
                        )
                    )

        return issues
