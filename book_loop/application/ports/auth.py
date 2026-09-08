from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from typing import Protocol

from book_loop.domain.models import User, UserPublic


@dataclass(frozen=True)
class AuthToken:
    value: str


@dataclass(frozen=True)
class RateLimitReservation:
    allowed: bool
    event_id: int | None = None
    retry_after_seconds: int | None = None


class AuthRepository(Protocol):
    def get_user_by_email(self, email: str) -> User | None: ...
    def get_user_by_id(self, user_id: str) -> User | None: ...
    def create_user(self, user: User) -> User: ...
    def create_email_verification_token(self, *, user_id: str, token_hash: str, expires_at: datetime) -> None: ...
    def consume_email_verification_token(self, *, token_hash: str, now: datetime) -> str | None: ...


class PasswordHasher(Protocol):
    def validate(self, password: str) -> str: ...
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, password_hash: str) -> bool: ...


class TokenService(Protocol):
    def issue(self, user: User | UserPublic) -> AuthToken: ...
    def decode(self, token: str) -> dict | None: ...


class AuthRateLimiter(Protocol):
    def consume(self, key: str, *, limit: int, window_seconds: int) -> RateLimitReservation: ...
    def release(self, event_id: int | None) -> None: ...
    def reset(self, key: str) -> None: ...


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def email_key(email: str) -> str:
    digest = hashlib.sha256(normalize_email(email).encode("utf-8")).hexdigest()
    return f"email:{digest}"


def ip_key(ip: str) -> str:
    digest = hashlib.sha256(ip.encode("utf-8")).hexdigest()
    return f"ip:{digest}"


def to_public_user(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, name=user.name, plan=user.plan, email_verified=user.email_verified_at is not None)
