from __future__ import annotations

from uuid import uuid4

from book_loop.application.ports.auth import AuthRepository, PasswordHasher, TokenService, to_public_user
from book_loop.domain.models import User, UserPublic


class RegisterUser:
    def __init__(self, repository: AuthRepository, password_hasher: PasswordHasher, token_service: TokenService) -> None:
        self.repository = repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, *, email: str, password: str, name: str = "") -> tuple[UserPublic, str]:
        password = self.password_hasher.validate(password)
        if self.repository.get_user_by_email(email):
            raise ValueError("User already exists")
        user = User(
            id=f"usr-{uuid4().hex}",
            email=email,
            password_hash=self.password_hasher.hash(password),
            name=name,
        )
        created = self.repository.create_user(user)
        public = to_public_user(created)
        return public, self.token_service.issue(public).value
