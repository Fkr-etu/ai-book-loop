from __future__ import annotations

import uuid

from book_loop.domain.workflow import ChapterWorkflowRun


class InMemoryWorkflowRunStore:
    """Non-durable workflow store for isolated tests and lightweight callers."""

    def __init__(self) -> None:
        self.runs: dict[tuple[str, int, str], ChapterWorkflowRun] = {}

    def get_or_create(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun:
        key = (book_id, chapter_number, idempotency_key)
        run = self.runs.get(key)
        if run is None:
            run = ChapterWorkflowRun(id=str(uuid.uuid4()), book_id=book_id, chapter_number=chapter_number, idempotency_key=idempotency_key)
            self.runs[key] = run
        return run.model_copy(deep=True)

    def save(self, run: ChapterWorkflowRun) -> None:
        self.runs[(run.book_id, run.chapter_number, run.idempotency_key)] = run.model_copy(deep=True)
