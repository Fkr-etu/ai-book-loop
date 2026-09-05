from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import psycopg

from book_loop.workflow.chapter_graph import ChapterWorkflow


logger = logging.getLogger("book_loop.observability")


@dataclass(frozen=True)
class ObservabilityEvent:
    event_type: str
    workflow_run_id: str | None = None
    book_id: str | None = None
    chapter_number: int | None = None
    attempt: int | None = None
    duration_ms: int | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityStore:
    """Persist structured workflow events while emitting JSON logs."""

    def __init__(self, database_url: str) -> None:
        self._postgres = database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://"))
        if self._postgres:
            url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
            self._connection = psycopg.connect(url)
            self._connection.execute(self._schema())
        elif database_url.startswith("sqlite:///"):
            path = database_url.removeprefix("sqlite:///")
            self._connection = sqlite3.connect(path, check_same_thread=False)
            self._connection.execute(self._schema())
        else:
            raise ValueError("Unsupported DATABASE_URL for observability")
        self._connection.commit()

    @staticmethod
    def _schema() -> str:
        return """
        CREATE TABLE IF NOT EXISTS observability_events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            workflow_run_id TEXT,
            book_id TEXT,
            chapter_number INTEGER,
            attempt INTEGER,
            duration_ms INTEGER,
            status TEXT,
            metadata TEXT NOT NULL
        )
        """

    def record(self, event: ObservabilityEvent) -> str:
        event_id = str(uuid.uuid4())
        occurred_at = datetime.now(timezone.utc).isoformat()
        metadata = json.dumps(event.metadata, ensure_ascii=False, sort_keys=True)
        params = (event_id, event.event_type, occurred_at, event.workflow_run_id, event.book_id, event.chapter_number, event.attempt, event.duration_ms, event.status, metadata)
        if self._postgres:
            self._connection.execute(
                """INSERT INTO observability_events
                (id, event_type, occurred_at, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                params,
            )
        else:
            self._connection.execute(
                """INSERT INTO observability_events
                (id, event_type, occurred_at, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                params,
            )
        self._connection.commit()
        logger.info(json.dumps({"event": event.event_type, "event_id": event_id, "occurred_at": occurred_at, **{k: v for k, v in {"workflow_run_id": event.workflow_run_id, "book_id": event.book_id, "chapter_number": event.chapter_number, "attempt": event.attempt, "duration_ms": event.duration_ms, "status": event.status}.items() if v is not None}, "metadata": event.metadata}, ensure_ascii=False, sort_keys=True))
        return event_id

    def close(self) -> None:
        self._connection.close()


class InstrumentedChapterWorkflow(ChapterWorkflow):
    """Add low-cardinality workflow telemetry without changing workflow semantics."""

    def __init__(self, *, observability: ObservabilityStore, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.observability = observability
        self._active_run_id: str | None = None
        self._active_book_id: str | None = None
        self._active_chapter: int | None = None

    def _record_step(self, event_type: str, state, started: float, *, status: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        self.observability.record(
            ObservabilityEvent(
                event_type=event_type,
                workflow_run_id=self._active_run_id,
                book_id=self._active_book_id,
                chapter_number=self._active_chapter,
                attempt=getattr(state, "attempt", None),
                duration_ms=max(0, int((time.perf_counter() - started) * 1000)),
                status=status,
                metadata=metadata or {},
            )
        )

    def _write(self, state):
        started = time.perf_counter()
        result = super()._write(state)
        self._record_step("chapter_generated", state, started, status="ok", metadata={"draft_chars": len(result["draft"])})
        return result

    def _review(self, state):
        started = time.perf_counter()
        result = super()._review(state)
        self._record_step("chapter_reviewed", state, started, status=result["decision"], metadata={"review_score": result["review_score"], "issue_count": len(result["review"].issues)})
        return result

    def _correct(self, state):
        started = time.perf_counter()
        self.observability.record(ObservabilityEvent("correction_started", self._active_run_id, self._active_book_id, self._active_chapter, state.attempt))
        result = super()._correct(state)
        self._record_step("correction_completed", state, started, status="ok", metadata={"draft_chars": len(result["draft"])})
        return result

    def _summarize(self, state):
        started = time.perf_counter()
        result = super()._summarize(state)
        self._record_step("chapter_approved", state, started, status="approved")
        return result

    def run(self, *, book, chapter_number: int, idempotency_key: str | None = None):
        started = time.perf_counter()
        key = idempotency_key or str(uuid.uuid4())
        self._active_book_id = book.id
        self._active_chapter = chapter_number
        run = self.workflow_store.get_or_create(book_id=book.id, chapter_number=chapter_number, idempotency_key=key) if self.workflow_store else None
        self._active_run_id = run.id if run else None
        self.observability.record(ObservabilityEvent("workflow_started", self._active_run_id, book.id, chapter_number, run.attempt if run else 0, metadata={"idempotency_key": key}))
        try:
            result = super().run(book=book, chapter_number=chapter_number, idempotency_key=key)
            status = "completed" if result.summary is not None else "needs_review"
            self.observability.record(ObservabilityEvent("workflow_finished", self._active_run_id, book.id, chapter_number, result.attempt, max(0, int((time.perf_counter() - started) * 1000)), status))
            return result
        except Exception as exc:
            self.observability.record(ObservabilityEvent("workflow_failed", self._active_run_id, book.id, chapter_number, metadata={"error_type": type(exc).__name__}))
            raise
        finally:
            self._active_run_id = None
            self._active_book_id = None
            self._active_chapter = None
