from __future__ import annotations

import logging
import os
import signal
import threading
import time
import uuid

from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.container import Container
from book_loop.infrastructure.database.analysis_jobs import PostgresAnalysisJobStore

logger = logging.getLogger("book_loop.worker")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


class AnalysisWorker:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.worker_id = os.getenv("WORKER_ID", f"worker-{uuid.uuid4()}")
        self.lease_seconds = int(os.getenv("ANALYSIS_JOB_LEASE_SECONDS", "900"))
        self.poll_seconds = float(os.getenv("ANALYSIS_JOB_POLL_SECONDS", "2"))
        self._stop = threading.Event()
        self.store = PostgresAnalysisJobStore(self.settings.database_url)
        self.container = Container(self.settings)

    def stop(self, *_args) -> None:
        self._stop.set()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        logger.info("analysis worker %s started", self.worker_id)
        try:
            while not self._stop.is_set():
                job = self.store.claim_next(
                    worker_id=self.worker_id,
                    lease_seconds=self.lease_seconds,
                )
                if job is None:
                    self._stop.wait(self.poll_seconds)
                    continue
                self._run_job(job.id)
        finally:
            self.store.close()
            logger.info("analysis worker %s stopped", self.worker_id)

    def _run_job(self, job_id: str) -> None:
        heartbeat_stop = threading.Event()
        heartbeat = threading.Thread(
            target=self._heartbeat_loop,
            args=(job_id, heartbeat_stop),
            daemon=True,
        )
        heartbeat.start()
        try:
            job = self.store.get(job_id)
            if job.analysis_type != "consistency":
                raise ValueError(f"Unsupported analysis type: {job.analysis_type}")
            job.progress = 10
            job.current_step = "analyzing"
            self._save_progress(job_id, job.progress, job.current_step)
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

    def _save_progress(self, job_id: str, progress: int, current_step: str) -> None:
        job = self.store.get(job_id)
        if job.worker_id != self.worker_id:
            raise RuntimeError("Analysis job ownership was lost")
        job.progress = progress
        job.current_step = current_step
        job.updated_at = job.updated_at
        with self.store._connection.transaction():
            self.store._save_locked(job)

    def _heartbeat_loop(self, job_id: str, stop: threading.Event) -> None:
        interval = max(1, self.lease_seconds // 3)
        while not stop.wait(interval):
            try:
                self.store.heartbeat(
                    job_id=job_id,
                    worker_id=self.worker_id,
                    lease_seconds=self.lease_seconds,
                )
            except Exception:
                logger.exception("heartbeat failed for analysis job %s", job_id)


if __name__ == "__main__":
    AnalysisWorker().run()
