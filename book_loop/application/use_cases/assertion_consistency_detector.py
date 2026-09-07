from __future__ import annotations

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.models import Assertion, Conflict, Evidence
from book_loop.domain.protocols import KnowledgeRepository


class AssertionConsistencyDetector:
    """Adapter exposing the existing assertion conflict rule to the unified engine."""

    rule_id = "ASSERTION_SUBJECT_PREDICATE_CONFLICT"

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self._detect_conflicts = DetectConflicts(repository)

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        self._detect_conflicts.execute(book_id=book_id)
        return self.list_existing(book_id=book_id)

    def list_existing(self, *, book_id: str) -> list[ConsistencyIssue]:
        conflicts = self.repository.list_conflicts(book_id=book_id)
        assertions = {a.id: a for a in self.repository.list_assertions(book_id=book_id)}
        evidence = {e.id: e for e in self.repository.list_evidence(book_id=book_id)}
        return [
            self._to_issue(conflict, assertions=assertions, evidence=evidence)
            for conflict in conflicts
            if conflict.left_assertion_id in assertions and conflict.right_assertion_id in assertions
        ]

    @classmethod
    def _to_issue(
        cls,
        conflict: Conflict,
        *,
        assertions: dict[str, Assertion],
        evidence: dict[str, Evidence],
    ) -> ConsistencyIssue:
        left = assertions[conflict.left_assertion_id]
        right = assertions[conflict.right_assertion_id]
        left_evidence = evidence.get(left.evidence_id)
        right_evidence = evidence.get(right.evidence_id)
        return ConsistencyIssue(
            id=conflict.id,
            category="contradiction",
            severity="warning",
            status=conflict.status.value,
            message=f"Deux assertions incompatibles portent sur « {left.subject} » / « {left.predicate} ».",
            left_assertion_id=left.id,
            right_assertion_id=right.id,
            left_statement=left.statement,
            right_statement=right.statement,
            left_evidence=left_evidence.excerpt if left_evidence else "",
            right_evidence=right_evidence.excerpt if right_evidence else "",
            confidence=min(left.confidence, right.confidence),
            rule_id=cls.rule_id,
            metadata={"detector": "assertion"},
            resolution_assertion_id=conflict.resolution_assertion_id,
        )
