from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitResult:
    retry_after_seconds: int | None = None

    @property
    def allowed(self) -> bool:
        return self.retry_after_seconds is None


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def email_key(email: str) -> str:
    digest = hashlib.sha256(normalize_email(email).encode("utf-8")).hexdigest()
    return f"email:{digest}"


def ip_key(ip: str) -> str:
    digest = hashlib.sha256(ip.encode("utf-8")).hexdigest()
    return f"ip:{digest}"
