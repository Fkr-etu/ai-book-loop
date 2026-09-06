from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from book_loop.application.services.plan_limits import limits_for
from book_loop.domain.models import BookState, SubscriptionPlan
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.workflow.chapter_graph import ChapterWorkflow, ChapterWorkflowState


class GenerateChapter:
    def __init__(self, workflow: ChapterWorkflow, repository=None) -> None:
        self.workflow = workflow
        self.repository = repository

    def _validate(self, book: BookState, chapter_number: int):
        if not book.outline_approved:
            raise ValueError("The author must approve the outline before generating chapters")
        chapter = next((chapter for chapter in book.chapters if chapter.number == chapter_number), None)
        if chapter is None:
            raise ValueError(f"Unknown chapter: {chapter_number}")
        previous = next((candidate for candidate in book.chapters if candidate.number == chapter_number - 1), None)
        if previous is not None and previous.status.value != "approved" and not previous.summary:
            raise ValueError(
                f"Chapter {chapter_number - 1} must be approved before generating chapter {chapter_number}"
            )
        return chapter

    def start(self, book: BookState, chapter_number: int, *, idempotency_key: str | None = None) -> ChapterWorkflowRun:
        chapter = self._validate(book, chapter_number)
        key = idempotency_key or f"chapter:{book.id}:{chapter_number}:v{chapter.current_version + 1}:{uuid4()}"

        if self.repository is not None and hasattr(self.repository, "consume_workflow_capacity"):
            user = self.repository.get_user_by_id(book.owner_id)
            if user is None:
                raise PermissionError("Unknown owner")
            plan = SubscriptionPlan(user.plan)
            period_start = datetime.now(timezone.utc).date().replace(day=1).isoformat()
            allowed = self.repository.consume_workflow_capacity(
                user_id=user.id,
                period_start=period_start,
                idempotency_key=key,
                monthly_limit=limits_for(plan).monthly_workflow_runs,
            )
            if not allowed:
                raise PermissionError("Monthly workflow capacity reached for the current plan")

        if self.workflow.workflow_store is None:
            from book_loop.infrastructure.database.workflow_store import InMemoryWorkflowRunStore
            self.workflow.workflow_store = InMemoryWorkflowRunStore()
        return self.workflow.workflow_store.get_or_create(
            book_id=book.id,
            chapter_number=chapter_number,
            idempotency_key=key,
        )

    def execute(self, book: BookState, chapter_number: int, *, idempotency_key: str | None = None) -> ChapterWorkflowState:
        run = self.start(book, chapter_number, idempotency_key=idempotency_key)
        return self.workflow.run(book=book, chapter_number=chapter_number, idempotency_key=run.idempotency_key)
