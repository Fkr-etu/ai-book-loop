from __future__ import annotations

from book_loop.application.ports.auth import AuthRepository, AuthRateLimiter, PasswordHasher, TokenService, to_public_user


class LoginUser:
    def __init__(self, repository: AuthRepository, password_hasher: PasswordHasher, token_service: TokenService, rate_limiter: AuthRateLimiter, *, email_limit: int, email_window_seconds: int, ip_limit: int, ip_window_seconds: int) -> None:
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.rate_limiter = rate_limiter
        self.email_limit = email_limit
        self.email_window_seconds = email_window_seconds
        self.ip_limit = ip_limit
        self.ip_window_seconds = ip_window_seconds

    def execute(self, *, email: str, password: str, email_key: str, ip_key: str) -> tuple[object, str]:
        reservations = []
        try:
            reservations.append(self.rate_limiter.consume(email_key, limit=self.email_limit, window_seconds=self.email_window_seconds))
            reservations.append(self.rate_limiter.consume(ip_key, limit=self.ip_limit, window_seconds=self.ip_window_seconds))
            user = self.repository.get_user_by_email(email)
            password_hash = user.password_hash if user else self.password_hasher.hash("dummy-password-for-timing-only")
            valid = self.password_hasher.verify(password, password_hash)
            if user is None or not valid:
                raise PermissionError("Invalid credentials")
            for reservation in reservations:
                self.rate_limiter.release(reservation.event_id)
            self.rate_limiter.reset(email_key)
            public = to_public_user(user)
            return public, self.token_service.issue(public).value
        except Exception:
            raise
