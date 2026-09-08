from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.auth import AuthRepository, AuthRateLimiter, PasswordHasher, TokenService, to_public_user
from book_loop.application.ports.email import EmailVerificationIssuer
from book_loop.domain.models import User, UserPublic


class RegisterUser:
    def __init__(self, repository: AuthRepository, password_hasher: PasswordHasher, token_service: TokenService, rate_limiter: AuthRateLimiter, *, rate_limit: int, rate_window_seconds: int, email_verification: EmailVerificationIssuer | None = None) -> None:
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.rate_limiter = rate_limiter
        self.rate_limit = rate_limit
        self.rate_window_seconds = rate_window_seconds
        self.email_verification = email_verification

    def execute(self, *, email: str, password: str, name: str, rate_key: str) -> tuple[UserPublic, str]:
        reservation = self.rate_limiter.consume(rate_key, limit=self.rate_limit, window_seconds=self.rate_window_seconds)
        if not reservation.allowed:
            raise PermissionError("Rate limit exceeded")
        password = self.password_hasher.validate(password)
        if self.repository.get_user_by_email(email):
            self.rate_limiter.release(reservation.event_id)
            raise ValueError("User already exists")
        user = User(id=f"usr-{uuid4().hex}", email=email, password_hash=self.password_hasher.hash(password), name=name)
        created = self.repository.create_user(user)
        self.rate_limiter.release(reservation.event_id)
        public = to_public_user(created)
        if self.email_verification is not None:
            self.email_verification.issue(user_id=created.id)
        return public, self.token_service.issue(public).value
