from __future__ import annotations

import json
from typing import Any

from book_loop.domain.temporal import TemporalScope, TemporalScopeKind


class TemporalContextRepositoryMixin:
    """Persistence operations for explicit narrative temporal scopes."""

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        self._connection.execute(
            """
            INSERT INTO assertion_temporal_contexts(assertion_id, kind, position)
            VALUES(?, ?, ?)
            ON CONFLICT(assertion_id) DO UPDATE SET kind=excluded.kind, position=excluded.position
            """,
            (assertion_id, scope.kind.value, scope.position),
        )
        self._connection.commit()

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        row = self._connection.execute(
            "SELECT kind, position FROM assertion_temporal_contexts WHERE assertion_id = ?",
            (assertion_id,),
        ).fetchone()
        if row is None:
            return None
        return TemporalScope(kind=TemporalScopeKind(row["kind"]), position=row["position"])

    def list_temporal_scopes(self, *, assertion_ids: list[str]) -> dict[str, TemporalScope]:
        if not assertion_ids:
            return {}
        rows = self._connection.execute(
            "SELECT assertion_id, kind, position FROM assertion_temporal_contexts WHERE assertion_id = ANY(?)",
            (assertion_ids,),
        ).fetchall()
        return {
            row["assertion_id"]: TemporalScope(
                kind=TemporalScopeKind(row["kind"]),
                position=row["position"],
            )
            for row in rows
        }
