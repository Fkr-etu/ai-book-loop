from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from book_loop.api.dependencies import get_owned_book, get_container
from book_loop.domain.models import Outline
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books/{book_id}/outline", tags=["outline"])


class UpdateOutlinePayload(BaseModel):
    outline: Outline


@router.post("/generate")
def generate_outline(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    return container.generate_outline().execute(book).model_dump(mode="json")


@router.put("")
def update_outline(book_id: str, payload: UpdateOutlinePayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try:
        updated_book = container.update_outline().execute(book, outline=payload.outline)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")


@router.post("/approve")
def approve_outline(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try:
        updated_book = container.approve_outline().execute(book)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")
