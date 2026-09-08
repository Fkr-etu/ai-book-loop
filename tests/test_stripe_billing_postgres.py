from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from book_loop.domain.models import SubscriptionPlan
from book_loop.infrastructure.stripe_billing import StripeBillingRepository


DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="DATABASE_URL is required for PostgreSQL integration tests"
)


USER_ID = "pg-stripe-billing-user"
CUSTOMER_ID = "cus_pg_stripe_billing"


def _repository() -> StripeBillingRepository:
    return StripeBillingRepository(DATABASE_URL)  # type: ignore[arg-type]


def _prepare_user(repository: StripeBillingRepository) -> None:
    connection = repository._connection
    connection.execute("DELETE FROM stripe_webhook_events WHERE event_id LIKE 'evt_pg_billing_%'")
    connection.execute("DELETE FROM users WHERE id = %s", (USER_ID,))
    connection.execute(
        """
        INSERT INTO users(id, email, password_hash, name, plan, stripe_customer_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (USER_ID, "pg-stripe-billing@example.com", "test-hash", "Billing Test", "free", CUSTOMER_ID),
    )


def _cleanup(repository: StripeBillingRepository) -> None:
    repository._connection.execute("DELETE FROM stripe_webhook_events WHERE event_id LIKE 'evt_pg_billing_%'")
    repository._connection.execute("DELETE FROM users WHERE id = %s", (USER_ID,))
    repository._connection.commit()
    repository.close()


def _state(repository: StripeBillingRepository) -> dict:
    return repository.get_billing_state(USER_ID)


def test_postgres_stripe_entitlement_lifecycle_and_idempotency() -> None:
    repository = _repository()
    try:
        _prepare_user(repository)

        period_end = datetime(2027, 1, 15, tzinfo=timezone.utc)
        assert repository.apply_subscription_event(
            event_id="evt_pg_billing_creator",
            event_type="customer.subscription.created",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_creator",
            status="active",
            plan=SubscriptionPlan.CREATOR,
            current_period_end=period_end,
            cancel_at_period_end=False,
        )
        state = _state(repository)
        assert state["plan"] == "creator"
        assert state["subscription_status"] == "active"
        assert state["stripe_subscription_id"] == "sub_pg_creator"
        assert state["subscription_current_period_end"] == period_end

        assert not repository.apply_subscription_event(
            event_id="evt_pg_billing_creator",
            event_type="customer.subscription.created",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_creator",
            status="active",
            plan=SubscriptionPlan.CREATOR,
            current_period_end=period_end,
            cancel_at_period_end=False,
        )
        assert _state(repository)["plan"] == "creator"

        assert repository.apply_subscription_event(
            event_id="evt_pg_billing_upgrade",
            event_type="customer.subscription.updated",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_pro",
            status="active",
            plan=SubscriptionPlan.PRO,
            current_period_end=period_end,
            cancel_at_period_end=True,
        )
        state = _state(repository)
        assert state["plan"] == "pro"
        assert state["stripe_subscription_id"] == "sub_pg_pro"
        assert state["subscription_cancel_at_period_end"] is True

        assert repository.apply_subscription_event(
            event_id="evt_pg_billing_deleted",
            event_type="customer.subscription.deleted",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_pro",
            status="canceled",
            plan=SubscriptionPlan.FREE,
            current_period_end=None,
            cancel_at_period_end=False,
        )
        state = _state(repository)
        assert state["plan"] == "free"
        assert state["subscription_status"] == "canceled"
        assert state["subscription_current_period_end"] is None
    finally:
        _cleanup(repository)


def test_postgres_stripe_entitlement_failure_rolls_back_event_marker() -> None:
    repository = _repository()
    event_id = "evt_pg_billing_rollback"
    try:
        _prepare_user(repository)

        with pytest.raises(ValueError, match="not linked"):
            repository.apply_subscription_event(
                event_id=event_id,
                event_type="customer.subscription.updated",
                customer_id="cus_unknown",
                subscription_id="sub_pg_unknown",
                status="active",
                plan=SubscriptionPlan.PRO,
                current_period_end=None,
                cancel_at_period_end=False,
            )

        assert repository._connection.execute(
            "SELECT 1 FROM stripe_webhook_events WHERE event_id = %s", (event_id,)
        ).fetchone() is None

        assert repository.apply_subscription_event(
            event_id=event_id,
            event_type="customer.subscription.updated",
            customer_id=CUSTOMER_ID,
            subscription_id="sub_pg_retry",
            status="active",
            plan=SubscriptionPlan.PRO,
            current_period_end=None,
            cancel_at_period_end=False,
        )
        assert _state(repository)["plan"] == "pro"
    finally:
        _cleanup(repository)
