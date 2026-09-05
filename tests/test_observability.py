from __future__ import annotations

import json
import sqlite3

from book_loop.infrastructure.observability import ObservabilityEvent, ObservabilityStore


def test_observability_store_persists_structured_event(tmp_path):
    database = tmp_path / "book.db"
    store = ObservabilityStore(f"sqlite:///{database}")

    event_id = store.record(
        ObservabilityEvent(
            event_type="chapter_reviewed",
            workflow_run_id="run-1",
            book_id="book-1",
            chapter_number=2,
            attempt=3,
            duration_ms=412,
            status="retry",
            metadata={"review_score": 6.5, "issue_count": 2},
        )
    )

    row = sqlite3.connect(database).execute(
        "SELECT id, event_type, workflow_run_id, book_id, chapter_number, attempt, duration_ms, status, metadata FROM observability_events"
    ).fetchone()
    assert row[:8] == (event_id, "chapter_reviewed", "run-1", "book-1", 2, 3, 412, "retry")
    assert json.loads(row[8]) == {"issue_count": 2, "review_score": 6.5}
    store.close()
