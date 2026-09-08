from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

import pytest

from book_loop.application.services.plan_limits import limits_for
from book_loop.application.use_cases.create_book import CreateBook
from book_loop.domain.models import BookState, SubscriptionPlan, User
from book_loop.infrastructure.database.postgres import PostgresBookRepository


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL is required for PostgreSQL integration tests")


OWNER_ID = "pg-capacity-owner"


def _repository() -> PostgresBookRepository:
    return PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]


def _create_user(repository: PostgresBookRepository, plan: SubscriptionPlan = SubscriptionPlan.FREE) -> None:
    repository.create_user(
        User(
            id=OWNER_ID,
            email="pg-capacity-owner@example.test",
            password_hash="not-a-real-password-hash",
            name="Capacity Test",
            plan=plan,
        )
    )


def _cleanup(repository: PostgresBookRepository) -> None:
    connection = repository._connection._connection
    connection.execute("DELETE FROM workflow_usage WHERE user_id = %s", (OWNER_ID,))
    connection.execute("DELETE FROM books WHERE data::jsonb ->> 'owner_id' = %s", (OWNER_ID,))
    connection.execute("DELETE FROM users WHERE id = %s", (OWNER_ID,))
    connection.commit()


def _book(book_id: str) -> BookState:
    return BookState(
        id=book_id,
        owner_id=OWNER_ID,
        title=f"Capacity {book_id}",
        theme="Test",
        author_idea="Capacity test",
    )


def test_postgres_book_capacity_tracks_upgrades_and_downgrades() -> None:
    repository = _repository()
    try:
        _cleanup(repository)
        _create_user(repository)
        create_book = CreateBook(repository)

        create_book.execute(owner_id=OWNER_ID, title="Book 1", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=OWNER_ID, title="Book 2", theme="Test", author_idea="Idea")

        repository._connection._connection.execute("UPDATE users SET plan = 'creator' WHERE id = %s", (OWNER_ID,))
        repository._connection.commit()
        create_book.execute(owner_id=OWNER_ID, title="Book 2", theme="Test", author_idea="Idea")
        create_book.execute(owner_id=OWNER_ID, title="Book 3", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=OWNER_ID, title="Book 4", theme="Test", author_idea="Idea")

        repository._connection._connection.execute("UPDATE users SET plan = 'pro' WHERE id = %s", (OWNER_ID,))
        repository._connection.commit()
        for index in range(4, 11):
            create_book.execute(owner_id=OWNER_ID, title=f"Book {index}", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=OWNER_ID, title="Book 11", theme="Test", author_idea="Idea")

        repository._connection._connection.execute("UPDATE users SET plan = 'free' WHERE id = %s", (OWNER_ID,))
        repository._connection.commit()
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=OWNER_ID, title="Book 12", theme="Test", author_idea="Idea")

        assert repository.count_books_for_owner(OWNER_ID) == limits_for(SubscriptionPlan.PRO).max_active_projects
    finally:
        _cleanup(repository)
        repository._connection.close()


def test_postgres_book_capacity_is_atomic_under_concurrency() -> None:
    repository = _repository()
    try:
        _cleanup(repository)
        _create_user(repository, SubscriptionPlan.FREE)
    finally:
        repository._connection.close()

    def create(index: int) -> bool:
        local_repository = _repository()
        try:
            try:
                CreateBook(local_repository).execute(
                    owner_id=OWNER_ID,
                    title=f"Concurrent {index}",
                    theme="Test",
                    author_idea="Concurrency",
                )
                return True
            except PermissionError:
                return False
        finally:
            local_repository._connection.close()

    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(create, range(8)))

        verification = _repository()
        try:
            assert sum(results) == 1
            assert verification.count_books_for_owner(OWNER_ID) == 1
        finally:
            verification._connection.close()
    finally:
        cleanup = _repository()
        try:
            _cleanup(cleanup)
        finally:
            cleanup._connection.close()


def test_postgres_workflow_capacity_enforces_limit_and_idempotency() -> None:
    repository = _repository()
    try:
        _cleanup(repository)
        _create_user(repository, SubscriptionPlan.FREE)
        period = "2026-09-01"
        limit = limits_for(SubscriptionPlan.FREE).monthly_workflow_runs

        keys = [f"workflow-{index}" for index in range(limit + 2)]
        results = [
            repository.consume_workflow_capacity(
                user_id=OWNER_ID,
                period_start=period,
                idempotency_key=key,
                monthly_limit=limit,
            )
            for key in keys
        ]

        assert results == [True] * limit + [False, False]
        assert repository.consume_workflow_capacity(
            user_id=OWNER_ID,
            period_start=period,
            idempotency_key=keys[0],
            monthly_limit=limit,
        ) is True

        count = repository._connection._connection.execute(
            "SELECT COUNT(*) AS count FROM workflow_usage WHERE user_id = %s AND period_start = %s",
            (OWNER_ID, period),
        ).fetchone()["count"]
        assert count == limit
    finally:
        _cleanup(repository)
        repository._connection.close()


def test_postgres_workflow_capacity_is_atomic_under_concurrency() -> None:
    repository = _repository()
    try:
        _cleanup(repository)
        _create_user(repository, SubscriptionPlan.FREE)
    finally:
        repository._connection.close()

    period = "2026-09-01"
    limit = limits_for(SubscriptionPlan.FREE).monthly_workflow_runs

    def consume(index: int) -> bool:
        local_repository = _repository()
        try:
            return local_repository.consume_workflow_capacity(
                user_id=OWNER_ID,
                period_start=period,
                idempotency_key=f"concurrent-workflow-{index}",
                monthly_limit=limit,
            )
        finally:
            local_repository._connection.close()

    try:
        with ThreadPoolExecutor(max_workers=12) as executor:
            results = list(executor.map(consume, range(12)))

        verification = _repository()
        try:
            assert sum(results) == limit
            count = verification._connection._connection.execute(
                "SELECT COUNT(*) AS count FROM workflow_usage WHERE user_id = %s AND period_start = %s",
                (OWNER_ID, period),
            ).fetchone()["count"]
            assert count == limit
        finally:
            verification._connection.close()
    finally:
        cleanup = _repository()
        try:
            _cleanup(cleanup)
        finally:
            cleanup._connection.close()
