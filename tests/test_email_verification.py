from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from book_loop.application.use_cases.verify_email import VerifyEmail
from book_loop.domain.models import SubscriptionPlan, User


class FakeRepository:
    def __init__(self) -> None:
        self.user = User(id="usr-1", email="author@example.com", password_hash="hash", plan=SubscriptionPlan.FREE)
        self.tokens: dict[str, tuple[str, datetime, bool]] = {}

    def get_user_by_id(self, user_id: str):
        return self.user if user_id == self.user.id else None

    def create_email_verification_token(self, *, user_id: str, token_hash: str, expires_at: datetime) -> None:
        self.tokens[token_hash] = (user_id, expires_at, False)

    def consume_email_verification_token(self, *, token_hash: str, now: datetime):
        token = self.tokens.get(token_hash)
        if token is None or token[2] or token[1] <= now:
            return None
        self.tokens[token_hash] = (token[0], token[1], True)
        self.user.email_verified_at = now.isoformat()
        return token[0]


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def send_verification_email(self, *, recipient: str, verification_url: str) -> None:
        self.sent.append((recipient, verification_url))


def test_issue_sends_unique_expiring_verification_link() -> None:
    repository = FakeRepository()
    sender = FakeEmailSender()
    use_case = VerifyEmail(repository, sender, "https://bookloop.example")

    use_case.issue(user_id="usr-1")

    assert len(sender.sent) == 1
    recipient, url = sender.sent[0]
    assert recipient == "author@example.com"
    assert url.startswith("https://bookloop.example/api/auth/verify-email?token=")
    assert len(repository.tokens) == 1
    _, expires_at, used = next(iter(repository.tokens.values()))
    assert expires_at > datetime.now(timezone.utc) + timedelta(hours=23)
    assert not used


def test_verify_email_consumes_token_and_is_single_use() -> None:
    repository = FakeRepository()
    sender = FakeEmailSender()
    use_case = VerifyEmail(repository, sender, "https://bookloop.example")
    use_case.issue(user_id="usr-1")
    token = sender.sent[0][1].split("token=", 1)[1]

    verified = use_case.execute(token=token)

    assert verified.email_verified is True
    assert repository.user.email_verified_at is not None
    with pytest.raises(ValueError, match="Invalid or expired verification token"):
        use_case.execute(token=token)


def test_expired_token_is_rejected() -> None:
    repository = FakeRepository()
    repository.tokens["expired"] = ("usr-1", datetime.now(timezone.utc) - timedelta(seconds=1), False)
    use_case = VerifyEmail(repository, FakeEmailSender(), "https://bookloop.example")

    with pytest.raises(ValueError, match="Invalid or expired verification token"):
        use_case.execute(token="expired")
