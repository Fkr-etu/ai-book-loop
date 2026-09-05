from __future__ import annotations

import json
import sqlite3
import uuid

from book_loop.domain.workflow import ChapterWorkflowRun


class SQLiteWorkflowRunStore:
    """Durable checkpoints for chapter generation runs.

    A run is uniquely identified by (book, chapter, idempotency key). Each
    checkpoint is committed independently so a process restart can resume from
    the last completed step.
    """

    def __init__(self, database_url: str) -> None:
        path = database_url.removeprefix("sqlite:///")
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                book_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                idempotency_key TEXT NOT NULL,
                status TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book_id, chapter_number, idempotency_key)
            )
            """
        )
        self._connection.commit()

    def get_or_create(
        self, *, book_id: str, chapter_number: int, idempotency_key: str
    ) -> ChapterWorkflowRun:
        row = self._connection.execute(
            "SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? AND idempotency_key = ?",
            (book_id, chapter_number, idempotency_key),
        ).fetchone()
        if row is not None:
            return ChapterWorkflowRun.model_validate(json.loads(row["state"]))

        run = ChapterWorkflowRun(
            id=str(uuid.uuid4()),
            book_id=book_id,
            chapter_number=chapter_number,
            idempotency_key=idempotency_key,
        )
        self._connection.execute(
            "INSERT INTO workflow_runs(id, book_id, chapter_number, idempotency_key, status, state) VALUES(?, ?, ?, ?, ?, ?)",
            (
                run.id,
                run.book_id,
                run.chapter_number,
                run.idempotency_key,
                run.status.value,
                json.dumps(run.model_dump(mode="json")),
            ),
        )
        self._connection.commit()
        return run

    def save(self, run: ChapterWorkflowRun) -> None:
        self._connection.execute(
            """
            UPDATE workflow_runs
            SET status = ?, state = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                run.status.value,
                json.dumps(run.model_dump(mode="json")),
                run.id,
            ),
        )
        self._connection.commit()
