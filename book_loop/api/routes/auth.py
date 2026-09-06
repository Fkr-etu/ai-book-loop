from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field, field_validator

from book_loop.api.dependencies import get_container, get_current_user, set_session_cookie
from book_loop.domain.models import User, UserPublic
from book_loop.infrastructure.auth import create_access_token, hash_password, validate_password, verify_password
from book_loop.infrastructure.auth_rate_limit import email_key, ip_key
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/auth", tags=["auth"])

GENERIC_AUTH_ERROR = "Adresse e-mail ou mot de passe incorrect."
GENERIC_REGISTER_ERROR = "Impossible de créer le compte. Vérifiez les informations saisies et réessayez."
RATE_LIMIT_ERROR = "Trop de tentatives. Réessayez dans quelques instants."
DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-only")


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    name: str = ""

    @field_validator("password")
    @classmethod
    def validate_password_policy(cls, value: str) -> str:
        return validate_password(value)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def _consume_or_raise(container: Container, *keys: str, limit: int, window_seconds: int) -> list[int]:
    event_ids: list[int] = []
    for key in keys:
        result = container.auth_rate_limiter.consume(key, limit=limit, window_seconds=window_seconds)
        if not result.allowed:
            for event_id in event_ids:
                container.auth_rate_limiter.release(event_id)
            raise HTTPException(
                status_code=429,
                detail=RATE_LIMIT_ERROR,
                headers={"Retry-After": "60"},
            )
        if result.event_id is not None:
            event_ids.append(result.event_id)
    return event_ids


@router.post("/register", status_code=201)
def register(payload: RegisterPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    event_ids = _consume_or_raise(
        container,
        ip_key(_client_ip(request)),
        limit=container.settings.auth_register_rate_limit,
        window_seconds=container.settings.auth_register_rate_window_seconds,
    )
    if container.repository.get_user_by_email(payload.email):
        return _reject_registration(container, event_ids)
    user = User(
        id=f"usr-{uuid.uuid4().hex}",
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
    )
    created = container.repository.create_user(user)
    for event_id in event_ids:
        container.auth_rate_limiter.release(event_id)
    public = UserPublic(id=created.id, email=created.email, name=created.name, plan=created.plan)
    set_session_cookie(response, create_access_token(public, secret_key=container.settings.auth_secret_key), container)
    return {"user": public.model_dump(mode="json")}


def _reject_registration(container: Container, event_ids: list[int]) -> Any:
    for event_id in event_ids:
        container.auth_rate_limiter.release(event_id)
    raise HTTPException(status_code=400, detail=GENERIC_REGISTER_ERROR)


@router.post("/login")
def login(payload: LoginPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    event_ids = _consume_or_raise(
        container,
        email_key(payload.email),
        ip_key(_client_ip(request)),
        limit=container.settings.auth_login_rate_limit,
        window_seconds=container.settings.auth_login_rate_window_seconds,
    )
    user = container.repository.get_user_by_email(payload.email)
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    valid = verify_password(payload.password, password_hash)
    if not user or not valid:
        raise HTTPException(status_code=401, detail=GENERIC_AUTH_ERROR)

    for event_id in event_ids:
        container.auth_rate_limiter.release(event_id)
    container.auth_rate_limiter.reset(email_key(payload.email))
    public = UserPublic(id=user.id, email=user.email, name=user.name, plan=user.plan)
    set_session_cookie(response, create_access_token(public, secret_key=container.settings.auth_secret_key), container)
    return {"user": public.model_dump(mode="json")}


@router.post("/logout")
def logout(response: Response) -> dict[str, Any]:
    from book_loop.infrastructure.auth import COOKIE_NAME

    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Déconnexion réussie."}


@router.get("/me")
def me(current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": current_user.model_dump(mode="json")}
