from __future__ import annotations

import json

from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.database.postgres import PostgresWorkflowRunStore


class PostgresWorkflowRunReader(PostgresWorkflowRunStore):
    """Read-only workflow projections used by the API layer."""

    def get(self, run_id: str) -> ChapterWorkflowRun:
        row = self._connection.execute(
            "SELECT state FROM workflow_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return ChapterWorkflowRun.model_validate(json.loads(row["state"]))

    def get_latest(self, *, book_id: str, chapter_number: int) -> ChapterWorkflowRun:
        row = self._connection.execute(
            "SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? "
            "ORDER BY updated_at DESC, created_at DESC LIMIT 1",
            (book_id, chapter_number),
        ).fetchone()
        if row is None:
            raise KeyError((book_id, chapter_number))
        return ChapterWorkflowRun.model_validate(json.loads(row["state"]))
