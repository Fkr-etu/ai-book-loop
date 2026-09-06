from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from book_loop.api.dependencies import get_container
from book_loop.domain.models import Outline
from book_loop.infrastructure.container import Container
from book_loop.api.routes.books import get_book

router = APIRouter(prefix="/api/books/{book_id}/outline", tags=["outline"])


class UpdateOutlinePayload(BaseModel):
    outline: Outline


@router.post("/generate")
def generate_outline(book_id: str, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    return container.generate_outline().execute(book).model_dump(mode="json")


@router.put("")
def update_outline(book_id: str, payload: UpdateOutlinePayload, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        updated_book = container.update_outline().execute(book, outline=payload.outline)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")


@router.post("/approve")
def approve_outline(book_id: str, container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_book(book_id, container)
    try:
        updated_book = container.approve_outline().execute(book)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")
