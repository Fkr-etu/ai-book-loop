from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets

from book_loop.application.ports.auth import AuthRepository, to_public_user
from book_loop.application.ports.email import EmailSender
from book_loop.domain.models import UserPublic

TOKEN_BYTES = 32
TOKEN_TTL = timedelta(hours=24)


class VerifyEmail:
    def __init__(self, repository: AuthRepository, email_sender: EmailSender, public_base_url: str) -> None:
        self.repository = repository
        self.email_sender = email_sender
        self.public_base_url = public_base_url.rstrip("/")

    def issue(self, *, user_id: str) -> None:
        user = self.repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        if user.email_verified_at is not None:
            return
        raw_token = secrets.token_urlsafe(TOKEN_BYTES)
        token_hash = sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + TOKEN_TTL
        self.repository.create_email_verification_token(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
        verification_url = f"{self.public_base_url}/verify-email?token={raw_token}"
        self.email_sender.send_verification_email(recipient=user.email, verification_url=verification_url)

    def execute(self, *, token: str) -> UserPublic:
        token_hash = sha256(token.encode("utf-8")).hexdigest()
        user_id = self.repository.consume_email_verification_token(token_hash=token_hash, now=datetime.now(timezone.utc))
        if user_id is None:
            raise ValueError("Invalid or expired verification token")
        user = self.repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")
        return to_public_user(user)
