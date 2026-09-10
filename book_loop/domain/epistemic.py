from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Protocol

from pydantic import BaseModel, Field, model_validator


class EpistemicStatus(StrEnum):
    """How an assertion is held within the narrative knowledge model."""

    CANONICAL = "canonical"
    REPORTED = "reported"
    BELIEVED = "believed"
    HYPOTHESIS = "hypothesis"
    UNCERTAIN = "uncertain"


class AuthorityLevel(IntEnum):
    """Relative authority of the source making an assertion."""

    INFERRED = 10
    CHARACTER = 20
    SOURCE = 30
    NARRATOR = 40
    CANONICAL = 50


class AssertionEpistemic(BaseModel):
    """Epistemic metadata kept separate from the assertion text itself."""

    status: EpistemicStatus = EpistemicStatus.REPORTED
    authority: AuthorityLevel = AuthorityLevel.SOURCE
    reliability: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_canonical_authority(self) -> "AssertionEpistemic":
        if self.status is EpistemicStatus.CANONICAL and self.authority is not AuthorityLevel.CANONICAL:
            raise ValueError("Canonical assertions require canonical authority")
        return self


class AssertionEpistemicStore(Protocol):
    """Port used by application services to read epistemic metadata."""

    def get_epistemic(self, *, assertion_id: str) -> AssertionEpistemic | None: ...


def should_defer_conflict(
    left: AssertionEpistemic,
    right: AssertionEpistemic,
) -> bool:
    """Return whether a disagreement needs adjudication rather than a hard conflict.

    A lower-certainty or lower-authority claim must not silently override a
    stronger claim. Such pairs remain useful review signals, but they are not
    deterministic contradictions.
    """

    if left.status is EpistemicStatus.UNCERTAIN or right.status is EpistemicStatus.UNCERTAIN:
        return True
    if left.status is EpistemicStatus.HYPOTHESIS or right.status is EpistemicStatus.HYPOTHESIS:
        return True
    if left.status is EpistemicStatus.BELIEVED or right.status is EpistemicStatus.BELIEVED:
        return True

    if left.authority != right.authority:
        stronger, weaker = sorted((left, right), key=lambda value: value.authority, reverse=True)
        if stronger.authority > weaker.authority and stronger.reliability >= weaker.reliability:
            return True

    return False
