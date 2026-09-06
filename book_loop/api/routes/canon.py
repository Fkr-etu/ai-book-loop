from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from book_loop.api.dependencies import get_container, get_current_user, get_owned_book
from book_loop.domain.models import ReviewDecisionType, UserPublic
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}", tags=["canon"])


class ReviewAssertionPayload(BaseModel):
    decision: str
    rationale: str = ""


@router.get("/assertions")
def list_assertions(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    assertions = container.repository.list_assertions(book_id=book_id)
    return {"assertions": [a.model_dump(mode="json") for a in assertions]}


@router.get("/conflicts")
def list_conflicts(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    conflicts = container.repository.list_conflicts(book_id=book_id)
    return {"conflicts": [conflict.model_dump(mode="json") for conflict in conflicts]}


@router.get("/canonical-facts")
def list_canonical_facts(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    facts = container.repository.list_active_canonical_facts(book_id=book_id)
    return {"facts": [fact.model_dump(mode="json") for fact in facts]}


@router.post("/assertions/{assertion_id}/review")
def review_assertion(book_id: str, assertion_id: str, payload: ReviewAssertionPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    current_user: UserPublic = get_current_user(request)
    try:
        decision_enum = ReviewDecisionType(payload.decision.lower())
        review = container.review_assertion().execute(
            book_id=book_id,
            assertion_id=assertion_id,
            decision=decision_enum,
            reviewer_id=current_user.id,
            rationale=payload.rationale,
        )
        return review.model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
