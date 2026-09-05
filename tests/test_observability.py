from __future__ import annotations

import json
import logging
import os

from book_loop.infrastructure.observability import ObservabilityEvent, ObservabilityStore


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://book_loop:book_loop@localhost:5432/book_loop_test")


def test_observability_event_is_persisted_and_logged(caplog) -> None:
    store = ObservabilityStore(DATABASE_URL)

    with caplog.at_level(logging.INFO, logger="book_loop.observability"):
        store.record(
            ObservabilityEvent(
                event_type="ChapterReviewed",
                workflow_run_id="run-1",
                book_id="book-1",
                chapter_number=3,
                attempt=2,
                duration_ms=125,
                status="completed",
                metadata={"review_score": 8, "issue_count": 1},
            )
        )

    row = store._connection.execute(
        "SELECT event_type, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata FROM observability_events"
    ).fetchone()

    assert row is not None
    assert tuple(row.values()) == (
        "ChapterReviewed",
        "run-1",
        "book-1",
        3,
        2,
        125,
        "completed",
        json.dumps({"issue_count": 1, "review_score": 8}, sort_keys=True),
    )
    assert "workflow_event" in caplog.text
    assert "ChapterReviewed" in caplog.text
    store.close()


def test_observability_store_creates_schema_on_startup() -> None:
    store = ObservabilityStore(DATABASE_URL)
    tables = store._connection.execute(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' AND tablename = 'observability_events'"
    ).fetchall()
    assert [row["tablename"] for row in tables] == ["observability_events"]
    store.close()
