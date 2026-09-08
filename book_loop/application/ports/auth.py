from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from book_loop.domain.models import User, UserPublic


@dataclass(frozen=True)
class AuthToken:
    value: str


@dataclass(frozen=True)
class RateLimitReservation:
    event_id: int | None = None


class AuthRepository(Protocol):
    def get_user_by_email(self, email: str) -> User | None: ...
    def get_user_by_id(self, user_id: str) -> User | None: ...
    def create_user(self, user: User) -> User: ...


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


def to_public_user(user: User) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, name=user.name, plan=user.plan)
