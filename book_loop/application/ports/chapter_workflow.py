from __future__ import annotations

from typing import Any, Protocol

from book_loop.domain.models import BookState
from book_loop.domain.workflow import ChapterWorkflowRun


class WorkflowRunStore(Protocol):
    def get(self, run_id: str) -> ChapterWorkflowRun: ...
    def latest(self, *, book_id: str, chapter_number: int) -> ChapterWorkflowRun | None: ...


class ChapterWorkflowPort(Protocol):
    def start_run(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun: ...
    def run(self, *, book: BookState, chapter_number: int, idempotency_key: str | None = None) -> Any: ...
