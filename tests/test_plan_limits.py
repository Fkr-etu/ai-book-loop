from book_loop.application.services.plan_limits import can_create_project, can_run_workflow, limits_for
from book_loop.domain.models import SubscriptionPlan


def test_free_capacity_is_intentionally_bounded():
    limits = limits_for(SubscriptionPlan.FREE)
    assert limits.max_active_projects == 1
    assert limits.monthly_workflow_runs == 5
    assert can_create_project(SubscriptionPlan.FREE, 0)
    assert not can_create_project(SubscriptionPlan.FREE, 1)
    assert can_run_workflow(SubscriptionPlan.FREE, 4)
    assert not can_run_workflow(SubscriptionPlan.FREE, 5)


def test_creator_capacity():
    limits = limits_for(SubscriptionPlan.CREATOR)
    assert limits.max_active_projects == 3
    assert limits.monthly_workflow_runs == 50
    assert can_create_project(SubscriptionPlan.CREATOR, 2)
    assert not can_create_project(SubscriptionPlan.CREATOR, 3)
    assert can_run_workflow(SubscriptionPlan.CREATOR, 49)
    assert not can_run_workflow(SubscriptionPlan.CREATOR, 50)


def test_pro_capacity():
    limits = limits_for(SubscriptionPlan.PRO)
    assert limits.max_active_projects == 10
    assert limits.monthly_workflow_runs == 200
    assert can_create_project(SubscriptionPlan.PRO, 9)
    assert not can_create_project(SubscriptionPlan.PRO, 10)
    assert can_run_workflow(SubscriptionPlan.PRO, 199)
    assert not can_run_workflow(SubscriptionPlan.PRO, 200)
