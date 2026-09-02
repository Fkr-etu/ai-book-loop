from __future__ import annotations

from datetime import datetime, timedelta, timezone
import argon2
import jwt

from book_loop.domain.models import User, UserPublic

_ph = argon2.PasswordHasher()

SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
COOKIE_NAME = "session_token"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
    except Exception:
        return False


def create_access_token(user: User | UserPublic, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
