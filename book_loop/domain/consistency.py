from __future__ import annotations

from pydantic import BaseModel, Field


class ConsistencyIssue(BaseModel):
    """Evidence-backed, author-facing representation of a corpus inconsistency."""

    id: str
    category: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str = Field(min_length=1)
    left_assertion_id: str
    right_assertion_id: str
    left_statement: str = Field(min_length=1)
    right_statement: str = Field(min_length=1)
    left_evidence: str = ""
    right_evidence: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    rule_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    resolution_assertion_id: str | None = None
