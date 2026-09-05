from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

import pytest

from book_loop.application.use_cases.review_assertion import ReviewAssertion
from book_loop.domain.models import CanonicalFact, ReviewDecisionType
from book_loop.infrastructure.database.postgres import PostgresBookRepository


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL is required for PostgreSQL integration tests")


def test_postgres_canonical_fact_history_and_active_invariant() -> None:
    repository = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
    try:
        connection = repository._connection._connection
        connection.execute("DELETE FROM canonical_facts WHERE book_id = %s", ("pg-test-book",))
        connection.commit()

        first = CanonicalFact(
            id="pg-fact-1",
            book_id="pg-test-book",
            assertion_id="pg-assertion-1",
            statement="Alice lives in Marseille.",
            subject="Alice",
            predicate="lives_in",
            object="Marseille",
            decision_id="pg-decision-1",
            version=1,
            active=False,
        )
        second = CanonicalFact(
            id="pg-fact-2",
            book_id="pg-test-book",
            assertion_id="pg-assertion-2",
            statement="Alice lives in Paris.",
            subject="Alice",
            predicate="lives_in",
            object="Paris",
            decision_id="pg-decision-2",
            version=2,
            active=True,
            previous_fact_id=first.id,
        )

        repository.save_canonical_fact(first)
        repository.save_canonical_fact(second)

        history = repository.list_canonical_fact_history(
            book_id="pg-test-book", subject="Alice", predicate="lives_in"
        )
        assert [fact.version for fact in history] == [1, 2]
        assert history[1].previous_fact_id == first.id
        assert [fact.id for fact in repository.list_active_canonical_facts(book_id="pg-test-book")] == [second.id]

        duplicate_active = second.model_copy(
            update={"id": "pg-fact-3", "version": 3, "previous_fact_id": second.id}
        )
        with pytest.raises(Exception):
            repository.save_canonical_fact(duplicate_active)
        connection.rollback()
    finally:
        repository._connection._connection.execute(
            "DELETE FROM canonical_facts WHERE book_id = %s", ("pg-test-book",)
        )
        repository._connection.commit()
        repository._connection.close()


def test_postgres_transaction_rolls_back_all_repository_operations() -> None:
    repository = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
    book_id = "pg-transaction-book"
    try:
        connection = repository._connection._connection
        connection.execute("DELETE FROM canonical_facts WHERE book_id = %s", (book_id,))
        connection.commit()

        fact = CanonicalFact(
            id="pg-rollback-fact",
            book_id=book_id,
            assertion_id="pg-rollback-assertion",
            statement="Rollback me.",
            subject="Rollback",
            predicate="state",
            object="temporary",
            decision_id="pg-rollback-decision",
            version=1,
            active=True,
        )

        with pytest.raises(RuntimeError, match="rollback"):
            with repository.transaction():
                repository.save_canonical_fact(fact)
                raise RuntimeError("rollback")

        assert repository.list_canonical_fact_history(
            book_id=book_id, subject="Rollback", predicate="state"
        ) == []
    finally:
        repository._connection._connection.execute(
            "DELETE FROM canonical_facts WHERE book_id = %s", (book_id,)
        )
        repository._connection.commit()
        repository._connection.close()


def test_postgres_concurrent_accepts_of_same_assertion_are_idempotent() -> None:
    book_id = "pg-concurrent-book"
    source_id = "pg-concurrent-source"
    assertion_id = "pg-concurrent-assertion"
    repository = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
    try:
        connection = repository._connection._connection
        connection.execute("DELETE FROM review_decisions WHERE assertion_id = %s", (assertion_id,))
        connection.execute("DELETE FROM canonical_facts WHERE book_id = %s", (book_id,))
        connection.execute("DELETE FROM assertions WHERE id = %s", (assertion_id,))
        connection.execute("DELETE FROM source_documents WHERE id = %s", (source_id,))
        connection.execute(
            """
            INSERT INTO source_documents(
                id, book_id, name, source_type, content, content_hash, metadata, version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (source_id, book_id, "concurrent.txt", "text", "Alice lives in Paris.", "pg-concurrent-hash", "{}", 1),
        )
        connection.execute(
            """
            INSERT INTO assertions(
                id, source_document_id, chunk_id, statement, subject, predicate,
                object, confidence, status, evidence_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                assertion_id,
                source_id,
                "pg-concurrent-chunk",
                "Alice lives in Paris.",
                "Alice",
                "lives_in",
                "Paris",
                0.99,
                "proposed",
                "pg-concurrent-evidence",
            ),
        )
        connection.commit()
    finally:
        repository._connection.close()

    def accept() -> str:
        local_repository = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
        try:
            decision = ReviewAssertion(local_repository).execute(
                book_id=book_id,
                assertion_id=assertion_id,
                decision=ReviewDecisionType.ACCEPT,
                reviewer_id="pg-reviewer",
            )
            return decision.id
        finally:
            local_repository._connection.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            decision_ids = list(executor.map(lambda _: accept(), range(2)))

        assert decision_ids[0] == decision_ids[1]

        verification = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
        try:
            decisions = verification.list_review_decisions(assertion_id=assertion_id)
            facts = verification.list_active_canonical_facts(book_id=book_id)
            assert len(decisions) == 1
            assert len(facts) == 1
            assert facts[0].assertion_id == assertion_id
        finally:
            verification._connection.close()
    finally:
        cleanup = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
        try:
            cleanup_connection = cleanup._connection._connection
            cleanup_connection.execute("DELETE FROM review_decisions WHERE assertion_id = %s", (assertion_id,))
            cleanup_connection.execute("DELETE FROM canonical_facts WHERE book_id = %s", (book_id,))
            cleanup_connection.execute("DELETE FROM assertions WHERE id = %s", (assertion_id,))
            cleanup_connection.execute("DELETE FROM source_documents WHERE id = %s", (source_id,))
            cleanup_connection.commit()
        finally:
            cleanup._connection.close()
