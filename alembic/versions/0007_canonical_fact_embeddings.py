"""Persist semantic embeddings for canonical facts."""

from alembic import op

revision = "0007_canonical_fact_embeddings"
down_revision = "0006_canon_review_decisions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS canonical_fact_embeddings (
            fact_id TEXT PRIMARY KEY,
            embedding DOUBLE PRECISION[] NOT NULL,
            model TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS ix_canonical_fact_embeddings_model
            ON canonical_fact_embeddings(model);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_canonical_fact_embeddings_model;
        DROP TABLE IF EXISTS canonical_fact_embeddings;
        """
    )
