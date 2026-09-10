from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from book_loop.domain.analysis_job import AnalysisJob, AnalysisJobStatus
from book_loop.worker import AnalysisWorker


class FakeStore:
    def __init__(self, job: AnalysisJob) -> None:
        self.job = job
        self.failed = None
        self.completed = None

    def get(self, job_id: str) -> AnalysisJob:
        assert job_id == self.job.id
        return self.job

    def update_progress(self, **kwargs):
        return self.job

    def complete(self, *, job_id: str, worker_id: str, result: dict) -> AnalysisJob:
        self.job.complete(result)
        self.completed = result
        return self.job

    def fail(self, *, job_id: str, worker_id: str, error_code: str, error_message: str, retry: bool) -> AnalysisJob:
        self.job.fail(error_code=error_code, error_message=error_message, retry=retry)
        self.failed = (error_code, retry)
        return self.job


class FakeAnalysis:
    def __init__(self, issues=None, error: Exception | None = None) -> None:
        self.issues = issues or []
        self.error = error

    def execute(self, *, book_id: str):
        if self.error:
            raise self.error
        return self.issues


def make_worker(store: FakeStore, analysis: FakeAnalysis) -> AnalysisWorker:
    worker = AnalysisWorker.__new__(AnalysisWorker)
    worker.store = store
    worker.worker_id = "test-worker"
    worker.container = SimpleNamespace(analyze_consistency=lambda: analysis)
    worker._heartbeat_loop = lambda job_id, stop: None
    return worker


def make_job() -> AnalysisJob:
    created = datetime.now(UTC) - timedelta(seconds=3)
    return AnalysisJob(
        id="job-1",
        book_id="book-1",
        owner_id="owner-1",
        idempotency_key="key-1",
        status=AnalysisJobStatus.RUNNING,
        attempt=1,
        started_at=created + timedelta(seconds=2),
        created_at=created,
    )


def test_success_emits_correlated_timing_fields(caplog) -> None:
    job = make_job()
    store = FakeStore(job)
    issue = SimpleNamespace(model_dump=lambda mode: {"id": "issue-1"})
    worker = make_worker(store, FakeAnalysis([issue]))

    with caplog.at_level("INFO", logger="book_loop.worker"):
        worker._run_job(job.id)

    record = next(item for item in caplog.records if item.msg == "analysis_job_succeeded")
    assert record.job_id == "job-1"
    assert record.book_id == "book-1"
    assert record.attempt == 1
    assert record.queue_wait_ms >= 2000
    assert record.execution_duration_ms >= 0
    assert record.issue_count == 1
    assert record.status == "succeeded"


def test_failure_emits_retry_and_correlation_fields(caplog) -> None:
    job = make_job()
    store = FakeStore(job)
    worker = make_worker(store, FakeAnalysis(error=RuntimeError("boom")))

    with caplog.at_level("INFO", logger="book_loop.worker"):
        worker._run_job(job.id)

    record = next(item for item in caplog.records if item.msg == "analysis_job_failure_recorded")
    assert record.job_id == "job-1"
    assert record.book_id == "book-1"
    assert record.attempt == 1
    assert record.retry_scheduled is True
    assert record.error_code == "analysis_failed"
    assert record.execution_duration_ms >= 0
