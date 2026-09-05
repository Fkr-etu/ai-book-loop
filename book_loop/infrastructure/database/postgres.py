from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from book_loop.domain.models import (
    AssertionStatus,
    BookState,
    CanonicalFact,
    Conflict,
    DocumentChunk,
    Evidence,
    ReviewDecision,
    SceneReview,
    SourceDocument,
    User,
)
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.database.repository import BookRepositoryMixin


def _normalize_postgres_url(database_url: str) -> str:
    """Accept both libpq URLs and SQLAlchemy-style postgres URLs."""
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    return database_url


class _PostgresConnectionAdapter:
    """Small DB-API compatibility layer for repository parameter style."""

    def __init__(self, database_url: str) -> None:
        self._connection = psycopg.connect(_normalize_postgres_url(database_url), row_factory=dict_row)
        self._transaction_depth = 0

    def execute(self, sql: str, params: tuple[Any, ...] = ()):
        sql = sql.replace("?", "%s")
        if "INSERT INTO workflow_runs" in sql and "ON CONFLICT" not in sql:
            sql += " ON CONFLICT DO NOTHING"
        return self._connection.execute(sql, params)

    def commit(self) -> None:
        if self._transaction_depth == 0:
            self._connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        outermost = self._transaction_depth == 0
        if outermost:
            self._connection.execute("BEGIN")
        self._transaction_depth += 1
        try:
            yield
        except Exception:
            self._transaction_depth -= 1
            if outermost:
                self._connection.rollback()
            raise
        else:
            self._transaction_depth -= 1
            if outermost:
                self._connection.commit()

    def close(self) -> None:
        self._connection.close()


class PostgresBookRepository(BookRepositoryMixin):
    """PostgreSQL repository for all persistent Book state."""

    def __init__(self, database_url: str) -> None:
        if not database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
            raise ValueError("PostgresBookRepository requires a PostgreSQL DATABASE_URL")
        self._connection = _PostgresConnectionAdapter(database_url)
        self._connection._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chapter_versions (id BIGSERIAL PRIMARY KEY, book_id TEXT NOT NULL, chapter_number INTEGER NOT NULL, version INTEGER NOT NULL, draft TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, chapter_number, version));
            CREATE TABLE IF NOT EXISTS reviews (id BIGSERIAL PRIMARY KEY, book_id TEXT NOT NULL, chapter_number INTEGER NOT NULL, version INTEGER NOT NULL, score DOUBLE PRECISION NOT NULL, approved BOOLEAN NOT NULL, issues TEXT NOT NULL, suggestions TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS source_documents (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, name TEXT NOT NULL, source_type TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL, metadata TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, content_hash));
            CREATE TABLE IF NOT EXISTS document_chunks (id TEXT PRIMARY KEY, source_document_id TEXT NOT NULL, content TEXT NOT NULL, sequence INTEGER NOT NULL, start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL, metadata TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS assertions (id TEXT PRIMARY KEY, source_document_id TEXT NOT NULL, chunk_id TEXT NOT NULL, statement TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL, confidence DOUBLE PRECISION NOT NULL, status TEXT NOT NULL, evidence_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, assertion_id TEXT NOT NULL, source_document_id TEXT NOT NULL, chunk_id TEXT NOT NULL, start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL, excerpt TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS conflicts (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, left_assertion_id TEXT NOT NULL, right_assertion_id TEXT NOT NULL, status TEXT NOT NULL, resolution_assertion_id TEXT, UNIQUE(left_assertion_id, right_assertion_id));
            CREATE TABLE IF NOT EXISTS review_decisions (id TEXT PRIMARY KEY, assertion_id TEXT NOT NULL, decision TEXT NOT NULL, reviewer_id TEXT, rationale TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS canonical_facts (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, assertion_id TEXT NOT NULL, statement TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL, decision_id TEXT NOT NULL, version INTEGER NOT NULL, active BOOLEAN NOT NULL, previous_fact_id TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, subject, predicate, version));
            """
        )
        self._connection._connection.execute("ALTER TABLE canonical_facts ADD COLUMN IF NOT EXISTS previous_fact_id TEXT")
        self._connection._connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_active_canonical_fact ON canonical_facts(book_id, subject, predicate) WHERE active = TRUE")
        self._connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._connection.transaction():
            yield

    def lock_assertion(self, assertion_id: str) -> None:
        self._connection.execute("SELECT id FROM assertions WHERE id = ? FOR UPDATE", (assertion_id,)).fetchone()


class PostgresWorkflowRunStore:
    """Durable PostgreSQL checkpoints for chapter generation runs."""

    def __init__(self, database_url: str) -> None:
        self._connection = _PostgresConnectionAdapter(database_url)
        self._connection._connection.execute(
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

    def get_or_create(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun:
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? AND idempotency_key = ?", (book_id, chapter_number, idempotency_key)).fetchone()
        if row is not None:
            return ChapterWorkflowRun.model_validate(json.loads(row["state"]))
        run = ChapterWorkflowRun(id=str(uuid.uuid4()), book_id=book_id, chapter_number=chapter_number, idempotency_key=idempotency_key)
        self._connection.execute("INSERT INTO workflow_runs(id, book_id, chapter_number, idempotency_key, status, state) VALUES(?, ?, ?, ?, ?, ?)", (run.id, run.book_id, run.chapter_number, run.idempotency_key, run.status.value, json.dumps(run.model_dump(mode="json"))))
        self._connection.commit()
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? AND idempotency_key = ?", (book_id, chapter_number, idempotency_key)).fetchone()
        if row is None:
            raise RuntimeError("Workflow run could not be created")
        return ChapterWorkflowRun.model_validate(json.loads(row["state"]))

    def save(self, run: ChapterWorkflowRun) -> None:
        self._connection.execute("UPDATE workflow_runs SET status = ?, state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (run.status.value, json.dumps(run.model_dump(mode="json")), run.id))
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
