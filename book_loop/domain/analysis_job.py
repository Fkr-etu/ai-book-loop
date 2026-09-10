from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AnalysisJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    book_id: str
    owner_id: str
    analysis_type: str = "consistency"
    status: AnalysisJobStatus = AnalysisJobStatus.QUEUED
    progress: int = Field(default=0, ge=0, le=100)
    current_step: str | None = None
    idempotency_key: str
    attempt: int = Field(default=0, ge=0)
    max_attempts: int = Field(default=3, ge=1)
    available_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    lease_until: datetime | None = None
    worker_id: str | None = None
    result: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def claim(self, *, worker_id: str, lease_seconds: int, now: datetime | None = None) -> "AnalysisJob":
        now = now or datetime.now(timezone.utc)
        self.status = AnalysisJobStatus.RUNNING
        self.attempt += 1
        self.started_at = self.started_at or now
        self.lease_until = now + timedelta(seconds=lease_seconds)
        self.worker_id = worker_id
        self.updated_at = now
        self.error_code = None
        self.error_message = None
        return self

    def heartbeat(self, *, lease_seconds: int, now: datetime | None = None) -> "AnalysisJob":
        now = now or datetime.now(timezone.utc)
        if self.status != AnalysisJobStatus.RUNNING:
            return self
        self.lease_until = now + timedelta(seconds=lease_seconds)
        self.updated_at = now
        return self

    def complete(self, result: dict[str, Any], now: datetime | None = None) -> "AnalysisJob":
        now = now or datetime.now(timezone.utc)
        self.status = AnalysisJobStatus.SUCCEEDED
        self.progress = 100
        self.current_step = None
        self.completed_at = now
        self.lease_until = None
        self.worker_id = None
        self.result = result
        self.updated_at = now
        return self

    def fail(self, *, error_code: str, error_message: str, retry: bool, now: datetime | None = None) -> "AnalysisJob":
        now = now or datetime.now(timezone.utc)
        if retry and self.attempt < self.max_attempts:
            self.status = AnalysisJobStatus.QUEUED
            self.available_at = now
            self.lease_until = None
            self.worker_id = None
        else:
            self.status = AnalysisJobStatus.FAILED
            self.failed_at = now
            self.lease_until = None
            self.worker_id = None
        self.error_code = error_code
        self.error_message = error_message
        self.updated_at = now
        return self
