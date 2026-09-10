from __future__ import annotations

from book_loop.application.ports.analysis_jobs import AnalysisJobStore
from book_loop.domain.analysis_job import AnalysisJob


class GetAnalysisJob:
    def __init__(self, repository, job_store: AnalysisJobStore) -> None:
        self.repository = repository
        self.job_store = job_store

    def execute(self, *, job_id: str, owner_id: str) -> AnalysisJob:
        job = self.job_store.get(job_id)
        if job.owner_id != owner_id:
            raise KeyError(job_id)
        return job
