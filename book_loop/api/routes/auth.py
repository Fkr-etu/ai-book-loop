from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

from book_loop.api.dependencies import COOKIE_NAME, get_container, get_current_user, set_session_cookie
from book_loop.application.ports.auth import email_key, ip_key
from book_loop.domain.models import UserPublic
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
    """Return the client IP from Cloud Run's appended X-Forwarded-For value.

    Cloud Run appends the connecting client address to X-Forwarded-For. Taking
    the first value would let a caller spoof the rate-limit key by supplying a
    forged leading address. The right-most value is the proxy-validated address
    for this deployment topology; when no forwarded header exists, use the
    direct ASGI client address (useful for local/test execution).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        values = [value.strip() for value in forwarded.split(",") if value.strip()]
        if values:
            return values[-1]
    return request.client.host if request.client else "unknown"


@router.post("/register", status_code=201)
def register(payload: RegisterPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    try:
        public, token = container.register_user_use_case.execute(email=str(payload.email), password=payload.password, name=payload.name, rate_key=ip_key(_client_ip(request)))
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


@router.get("/verify-email")
def verify_email(token: str, response: Response, container: Container = Depends(get_container)) -> dict[str, Any]:
    try:
        user = container.verify_email_use_case.execute(token=token)
    except ValueError:
        raise HTTPException(status_code=400, detail="Lien de vérification invalide ou expiré.")
    session = container.token_service.issue(user).value
    set_session_cookie(response, session, container)
    return {"user": user.model_dump(mode="json"), "message": "Adresse e-mail vérifiée."}


@router.post("/login")
def login(payload: LoginPayload, response: Response, request: Request, container: Container = Depends(get_container)) -> dict[str, Any]:
    try:
        public, token = container.login_user_use_case.execute(email=str(payload.email), password=payload.password, email_key=email_key(str(payload.email)), ip_key=ip_key(_client_ip(request)))
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
