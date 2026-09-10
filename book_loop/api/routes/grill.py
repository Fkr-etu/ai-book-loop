from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.application.use_cases.grill import GrillMessage, GrillResponse
from book_loop.domain.models import UserPublic
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/grill", tags=["grill"])


class GrillRequest(BaseModel):
    messages: list[GrillMessage] = Field(default_factory=list)
    turn: int = Field(ge=1)


@router.post("", response_model=GrillResponse)
def grill(
    book_id: str,
    payload: GrillRequest,
    request: Request,
    container: Container = Depends(get_container),
) -> GrillResponse:
    book = get_owned_book(book_id, request, container)
    try:
        return container.grill().execute(book=book, messages=payload.messages, turn=payload.turn)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
