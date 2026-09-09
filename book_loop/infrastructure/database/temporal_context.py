from __future__ import annotations

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


class TemporalContextStore:
    """Adapter that lets existing repositories expose temporal context without changing their public base class."""

    def __init__(self, repository: object) -> None:
        connection = getattr(repository, "_connection", None)
        if connection is None:
            raise TypeError("Repository does not expose a database connection")
        self._connection = connection

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None:
        TemporalContextRepositoryMixin.save_temporal_scope(self, assertion_id=assertion_id, scope=scope)

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None:
        return TemporalContextRepositoryMixin.get_temporal_scope(self, assertion_id=assertion_id)
