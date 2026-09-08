from __future__ import annotations

from book_loop.application.ports.auth import AuthRepository, TokenService, to_public_user
from book_loop.domain.models import UserPublic


class AuthenticateUser:
    def __init__(self, repository: AuthRepository, token_service: TokenService) -> None:
        self.repository = repository
        self.token_service = token_service

    def execute(self, *, token: str) -> UserPublic:
        payload = self.token_service.decode(token)
        if not payload or not isinstance(payload.get("sub"), str):
            raise PermissionError("Invalid session")
        user = self.repository.get_user_by_id(payload["sub"])
        if user is None:
            raise PermissionError("Unknown user")
        return to_public_user(user)
