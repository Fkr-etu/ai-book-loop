from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from starlette.responses import Response

from book_loop.api.dependencies import get_current_user
from book_loop.domain.models import SubscriptionPlan

router = APIRouter(prefix="/api/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    plan: Literal["creator", "pro"]
    billing_cycle: Literal["monthly", "yearly"]


@router.post("/checkout")
def create_checkout(request: Request, payload: CheckoutRequest) -> dict[str, str]:
    current_user = get_current_user(request)
    container = request.app.state.container
    try:
        url = container.billing.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
            plan=SubscriptionPlan(payload.plan),
            billing_cycle=payload.billing_cycle,
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"url": url}


@router.post("/portal")
def create_portal(request: Request) -> dict[str, str]:
    current_user = get_current_user(request)
    container = request.app.state.container
    try:
        url = container.billing.create_portal_session(user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Response:
    container = request.app.state.container
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    try:
        container.billing.handle_webhook(await request.body(), signature)
    except Exception as exc:
        # Do not acknowledge malformed/unauthenticated events: Stripe must retry them.
        if exc.__class__.__module__.startswith("stripe") or isinstance(exc, (ValueError, RuntimeError)):
            raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc
        raise
    return Response(status_code=200)
