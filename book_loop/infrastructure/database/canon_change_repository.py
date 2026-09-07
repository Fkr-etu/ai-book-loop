from __future__ import annotations

from typing import Any

from book_loop.domain.canon_change import (
    CanonChangeProposal,
    CanonChangeProposalStatus,
    CanonChangeReviewDecision,
    CanonChangeReviewDecisionType,
)


class CanonChangeRepositoryMixin:
    """Persistence adapter for author-authored Canon change proposals."""

    def save_canon_change_proposal(self, proposal: CanonChangeProposal) -> None:
        self._connection.execute(
            """
            INSERT INTO canon_change_proposals
              (id, book_id, canonical_fact_id, statement, subject, predicate, object, proposer_id, rationale, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
            """,
            (proposal.id, proposal.book_id, proposal.canonical_fact_id, proposal.statement,
             proposal.subject, proposal.predicate, proposal.object, proposal.proposer_id,
             proposal.rationale, proposal.status.value, proposal.created_at),
        )
        self._connection.commit()

    def get_canon_change_proposal(self, proposal_id: str) -> CanonChangeProposal:
        row = self._connection.execute("SELECT * FROM canon_change_proposals WHERE id = ?", (proposal_id,)).fetchone()
        if row is None:
            raise KeyError(f"Unknown Canon change proposal: {proposal_id}")
        return self._canon_change_proposal_from_row(row)

    def list_canon_change_proposals(self, *, book_id: str) -> list[CanonChangeProposal]:
        rows = self._connection.execute("SELECT * FROM canon_change_proposals WHERE book_id = ? ORDER BY created_at, id", (book_id,)).fetchall()
        return [self._canon_change_proposal_from_row(row) for row in rows]

    def set_canon_change_proposal_status(self, proposal_id: str, status: CanonChangeProposalStatus) -> None:
        cursor = self._connection.execute("UPDATE canon_change_proposals SET status = ? WHERE id = ?", (status.value, proposal_id))
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown Canon change proposal: {proposal_id}")
        self._connection.commit()

    def save_canon_change_review_decision(self, decision: CanonChangeReviewDecision) -> None:
        self._connection.execute(
            "INSERT INTO canon_change_review_decisions(id, proposal_id, decision, reviewer_id, rationale, created_at) VALUES (?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))",
            (decision.id, decision.proposal_id, decision.decision.value, decision.reviewer_id, decision.rationale, decision.created_at),
        )
        self._connection.commit()

    def list_canon_change_review_decisions(self, *, proposal_id: str) -> list[CanonChangeReviewDecision]:
        rows = self._connection.execute("SELECT * FROM canon_change_review_decisions WHERE proposal_id = ? ORDER BY created_at, id", (proposal_id,)).fetchall()
        return [CanonChangeReviewDecision(
            id=row["id"], proposal_id=row["proposal_id"], decision=CanonChangeReviewDecisionType(row["decision"]),
            reviewer_id=row["reviewer_id"], rationale=row["rationale"], created_at=row["created_at"],
        ) for row in rows]

    @staticmethod
    def _canon_change_proposal_from_row(row: Any) -> CanonChangeProposal:
        return CanonChangeProposal(
            id=row["id"], book_id=row["book_id"], canonical_fact_id=row["canonical_fact_id"], statement=row["statement"],
            subject=row["subject"], predicate=row["predicate"], object=row["object"], proposer_id=row["proposer_id"],
            rationale=row["rationale"], status=row["status"], created_at=row["created_at"],
        )
