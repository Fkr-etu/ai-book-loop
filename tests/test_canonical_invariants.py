from __future__ import annotations

import sqlite3

import pytest

from book_loop.application.use_cases.get_canonical_fact_history import GetCanonicalFactHistory
from book_loop.application.use_cases.list_canonical_facts import ListCanonicalFacts
from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.domain.models import Assertion, DocumentChunk, Evidence, ReviewDecisionType, SourceDocument
from book_loop.infrastructure.database.repository import SQLiteBookRepository


def _seed(repository: SQLiteBookRepository, *, value: str = "32", assertion_id: str = "assertion-1") -> Assertion:
    source = SourceDocument(
        id=f"source-{assertion_id}", book_id="book-1", name="notes", source_type="text",
        content=f"Alice is {value}.", content_hash=(assertion_id + "a" * 64)[:64],
    )
    repository.save_source(source)
    chunk = DocumentChunk(
        id=f"chunk-{assertion_id}", source_document_id=source.id, content=source.content,
        sequence=0, start_offset=0, end_offset=len(source.content),
    )
    repository.save_chunk(chunk)
    assertion = Assertion(
        id=assertion_id, source_document_id=source.id, chunk_id=chunk.id,
        statement=source.content, subject="Alice", predicate="age", object=value,
        confidence=0.9, evidence_id=f"evidence-{assertion_id}",
    )
    repository.save_evidence(Evidence(
        id=assertion.evidence_id, assertion_id=assertion.id, source_document_id=source.id,
        chunk_id=chunk.id, start_offset=0, end_offset=len(source.content), excerpt=source.content,
    ))
    repository.save_assertion(assertion)
    return assertion


def test_acceptance_is_idempotent_and_history_is_immutable(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "canon.db"))
    first = _seed(repository, value="32", assertion_id="assertion-1")

    decision_1 = ReviewAssertion(repository).execute(
        book_id="book-1", assertion_id=first.id, decision=ReviewDecisionType.ACCEPT, reviewer_id="user-1"
    )
    decision_2 = ReviewAssertion(repository).execute(
        book_id="book-1", assertion_id=first.id, decision=ReviewDecisionType.ACCEPT, reviewer_id="user-1"
    )

    assert decision_2.id == decision_1.id
    history = GetCanonicalFactHistory(repository).execute(book_id="book-1", subject="Alice", predicate="age")
    assert len(history) == 1
    assert history[0].version == 1
    assert history[0].active is True


def test_replacing_canonical_fact_creates_a_new_active_version(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "canon.db"))
    first = _seed(repository, value="32", assertion_id="assertion-1")
    ReviewAssertion(repository).execute(book_id="book-1", assertion_id=first.id, decision=ReviewDecisionType.ACCEPT)

    second = _seed(repository, value="33", assertion_id="assertion-2")
    ReviewAssertion(repository).execute(book_id="book-1", assertion_id=second.id, decision=ReviewDecisionType.ACCEPT)

    facts = GetCanonicalFactHistory(repository).execute(book_id="book-1", subject="Alice", predicate="age")
    assert [fact.version for fact in facts] == [1, 2]
    assert facts[0].active is False
    assert facts[1].active is True
    assert facts[1].previous_fact_id == facts[0].id
    assert [fact.version for fact in ListCanonicalFacts(repository).execute(book_id="book-1")] == [2]


def test_database_rejects_two_active_facts_for_same_subject_and_predicate(tmp_path):
    repository = SQLiteBookRepository(str(tmp_path / "canon.db"))
    first = _seed(repository, value="32", assertion_id="assertion-1")
    ReviewAssertion(repository).execute(book_id="book-1", assertion_id=first.id, decision=ReviewDecisionType.ACCEPT)

    fact = repository.list_active_canonical_facts(book_id="book-1")[0]
    with pytest.raises(sqlite3.IntegrityError):
        repository._connection.execute(
            "INSERT INTO canonical_facts(id, book_id, assertion_id, statement, subject, predicate, object, decision_id, version, active, previous_fact_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("illegal-fact", "book-1", "assertion-2", "Alice is 33.", "Alice", "age", "33", "illegal-decision", fact.version + 1, 1, fact.id),
        )
