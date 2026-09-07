from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class ConsistencyDetector(Protocol):
    """A consistency detector that reuses the existing knowledge layer."""

    def detect(self, *, book_id: str) -> Sequence[object]: ...


class UnifiedConsistencyEngine:
    """Run registered consistency detectors and fuse their issues.

    Detectors own detection rules; the engine owns orchestration and stable deduplication.
    It deliberately knows nothing about assertion, Canon or LLM implementations, preventing
    future detectors from creating parallel consistency pipelines.
    """

    def __init__(self, detectors: Sequence[ConsistencyDetector]) -> None:
        self._detectors = tuple(detectors)

    def detect(self, *, book_id: str) -> list[object]:
        issues: dict[str, object] = {}
        for detector in self._detectors:
            for issue in detector.detect(book_id=book_id):
                issue_id = getattr(issue, "id", None)
                if not isinstance(issue_id, str) or not issue_id:
                    raise ValueError("Consistency detector issues must expose a stable id")
                issues.setdefault(issue_id, issue)
        return list(issues.values())
