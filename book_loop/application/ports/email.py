from __future__ import annotations

from typing import Protocol


class EmailSender(Protocol):
    def send_verification_email(self, *, recipient: str, verification_url: str) -> None: ...


class EmailVerificationIssuer(Protocol):
    def issue(self, *, user_id: str) -> None: ...
