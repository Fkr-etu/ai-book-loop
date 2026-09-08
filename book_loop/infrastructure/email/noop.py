from __future__ import annotations


class NoopEmailSender:
    """Local/test adapter; production wiring always uses Resend."""

    def send_verification_email(self, *, recipient: str, verification_url: str) -> None:
        return None
