from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import psycopg


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
    """Persist workflow events to PostgreSQL and mirror them to structured logs."""

    def __init__(self, database_url: str) -> None:
        if not database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
            raise ValueError("ObservabilityStore requires a PostgreSQL DATABASE_URL")
        url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        self._connection = psycopg.connect(url, autocommit=True)
        self._connection.execute(
            """
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
        )

    def record(self, event: ObservabilityEvent) -> None:
        event_id = str(uuid.uuid4())
        occurred_at = datetime.now(UTC).isoformat()
        metadata = json.dumps(event.metadata, ensure_ascii=False, sort_keys=True)
        self._connection.execute(
            """
            INSERT INTO observability_events
            (id, event_type, occurred_at, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (event_id, event.event_type, occurred_at, event.workflow_run_id, event.book_id, event.chapter_number, event.attempt, event.duration_ms, event.status, metadata),
        )
        logger.info(
            "workflow_event event_type=%s",
            event.event_type,
            extra={
                "event_type": event.event_type,
                "workflow_run_id": event.workflow_run_id,
                "book_id": event.book_id,
                "chapter_number": event.chapter_number,
                "attempt": event.attempt,
                "duration_ms": event.duration_ms,
                "status": event.status,
                "metadata": event.metadata,
            },
        )

    def close(self) -> None:
        self._connection.close()
