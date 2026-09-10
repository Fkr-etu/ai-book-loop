from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import book_loop.worker as worker_module
from book_loop.domain.analysis_job import AnalysisJob, AnalysisJobStatus


class FakeIssue:
    def model_dump(self, *, mode: str):
        assert mode == "json"
        return {
            "id": "issue-1",
            "message": "Contradiction détectée",
            "severity": "warning",
            "left_statement": "Maya est à Paris.",
            "right_statement": "Maya est à Lyon.",
        }


class FakeHeartbeatStore:
    def __init__(self, _database_url: str):
        self.closed = False

    def heartbeat(self, **_kwargs):
        return None

    def close(self):
        self.closed = True


class FakeWorkerStore:
    def __init__(self, job: AnalysisJob, completion_status: AnalysisJobStatus):
        self.job = job
        self.completion_status = completion_status
        self.completed_result = None
        self.failure_args = None

    def get(self, job_id: str):
        assert job_id == self.job.id
        return self.job

    def update_progress(self, **kwargs):
        assert kwargs["job_id"] == self.job.id
        assert kwargs["progress"] == 10
        assert kwargs["current_step"] == "analyzing"

    def complete(self, *, job_id: str, worker_id: str, result: dict):
        assert job_id == self.job.id
        assert worker_id == "worker-test"
        self.completed_result = result
        self.job.status = self.completion_status
        self.job.progress = 100
        self.job.completed_at = datetime.now(UTC)
        return self.job

    def fail(self, **kwargs):
        self.failure_args = kwargs
        self.job.fail(
            error_code=kwargs["error_code"],
            error_message=kwargs["error_message"],
            retry=kwargs["retry"],
        )
        return self.job


def make_worker(store: FakeWorkerStore, issues=None):
    worker = object.__new__(worker_module.AnalysisWorker)
    worker.worker_id = "worker-test"
    worker.lease_seconds = 900
    worker.store = store
    worker.settings = SimpleNamespace(database_url="postgresql://test")
    worker.container = SimpleNamespace(
        analyze_consistency=lambda: SimpleNamespace(execute=lambda book_id: issues or [])
    )
    return worker


def test_worker_run_job_persists_success_result(monkeypatch):
    job = AnalysisJob(
        book_id="book-1",
        owner_id="user-1",
        idempotency_key="key",
        status=AnalysisJobStatus.RUNNING,
        attempt=1,
        started_at=datetime.now(UTC) - timedelta(seconds=2),
        worker_id="worker-test",
    )
    store = FakeWorkerStore(job, AnalysisJobStatus.SUCCEEDED)
    worker = make_worker(store, [FakeIssue()])
    monkeypatch.setattr(worker_module, "PostgresAnalysisJobStore", FakeHeartbeatStore)

    worker._run_job(job.id)

    assert store.completed_result == {"issues": [FakeIssue().model_dump(mode="json")]}
    assert store.failure_args is None


def test_worker_run_job_records_failure_and_retries(monkeypatch):
    job = AnalysisJob(
        book_id="book-1",
        owner_id="user-1",
        idempotency_key="key",
        status=AnalysisJobStatus.RUNNING,
        attempt=1,
        max_attempts=3,
        started_at=datetime.now(UTC),
        worker_id="worker-test",
    )
    store = FakeWorkerStore(job, AnalysisJobStatus.SUCCEEDED)
    worker = make_worker(store)
    worker.container = SimpleNamespace(
        analyze_consistency=lambda: SimpleNamespace(
            execute=lambda _book_id: (_ for _ in ()).throw(RuntimeError("boom"))
        )
    )
    monkeypatch.setattr(worker_module, "PostgresAnalysisJobStore", FakeHeartbeatStore)

    worker._run_job(job.id)

    assert store.failure_args["error_code"] == "analysis_failed"
    assert store.failure_args["retry"] is True
    assert job.status == AnalysisJobStatus.QUEUED


def test_worker_run_job_stops_retrying_at_max_attempts(monkeypatch):
    job = AnalysisJob(
        book_id="book-1",
        owner_id="user-1",
        idempotency_key="key",
        status=AnalysisJobStatus.RUNNING,
        attempt=3,
        max_attempts=3,
        started_at=datetime.now(UTC),
        worker_id="worker-test",
    )
    store = FakeWorkerStore(job, AnalysisJobStatus.SUCCEEDED)
    worker = make_worker(store)
    worker.container = SimpleNamespace(
        analyze_consistency=lambda: SimpleNamespace(
            execute=lambda _book_id: (_ for _ in ()).throw(RuntimeError("boom"))
        )
    )
    monkeypatch.setattr(worker_module, "PostgresAnalysisJobStore", FakeHeartbeatStore)

    worker._run_job(job.id)

    assert store.failure_args["retry"] is True
    assert job.status == AnalysisJobStatus.FAILED
    assert job.failed_at is not None
