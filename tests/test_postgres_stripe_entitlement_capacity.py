from __future__ import annotations

import os

import pytest

from book_loop.application.use_cases.create_book import CreateBook
from book_loop.domain.models import BookState, SubscriptionPlan, User
from book_loop.infrastructure.database.postgres import PostgresBookRepository
from book_loop.infrastructure.stripe_billing import StripeBillingRepository


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="DATABASE_URL is required for PostgreSQL integration tests"
)


USER_ID = "pg-stripe-entitlement-user"
CUSTOMER_ID = "cus_pg_stripe_entitlement"


def _book(book_id: str) -> BookState:
    return BookState(
        id=book_id,
        owner_id=USER_ID,
        title=f"Stripe entitlement {book_id}",
        theme="Test",
        author_idea="Stripe entitlement test",
    )


def _cleanup(repository: PostgresBookRepository, billing: StripeBillingRepository) -> None:
    connection = repository._connection._connection
    connection.execute("DELETE FROM workflow_usage WHERE user_id = %s", (USER_ID,))
    connection.execute("DELETE FROM books WHERE data::jsonb ->> 'owner_id' = %s", (USER_ID,))
    billing._connection.execute("DELETE FROM stripe_webhook_events WHERE event_id LIKE 'evt_pg_stripe_entitlement_%'")
    connection.execute("DELETE FROM users WHERE id = %s", (USER_ID,))
    connection.commit()


def test_postgres_stripe_events_drive_project_entitlements() -> None:
    repository = PostgresBookRepository(DATABASE_URL)  # type: ignore[arg-type]
    billing = StripeBillingRepository(DATABASE_URL)  # type: ignore[arg-type]
    try:
        _cleanup(repository, billing)
        repository.create_user(
            User(
                id=USER_ID,
                email="pg-stripe-entitlement@example.test",
                password_hash="not-a-real-password-hash",
                name="Stripe Entitlement Test",
                plan=SubscriptionPlan.FREE,
            )
        )
        billing.set_customer_id(USER_ID, CUSTOMER_ID)
        create_book = CreateBook(repository)

        create_book.execute(owner_id=USER_ID, title="Book 1", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=USER_ID, title="Book 2", theme="Test", author_idea="Idea")

        assert billing.apply_subscription_event(
            event_id="evt_pg_stripe_entitlement_creator",
            event_type="customer.subscription.updated",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_creator",
            status="active",
            plan=SubscriptionPlan.CREATOR,
            current_period_end=None,
            cancel_at_period_end=False,
        )
        assert billing.get_billing_state(USER_ID)["plan"] == SubscriptionPlan.CREATOR.value
        create_book.execute(owner_id=USER_ID, title="Book 2", theme="Test", author_idea="Idea")
        create_book.execute(owner_id=USER_ID, title="Book 3", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=USER_ID, title="Book 4", theme="Test", author_idea="Idea")

        assert billing.apply_subscription_event(
            event_id="evt_pg_stripe_entitlement_pro",
            event_type="customer.subscription.updated",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_pro",
            status="active",
            plan=SubscriptionPlan.PRO,
            current_period_end=None,
            cancel_at_period_end=True,
        )
        state = billing.get_billing_state(USER_ID)
        assert state["plan"] == SubscriptionPlan.PRO.value
        assert state["subscription_cancel_at_period_end"] is True
        for index in range(4, 11):
            create_book.execute(owner_id=USER_ID, title=f"Book {index}", theme="Test", author_idea="Idea")
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=USER_ID, title="Book 11", theme="Test", author_idea="Idea")

        assert billing.apply_subscription_event(
            event_id="evt_pg_stripe_entitlement_canceled",
            event_type="customer.subscription.deleted",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_pro",
            status="canceled",
            plan=SubscriptionPlan.FREE,
            current_period_end=None,
            cancel_at_period_end=False,
        )
        assert billing.get_billing_state(USER_ID)["plan"] == SubscriptionPlan.FREE.value
        with pytest.raises(PermissionError, match="Project capacity"):
            create_book.execute(owner_id=USER_ID, title="Book 11", theme="Test", author_idea="Idea")
    finally:
        _cleanup(repository, billing)
        billing._connection.close()
        repository._connection.close()
