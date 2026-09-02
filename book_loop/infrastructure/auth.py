from __future__ import annotations

from datetime import datetime, timedelta, timezone
import argon2
import jwt

from book_loop.domain.models import User, UserPublic

_ph = argon2.PasswordHasher()
ALGORITHM = "HS256"
COOKIE_NAME = "__Host-session_token"
ACCESS_TOKEN_EXPIRE_DAYS = 7


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
    payload = {
        "sub": user.id,
        "exp": expire,
    }
    return jwt.encode(payload, _key(secret_key), algorithm=ALGORITHM)


def decode_access_token(token: str, *, secret_key: str) -> dict | None:
    try:
        return jwt.decode(token, _key(secret_key), algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
