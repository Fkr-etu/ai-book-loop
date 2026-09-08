from __future__ import annotations

from fastapi import HTTPException, Request, Response

from book_loop.domain.models import BookState, UserPublic
from book_loop.infrastructure.container import Container

COOKIE_NAME = "session_token"


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_current_user(request: Request) -> UserPublic:
    container = get_container(request)
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié.")
    try:
        return container.authenticate_user_use_case.execute(token=token)
    except PermissionError:
        raise HTTPException(status_code=401, detail="Session invalide ou expirée.")


def get_book(book_id: str, container: Container) -> BookState:
    try:
        return container.repository.get(book_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Livre {book_id} introuvable.")


def get_owned_book(book_id: str, request: Request, container: Container) -> BookState:
    """Return a book only when it belongs to the authenticated user."""
    current_user = get_current_user(request)
    book = get_book(book_id, container)
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Livre introuvable.")
    return book


def set_session_cookie(response: Response, token: str, container: Container) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=container.settings.auth_cookie_secure,
        samesite=container.settings.auth_cookie_samesite,
        path="/",
        max_age=7 * 24 * 3600,
    )
