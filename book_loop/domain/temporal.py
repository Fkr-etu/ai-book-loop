from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class TemporalScopeKind(StrEnum):
    TIMELESS = "timeless"
    STORY_POINT = "story_point"


class TemporalScope(BaseModel):
    """Narrative validity scope used to distinguish state evolution from contradiction."""

    kind: TemporalScopeKind = TemporalScopeKind.TIMELESS
    position: int | None = Field(default=None, ge=0)

    def overlaps(self, other: "TemporalScope") -> bool:
        if self.kind is TemporalScopeKind.TIMELESS or other.kind is TemporalScopeKind.TIMELESS:
            return True
        if self.position is None or other.position is None:
            return True
        return self.position == other.position
