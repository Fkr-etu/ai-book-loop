from __future__ import annotations

from book_loop.application.ports.auth import AuthRepository, AuthRateLimiter, PasswordHasher, TokenService, to_public_user
from book_loop.domain.models import UserPublic


class LoginUser:
    def __init__(self, repository: AuthRepository, password_hasher: PasswordHasher, token_service: TokenService, rate_limiter: AuthRateLimiter, *, email_limit: int, email_window_seconds: int, ip_limit: int, ip_window_seconds: int, dummy_password_hash: str) -> None:
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.rate_limiter = rate_limiter
        self.email_limit = email_limit
        self.email_window_seconds = email_window_seconds
        self.ip_limit = ip_limit
        self.ip_window_seconds = ip_window_seconds
        self.dummy_password_hash = dummy_password_hash

    def execute(self, *, email: str, password: str, email_key: str, ip_key: str) -> tuple[UserPublic, str]:
        reservations = []
        email_reservation = self.rate_limiter.consume(email_key, limit=self.email_limit, window_seconds=self.email_window_seconds)
        if not email_reservation.allowed:
            raise PermissionError("Rate limit exceeded")
        reservations.append(email_reservation)

        ip_reservation = self.rate_limiter.consume(ip_key, limit=self.ip_limit, window_seconds=self.ip_window_seconds)
        if not ip_reservation.allowed:
            self.rate_limiter.release(email_reservation.event_id)
            raise PermissionError("Rate limit exceeded")
        reservations.append(ip_reservation)

        user = self.repository.get_user_by_email(email)
        password_hash = user.password_hash if user else self.dummy_password_hash
        valid = self.password_hasher.verify(password, password_hash)
        if user is None or not valid:
            raise PermissionError("Invalid credentials")

        for reservation in reservations:
            self.rate_limiter.release(reservation.event_id)
        self.rate_limiter.reset(email_key)
        public = to_public_user(user)
        return public, self.token_service.issue(public).value
