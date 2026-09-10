from __future__ import annotations

import os
import threading

import pytest

from book_loop.domain.analysis_job import AnalysisJobStatus
from book_loop.infrastructure.database.analysis_jobs import PostgresAnalysisJobStore


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if not value or not value.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
        pytest.skip("PostgreSQL DATABASE_URL is required")
    return value


def test_two_workers_claim_different_jobs(database_url: str):
    first = PostgresAnalysisJobStore(database_url)
    second = PostgresAnalysisJobStore(database_url)
    try:
        first.enqueue(book_id="book-1", owner_id="user-1", analysis_type="consistency", idempotency_key="job-1")
        first.enqueue(book_id="book-2", owner_id="user-1", analysis_type="consistency", idempotency_key="job-2")
        barrier = threading.Barrier(2)
        claimed: list[str] = []

        def claim(store, worker_id: str) -> None:
            barrier.wait()
            job = store.claim_next(worker_id=worker_id, lease_seconds=60)
            assert job is not None
            claimed.append(job.id)

        threads = [
            threading.Thread(target=claim, args=(first, "worker-a")),
            threading.Thread(target=claim, args=(second, "worker-b")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(claimed) == 2
        assert len(set(claimed)) == 2
    finally:
        first.close()
        second.close()


def test_expired_running_job_is_reclaimable(database_url: str):
    first = PostgresAnalysisJobStore(database_url)
    second = PostgresAnalysisJobStore(database_url)
    try:
        job = first.enqueue(book_id="book-1", owner_id="user-1", analysis_type="consistency", idempotency_key="recovery")
        claimed = first.claim_next(worker_id="worker-a", lease_seconds=1)
        assert claimed is not None

        first._connection.execute(
            "UPDATE analysis_jobs SET lease_until = CURRENT_TIMESTAMP - INTERVAL '1 second' WHERE id = ?",
            (job.id,),
        )
        first._connection.commit()

        recovered = second.claim_next(worker_id="worker-b", lease_seconds=60)
        assert recovered is not None
        assert recovered.id == job.id
        assert recovered.status == AnalysisJobStatus.RUNNING
        assert recovered.worker_id == "worker-b"
        assert recovered.attempt == 2
    finally:
        first.close()
        second.close()
