from __future__ import annotations

from pydantic import BaseModel, Field

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.domain.models import Assertion, Conflict, Evidence
from book_loop.domain.protocols import KnowledgeRepository


class ConsistencyIssue(BaseModel):
    """Evidence-backed, author-facing representation of a corpus inconsistency."""

    id: str
    category: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str = Field(min_length=1)
    left_assertion_id: str
    right_assertion_id: str
    left_statement: str = Field(min_length=1)
    right_statement: str = Field(min_length=1)
    left_evidence: str = ""
    right_evidence: str = ""
    resolution_assertion_id: str | None = None


class AnalyzeConsistency:
    """Build an evidence-backed consistency report from the book knowledge layer.

    Detection is deliberately conservative: the first version surfaces only deterministic
    assertion conflicts. It never edits manuscript content or decides which assertion wins.
    """

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self._detect_conflicts = DetectConflicts(repository)

    def execute(self, *, book_id: str) -> list[ConsistencyIssue]:
        self._detect_conflicts.execute(book_id=book_id)
        conflicts = self.repository.list_conflicts(book_id=book_id)
        assertions = {a.id: a for a in self.repository.list_assertions(book_id=book_id)}
        evidence = {e.id: e for e in self.repository.list_evidence(book_id=book_id)}
        return [
            self._to_issue(conflict, assertions=assertions, evidence=evidence)
            for conflict in conflicts
        ]

    @staticmethod
    def _to_issue(
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
            resolution_assertion_id=conflict.resolution_assertion_id,
        )
