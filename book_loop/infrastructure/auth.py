from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re

import argon2
import jwt

from book_loop.application.ports.auth import AuthToken
from book_loop.domain.models import User, UserPublic

_ph = argon2.PasswordHasher()
ALGORITHM = "HS256"
COOKIE_NAME = "session_token"
ACCESS_TOKEN_EXPIRE_DAYS = 7
PASSWORD_MIN_LENGTH = 12
PASSWORD_POLICY_MESSAGE = (
    "Le mot de passe doit contenir au moins 12 caractères, "
    "une majuscule, une minuscule, un chiffre et un caractère spécial."
)


def validate_password(password: str) -> str:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"[A-Z]", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"[a-z]", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"\d", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    return password


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, password)
    except (argon2.exceptions.VerifyMismatchError, argon2.exceptions.InvalidHashError):
        return False


def _key(secret_key: str) -> str:
    if not secret_key:
        raise RuntimeError("AUTH_SECRET_KEY must be configured")
    return secret_key


def create_access_token(
    user: User | UserPublic,
    *,
    secret_key: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    return jwt.encode({"sub": user.id, "exp": expire}, _key(secret_key), algorithm=ALGORITHM)


def decode_access_token(token: str, *, secret_key: str) -> dict | None:
    try:
        return jwt.decode(token, _key(secret_key), algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


class Argon2PasswordHasher:
    def validate(self, password: str) -> str:
        return validate_password(password)

    def hash(self, password: str) -> str:
        return hash_password(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return verify_password(password, password_hash)


class JwtTokenService:
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    def issue(self, user: User | UserPublic) -> AuthToken:
        return AuthToken(create_access_token(user, secret_key=self.secret_key))

    def decode(self, token: str) -> dict | None:
        return decode_access_token(token, secret_key=self.secret_key)
