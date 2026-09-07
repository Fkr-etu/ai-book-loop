from __future__ import annotations

from dataclasses import dataclass

from book_loop.domain.models import SubscriptionPlan
from book_loop.infrastructure.config import Settings
from book_loop.infrastructure.stripe_billing import StripeBillingService


@dataclass
class FakeRepository:
    customer_id: str | None = None
    applied: dict | None = None

    def get_customer_id(self, user_id: str) -> str | None:
        return self.customer_id

    def set_customer_id(self, user_id: str, customer_id: str) -> None:
        self.customer_id = customer_id

    def apply_subscription(self, **kwargs) -> None:
        self.applied = kwargs


def settings() -> Settings:
    return Settings(
        database_url="postgresql://book_loop:book_loop@localhost:5432/book_loop",
        stripe_secret_key="sk_test_x",
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
