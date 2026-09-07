from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class CanonChangeProposalStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class CanonChangeProposal(BaseModel):
    """An author-intended Canon change, without fabricated source provenance."""

    id: str
    book_id: str
    canonical_fact_id: str
    statement: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    proposer_id: str | None = None
    rationale: str = ""
    status: CanonChangeProposalStatus = CanonChangeProposalStatus.PROPOSED
    created_at: str | None = None


class CanonChangeReviewDecisionType(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"


class CanonChangeReviewDecision(BaseModel):
    """The explicit editorial decision that may activate a proposed Canon change."""

    id: str
    proposal_id: str
    decision: CanonChangeReviewDecisionType
    reviewer_id: str | None = None
    rationale: str = ""
    created_at: str | None = None
