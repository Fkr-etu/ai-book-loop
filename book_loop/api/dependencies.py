from __future__ import annotations

from fastapi import HTTPException, Request, Response

from book_loop.domain.models import UserPublic
from book_loop.infrastructure.auth import COOKIE_NAME, create_access_token, decode_access_token
from book_loop.infrastructure.container import Container


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

    payload = decode_access_token(token, secret_key=container.settings.auth_secret_key)
    if not payload or not isinstance(payload.get("sub"), str):
        raise HTTPException(status_code=401, detail="Session invalide ou expirée.")

    user = container.repository.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")
    return UserPublic(id=user.id, email=user.email, name=user.name, plan=user.plan)


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
