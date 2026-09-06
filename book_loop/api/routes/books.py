from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_book, get_container
from book_loop.domain.models import UserPublic
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books", tags=["books"])


class CreateBookPayload(BaseModel):
    title: str
    theme: str
    author_idea: str
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)


@router.get("")
def list_books(request: Request, container: Container = Depends(get_container)) -> list[dict[str, Any]]:
    current_user: UserPublic = request.state.user
    books = container.repository.list_books_for_owner(current_user.id)
    return [book.model_dump(mode="json") for book in books]


@router.get("/{book_id}")
def read_book(book_id: str, container: Container = Depends(get_container)) -> dict[str, Any]:
    return get_book(book_id, container).model_dump(mode="json")


@router.post("")
def create_book(payload: CreateBookPayload, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    current_user: UserPublic = request.state.user
    try:
        book = container.create_book().execute(
            owner_id=current_user.id,
            title=payload.title,
            theme=payload.theme,
            author_idea=payload.author_idea,
            lore=payload.lore,
            constraints=payload.constraints,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    return book.model_dump(mode="json")


@router.put("/{book_id}")
def update_book(book_id: str, updates: dict[str, Any] = Body(...), container: Container = Depends(get_container)) -> dict[str, Any]:
    get_book(book_id, container)
    try:
        updated_book = container.update_book().execute(book_id, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return updated_book.model_dump(mode="json")
