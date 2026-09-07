from __future__ import annotations

from typing import cast

from book_loop.application.use_cases.assertion_consistency_detector import AssertionConsistencyDetector
from book_loop.application.use_cases.boolean_contradiction_consistency_detector import BooleanContradictionConsistencyDetector
from book_loop.application.use_cases.character_continuity_detector import CharacterContinuityDetector
from book_loop.application.use_cases.consistency_engine import UnifiedConsistencyEngine
from book_loop.application.use_cases.inverse_relation_consistency_detector import InverseRelationConsistencyDetector
from book_loop.application.use_cases.temporal_relation_consistency_detector import TemporalRelationConsistencyDetector
from book_loop.application.use_cases.timeline_consistency_detector import TimelineConsistencyDetector
from book_loop.application.use_cases.world_continuity_detector import WorldContinuityDetector
from book_loop.domain.consistency import ConsistencyIssue
from book_loop.domain.protocols import KnowledgeRepository


class AnalyzeConsistency:
    """Build an evidence-backed consistency report through the unified engine."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self._assertion_detector = AssertionConsistencyDetector(repository)
        self._timeline_detector = TimelineConsistencyDetector(repository)
        self._temporal_relation_detector = TemporalRelationConsistencyDetector(repository)
        self._inverse_relation_detector = InverseRelationConsistencyDetector(repository)
        self._boolean_detector = BooleanContradictionConsistencyDetector(repository)
        self._character_detector = CharacterContinuityDetector(repository)
        self._world_detector = WorldContinuityDetector(repository)
        self._engine = UnifiedConsistencyEngine(
            (
                self._assertion_detector,
                self._timeline_detector,
                self._temporal_relation_detector,
                self._inverse_relation_detector,
                self._boolean_detector,
                self._character_detector,
                self._world_detector,
            )
        )

    def execute(self, *, book_id: str) -> list[ConsistencyIssue]:
        return cast(list[ConsistencyIssue], self._engine.detect(book_id=book_id))

    def list_existing(self, *, book_id: str) -> list[ConsistencyIssue]:
        """Preserve the existing read-only API while using the assertion projection."""
        return self._assertion_detector.list_existing(book_id=book_id)
