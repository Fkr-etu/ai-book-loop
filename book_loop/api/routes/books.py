from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from book_loop.api.dependencies import get_container, get_owned_book
from book_loop.domain.models import UserPublic
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/books", tags=["books"])


class CreateBookPayload(BaseModel):
    title: str
    theme: str
    author_idea: str
    lore: str = ""
    constraints: list[str] = Field(default_factory=list)


def _serialize_book(book: Any, container: Container) -> dict[str, Any]:
    """Serialize the durable book state and hydrate its persisted chapter drafts."""
    response = book.model_dump(mode="json")
    for chapter in response["chapters"]:
        versions = container.repository.list_chapter_versions(book.id, chapter["number"])
        chapter["versions"] = [
            {
                "id": version["id"],
                "versionNumber": version["version"],
                "content": version["draft"],
                "createdAt": version["created_at"],
                "source": "ai",
                "status": chapter["status"],
            }
            for version in versions
        ]
    return response


@router.get("")
def list_books(request: Request, container: Container = Depends(get_container)) -> list[dict[str, Any]]:
    current_user: UserPublic = request.state.user
    books = container.repository.list_books_for_owner(current_user.id)
    return [_serialize_book(book, container) for book in books]


@router.get("/{book_id}")
def read_book(book_id: str, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    return _serialize_book(get_owned_book(book_id, request, container), container)


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
    return _serialize_book(book, container)


@router.put("/{book_id}")
def update_book(book_id: str, request: Request, updates: dict[str, Any] = Body(...), container: Container = Depends(get_container)) -> dict[str, Any]:
    book = get_owned_book(book_id, request, container)
    try:
        updated_book = container.update_book().execute(book.id, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return _serialize_book(updated_book, container)
