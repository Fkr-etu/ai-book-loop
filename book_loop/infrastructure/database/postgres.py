from __future__ import annotations

import json
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row

from book_loop.domain.models import AssertionStatus, BookState, CanonicalFact, Conflict, DocumentChunk, Evidence, ReviewDecision, SceneReview, SourceDocument, SubscriptionPlan, User
from book_loop.domain.workflow import ChapterWorkflowRun
from book_loop.infrastructure.database.repository import BookRepositoryMixin


def _normalize_postgres_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    return database_url


class _PostgresConnectionAdapter:
    def __init__(self, database_url: str) -> None:
        self._connection = psycopg.connect(_normalize_postgres_url(database_url), row_factory=dict_row, autocommit=True)
        self._transaction_depth = 0
    def execute(self, sql: str, params: tuple[Any, ...] = ()):
        sql = sql.replace("?", "%s")
        if "INSERT INTO workflow_runs" in sql and "ON CONFLICT" not in sql:
            sql += " ON CONFLICT DO NOTHING"
        return self._connection.execute(sql, params)
    def commit(self) -> None:
        if self._transaction_depth == 0: self._connection.commit()
    def rollback(self) -> None:
        if self._transaction_depth == 0: self._connection.rollback()
    @contextmanager
    def transaction(self) -> Iterator[None]:
        outermost = self._transaction_depth == 0
        if outermost: self._connection.execute("BEGIN")
        self._transaction_depth += 1
        try: yield
        except Exception:
            self._transaction_depth -= 1
            if outermost: self._connection.rollback()
            raise
        else:
            self._transaction_depth -= 1
            if outermost: self._connection.commit()
    def close(self) -> None: self._connection.close()


class PostgresBookRepository(BookRepositoryMixin):
    def __init__(self, database_url: str) -> None:
        if not database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
            raise ValueError("PostgresBookRepository requires a PostgreSQL DATABASE_URL")
        self._connection = _PostgresConnectionAdapter(database_url)
        self._connection._connection.execute("""
            CREATE TABLE IF NOT EXISTS books (id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chapter_versions (id BIGSERIAL PRIMARY KEY, book_id TEXT NOT NULL, chapter_number INTEGER NOT NULL, version INTEGER NOT NULL, draft TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, chapter_number, version));
            CREATE TABLE IF NOT EXISTS reviews (id BIGSERIAL PRIMARY KEY, book_id TEXT NOT NULL, chapter_number INTEGER NOT NULL, version INTEGER NOT NULL, score DOUBLE PRECISION NOT NULL, approved BOOLEAN NOT NULL, issues TEXT NOT NULL, suggestions TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, name TEXT NOT NULL DEFAULT '', plan TEXT NOT NULL DEFAULT 'free', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS source_documents (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, name TEXT NOT NULL, source_type TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL, metadata TEXT NOT NULL, version INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, content_hash));
            CREATE TABLE IF NOT EXISTS document_chunks (id TEXT PRIMARY KEY, source_document_id TEXT NOT NULL, content TEXT NOT NULL, sequence INTEGER NOT NULL, start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL, metadata TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS assertions (id TEXT PRIMARY KEY, source_document_id TEXT NOT NULL, chunk_id TEXT NOT NULL, statement TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL, confidence DOUBLE PRECISION NOT NULL, status TEXT NOT NULL, evidence_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, assertion_id TEXT NOT NULL, source_document_id TEXT NOT NULL, chunk_id TEXT NOT NULL, start_offset INTEGER NOT NULL, end_offset INTEGER NOT NULL, excerpt TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS conflicts (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, left_assertion_id TEXT NOT NULL, right_assertion_id TEXT NOT NULL, status TEXT NOT NULL, resolution_assertion_id TEXT);
            CREATE TABLE IF NOT EXISTS review_decisions (id TEXT PRIMARY KEY, assertion_id TEXT NOT NULL, decision TEXT NOT NULL, reviewer_id TEXT, rationale TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS canonical_facts (id TEXT PRIMARY KEY, book_id TEXT NOT NULL, assertion_id TEXT NOT NULL, statement TEXT NOT NULL, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL, decision_id TEXT NOT NULL, version INTEGER NOT NULL, active BOOLEAN NOT NULL, previous_fact_id TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, subject, predicate, version));
            CREATE TABLE IF NOT EXISTS workflow_usage (user_id TEXT NOT NULL, period_start DATE NOT NULL, idempotency_key TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id, period_start, idempotency_key));
            CREATE TABLE IF NOT EXISTS book_usage_identities (book_id TEXT PRIMARY KEY, identity TEXT NOT NULL UNIQUE, user_id TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS workflow_usage_scoped (quota_subject TEXT NOT NULL, period_start DATE NOT NULL, idempotency_key TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(quota_subject, period_start, idempotency_key));
        """)
        self._connection._connection.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS plan TEXT NOT NULL DEFAULT 'free'")
        self._connection._connection.execute("ALTER TABLE canonical_facts ADD COLUMN IF NOT EXISTS previous_fact_id TEXT")
        self._connection._connection.execute("ALTER TABLE book_usage_identities ADD COLUMN IF NOT EXISTS user_id TEXT")
        self._connection._connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_active_canonical_fact ON canonical_facts(book_id, subject, predicate) WHERE active = TRUE")
        self._connection._connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_conflict_assertion_pair ON conflicts(left_assertion_id, right_assertion_id)")
        self._connection.commit()
    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self._connection.transaction(): yield
    def lock_assertion(self, assertion_id: str) -> None:
        self._connection.execute("SELECT id FROM assertions WHERE id = ? FOR UPDATE", (assertion_id,)).fetchone()
    def count_books_for_owner(self, owner_id: str) -> int:
        row = self._connection.execute("SELECT COUNT(*) AS count FROM books WHERE data::jsonb ->> 'owner_id' = ?", (owner_id,)).fetchone(); return int(row["count"])
    def save_new_book_with_capacity(self, book: BookState, max_active_projects: int) -> None:
        with self.transaction():
            self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(?))", (book.owner_id,))
            row = self._connection.execute("SELECT COUNT(*) AS count FROM books WHERE data::jsonb ->> 'owner_id' = ?", (book.owner_id,)).fetchone()
            if int(row["count"]) >= max_active_projects: raise PermissionError("Project capacity reached for the current plan")
            self._connection.execute("INSERT INTO books(id, data) VALUES(?, ?)", (book.id, json.dumps(book.model_dump(mode="json"))))
    def get_book_identity(self, *, book_id: str) -> str | None:
        row = self._connection.execute("SELECT identity FROM book_usage_identities WHERE book_id = ?", (book_id,)).fetchone()
        return str(row["identity"]) if row is not None else None
    def register_book_identity(self, *, book_id: str, identity: str) -> None:
        raise RuntimeError("Book identity must be registered as part of free-tier consumption")
    def consume_free_workflow_capacity(self, *, user_id: str, book_id: str, book_identity: str, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        with self.transaction():
            self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(?))", (f"free-book:{book_identity}",))
            existing = self._connection.execute("SELECT 1 FROM workflow_usage WHERE user_id = ? AND period_start = ? AND idempotency_key = ?", (user_id, period_start, idempotency_key)).fetchone()
            if existing is not None: return True
            usage = self._connection.execute("SELECT COUNT(*) AS count FROM workflow_usage WHERE user_id = ? AND period_start = ?", (user_id, period_start)).fetchone()
            if int(usage["count"]) >= monthly_limit: return False
            identity_row = self._connection.execute("SELECT user_id FROM book_usage_identities WHERE identity = ?", (book_identity,)).fetchone()
            if identity_row is not None and identity_row["user_id"] != user_id: return False
            if identity_row is None:
                self._connection.execute("INSERT INTO book_usage_identities(book_id, identity, user_id) VALUES(?, ?, ?)", (book_id, book_identity, user_id))
            self._connection.execute("INSERT INTO workflow_usage(user_id, period_start, idempotency_key) VALUES(?, ?, ?)", (user_id, period_start, idempotency_key))
            return True
    def consume_workflow_capacity(self, *, quota_subject: str | None = None, user_id: str | None = None, period_start: str, idempotency_key: str, monthly_limit: int) -> bool:
        if user_id is not None and quota_subject is None:
            with self.transaction():
                self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(?))", (user_id,))
                inserted = self._connection.execute("""INSERT INTO workflow_usage(user_id, period_start, idempotency_key)
                    SELECT ?, ?, ? WHERE (SELECT COUNT(*) FROM workflow_usage WHERE user_id = ? AND period_start = ?) < ?
                    ON CONFLICT(user_id, period_start, idempotency_key) DO NOTHING RETURNING idempotency_key""", (user_id, period_start, idempotency_key, user_id, period_start, monthly_limit)).fetchone()
                if inserted is not None: return True
                existing = self._connection.execute("SELECT 1 FROM workflow_usage WHERE user_id = ? AND period_start = ? AND idempotency_key = ?", (user_id, period_start, idempotency_key)).fetchone()
                return existing is not None
        subject = quota_subject
        if subject is None:
            raise ValueError("Either quota_subject or user_id is required")
        with self.transaction():
            self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(?))", (subject,))
            inserted = self._connection.execute("""INSERT INTO workflow_usage_scoped(quota_subject, period_start, idempotency_key)
                SELECT ?, ?, ? WHERE (SELECT COUNT(*) FROM workflow_usage_scoped WHERE quota_subject = ? AND period_start = ?) < ?
                ON CONFLICT(quota_subject, period_start, idempotency_key) DO NOTHING RETURNING idempotency_key""", (subject, period_start, idempotency_key, subject, period_start, monthly_limit)).fetchone()
            if inserted is not None: return True
            existing = self._connection.execute("SELECT 1 FROM workflow_usage_scoped WHERE quota_subject = ? AND period_start = ? AND idempotency_key = ?", (subject, period_start, idempotency_key)).fetchone()
            return existing is not None


class PostgresWorkflowRunStore:
    def __init__(self, database_url: str):
        self._connection = _PostgresConnectionAdapter(database_url)
        self._connection._connection.execute("""CREATE TABLE IF NOT EXISTS workflow_runs (
            id TEXT PRIMARY KEY, book_id TEXT NOT NULL, chapter_number INTEGER NOT NULL, idempotency_key TEXT NOT NULL,
            status TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(book_id, chapter_number, idempotency_key))""")
        self._connection.commit()
    def get_or_create(self, *, book_id: str, chapter_number: int, idempotency_key: str) -> ChapterWorkflowRun:
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? AND idempotency_key = ?", (book_id, chapter_number, idempotency_key)).fetchone()
        if row is not None: return ChapterWorkflowRun.model_validate(json.loads(row["state"]))
        run = ChapterWorkflowRun(id=str(uuid.uuid4()), book_id=book_id, chapter_number=chapter_number, idempotency_key=idempotency_key)
        self._connection.execute("INSERT INTO workflow_runs(id, book_id, chapter_number, idempotency_key, status, state) VALUES(?, ?, ?, ?, ?, ?)", (run.id, run.book_id, run.chapter_number, run.idempotency_key, run.status.value, json.dumps(run.model_dump(mode="json"))))
        self._connection.commit()
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? AND idempotency_key = ?", (book_id, chapter_number, idempotency_key)).fetchone()
        if row is None: raise RuntimeError("Workflow run could not be created")
        return ChapterWorkflowRun.model_validate(json.loads(row["state"]))
    def get(self, run_id: str) -> ChapterWorkflowRun:
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE id = ?", (run_id,)).fetchone()
        if row is None: raise KeyError(run_id)
        return ChapterWorkflowRun.model_validate(json.loads(row["state"]))
    def latest(self, *, book_id: str, chapter_number: int) -> ChapterWorkflowRun | None:
        row = self._connection.execute("SELECT state FROM workflow_runs WHERE book_id = ? AND chapter_number = ? ORDER BY updated_at DESC, created_at DESC LIMIT 1", (book_id, chapter_number)).fetchone()
        return ChapterWorkflowRun.model_validate(json.loads(row["state"])) if row is not None else None
    def save(self, run: ChapterWorkflowRun) -> None:
        self._connection.execute("UPDATE workflow_runs SET status = ?, state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (run.status.value, json.dumps(run.model_dump(mode="json")), run.id)); self._connection.commit()
    def close(self) -> None: self._connection.close()
