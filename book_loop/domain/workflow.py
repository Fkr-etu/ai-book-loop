from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from book_loop.domain.models import SceneReview


class WorkflowRunStatus(StrEnum):
    RUNNING = "running"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"


class WorkflowStep(StrEnum):
    WRITE = "write"
    REVIEW = "review"
    CORRECT = "correct"
    SUMMARIZE = "summarize"


class ChapterWorkflowRun(BaseModel):
    id: str
    book_id: str
    chapter_number: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1)
    status: WorkflowRunStatus = WorkflowRunStatus.RUNNING
    step: WorkflowStep = WorkflowStep.WRITE
    attempt: int = Field(default=0, ge=0)
    draft: str = ""
    review: SceneReview | None = None
    decision: str | None = None
    summary: str | None = None
