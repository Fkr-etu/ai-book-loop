from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from book_loop.domain.models import BookState
from book_loop.domain.workflow import ChapterWorkflowRun


@dataclass(frozen=True)
class ObservabilityEvent:
    event_type: str
    workflow_run_id: str | None = None
    book_id: str | None = None
    chapter_number: int | None = None
    attempt: int | None = None
    duration_ms: int | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityPort(Protocol):
    def record(self, event: ObservabilityEvent) -> None: ...


class WorkflowRunStore(Protocol):
    def get_or_create(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun: ...
    def get(self, run_id: str) -> ChapterWorkflowRun: ...
    def latest(self, *, book_id: str, chapter_number: int) -> ChapterWorkflowRun | None: ...
    def save(self, run: ChapterWorkflowRun) -> None: ...


class ChapterWorkflowPort(Protocol):
    def start_run(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun: ...
    def run(self, *, book: BookState, chapter_number: int, idempotency_key: str | None = None) -> Any: ...
