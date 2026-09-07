from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import psycopg
import stripe
from psycopg.rows import dict_row

from book_loop.domain.models import SubscriptionPlan
from book_loop.infrastructure.config import Settings


PAID_SUBSCRIPTION_STATUSES = {"active", "trialing"}


def _normalize_postgres_url(database_url: str) -> str:
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    return database_url


class StripeBillingRepository:
    """Persistence adapter for Stripe-owned billing metadata."""

    def __init__(self, database_url: str) -> None:
        self._connection = psycopg.connect(_normalize_postgres_url(database_url), row_factory=dict_row, autocommit=True)
        self._connection.execute("""
            ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status TEXT NOT NULL DEFAULT 'inactive';
            ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_current_period_end TIMESTAMPTZ;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE;
            CREATE UNIQUE INDEX IF NOT EXISTS ux_users_stripe_customer_id ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;
            CREATE UNIQUE INDEX IF NOT EXISTS ux_users_stripe_subscription_id ON users(stripe_subscription_id) WHERE stripe_subscription_id IS NOT NULL;
            CREATE TABLE IF NOT EXISTS stripe_webhook_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

    def get_customer_id(self, user_id: str) -> str | None:
        row = self._connection.execute("SELECT stripe_customer_id FROM users WHERE id = %s", (user_id,)).fetchone()
        return row["stripe_customer_id"] if row else None

    def get_subscription_status(self, user_id: str) -> str:
        row = self._connection.execute("SELECT subscription_status FROM users WHERE id = %s", (user_id,)).fetchone()
        return str(row["subscription_status"]) if row else "inactive"

    def set_customer_id(self, user_id: str, customer_id: str) -> None:
        self._connection.execute("UPDATE users SET stripe_customer_id = %s WHERE id = %s", (customer_id, user_id))

    def record_event(self, event_id: str, event_type: str) -> bool:
        row = self._connection.execute(
            "INSERT INTO stripe_webhook_events(event_id, event_type) VALUES(%s, %s) ON CONFLICT(event_id) DO NOTHING RETURNING event_id",
            (event_id, event_type),
        ).fetchone()
        return row is not None

    def apply_subscription(self, *, customer_id: str, subscription_id: str | None, status: str, plan: SubscriptionPlan, current_period_end: datetime | None, cancel_at_period_end: bool) -> None:
        self._connection.execute(
            """
            UPDATE users
            SET stripe_subscription_id = %s,
                subscription_status = %s,
                subscription_current_period_end = %s,
                subscription_cancel_at_period_end = %s,
                plan = %s
            WHERE stripe_customer_id = %s
            """,
            (subscription_id, status, current_period_end, cancel_at_period_end, plan.value, customer_id),
        )

    def close(self) -> None:
        self._connection.close()


class StripeBillingService:
    def __init__(self, settings: Settings, repository: StripeBillingRepository) -> None:
        self.settings = settings
        self.repository = repository
        stripe.api_key = settings.stripe_secret_key

    def _price_id(self, plan: SubscriptionPlan, billing_cycle: str) -> str:
        prices = {
            (SubscriptionPlan.CREATOR, "monthly"): self.settings.stripe_creator_monthly_price_id,
            (SubscriptionPlan.CREATOR, "yearly"): self.settings.stripe_creator_yearly_price_id,
            (SubscriptionPlan.PRO, "monthly"): self.settings.stripe_pro_monthly_price_id,
            (SubscriptionPlan.PRO, "yearly"): self.settings.stripe_pro_yearly_price_id,
        }
        price_id = prices.get((plan, billing_cycle), "")
        if not price_id:
            raise ValueError(f"Stripe price is not configured for {plan.value}/{billing_cycle}")
        return price_id

    def create_checkout_session(self, *, user_id: str, email: str, plan: SubscriptionPlan, billing_cycle: str) -> str:
        if plan is SubscriptionPlan.FREE:
            raise ValueError("Free plan does not require checkout")
        if billing_cycle not in {"monthly", "yearly"}:
            raise ValueError("billing_cycle must be monthly or yearly")
        if not self.settings.stripe_secret_key:
            raise RuntimeError("Stripe is not configured")
        if self.repository.get_subscription_status(user_id) in PAID_SUBSCRIPTION_STATUSES:
            raise ValueError("An active Stripe subscription already exists; use the billing portal to change it")

        customer_id = self.repository.get_customer_id(user_id)
        if not customer_id:
            customer = stripe.Customer.create(email=email, metadata={"user_id": user_id})
            customer_id = customer.id
            self.repository.set_customer_id(user_id, customer_id)

        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            client_reference_id=user_id,
            line_items=[{"price": self._price_id(plan, billing_cycle), "quantity": 1}],
            metadata={"user_id": user_id, "plan": plan.value, "billing_cycle": billing_cycle},
            subscription_data={"metadata": {"user_id": user_id, "plan": plan.value}},
            success_url=self.settings.stripe_success_url,
            cancel_url=self.settings.stripe_cancel_url,
        )
        if not session.url:
            raise RuntimeError("Stripe did not return a checkout URL")
        return session.url

    def create_portal_session(self, *, user_id: str) -> str:
        customer_id = self.repository.get_customer_id(user_id)
        if not customer_id:
            raise ValueError("No Stripe customer exists for this user")
        session = stripe.billing_portal.Session.create(customer=customer_id, return_url=self.settings.stripe_portal_return_url)
        if not session.url:
            raise RuntimeError("Stripe did not return a portal URL")
        return session.url

    def handle_webhook(self, payload: bytes, signature: str) -> None:
        if not self.settings.stripe_webhook_secret:
            raise RuntimeError("Stripe webhook secret is not configured")
        event = stripe.Webhook.construct_event(payload, signature, self.settings.stripe_webhook_secret)
        if not self.repository.record_event(event["id"], event["type"]):
            return

        event_type = event["type"]
        data: Any = event["data"]["object"]
        if event_type == "checkout.session.completed":
            subscription_id = data.get("subscription")
            customer_id = data.get("customer")
            if subscription_id and customer_id:
                self._apply_subscription(stripe.Subscription.retrieve(subscription_id), customer_id=customer_id)
            return
        if event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted"}:
            self._apply_subscription(data, customer_id=data.get("customer"))

    def _apply_subscription(self, subscription: Any, *, customer_id: str | None) -> None:
        if not customer_id:
            return
        status = str(subscription.get("status", "inactive"))
        items = subscription.get("items", {}).get("data", [])
        price_id = items[0].get("price", {}).get("id") if items else None
        plan = self._plan_for_price(price_id) if status in PAID_SUBSCRIPTION_STATUSES else SubscriptionPlan.FREE
        period_end = subscription.get("current_period_end")
        self.repository.apply_subscription(
            customer_id=customer_id,
            subscription_id=subscription.get("id"),
            status=status,
            plan=plan,
            current_period_end=datetime.fromtimestamp(period_end, tz=timezone.utc) if period_end else None,
            cancel_at_period_end=bool(subscription.get("cancel_at_period_end", False)),
        )

    def _plan_for_price(self, price_id: str | None) -> SubscriptionPlan:
        if price_id in {self.settings.stripe_creator_monthly_price_id, self.settings.stripe_creator_yearly_price_id}:
            return SubscriptionPlan.CREATOR
        if price_id in {self.settings.stripe_pro_monthly_price_id, self.settings.stripe_pro_yearly_price_id}:
            return SubscriptionPlan.PRO
        return SubscriptionPlan.FREE
