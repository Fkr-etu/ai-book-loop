from __future__ import annotations

from typing import Protocol


class BookUsagePort(Protocol):
    """Application port for free-tier book eligibility and workflow consumption."""

    def get_book_identity(self, *, book_id: str) -> str | None: ...

    def consume_free_workflow_capacity(
        self,
        *,
        user_id: str,
        book_id: str,
        book_identity: str,
        period_start: str,
        idempotency_key: str,
        monthly_limit: int,
    ) -> bool: ...

    def consume_workflow_capacity(
        self,
        *,
        quota_subject: str,
        period_start: str,
        idempotency_key: str,
        monthly_limit: int,
    ) -> bool: ...
