from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

from book_loop.api.dependencies import get_container, get_current_user, set_session_cookie
from book_loop.domain.models import UserPublic
from book_loop.infrastructure.auth import COOKIE_NAME
from book_loop.infrastructure.auth_rate_limit import email_key, ip_key
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/auth", tags=["auth"])

GENERIC_AUTH_ERROR = "Adresse e-mail ou mot de passe incorrect."
GENERIC_REGISTER_ERROR = "Impossible de créer le compte. Vérifiez les informations saisies et réessayez."
RATE_LIMIT_ERROR = "Trop de tentatives. Réessayez dans quelques instants."


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    name: str = ""


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register", status_code=201)
def register(payload: RegisterPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    try:
        public, token = container.register_user_use_case.execute(
            email=str(payload.email),
            password=payload.password,
            name=payload.name,
            rate_key=ip_key(_client_ip(request)),
        )
    except PermissionError as exc:
        if str(exc) == "Rate limit exceeded":
            raise HTTPException(status_code=429, detail=RATE_LIMIT_ERROR, headers={"Retry-After": "60"})
        raise HTTPException(status_code=400, detail=GENERIC_REGISTER_ERROR)
    except ValueError as exc:
        if str(exc) == "User already exists":
            raise HTTPException(status_code=400, detail=GENERIC_REGISTER_ERROR)
        raise HTTPException(status_code=422, detail=str(exc))
    set_session_cookie(response, token, container)
    return {"user": public.model_dump(mode="json")}


@router.post("/login")
def login(payload: LoginPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    try:
        public, token = container.login_user_use_case.execute(
            email=str(payload.email),
            password=payload.password,
            email_key=email_key(str(payload.email)),
            ip_key=ip_key(_client_ip(request)),
        )
    except PermissionError as exc:
        if str(exc) == "Rate limit exceeded":
            raise HTTPException(status_code=429, detail=RATE_LIMIT_ERROR, headers={"Retry-After": "60"})
        raise HTTPException(status_code=401, detail=GENERIC_AUTH_ERROR)
    set_session_cookie(response, token, container)
    return {"user": public.model_dump(mode="json")}


@router.post("/logout")
def logout(response: Response) -> dict[str, Any]:
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Déconnexion réussie."}


@router.get("/me")
def me(current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
    return {"user": current_user.model_dump(mode="json")}
