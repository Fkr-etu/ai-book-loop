from __future__ import annotations

from dataclasses import dataclass

from book_loop.domain.models import SubscriptionPlan


@dataclass(frozen=True)
class PlanLimits:
    max_active_projects: int
    monthly_workflow_runs: int


PLAN_LIMITS: dict[SubscriptionPlan, PlanLimits] = {
    SubscriptionPlan.FREE: PlanLimits(max_active_projects=1, monthly_workflow_runs=5),
    SubscriptionPlan.CREATOR: PlanLimits(max_active_projects=3, monthly_workflow_runs=50),
    SubscriptionPlan.PRO: PlanLimits(max_active_projects=10, monthly_workflow_runs=200),
}


def limits_for(plan: SubscriptionPlan) -> PlanLimits:
    """Return the authoritative backend capacity for a subscription plan."""
    return PLAN_LIMITS[plan]


def can_create_project(plan: SubscriptionPlan, active_projects: int) -> bool:
    return active_projects < limits_for(plan).max_active_projects


def can_run_workflow(plan: SubscriptionPlan, monthly_runs: int) -> bool:
    return monthly_runs < limits_for(plan).monthly_workflow_runs
