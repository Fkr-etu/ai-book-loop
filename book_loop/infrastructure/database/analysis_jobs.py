from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from book_loop.domain.analysis_job import AnalysisJob, AnalysisJobStatus
from book_loop.infrastructure.database.postgres import _PostgresConnectionAdapter


class PostgresAnalysisJobStore:
    """Durable queue/lease implementation backed exclusively by PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        self._connection = _PostgresConnectionAdapter(database_url)

    @staticmethod
    def _job_from_row(row: dict[str, Any]) -> AnalysisJob:
        return AnalysisJob.model_validate(row)

    def enqueue(self, *, book_id: str, owner_id: str, analysis_type: str, idempotency_key: str, max_attempts: int = 3) -> AnalysisJob:
        job_id = str(uuid4())
        with self._connection.transaction():
            self._connection.execute(
                """
                INSERT INTO analysis_jobs (
                    id, book_id, owner_id, analysis_type, status, progress,
                    idempotency_key, attempt, max_attempts, available_at,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 0, ?, 0, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (book_id, analysis_type, idempotency_key) DO NOTHING
                """,
                (job_id, book_id, owner_id, analysis_type, AnalysisJobStatus.QUEUED.value, idempotency_key, max_attempts),
            )
            row = self._connection.execute(
                "SELECT * FROM analysis_jobs WHERE book_id = ? AND analysis_type = ? AND idempotency_key = ?",
                (book_id, analysis_type, idempotency_key),
            ).fetchone()
        if row is None:
            raise RuntimeError("Analysis job could not be created")
        return self._job_from_row(row)

    def get(self, job_id: str) -> AnalysisJob:
        row = self._connection.execute("SELECT * FROM analysis_jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return self._job_from_row(row)

    def get_by_idempotency(self, *, book_id: str, analysis_type: str, idempotency_key: str) -> AnalysisJob | None:
        row = self._connection.execute(
            "SELECT * FROM analysis_jobs WHERE book_id = ? AND analysis_type = ? AND idempotency_key = ?",
            (book_id, analysis_type, idempotency_key),
        ).fetchone()
        return self._job_from_row(row) if row is not None else None

    def claim_next(self, *, worker_id: str, lease_seconds: int) -> AnalysisJob | None:
        now = datetime.now(timezone.utc)
        with self._connection.transaction():
            row = self._connection.execute(
                """
                SELECT * FROM analysis_jobs
                WHERE (status = ? AND available_at <= CURRENT_TIMESTAMP)
                   OR (status = ? AND lease_until IS NOT NULL AND lease_until < CURRENT_TIMESTAMP)
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT 1
                """,
                (AnalysisJobStatus.QUEUED.value, AnalysisJobStatus.RUNNING.value),
            ).fetchone()
            if row is None:
                return None
            job = self._job_from_row(row)
            job.claim(worker_id=worker_id, lease_seconds=lease_seconds, now=now)
            self._save_locked(job)
            return job

    def update_progress(self, *, job_id: str, worker_id: str, progress: int, current_step: str | None) -> AnalysisJob:
        with self._connection.transaction():
            row = self._connection.execute("SELECT * FROM analysis_jobs WHERE id = ? FOR UPDATE", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            job = self._job_from_row(row)
            self._assert_owner(job, worker_id)
            job.progress = progress
            job.current_step = current_step
            job.updated_at = datetime.now(timezone.utc)
            self._save_locked(job)
            return job

    def heartbeat(self, *, job_id: str, worker_id: str, lease_seconds: int) -> AnalysisJob:
        with self._connection.transaction():
            row = self._connection.execute("SELECT * FROM analysis_jobs WHERE id = ? FOR UPDATE", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            job = self._job_from_row(row)
            self._assert_owner(job, worker_id)
            job.heartbeat(lease_seconds=lease_seconds)
            self._save_locked(job)
            return job

    def complete(self, *, job_id: str, worker_id: str, result: dict) -> AnalysisJob:
        with self._connection.transaction():
            row = self._connection.execute("SELECT * FROM analysis_jobs WHERE id = ? FOR UPDATE", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            job = self._job_from_row(row)
            self._assert_owner(job, worker_id)
            job.complete(result)
            self._save_locked(job)
            return job

    def fail(self, *, job_id: str, worker_id: str, error_code: str, error_message: str, retry: bool) -> AnalysisJob:
        with self._connection.transaction():
            row = self._connection.execute("SELECT * FROM analysis_jobs WHERE id = ? FOR UPDATE", (job_id,)).fetchone()
            if row is None:
                raise KeyError(job_id)
            job = self._job_from_row(row)
            self._assert_owner(job, worker_id)
            job.fail(error_code=error_code, error_message=error_message, retry=retry)
            self._save_locked(job)
            return job

    def _assert_owner(self, job: AnalysisJob, worker_id: str) -> None:
        if job.status != AnalysisJobStatus.RUNNING or job.worker_id != worker_id:
            raise RuntimeError("Analysis job is not owned by this worker")

    def _save_locked(self, job: AnalysisJob) -> None:
        self._connection.execute(
            """
            UPDATE analysis_jobs SET
                status = ?, progress = ?, current_step = ?, attempt = ?,
                available_at = ?, started_at = ?, completed_at = ?, failed_at = ?,
                lease_until = ?, worker_id = ?, result = ?, error_code = ?,
                error_message = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                job.status.value,
                job.progress,
                job.current_step,
                job.attempt,
                job.available_at,
                job.started_at,
                job.completed_at,
                job.failed_at,
                job.lease_until,
                job.worker_id,
                json.dumps(job.result) if job.result is not None else None,
                job.error_code,
                job.error_message,
                job.updated_at,
                job.id,
            ),
        )

    def close(self) -> None:
        self._connection.close()
