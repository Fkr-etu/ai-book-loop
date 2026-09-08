from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from book_loop.application.ports.book_usage import BookUsagePort
from book_loop.application.ports.chapter_workflow import ChapterWorkflowPort, WorkflowRunStore
from book_loop.application.services.book_identity import book_identity
from book_loop.application.services.plan_limits import limits_for
from book_loop.domain.models import BookState, SubscriptionPlan
from book_loop.domain.protocols import BookRepository
from book_loop.domain.workflow import ChapterWorkflowRun


class _LegacyBookUsageAdapter:
    """Compatibility adapter for lightweight repositories used by older tests."""

    def __init__(self, repository: BookRepository) -> None:
        self._repository = repository
        self._identities: dict[str, str] = {}

    def register_book_identity(self, *, book_id: str, identity: str) -> None:
        self._identities.setdefault(book_id, identity)

    def get_book_identity(self, *, book_id: str) -> str | None:
        return self._identities.get(book_id)

    def consume_free_workflow_capacity(self, *, user_id: str, book_identity: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        del book_identity
        return self._repository.consume_workflow_capacity(
            quota_subject=f"user:{user_id}",
            period_start=period_start,
            idempotency_key=idempotency_key,
            monthly_limit=monthly_limit,
        )

    def consume_workflow_capacity(self, *, quota_subject: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        return self._repository.consume_workflow_capacity(
            quota_subject=quota_subject,
            period_start=period_start,
            idempotency_key=idempotency_key,
            monthly_limit=monthly_limit,
        )


class GenerateChapter:
    def __init__(self, workflow: ChapterWorkflowPort, repository: BookRepository, workflow_store: WorkflowRunStore, book_usage: BookUsagePort | None = None) -> None:
        self.workflow = workflow
        self.repository = repository
        self.workflow_store = workflow_store
        self.book_usage: BookUsagePort = book_usage or _LegacyBookUsageAdapter(repository)  # type: ignore[assignment]

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

    def _ensure_book_identity(self, book: BookState) -> str:
        identity = self.book_usage.get_book_identity(book_id=book.id)
        if identity is not None:
            return identity
        identity = book_identity(
            title=book.title,
            theme=book.theme,
            author_idea=book.author_idea,
            lore=book.lore,
            constraints=book.constraints,
        )
        self.book_usage.register_book_identity(book_id=book.id, identity=identity)
        return identity

    def start(self, book: BookState, chapter_number: int, *, idempotency_key: str | None = None) -> ChapterWorkflowRun:
        chapter = self._validate(book, chapter_number)
        key = idempotency_key or f"chapter:{book.id}:{chapter_number}:v{chapter.current_version + 1}:{uuid4()}"

        user = self.repository.get_user_by_id(book.owner_id)
        if user is None:
            raise PermissionError("Unknown owner")
        plan = SubscriptionPlan(user.plan)
        period_start = datetime.now(timezone.utc).date().replace(day=1).isoformat()

        if plan is SubscriptionPlan.FREE:
            identity = self._ensure_book_identity(book)
            allowed = self.book_usage.consume_free_workflow_capacity(
                user_id=user.id,
                book_identity=identity,
                period_start=period_start,
                idempotency_key=key,
                monthly_limit=limits_for(plan).monthly_workflow_runs,
            )
            if not allowed:
                raise PermissionError("This book has already used the free tier")
        else:
            allowed = self.book_usage.consume_workflow_capacity(
                quota_subject=f"user:{user.id}",
                period_start=period_start,
                idempotency_key=key,
                monthly_limit=limits_for(plan).monthly_workflow_runs,
            )
            if not allowed:
                raise PermissionError("Monthly workflow capacity reached for the current plan")

        return self.workflow.start_run(
            book_id=book.id,
            chapter_number=chapter_number,
            idempotency_key=key,
        )

    def execute(self, book: BookState, chapter_number: int, *, idempotency_key: str | None = None) -> Any:
        run = self.start(book, chapter_number, idempotency_key=idempotency_key)
        return self.workflow.run(book=book, chapter_number=chapter_number, idempotency_key=run.idempotency_key)

    def latest(self, book_id: str, chapter_number: int) -> ChapterWorkflowRun | None:
        return self.workflow_store.latest(book_id=book_id, chapter_number=chapter_number)

    def get_run(self, run_id: str) -> ChapterWorkflowRun:
        return self.workflow_store.get(run_id)
