from __future__ import annotations

from book_loop.application.use_cases.narrative_consistency_support import (
    active_assertions,
    build_issue,
    evidence_map,
    normalize_key,
    parse_year,
)
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.models import Assertion
from book_loop.domain.protocols import KnowledgeRepository


_BIRTH_PREDICATES = {"birth", "born", "birth_date", "date_of_birth"}
_DEATH_PREDICATES = {"death", "died", "death_date", "date_of_death"}


class TimelineConsistencyDetector:
    """Detect impossible birth/death chronology using explicit assertion dates."""

    rule_id = "TIMELINE_BIRTH_AFTER_DEATH"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        assertions = active_assertions(self.repository.list_assertions(book_id=book_id))
        evidence = evidence_map(self.repository.list_evidence(book_id=book_id))
        births: dict[str, list[Assertion]] = {}
        deaths: dict[str, list[Assertion]] = {}
        for assertion in assertions:
            predicate = normalize_key(assertion.predicate)
            if predicate in _BIRTH_PREDICATES and parse_year(assertion.object) is not None:
                births.setdefault(assertion.subject.casefold(), []).append(assertion)
            elif predicate in _DEATH_PREDICATES and parse_year(assertion.object) is not None:
                deaths.setdefault(assertion.subject.casefold(), []).append(assertion)

        issues: list[ConsistencyIssue] = []
        for subject, birth_assertions in births.items():
            for birth in birth_assertions:
                birth_year = parse_year(birth.object)
                if birth_year is None:
                    continue
                for death in deaths.get(subject, []):
                    death_year = parse_year(death.object)
                    if death_year is None or birth_year <= death_year:
                        continue
                    issues.append(
                        build_issue(
                            rule_id=self.rule_id,
                            book_id=book_id,
                            category="timeline",
                            severity="error",
                            message=(
                                f"La chronologie est impossible : naissance en {birth_year} "
                                f"après le décès en {death_year}."
                            ),
                            left=birth,
                            right=death,
                            evidence=evidence,
                        )
                    )
        return issues
