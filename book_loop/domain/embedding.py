from __future__ import annotations

from pydantic import BaseModel, Field


class CanonicalFactEmbedding(BaseModel):
    """Persisted semantic index entry for one canonical fact version."""

    fact_id: str
    embedding: tuple[float, ...] = Field(min_length=1)
    model: str = Field(min_length=1)
