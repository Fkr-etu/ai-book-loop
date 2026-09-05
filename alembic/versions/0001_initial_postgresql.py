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
        CREATE TABLE books (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        );

        CREATE TABLE chapter_versions (
            id BIGSERIAL PRIMARY KEY,
            book_id TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            version INTEGER NOT NULL,
            draft TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book_id, chapter_number, version)
        );

        CREATE TABLE reviews (
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

        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE source_documents (
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

        CREATE TABLE document_chunks (
            id TEXT PRIMARY KEY,
            source_document_id TEXT NOT NULL,
            content TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            metadata TEXT NOT NULL
        );

        CREATE TABLE assertions (
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

        CREATE TABLE evidence (
            id TEXT PRIMARY KEY,
            assertion_id TEXT NOT NULL,
            source_document_id TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            excerpt TEXT NOT NULL
        );

        CREATE TABLE conflicts (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            left_assertion_id TEXT NOT NULL,
            right_assertion_id TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution_assertion_id TEXT
        );

        CREATE TABLE review_decisions (
            id TEXT PRIMARY KEY,
            assertion_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reviewer_id TEXT,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE canonical_facts (
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

        CREATE TABLE workflow_runs (
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

        CREATE TABLE observability_events (
            id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            run_id TEXT,
            book_id TEXT,
            chapter_number INTEGER,
            step TEXT,
            attempt INTEGER,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE UNIQUE INDEX uq_active_canonical_fact
            ON canonical_facts(book_id, subject, predicate)
            WHERE active = TRUE;

        CREATE UNIQUE INDEX uq_conflict_assertion_pair
            ON conflicts(left_assertion_id, right_assertion_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE observability_events;
        DROP TABLE workflow_runs;
        DROP TABLE canonical_facts;
        DROP TABLE review_decisions;
        DROP TABLE conflicts;
        DROP TABLE evidence;
        DROP TABLE assertions;
        DROP TABLE document_chunks;
        DROP TABLE source_documents;
        DROP TABLE users;
        DROP TABLE reviews;
        DROP TABLE chapter_versions;
        DROP TABLE books;
        """
    )
