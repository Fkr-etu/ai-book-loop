from __future__ import annotations

import logging
import os
import signal
import threading
import uuid
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container
from book_loop.infrastructure.database.analysis_jobs import PostgresAnalysisJobStore
from book_loop.infrastructure.structured_logging import log_event

logger = logging.getLogger("book_loop.worker")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def log_message(self, format: str, *args) -> None:
        return


class AnalysisWorker:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.worker_id = os.getenv("WORKER_ID", f"worker-{uuid.uuid4()}")
        self.lease_seconds = int(os.getenv("ANALYSIS_JOB_LEASE_SECONDS", "900"))
        self.poll_seconds = float(os.getenv("ANALYSIS_JOB_POLL_SECONDS", "2"))
        self._stop = threading.Event()
        self.store = PostgresAnalysisJobStore(self.settings.database_url)
        self.container = Container(self.settings)
        self.health_server: ThreadingHTTPServer | None = None

    def stop(self, *_args) -> None:
        self._stop.set()
        if self.health_server is not None:
            self.health_server.shutdown()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self._start_health_server()
        log_event(logger, logging.INFO, "analysis_worker_started", worker_id=self.worker_id)
        try:
            while not self._stop.is_set():
                job = self.store.claim_next(worker_id=self.worker_id, lease_seconds=self.lease_seconds)
                if job is None:
                    self._stop.wait(self.poll_seconds)
                    continue
                self._run_job(job.id)
        finally:
            self.store.close()
            if self.health_server is not None:
                self.health_server.server_close()
            log_event(logger, logging.INFO, "analysis_worker_stopped", worker_id=self.worker_id)

    def _start_health_server(self) -> None:
        port = int(os.getenv("PORT", "8080"))
        self.health_server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
        thread = threading.Thread(target=self.health_server.serve_forever, daemon=True)
        thread.start()

    def _run_job(self, job_id: str) -> None:
        heartbeat_stop = threading.Event()
        heartbeat = threading.Thread(target=self._heartbeat_loop, args=(job_id, heartbeat_stop), daemon=True)
        heartbeat.start()
        execution_started = datetime.now(UTC)
        try:
            job = self.store.get(job_id)
            if job.analysis_type == "consistency":
                self._run_consistency(job_id=job_id, job=job, execution_started=execution_started)
            elif job.analysis_type == "ingestion":
                self._run_ingestion(job_id=job_id, job=job, execution_started=execution_started)
            else:
                raise ValueError(f"Unsupported analysis type: {job.analysis_type}")
        except Exception:
            log_event(logger, logging.ERROR, "analysis_job_failed", job_id=job_id, worker_id=self.worker_id)
            try:
                failed = self.store.fail(
                    job_id=job_id,
                    worker_id=self.worker_id,
                    error_code="analysis_failed",
                    error_message="L’analyse n’a pas pu être terminée. Veuillez réessayer.",
                    retry=True,
                )
                log_event(
                    logger,
                    logging.INFO,
                    "analysis_job_failure_recorded",
                    job_id=failed.id,
                    book_id=failed.book_id,
                    analysis_type=failed.analysis_type,
                    worker_id=self.worker_id,
                    attempt=failed.attempt,
                    max_attempts=failed.max_attempts,
                    retry_scheduled=failed.status.value == "queued",
                    execution_duration_ms=self._elapsed_ms(execution_started, datetime.now(UTC)),
                    status=failed.status.value,
                    error_code=failed.error_code,
                )
            except Exception:
                log_event(logger, logging.ERROR, "analysis_job_failure_persist_error", job_id=job_id, worker_id=self.worker_id)
        finally:
            heartbeat_stop.set()
            heartbeat.join(timeout=1)

    def _run_consistency(self, *, job_id: str, job, execution_started: datetime) -> None:
        queue_wait_ms = self._elapsed_ms(job.created_at, job.started_at)
        self.store.update_progress(job_id=job_id, worker_id=self.worker_id, progress=10, current_step="analyzing")
        issues = self.container.analyze_consistency().execute(book_id=job.book_id)
        execution_duration_ms = self._elapsed_ms(execution_started, datetime.now(UTC))
        result = {"issues": [issue.model_dump(mode="json") for issue in issues]}
        completed = self.store.complete(job_id=job_id, worker_id=self.worker_id, result=result)
        log_event(
            logger,
            logging.INFO,
            "analysis_job_succeeded",
            job_id=completed.id,
            book_id=completed.book_id,
            analysis_type=completed.analysis_type,
            worker_id=self.worker_id,
            attempt=completed.attempt,
            max_attempts=completed.max_attempts,
            queue_wait_ms=queue_wait_ms,
            execution_duration_ms=execution_duration_ms,
            issue_count=len(issues),
            status=completed.status.value,
        )

    def _run_ingestion(self, *, job_id: str, job, execution_started: datetime) -> None:
        self.store.update_progress(job_id=job_id, worker_id=self.worker_id, progress=5, current_step="preparing")

        def on_chunk_progress(done: int, total: int) -> None:
            progress = 10 if total == 0 else 10 + int(done / total * 85)
            self.store.update_progress(job_id=job_id, worker_id=self.worker_id, progress=min(progress, 95), current_step=f"chunk {done}/{total}")

        result = self.container.ingest_document().process_by_hash(
            book_id=job.book_id,
            content_hash=job.idempotency_key,
            on_chunk_progress=on_chunk_progress,
        )
        completed = self.store.complete(
            job_id=job_id,
            worker_id=self.worker_id,
            result={
                "source_document": result.source_document.model_dump(mode="json"),
                "chunks": len(result.chunks),
                "assertions": len(result.assertions),
                "evidence": len(result.evidence),
            },
        )
        log_event(
            logger,
            logging.INFO,
            "analysis_job_succeeded",
            job_id=completed.id,
            book_id=completed.book_id,
            analysis_type=completed.analysis_type,
            worker_id=self.worker_id,
            attempt=completed.attempt,
            max_attempts=completed.max_attempts,
            execution_duration_ms=self._elapsed_ms(execution_started, datetime.now(UTC)),
            chunk_count=len(result.chunks),
            assertion_count=len(result.assertions),
            status=completed.status.value,
        )

    @staticmethod
    def _elapsed_ms(start: datetime | None, end: datetime | None) -> int | None:
        if start is None or end is None:
            return None
        return max(0, int((end - start).total_seconds() * 1000))

    def _heartbeat_loop(self, job_id: str, stop: threading.Event) -> None:
        interval = max(1, self.lease_seconds // 3)
        heartbeat_store = PostgresAnalysisJobStore(self.settings.database_url)
        try:
            while not stop.wait(interval):
                try:
                    heartbeat_store.heartbeat(job_id=job_id, worker_id=self.worker_id, lease_seconds=self.lease_seconds)
                except Exception:
                    log_event(logger, logging.ERROR, "analysis_job_heartbeat_failed", job_id=job_id, worker_id=self.worker_id)
        finally:
            heartbeat_store.close()


if __name__ == "__main__":
    AnalysisWorker().run()
