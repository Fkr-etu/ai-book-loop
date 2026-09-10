from __future__ import annotations

import logging
import os
import signal
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container
from book_loop.infrastructure.database.analysis_jobs import PostgresAnalysisJobStore

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
        logger.info("analysis worker %s started", self.worker_id)
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
            logger.info("analysis worker %s stopped", self.worker_id)

    def _start_health_server(self) -> None:
        port = int(os.getenv("PORT", "8080"))
        self.health_server = ThreadingHTTPServer(("0.0.0.0", port), _HealthHandler)
        thread = threading.Thread(target=self.health_server.serve_forever, daemon=True)
        thread.start()

    def _run_job(self, job_id: str) -> None:
        heartbeat_stop = threading.Event()
        heartbeat = threading.Thread(target=self._heartbeat_loop, args=(job_id, heartbeat_stop), daemon=True)
        heartbeat.start()
        try:
            job = self.store.get(job_id)
            if job.analysis_type != "consistency":
                raise ValueError(f"Unsupported analysis type: {job.analysis_type}")
            self.store.update_progress(job_id=job_id, worker_id=self.worker_id, progress=10, current_step="analyzing")
            issues = self.container.analyze_consistency().execute(book_id=job.book_id)
            result = {"issues": [issue.model_dump(mode="json") for issue in issues]}
            self.store.complete(job_id=job_id, worker_id=self.worker_id, result=result)
            logger.info("analysis job %s completed", job_id)
        except Exception:
            logger.exception("analysis job %s failed", job_id)
            try:
                self.store.fail(
                    job_id=job_id,
                    worker_id=self.worker_id,
                    error_code="analysis_failed",
                    error_message="L’analyse n’a pas pu être terminée. Veuillez réessayer.",
                    retry=True,
                )
            except Exception:
                logger.exception("could not persist failure for analysis job %s", job_id)
        finally:
            heartbeat_stop.set()
            heartbeat.join(timeout=1)

    def _heartbeat_loop(self, job_id: str, stop: threading.Event) -> None:
        interval = max(1, self.lease_seconds // 3)
        heartbeat_store = PostgresAnalysisJobStore(self.settings.database_url)
        try:
            while not stop.wait(interval):
                try:
                    heartbeat_store.heartbeat(job_id=job_id, worker_id=self.worker_id, lease_seconds=self.lease_seconds)
                except Exception:
                    logger.exception("heartbeat failed for analysis job %s", job_id)
        finally:
            heartbeat_store.close()


if __name__ == "__main__":
    AnalysisWorker().run()
