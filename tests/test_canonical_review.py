from __future__ import annotations

from book_loop.application.use_cases.detect_conflicts import DetectConflicts
from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.domain.models import (
    Assertion,
    AssertionStatus,
    DocumentChunk,
    Evidence,
    ExtractedAssertion,
    ReviewDecisionType,
    SourceDocument,
)
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def _seed_assertions(repository: SQLiteBookRepository) -> tuple[Assertion, Assertion]:
    source = SourceDocument(
        id="source-1", book_id="book-1", name="notes", source_type="text",
        content="Alice is 32. Alice is 33.", content_hash="a" * 64,
    )
    repository.save_source(source)
    for sequence, (statement, value) in enumerate((("Alice is 32.", "32"), ("Alice is 33.", "33"))):
        chunk = DocumentChunk(
            id=f"chunk-{sequence}", source_document_id=source.id,
            content=statement, sequence=sequence, start_offset=sequence * 14,
            end_offset=sequence * 14 + len(statement),
        )
        repository.save_chunk(chunk)
        assertion = Assertion(
            id=f"assertion-{sequence}", source_document_id=source.id, chunk_id=chunk.id,
            statement=statement, subject="Alice", predicate="age", object=value,
            confidence=0.9, evidence_id=f"evidence-{sequence}",
        )
        repository.save_evidence(Evidence(
            id=assertion.evidence_id, assertion_id=assertion.id, source_document_id=source.id,
            chunk_id=chunk.id, start_offset=chunk.start_offset, end_offset=chunk.end_offset,
            excerpt=statement,
        ))
        repository.save_assertion(assertion)
    assertions = repository.list_assertions(book_id="book-1")
    return assertions[0], assertions[1]


def test_detects_competing_subject_predicate_values(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "knowledge.db"))
    left, right = _seed_assertions(repository)

    conflicts = DetectConflicts(repository).execute(book_id="book-1")

    assert len(conflicts) == 1
    assert {conflicts[0].left_assertion_id, conflicts[0].right_assertion_id} == {left.id, right.id}


def test_acceptance_creates_versioned_canonical_fact_and_audit_decision(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "knowledge.db"))
    left, right = _seed_assertions(repository)
    DetectConflicts(repository).execute(book_id="book-1")

    decision = ReviewAssertion(repository).execute(
        book_id="book-1", assertion_id=left.id, decision=ReviewDecisionType.ACCEPT,
        reviewer_id="user-1", rationale="The first source is authoritative.",
    )

    assert decision.decision is ReviewDecisionType.ACCEPT
    statuses = {a.id: a.status for a in repository.list_assertions(book_id="book-1")}
    assert statuses[left.id] is AssertionStatus.ACCEPTED
    assert statuses[right.id] is AssertionStatus.REJECTED

    row = repository._connection.execute(
        "SELECT assertion_id, decision_id, version, active FROM canonical_facts WHERE book_id = ?",
        ("book-1",),
    ).fetchone()
    assert row["assertion_id"] == left.id
    assert row["decision_id"] == decision.id
    assert row["version"] == 1
    assert row["active"] == 1

    conflict = repository._connection.execute("SELECT status, resolution_assertion_id FROM conflicts").fetchone()
    assert conflict["status"] == "resolved"
    assert conflict["resolution_assertion_id"] == left.id

    audit = repository._connection.execute("SELECT decision FROM review_decisions ORDER BY rowid").fetchall()
    assert [row["decision"] for row in audit] == ["accept", "reject"]
