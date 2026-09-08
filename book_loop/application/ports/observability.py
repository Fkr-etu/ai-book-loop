from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class WorkflowEvent:
    event_type: str
    workflow_run_id: str | None = None
    book_id: str | None = None
    chapter_number: int | None = None
    attempt: int | None = None
    duration_ms: int | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkflowObserver(Protocol):
    def record(self, event: WorkflowEvent) -> None: ...
