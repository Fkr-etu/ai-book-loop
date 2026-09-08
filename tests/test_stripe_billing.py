from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
import stripe
from stripe import SignatureVerificationError

from book_loop.domain.models import SubscriptionPlan
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.stripe_billing import StripeBillingService


@dataclass
class FakeRepository:
    customer_id: str | None = None
    subscription_status: str = "inactive"
    applied: dict | None = None
    billing_state: dict | None = None
    recorded_events: set[str] | None = None
    fail_event_once: bool = False

    def __post_init__(self) -> None:
        if self.recorded_events is None:
            self.recorded_events = set()

    def get_customer_id(self, user_id: str) -> str | None:
        return self.customer_id

    def get_subscription_status(self, user_id: str) -> str:
        return self.subscription_status

    def get_billing_state(self, user_id: str) -> dict:
        return self.billing_state or {
            "plan": "free",
            "subscription_status": "inactive",
            "subscription_current_period_end": None,
            "subscription_cancel_at_period_end": False,
        }

    def set_customer_id(self, user_id: str, customer_id: str) -> None:
        self.customer_id = customer_id

    def record_event(self, event_id: str, event_type: str) -> bool:
        assert self.recorded_events is not None
        if event_id in self.recorded_events:
            return False
        self.recorded_events.add(event_id)
        return True

    def apply_subscription(self, **kwargs) -> None:
        self.applied = kwargs

    def apply_subscription_event(self, **kwargs) -> bool:
        event_id = kwargs["event_id"]
        if self.recorded_events is None:
            self.recorded_events = set()
        if event_id in self.recorded_events:
            return False
        if self.fail_event_once:
            self.fail_event_once = False
            raise RuntimeError("transient database failure")
        self.recorded_events.add(event_id)
        self.applied = {
            key: value for key, value in kwargs.items() if key not in {"event_id", "event_type"}
        }
        return True


def settings() -> Settings:
    return Settings(
        database_url="postgresql://book_loop:book_loop@localhost:5432/book_loop",
        stripe_secret_key="sk_test_x",
        stripe_webhook_secret="whsec_test",
        stripe_creator_monthly_price_id="price_creator_monthly",
        stripe_creator_yearly_price_id="price_creator_yearly",
        stripe_pro_monthly_price_id="price_pro_monthly",
        stripe_pro_yearly_price_id="price_pro_yearly",
    )


def test_price_mapping_is_server_side():
    service = StripeBillingService(settings(), FakeRepository())
    assert service._price_id(SubscriptionPlan.CREATOR, "monthly") == "price_creator_monthly"
    assert service._price_id(SubscriptionPlan.CREATOR, "yearly") == "price_creator_yearly"
    assert service._price_id(SubscriptionPlan.PRO, "monthly") == "price_pro_monthly"
    assert service._price_id(SubscriptionPlan.PRO, "yearly") == "price_pro_yearly"


def test_unknown_price_fails_closed_to_free_plan():
    service = StripeBillingService(settings(), FakeRepository())
    assert service._plan_for_price("price_unknown") is SubscriptionPlan.FREE


def test_active_subscription_cannot_start_second_checkout():
    repository = FakeRepository(subscription_status="active")
    service = StripeBillingService(settings(), repository)
    with pytest.raises(ValueError, match="active Stripe subscription"):
        service.create_checkout_session(
            user_id="user-1",
            email="author@example.com",
            plan=SubscriptionPlan.PRO,
            billing_cycle="monthly",
        )


def test_billing_state_hides_stripe_identifiers():
    repository = FakeRepository(
        billing_state={
            "plan": "creator",
            "subscription_status": "active",
            "subscription_current_period_end": None,
            "subscription_cancel_at_period_end": False,
            "stripe_customer_id": "cus_secret",
            "stripe_subscription_id": "sub_secret",
        }
    )
    service = StripeBillingService(settings(), repository)
    state = service.get_billing_state(user_id="user-1")
    assert state["plan"] == "creator"
    assert "stripe_customer_id" not in state
    assert "stripe_subscription_id" not in state


def subscription_payload(*, status: str = "active", price_id: str = "price_pro_monthly") -> dict:
    return {
        "id": "sub_123",
        "customer": "cus_123",
        "status": status,
        "current_period_end": 1_800_000_000,
        "cancel_at_period_end": True,
        "items": {"data": [{"price": {"id": price_id}}]},
    }


def test_active_subscription_grants_plan_and_persists_period():
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)

    service._apply_subscription(subscription_payload(), customer_id="cus_123")

    assert repository.applied is not None
    assert repository.applied["plan"] is SubscriptionPlan.PRO
    assert repository.applied["subscription_id"] == "sub_123"
    assert repository.applied["status"] == "active"
    assert repository.applied["cancel_at_period_end"] is True
    assert repository.applied["current_period_end"] == datetime.fromtimestamp(1_800_000_000, tz=timezone.utc)


def test_trialing_subscription_grants_creator_plan():
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)

    service._apply_subscription(
        subscription_payload(status="trialing", price_id="price_creator_yearly"),
        customer_id="cus_123",
    )

    assert repository.applied is not None
    assert repository.applied["plan"] is SubscriptionPlan.CREATOR
    assert repository.applied["status"] == "trialing"


@pytest.mark.parametrize("status", ["canceled", "past_due", "unpaid", "incomplete"])
def test_non_paid_subscription_fails_closed_to_free(status: str):
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)

    service._apply_subscription(
        subscription_payload(status=status, price_id="price_pro_monthly"),
        customer_id="cus_123",
    )

    assert repository.applied is not None
    assert repository.applied["plan"] is SubscriptionPlan.FREE
    assert repository.applied["status"] == status


def test_webhook_rejects_invalid_signature(monkeypatch):
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)

    def reject(*args, **kwargs):
        raise SignatureVerificationError("invalid signature", "sig_header")

    monkeypatch.setattr(stripe.Webhook, "construct_event", reject)

    with pytest.raises(SignatureVerificationError):
        service.handle_webhook(b"{}", "bad-signature")

    assert repository.recorded_events == set()


def test_webhook_is_idempotent(monkeypatch):
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)
    event = {
        "id": "evt_123",
        "type": "customer.subscription.updated",
        "data": {"object": subscription_payload()},
    }
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda *args, **kwargs: event)

    service.handle_webhook(b"payload", "valid-signature")
    first_application = repository.applied
    service.handle_webhook(b"payload", "valid-signature")

    assert repository.recorded_events == {"evt_123"}
    assert repository.applied is first_application


def test_webhook_processing_failure_is_retryable(monkeypatch):
    repository = FakeRepository(fail_event_once=True)
    service = StripeBillingService(settings(), repository)
    event = {
        "id": "evt_retry",
        "type": "customer.subscription.updated",
        "data": {"object": subscription_payload()},
    }
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda *args, **kwargs: event)

    with pytest.raises(RuntimeError, match="transient database failure"):
        service.handle_webhook(b"payload", "valid-signature")

    assert repository.recorded_events == set()
    assert repository.applied is None

    service.handle_webhook(b"payload", "valid-signature")

    assert repository.recorded_events == {"evt_retry"}
    assert repository.applied is not None
    assert repository.applied["plan"] is SubscriptionPlan.PRO


def test_checkout_completed_retrieves_subscription_and_applies_it(monkeypatch):
    repository = FakeRepository()
    service = StripeBillingService(settings(), repository)
    event = {
        "id": "evt_checkout",
        "type": "checkout.session.completed",
        "data": {"object": {"customer": "cus_123", "subscription": "sub_123"}},
    }
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda *args, **kwargs: event)
    monkeypatch.setattr(
        stripe.Subscription,
        "retrieve",
        lambda subscription_id: subscription_payload(price_id="price_creator_monthly"),
    )

    service.handle_webhook(b"payload", "valid-signature")

    assert repository.applied is not None
    assert repository.applied["plan"] is SubscriptionPlan.CREATOR
    assert repository.applied["customer_id"] == "cus_123"
