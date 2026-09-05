from __future__ import annotations

import os

import pytest

from book_loop.domain.models import CanonicalFact
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
