from __future__ import annotations

from typing import Any, Protocol

from book_loop.domain.models import BookState
from book_loop.domain.workflow import ChapterWorkflowRun


class WorkflowRunStore(Protocol):
    def get_or_create(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun: ...
    def get(self, run_id: str) -> ChapterWorkflowRun: ...
    def latest(self, *, book_id: str, chapter_number: int) -> ChapterWorkflowRun | None: ...
    def save(self, run: ChapterWorkflowRun) -> None: ...


class ChapterWorkflowPort(Protocol):
    def run(self, *, book: BookState, chapter_number: int, idempotency_key: str | None = None) -> Any: ...
