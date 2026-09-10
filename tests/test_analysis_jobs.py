from datetime import datetime, timedelta, timezone

import pytest

from book_loop.application.use_cases.get_analysis_job import GetAnalysisJob
from book_loop.application.use_cases.start_consistency_analysis import StartConsistencyAnalysis
from book_loop.domain.analysis_job import AnalysisJob, AnalysisJobStatus


class FakeRepository:
    def __init__(self, owner_id: str = "user-1") -> None:
        self.book = type("Book", (), {"owner_id": owner_id})()

    def get(self, book_id: str):
        return self.book


class FakeJobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, AnalysisJob] = {}
        self.by_key: dict[tuple[str, str, str], AnalysisJob] = {}

    def enqueue(self, *, book_id, owner_id, analysis_type, idempotency_key, max_attempts=3):
        key = (book_id, analysis_type, idempotency_key)
        if key in self.by_key:
            return self.by_key[key]
        job = AnalysisJob(book_id=book_id, owner_id=owner_id, analysis_type=analysis_type, idempotency_key=idempotency_key, max_attempts=max_attempts)
        self.jobs[job.id] = job
        self.by_key[key] = job
        return job

    def get(self, job_id):
        return self.jobs[job_id]


def test_claim_sets_lease_and_running_state():
    job = AnalysisJob(book_id="book-1", owner_id="user-1", idempotency_key="key")
    now = datetime(2026, 9, 10, tzinfo=timezone.utc)

    job.claim(worker_id="worker-1", lease_seconds=60, now=now)

    assert job.status == AnalysisJobStatus.RUNNING
    assert job.attempt == 1
    assert job.worker_id == "worker-1"
    assert job.lease_until == now + timedelta(seconds=60)


def test_expired_worker_can_be_reclaimed_as_queued_transition():
    job = AnalysisJob(book_id="book-1", owner_id="user-1", idempotency_key="key", attempt=1)
    job.claim(worker_id="worker-1", lease_seconds=1)
    job.fail(error_code="crash", error_message="retry", retry=True)

    assert job.status == AnalysisJobStatus.QUEUED
    assert job.worker_id is None
    assert job.lease_until is None


def test_failure_becomes_terminal_after_max_attempts():
    job = AnalysisJob(book_id="book-1", owner_id="user-1", idempotency_key="key", attempt=3, max_attempts=3)
    job.status = AnalysisJobStatus.RUNNING
    job.worker_id = "worker-1"

    job.fail(error_code="analysis_failed", error_message="failed", retry=True)

    assert job.status == AnalysisJobStatus.FAILED
    assert job.failed_at is not None


def test_start_is_idempotent():
    repository = FakeRepository()
    store = FakeJobStore()
    use_case = StartConsistencyAnalysis(repository, store)

    first = use_case.execute(book_id="book-1", owner_id="user-1", idempotency_key="same")
    second = use_case.execute(book_id="book-1", owner_id="user-1", idempotency_key="same")

    assert first.id == second.id
    assert len(store.jobs) == 1


def test_start_rejects_other_owner():
    repository = FakeRepository(owner_id="other-user")
    store = FakeJobStore()

    with pytest.raises(KeyError):
        StartConsistencyAnalysis(repository, store).execute(
            book_id="book-1", owner_id="user-1", idempotency_key="key"
        )


def test_get_job_rejects_other_owner():
    repository = FakeRepository()
    store = FakeJobStore()
    job = store.enqueue(book_id="book-1", owner_id="user-1", analysis_type="consistency", idempotency_key="key")

    with pytest.raises(KeyError):
        GetAnalysisJob(repository, store).execute(job_id=job.id, owner_id="other-user")
