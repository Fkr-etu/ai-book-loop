"""Create the initial PostgreSQL persistence schema.

Revision ID: 0001_initial_postgresql
Revises:
"""

from alembic import op

revision = "0001_initial_postgresql"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chapter_versions (
            id BIGSERIAL PRIMARY KEY,
            book_id TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            version INTEGER NOT NULL,
            draft TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book_id, chapter_number, version)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id BIGSERIAL PRIMARY KEY,
            book_id TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            version INTEGER NOT NULL,
            score DOUBLE PRECISION NOT NULL,
            approved BOOLEAN NOT NULL,
            issues TEXT NOT NULL,
            suggestions TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS source_documents (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            metadata TEXT NOT NULL,
            version INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book_id, content_hash)
        );

        CREATE TABLE IF NOT EXISTS document_chunks (
            id TEXT PRIMARY KEY,
            source_document_id TEXT NOT NULL,
            content TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            metadata TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assertions (
            id TEXT PRIMARY KEY,
            source_document_id TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            statement TEXT NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            confidence DOUBLE PRECISION NOT NULL,
            status TEXT NOT NULL,
            evidence_id TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            assertion_id TEXT NOT NULL,
            source_document_id TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            excerpt TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS conflicts (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            left_assertion_id TEXT NOT NULL,
            right_assertion_id TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution_assertion_id TEXT
        );

        CREATE TABLE IF NOT EXISTS review_decisions (
            id TEXT PRIMARY KEY,
            assertion_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reviewer_id TEXT,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS canonical_facts (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            assertion_id TEXT NOT NULL,
            statement TEXT NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            decision_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            active BOOLEAN NOT NULL,
            previous_fact_id TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book_id, subject, predicate, version)
        );

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
        );

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
        );

        CREATE UNIQUE INDEX IF NOT EXISTS uq_active_canonical_fact
            ON canonical_facts(book_id, subject, predicate)
            WHERE active = TRUE;

        CREATE UNIQUE INDEX IF NOT EXISTS uq_conflict_assertion_pair
            ON conflicts(left_assertion_id, right_assertion_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS observability_events;
        DROP TABLE IF EXISTS workflow_runs;
        DROP TABLE IF EXISTS canonical_facts;
        DROP TABLE IF EXISTS review_decisions;
        DROP TABLE IF EXISTS conflicts;
        DROP TABLE IF EXISTS evidence;
        DROP TABLE IF EXISTS assertions;
        DROP TABLE IF EXISTS document_chunks;
        DROP TABLE IF EXISTS source_documents;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS reviews;
        DROP TABLE IF EXISTS chapter_versions;
        DROP TABLE IF EXISTS books;
        """
    )
