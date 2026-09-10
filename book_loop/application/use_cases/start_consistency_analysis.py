from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.analysis_jobs import AnalysisJobStore
from book_loop.domain.analysis_job import AnalysisJob


class StartConsistencyAnalysis:
    """Create durable execution intent without running the analysis in HTTP."""

    def __init__(self, repository, job_store: AnalysisJobStore) -> None:
        self.repository = repository
        self.job_store = job_store

    def execute(
        self,
        *,
        book_id: str,
        owner_id: str,
        idempotency_key: str | None = None,
    ) -> AnalysisJob:
        book = self.repository.get(book_id)
        if book.owner_id != owner_id:
            raise KeyError(book_id)
        key = idempotency_key or str(uuid4())
        return self.job_store.enqueue(
            book_id=book_id,
            owner_id=owner_id,
            analysis_type="consistency",
            idempotency_key=key,
        )
