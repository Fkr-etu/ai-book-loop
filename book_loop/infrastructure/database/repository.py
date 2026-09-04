from __future__ import annotations

import json
import sqlite3

from book_loop.domain.models import (
    Assertion,
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


class SQLiteBookRepository:
    def __init__(self, database_url: str) -> None:
        self._path = database_url.removeprefix("sqlite:///")
        self._connection = sqlite3.connect(self._path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (id TEXT PRIMARY KEY, data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS chapter_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                version INTEGER NOT NULL,
                draft TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book_id, chapter_number, version)
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id TEXT NOT NULL,
                chapter_number INTEGER NOT NULL,
                version INTEGER NOT NULL,
                score INTEGER NOT NULL,
                approved INTEGER NOT NULL,
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
                confidence REAL NOT NULL,
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
                resolution_assertion_id TEXT,
                UNIQUE(left_assertion_id, right_assertion_id)
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
                active INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(book_id, subject, predicate, version)
            );
            """
        )
        self._connection.commit()

    def save(self, book: BookState) -> None:
        data = json.dumps(book.model_dump(mode="json"))
        self._connection.execute(
            "INSERT INTO books(id, data) VALUES(?, ?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
            (book.id, data),
        )
        self._connection.commit()

    def get(self, book_id: str) -> BookState:
        row = self._connection.execute("SELECT data FROM books WHERE id = ?", (book_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown book: {book_id}")
        return BookState.model_validate(json.loads(row["data"]))

    def next_chapter_version(self, book_id: str, chapter_number: int) -> int:
        row = self._connection.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 AS next_version FROM chapter_versions WHERE book_id = ? AND chapter_number = ?",
            (book_id, chapter_number),
        ).fetchone()
        return int(row["next_version"])

    def save_chapter_version(self, book_id: str, chapter_number: int, version: int, draft: str) -> None:
        self._connection.execute(
            "INSERT INTO chapter_versions(book_id, chapter_number, version, draft) VALUES(?, ?, ?, ?)",
            (book_id, chapter_number, version, draft),
        )
        self._connection.commit()

    def get_chapter_version(self, book_id: str, chapter_number: int, version: int) -> str:
        row = self._connection.execute(
            "SELECT draft FROM chapter_versions WHERE book_id = ? AND chapter_number = ? AND version = ?",
            (book_id, chapter_number, version),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown chapter version: {chapter_number} v{version}")
        return str(row["draft"])

    def save_review(self, book_id: str, chapter_number: int, version: int, review: SceneReview) -> None:
        self._connection.execute(
            "INSERT INTO reviews(book_id, chapter_number, version, score, approved, issues, suggestions) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (book_id, chapter_number, version, review.score, int(review.approved), json.dumps(review.issues), json.dumps(review.suggestions)),
        )
        self._connection.commit()

    def find_source_by_hash(self, *, book_id: str, content_hash: str) -> SourceDocument | None:
        row = self._connection.execute(
            "SELECT * FROM source_documents WHERE book_id = ? AND content_hash = ?",
            (book_id, content_hash),
        ).fetchone()
        return self._source_from_row(row) if row is not None else None

    def save_source(self, source: SourceDocument) -> None:
        self._connection.execute(
            "INSERT INTO source_documents(id, book_id, name, source_type, content, content_hash, metadata, version) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (source.id, source.book_id, source.name, source.source_type, source.content, source.content_hash, json.dumps(source.metadata), source.version),
        )
        self._connection.commit()

    def save_chunk(self, chunk: DocumentChunk) -> None:
        self._connection.execute(
            "INSERT INTO document_chunks(id, source_document_id, content, sequence, start_offset, end_offset, metadata) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (chunk.id, chunk.source_document_id, chunk.content, chunk.sequence, chunk.start_offset, chunk.end_offset, json.dumps(chunk.metadata)),
        )
        self._connection.commit()

    def save_assertion(self, assertion: Assertion) -> None:
        self._connection.execute(
            "INSERT INTO assertions(id, source_document_id, chunk_id, statement, subject, predicate, object, confidence, status, evidence_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (assertion.id, assertion.source_document_id, assertion.chunk_id, assertion.statement, assertion.subject, assertion.predicate, assertion.object, assertion.confidence, assertion.status.value, assertion.evidence_id),
        )
        self._connection.commit()

    def save_evidence(self, evidence: Evidence) -> None:
        self._connection.execute(
            "INSERT INTO evidence(id, assertion_id, source_document_id, chunk_id, start_offset, end_offset, excerpt) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (evidence.id, evidence.assertion_id, evidence.source_document_id, evidence.chunk_id, evidence.start_offset, evidence.end_offset, evidence.excerpt),
        )
        self._connection.commit()

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        rows = self._connection.execute(
            "SELECT a.* FROM assertions a JOIN source_documents s ON s.id = a.source_document_id WHERE s.book_id = ? ORDER BY a.rowid",
            (book_id,),
        ).fetchall()
        return [self._assertion_from_row(row) for row in rows]

    def list_evidence(self, *, book_id: str) -> list[Evidence]:
        rows = self._connection.execute(
            "SELECT e.* FROM evidence e JOIN source_documents s ON s.id = e.source_document_id WHERE s.book_id = ? ORDER BY e.rowid",
            (book_id,),
        ).fetchall()
        return [
            Evidence(
                id=row["id"],
                assertion_id=row["assertion_id"],
                source_document_id=row["source_document_id"],
                chunk_id=row["chunk_id"],
                start_offset=row["start_offset"],
                end_offset=row["end_offset"],
                excerpt=row["excerpt"],
            )
            for row in rows
        ]

    def save_conflict(self, conflict: Conflict) -> None:
        left, right = sorted((conflict.left_assertion_id, conflict.right_assertion_id))
        self._connection.execute(
            """
            INSERT INTO conflicts(id, book_id, left_assertion_id, right_assertion_id, status, resolution_assertion_id)
            VALUES(?, ?, ?, ?, ?, ?)
            ON CONFLICT(left_assertion_id, right_assertion_id) DO UPDATE SET
              status=excluded.status, resolution_assertion_id=excluded.resolution_assertion_id
            """,
            (conflict.id, conflict.book_id, left, right, conflict.status.value, conflict.resolution_assertion_id),
        )
        self._connection.commit()

    def list_conflicts(self, *, book_id: str) -> list[Conflict]:
        rows = self._connection.execute(
            "SELECT * FROM conflicts WHERE book_id = ? ORDER BY rowid",
            (book_id,),
        ).fetchall()
        return [
            Conflict(
                id=row["id"],
                book_id=row["book_id"],
                left_assertion_id=row["left_assertion_id"],
                right_assertion_id=row["right_assertion_id"],
                status=row["status"],
                resolution_assertion_id=row["resolution_assertion_id"],
            )
            for row in rows
        ]
