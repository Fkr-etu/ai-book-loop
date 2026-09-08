from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from book_loop.application.ports.auth import RateLimitReservation


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

    def consume(self, key: str, *, limit: int, window_seconds: int) -> RateLimitReservation:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)
        with self._transaction():
            self._connection.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (key,)).fetchone()
            self._connection.execute("DELETE FROM auth_rate_limit_events WHERE rate_key = %s AND attempted_at < %s", (key, window_start))
            row = self._connection.execute("SELECT attempted_at FROM auth_rate_limit_events WHERE rate_key = %s ORDER BY attempted_at ASC LIMIT 1", (key,)).fetchone()
            count = self._connection.execute("SELECT COUNT(*) AS count FROM auth_rate_limit_events WHERE rate_key = %s", (key,)).fetchone()
            if int(count["count"]) >= limit and row is not None:
                retry_after = max(1, int((row["attempted_at"] + timedelta(seconds=window_seconds) - now).total_seconds()))
                return RateLimitReservation(allowed=False, retry_after_seconds=retry_after)
            inserted = self._connection.execute("INSERT INTO auth_rate_limit_events(rate_key, attempted_at) VALUES(%s, %s) RETURNING id", (key, now)).fetchone()
            return RateLimitReservation(allowed=True, event_id=int(inserted["id"]))

    def release(self, event_id: int | None) -> None:
        if event_id is None:
            return
        with self._transaction():
            self._connection.execute("DELETE FROM auth_rate_limit_events WHERE id = %s", (event_id,))

    def reset(self, key: str) -> None:
        with self._transaction():
            self._connection.execute("DELETE FROM auth_rate_limit_events WHERE rate_key = %s", (key,))

    def close(self) -> None:
        self._connection.close()
