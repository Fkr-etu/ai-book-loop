from __future__ import annotations

from book_loop.domain.models import BookState
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.database.postgres import PostgresWorkflowRunStore
from book_loop.workflow.chapter_graph import ChapterWorkflow


class ChapterWorkflowAdapter:
    """Infrastructure adapter exposing the workflow through the application port."""

    def __init__(self, workflow: ChapterWorkflow, store: PostgresWorkflowRunStore) -> None:
        self.workflow = workflow
        self.store = store

    def start_run(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun:
        return self.store.get_or_create(
            book_id=book_id,
            chapter_number=chapter_number,
            idempotency_key=idempotency_key,
        )

    def run(self, *, book: BookState, chapter_number: int, idempotency_key: str | None = None):
        return self.workflow.run(
            book=book,
            chapter_number=chapter_number,
            idempotency_key=idempotency_key,
        )
