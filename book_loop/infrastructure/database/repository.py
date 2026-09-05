from __future__ import annotations

import json
from typing import Any

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


class BookRepositoryMixin:
    """Persistence operations shared by the PostgreSQL repository adapter."""

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
            (book_id, chapter_number, version, review.score, review.approved, json.dumps(review.issues), json.dumps(review.suggestions)),
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

    def list_evidence(self, *, book_id: str) -> list[Evidence]:
        rows = self._connection.execute(
            "SELECT e.* FROM evidence e JOIN source_documents s ON s.id = e.source_document_id WHERE s.book_id = ? ORDER BY e.id",
            (book_id,),
        ).fetchall()
        return [Evidence(id=row["id"], assertion_id=row["assertion_id"], source_document_id=row["source_document_id"], chunk_id=row["chunk_id"], start_offset=row["start_offset"], end_offset=row["end_offset"], excerpt=row["excerpt"]) for row in rows]

    def list_assertions(self, *, book_id: str) -> list[Assertion]:
        rows = self._connection.execute(
            "SELECT a.* FROM assertions a JOIN source_documents s ON s.id = a.source_document_id WHERE s.book_id = ? ORDER BY a.id",
            (book_id,),
        ).fetchall()
        return [self._assertion_from_row(row) for row in rows]

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
        rows = self._connection.execute("SELECT * FROM conflicts WHERE book_id = ? ORDER BY id", (book_id,)).fetchall()
        return [Conflict(id=row["id"], book_id=row["book_id"], left_assertion_id=row["left_assertion_id"], right_assertion_id=row["right_assertion_id"], status=row["status"], resolution_assertion_id=row["resolution_assertion_id"]) for row in rows]

    def resolve_conflict(self, left_assertion_id: str, right_assertion_id: str, resolution_assertion_id: str) -> None:
        left, right = sorted((left_assertion_id, right_assertion_id))
        self._connection.execute(
            "UPDATE conflicts SET status = 'resolved', resolution_assertion_id = ? WHERE left_assertion_id = ? AND right_assertion_id = ?",
            (resolution_assertion_id, left, right),
        )
        self._connection.commit()

    def save_review_decision(self, decision: ReviewDecision) -> None:
        self._connection.execute(
            "INSERT INTO review_decisions(id, assertion_id, decision, reviewer_id, rationale) VALUES(?, ?, ?, ?, ?)",
            (decision.id, decision.assertion_id, decision.decision.value, decision.reviewer_id, decision.rationale),
        )
        self._connection.commit()

    def list_review_decisions(self, *, assertion_id: str) -> list[ReviewDecision]:
        rows = self._connection.execute("SELECT * FROM review_decisions WHERE assertion_id = ? ORDER BY id", (assertion_id,)).fetchall()
        return [ReviewDecision(id=row["id"], assertion_id=row["assertion_id"], decision=row["decision"], reviewer_id=row["reviewer_id"], rationale=row["rationale"], created_at=row["created_at"]) for row in rows]

    def next_canonical_version(self, *, book_id: str, subject: str, predicate: str) -> int:
        row = self._connection.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 AS next_version FROM canonical_facts WHERE book_id = ? AND subject = ? AND predicate = ?",
            (book_id, subject, predicate),
        ).fetchone()
        return int(row["next_version"])

    def deactivate_canonical_facts(self, *, book_id: str, subject: str, predicate: str) -> None:
        self._connection.execute(
            "UPDATE canonical_facts SET active = FALSE WHERE book_id = ? AND subject = ? AND predicate = ? AND active = TRUE",
            (book_id, subject, predicate),
        )
        self._connection.commit()

    def save_canonical_fact(self, fact: CanonicalFact) -> None:
        self._connection.execute(
            "INSERT INTO canonical_facts(id, book_id, assertion_id, statement, subject, predicate, object, decision_id, version, active, previous_fact_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (fact.id, fact.book_id, fact.assertion_id, fact.statement, fact.subject, fact.predicate, fact.object, fact.decision_id, fact.version, fact.active, fact.previous_fact_id),
        )
        self._connection.commit()

    def list_active_canonical_facts(self, *, book_id: str) -> list[CanonicalFact]:
        rows = self._connection.execute("SELECT * FROM canonical_facts WHERE book_id = ? AND active = TRUE ORDER BY subject, predicate, version", (book_id,)).fetchall()
        return [self._canonical_fact_from_row(row) for row in rows]

    def list_canonical_fact_history(self, *, book_id: str, subject: str, predicate: str) -> list[CanonicalFact]:
        rows = self._connection.execute("SELECT * FROM canonical_facts WHERE book_id = ? AND subject = ? AND predicate = ? ORDER BY version", (book_id, subject, predicate)).fetchall()
        return [self._canonical_fact_from_row(row) for row in rows]

    def set_assertion_status(self, assertion_id: str, status: AssertionStatus) -> None:
        cursor = self._connection.execute("UPDATE assertions SET status = ? WHERE id = ?", (status.value, assertion_id))
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown assertion: {assertion_id}")
        self._connection.commit()

    @staticmethod
    def _source_from_row(row: Any) -> SourceDocument:
        return SourceDocument(id=row["id"], book_id=row["book_id"], name=row["name"], source_type=row["source_type"], content=row["content"], content_hash=row["content_hash"], metadata=json.loads(row["metadata"]), version=row["version"])

    @staticmethod
    def _assertion_from_row(row: Any) -> Assertion:
        return Assertion(id=row["id"], source_document_id=row["source_document_id"], chunk_id=row["chunk_id"], statement=row["statement"], subject=row["subject"], predicate=row["predicate"], object=row["object"], confidence=row["confidence"], status=row["status"], evidence_id=row["evidence_id"])

    @staticmethod
    def _canonical_fact_from_row(row: Any) -> CanonicalFact:
        return CanonicalFact(id=row["id"], book_id=row["book_id"], assertion_id=row["assertion_id"], statement=row["statement"], subject=row["subject"], predicate=row["predicate"], object=row["object"], decision_id=row["decision_id"], version=row["version"], active=bool(row["active"]), previous_fact_id=row["previous_fact_id"])

    def create_user(self, user: User) -> User:
        self._connection.execute("INSERT INTO users(id, email, password_hash, name) VALUES(?, ?, ?, ?)", (user.id, user.email.lower().strip(), user.password_hash, user.name))
        self._connection.commit()
        return self.get_user_by_email(user.email)  # type: ignore

    def get_user_by_email(self, email: str) -> User | None:
        row = self._connection.execute("SELECT id, email, password_hash, name, created_at FROM users WHERE lower(email) = ?", (email.lower().strip(),)).fetchone()
        if row is None:
            return None
        return User(id=row["id"], email=row["email"], password_hash=row["password_hash"], name=row["name"], created_at=row["created_at"])

    def get_user_by_id(self, user_id: str) -> User | None:
        row = self._connection.execute("SELECT id, email, password_hash, name, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        return User(id=row["id"], email=row["email"], password_hash=row["password_hash"], name=row["name"], created_at=row["created_at"])
