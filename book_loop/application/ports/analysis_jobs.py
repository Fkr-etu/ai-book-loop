from __future__ import annotations

from typing import Protocol

from book_loop.domain.analysis_job import AnalysisJob


class AnalysisJobStore(Protocol):
    def enqueue(
        self,
        *,
        book_id: str,
        owner_id: str,
        analysis_type: str,
        idempotency_key: str,
        max_attempts: int = 3,
    ) -> AnalysisJob: ...

    def get(self, job_id: str) -> AnalysisJob: ...

    def get_by_idempotency(
        self, *, book_id: str, analysis_type: str, idempotency_key: str
    ) -> AnalysisJob | None: ...

    def claim_next(self, *, worker_id: str, lease_seconds: int) -> AnalysisJob | None: ...

    def update_progress(
        self,
        *,
        job_id: str,
        worker_id: str,
        progress: int,
        current_step: str | None,
    ) -> AnalysisJob: ...

    def heartbeat(self, *, job_id: str, worker_id: str, lease_seconds: int) -> AnalysisJob: ...

    def complete(self, *, job_id: str, worker_id: str, result: dict) -> AnalysisJob: ...

    def fail(
        self,
        *,
        job_id: str,
        worker_id: str,
        error_code: str,
        error_message: str,
        retry: bool,
    ) -> AnalysisJob: ...
