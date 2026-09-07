from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from book_loop.application.use_cases.analyze_consistency import ConsistencyIssue


class ConsistencyDetector(Protocol):
    """A consistency detector that reuses the existing knowledge layer."""

    def detect(self, *, book_id: str) -> Sequence[ConsistencyIssue]: ...


class UnifiedConsistencyEngine:
    """Run all registered consistency detectors and fuse their issues.

    Detectors own detection rules; the engine owns orchestration and stable deduplication.
    This keeps the existing assertion/conflict detector as the source of truth while making
    room for future character, chronology and semantic detectors without parallel pipelines.
    """

    def __init__(self, detectors: Sequence[ConsistencyDetector]) -> None:
        self._detectors = tuple(detectors)

    def detect(self, *, book_id: str) -> list[ConsistencyIssue]:
        issues: dict[str, ConsistencyIssue] = {}
        for detector in self._detectors:
            for issue in detector.detect(book_id=book_id):
                issues.setdefault(issue.id, issue)
        return list(issues.values())
