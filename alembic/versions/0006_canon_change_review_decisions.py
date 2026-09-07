"""Persist explicit review decisions for Canon change proposals."""

from alembic import op

revision = "0006_canon_review_decisions"
down_revision = "0005_canon_change_proposals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS canon_change_review_decisions (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            reviewer_id TEXT,
            rationale TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_canon_change_review_decisions_proposal
            ON canon_change_review_decisions(proposal_id, created_at, id);
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_canon_change_review_decisions_proposal; DROP TABLE IF EXISTS canon_change_review_decisions;")
