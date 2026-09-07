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


class CanonChangeProposalPayload(BaseModel):
    fact_id: str
    statement: str
    object: str
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


@router.get("/consistency/issues")
def list_consistency_issues(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    issues = container.analyze_consistency().list_existing(book_id=book_id)
    return {"issues": [issue.model_dump(mode="json") for issue in issues]}


@router.post("/consistency/analyze")
def analyze_consistency(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    issues = container.analyze_consistency().execute(book_id=book_id)
    return {"issues": [issue.model_dump(mode="json") for issue in issues]}


@router.get("/canonical-facts")
def list_canonical_facts(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    facts = container.repository.list_active_canonical_facts(book_id=book_id)
    return {"facts": [fact.model_dump(mode="json") for fact in facts]}


@router.get("/canonical-facts/{fact_id}/impact")
def analyze_canon_change(book_id: str, fact_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    try:
        report = container.analyze_canon_change().execute(book_id=book_id, changed_fact_id=fact_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"changed_fact_id": report.changed_fact_id, "findings": [{"fact_id": finding.fact_id, "assertion_id": finding.assertion_id, "statement": finding.statement, "source_document_id": finding.source_document_id, "chunk_id": finding.chunk_id, "excerpt": finding.excerpt, "start_offset": finding.start_offset, "end_offset": finding.end_offset, "risk": finding.risk.value, "dependency_depth": finding.dependency_depth} for finding in report.findings]}


@router.get("/canon-change-proposals")
def list_canon_change_proposals(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    """List author proposals without changing active Canon."""
    get_owned_book(book_id, request, container)
    proposals = container.repository.list_canon_change_proposals(book_id=book_id)
    return {"proposals": [proposal.model_dump(mode="json") for proposal in proposals]}


@router.post("/canon-change-proposals", status_code=201)
def propose_canon_change(book_id: str, payload: CanonChangeProposalPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    """Create an author proposal; Canon remains unchanged until a later review decision."""
    get_owned_book(book_id, request, container)
    current_user: UserPublic = get_current_user(request)
    try:
        proposal = container.propose_canon_change().execute(
            book_id=book_id,
            fact_id=payload.fact_id,
            statement=payload.statement,
            object=payload.object,
            proposer_id=current_user.id,
            rationale=payload.rationale,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return proposal.model_dump(mode="json")


@router.post("/assertions/{assertion_id}/review")
def review_assertion(book_id: str, assertion_id: str, payload: ReviewAssertionPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    get_owned_book(book_id, request, container)
    current_user: UserPublic = get_current_user(request)
    try:
        decision_enum = ReviewDecisionType(payload.decision.lower())
        review = container.review_assertion().execute(book_id=book_id, assertion_id=assertion_id, decision=decision_enum, reviewer_id=current_user.id, rationale=payload.rationale)
        return review.model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
