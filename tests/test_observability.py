import json
import logging
import sqlite3

from book_loop.infrastructure.observability import ObservabilityEvent, ObservabilityStore


def test_observability_event_is_persisted_and_logged(tmp_path, caplog) -> None:
    database_url = f"sqlite:///{tmp_path / 'observability.db'}"
    store = ObservabilityStore(database_url)

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

    connection = sqlite3.connect(tmp_path / "observability.db")
    row = connection.execute(
        "SELECT event_type, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata FROM observability_events"
    ).fetchone()

    assert row[:7] == ("ChapterReviewed", "run-1", "book-1", 3, 2, 125, "completed")
    assert json.loads(row[7]) == {"issue_count": 1, "review_score": 8}
    assert "workflow_event" in caplog.text
    assert "ChapterReviewed" in caplog.text

    store.close()
    connection.close()


def test_observability_store_creates_schema_on_startup(tmp_path) -> None:
    store = ObservabilityStore(f"sqlite:///{tmp_path / 'observability.db'}")
    tables = store._connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='observability_events'"
    ).fetchall()
    assert tables == [("observability_events",)]
    store.close()
