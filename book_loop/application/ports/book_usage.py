from __future__ import annotations

from typing import Protocol


class BookUsagePort(Protocol):
    """Application port for free-tier book identity and workflow consumption."""

    def register_book_identity(self, *, book_id: str, identity: str) -> None: ...

    def get_book_identity(self, *, book_id: str) -> str | None: ...

    def consume_workflow_capacity(
        self,
        *,
        quota_subject: str,
        period_start: str,
        idempotency_key: str,
        monthly_limit: int,
    ) -> bool: ...
