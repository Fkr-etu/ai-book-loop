from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field

from book_loop.api.dependencies import get_container, get_current_user, set_session_cookie
from book_loop.domain.models import User, UserPublic
from book_loop.infrastructure.auth import create_access_token, hash_password, verify_password
from book_loop.infrastructure.container import Container

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(payload: RegisterPayload, response: Response, container: Container = Depends(get_container)) -> dict[str, Any]:
    if container.repository.get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cette adresse e-mail.")
    user = User(
        id=f"usr-{uuid.uuid4().hex}",
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
    )
    created = container.repository.create_user(user)
    public = UserPublic(id=created.id, email=created.email, name=created.name, plan=created.plan)
    set_session_cookie(response, create_access_token(public, secret_key=container.settings.auth_secret_key), container)
    return {"user": public.model_dump(mode="json")}


@router.post("/login")
def login(payload: LoginPayload, response: Response, container: Container = Depends(get_container)) -> dict[str, Any]:
    user = container.repository.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Adresse e-mail ou mot de passe incorrect.")
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
