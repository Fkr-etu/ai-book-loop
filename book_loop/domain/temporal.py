from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, Field, model_validator


class TemporalScopeKind(StrEnum):
    TIMELESS = "timeless"
    STORY_POINT = "story_point"


class TemporalRelation(StrEnum):
    """Deterministic relation between two ordered narrative scopes."""

    BEFORE = "before"
    OVERLAPS = "overlaps"
    DURING = "during"
    CONTAINS = "contains"
    SIMULTANEOUS = "simultaneous"
    AFTER = "after"


class TemporalScope(BaseModel):
    """Narrative validity scope used to distinguish state evolution from contradiction.

    ``position`` remains the backward-compatible representation of a single story
    point. ``end_position`` optionally turns it into an inclusive story interval.
    A timeless scope keeps the historical conservative overlap behaviour.
    """

    kind: TemporalScopeKind = TemporalScopeKind.TIMELESS
    position: int | None = Field(default=None, ge=0)
    end_position: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "TemporalScope":
        if self.kind is TemporalScopeKind.TIMELESS:
            if self.position is not None or self.end_position is not None:
                raise ValueError("A timeless scope cannot define story positions")
            return self
        if self.position is None:
            raise ValueError("A story-point scope requires position")
        if self.end_position is not None and self.end_position < self.position:
            raise ValueError("end_position must be greater than or equal to position")
        return self

    @property
    def start(self) -> int | None:
        return self.position

    @property
    def end(self) -> int | None:
        if self.kind is TemporalScopeKind.TIMELESS:
            return None
        return self.position if self.end_position is None else self.end_position

    def relation_to(self, other: "TemporalScope") -> TemporalRelation | None:
        """Return the deterministic interval relation, or None for timeless scopes."""
        if self.kind is TemporalScopeKind.TIMELESS or other.kind is TemporalScopeKind.TIMELESS:
            return None
        assert self.start is not None and self.end is not None
        assert other.start is not None and other.end is not None

        if self.end < other.start:
            return TemporalRelation.BEFORE
        if other.end < self.start:
            return TemporalRelation.AFTER
        if self.start == other.start and self.end == other.end:
            return TemporalRelation.SIMULTANEOUS
        if self.start >= other.start and self.end <= other.end:
            return TemporalRelation.DURING
        if self.start <= other.start and self.end >= other.end:
            return TemporalRelation.CONTAINS
        return TemporalRelation.OVERLAPS

    def overlaps(self, other: "TemporalScope") -> bool:
        """Preserve the existing conservative overlap semantics."""
        relation = self.relation_to(other)
        if relation is None:
            return True
        return relation in {
            TemporalRelation.OVERLAPS,
            TemporalRelation.DURING,
            TemporalRelation.CONTAINS,
            TemporalRelation.SIMULTANEOUS,
        }


class AssertionTemporalContextStore(Protocol):
    """Port used by application services to persist and read assertion temporal scope."""

    def get_temporal_scope(self, *, assertion_id: str) -> TemporalScope | None: ...

    def save_temporal_scope(self, *, assertion_id: str, scope: TemporalScope) -> None: ...
