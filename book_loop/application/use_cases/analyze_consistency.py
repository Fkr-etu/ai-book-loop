from __future__ import annotations

from book_loop.application.use_cases.assertion_consistency_detector import AssertionConsistencyDetector
from book_loop.application.use_cases.consistency_engine import UnifiedConsistencyEngine
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.protocols import KnowledgeRepository


class AnalyzeConsistency:
    """Build an evidence-backed consistency report through the unified engine."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self._assertion_detector = AssertionConsistencyDetector(repository)
        self._engine = UnifiedConsistencyEngine((self._assertion_detector,))

    def execute(self, *, book_id: str) -> list[ConsistencyIssue]:
        return [issue for issue in self._engine.detect(book_id=book_id)]  # type: ignore[misc]

    def list_existing(self, *, book_id: str) -> list[ConsistencyIssue]:
        """Preserve the existing read-only API while using the same detector projection."""
        return self._assertion_detector.list_existing(book_id=book_id)
