from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from book_loop.domain.models import Assertion, Conflict, ConflictStatus
from book_loop.domain.protocols import KnowledgeRepository


class DetectConflicts:
    """Detect mutually exclusive assertions without deciding which one is true."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository

    def execute(self, *, book_id: str) -> list[Conflict]:
        assertions = [
            assertion
            for assertion in self.repository.list_assertions(book_id=book_id)
            if assertion.status.value != "rejected"
        ]
        existing = {
            (conflict.left_assertion_id, conflict.right_assertion_id): conflict
            for conflict in self.repository.list_conflicts(book_id=book_id)
        }
        conflicts: list[Conflict] = []
        for index, left in enumerate(assertions):
            for right in assertions[index + 1 :]:
                if not self._conflicts(left, right):
                    continue
                left_id, right_id = sorted((left.id, right.id))
                key = (left_id, right_id)
                prior = existing.get(key)
                if prior is not None:
                    if prior.status is ConflictStatus.OPEN:
                        conflicts.append(prior)
                    continue
                conflict = Conflict(
                    id=str(uuid5(NAMESPACE_URL, f"book:{book_id}:conflict:{left_id}:{right_id}")),
                    book_id=book_id,
                    left_assertion_id=left_id,
                    right_assertion_id=right_id,
                )
                self.repository.save_conflict(conflict)
                conflicts.append(conflict)
        return conflicts

    @staticmethod
    def _conflicts(left: Assertion, right: Assertion) -> bool:
        if left.id == right.id:
            return False
        return (
            left.subject.strip().casefold() == right.subject.strip().casefold()
            and left.predicate.strip().casefold() == right.predicate.strip().casefold()
            and left.object.strip().casefold() != right.object.strip().casefold()
        )
