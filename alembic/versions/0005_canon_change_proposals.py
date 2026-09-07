"""Persist author-authored Canon change proposals."""

from alembic import op

revision = "0005_canon_change_proposals"
down_revision = "0004_stripe_billing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS canon_change_proposals (
            id TEXT PRIMARY KEY,
            book_id TEXT NOT NULL,
            canonical_fact_id TEXT NOT NULL,
            statement TEXT NOT NULL,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            proposer_id TEXT,
            rationale TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'proposed',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_canon_change_proposals_book
            ON canon_change_proposals(book_id, created_at, id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_canon_change_proposals_book;
        DROP TABLE IF EXISTS canon_change_proposals;
        """
    )
