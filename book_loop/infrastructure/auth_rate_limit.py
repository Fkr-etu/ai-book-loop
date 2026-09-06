from __future__ import annotations

import hashlib
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

import psycopg
from psycopg.rows import dict_row


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


class AuthRateLimiter:
    """PostgreSQL-backed sliding-window limiter shared by all Cloud Run instances."""

    def __init__(self, database_url: str) -> None:
        url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        self._connection = psycopg.connect(url, row_factory=dict_row, autocommit=True)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_rate_limit_events (
                id BIGSERIAL PRIMARY KEY,
                rate_key TEXT NOT NULL,
                attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS ix_auth_rate_limit_events_key_time
                ON auth_rate_limit_events(rate_key, attempted_at);
            """
        )

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        self._connection.execute("BEGIN")
        try:
            yield
        except Exception:
            self._connection.rollback()
            raise
        else:
            self._connection.commit()

    def consume(self, key: str, *, limit: int, window_seconds: int) -> RateLimitResult:
        """Consume one attempt; return a non-sensitive retry delay when throttled."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)

        with self._transaction():
            self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (key,)).fetchone()
            self._connection.execute(
                "DELETE FROM auth_rate_limit_events WHERE rate_key = %s AND attempted_at < %s",
                (key, window_start),
            )
            row = self._connection.execute(
                "SELECT attempted_at FROM auth_rate_limit_events WHERE rate_key = %s ORDER BY attempted_at ASC LIMIT 1",
                (key,),
            ).fetchone()
            count = self._connection.execute(
                "SELECT COUNT(*) AS count FROM auth_rate_limit_events WHERE rate_key = %s",
                (key,),
            ).fetchone()
            if int(count["count"]) >= limit and row is not None:
                retry_after = max(1, int((row["attempted_at"] + timedelta(seconds=window_seconds) - now).total_seconds()))
                return RateLimitResult(retry_after_seconds=retry_after)

            self._connection.execute(
                "INSERT INTO auth_rate_limit_events(rate_key, attempted_at) VALUES(%s, %s)",
                (key, now),
            )
            return RateLimitResult()

    def reset(self, key: str) -> None:
        with self._transaction():
            self._connection.execute("DELETE FROM auth_rate_limit_events WHERE rate_key = %s", (key,))

    def close(self) -> None:
        self._connection.close()
