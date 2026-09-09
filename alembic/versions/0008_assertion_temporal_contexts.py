"""Persist explicit temporal context for assertions."""

from alembic import op

revision = "0008_assertion_temporal_contexts"
down_revision = "0007_canonical_fact_embeddings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS assertion_temporal_contexts (
            assertion_id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            position INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT ck_assertion_temporal_context_kind
                CHECK (kind IN ('timeless', 'story_point')),
            CONSTRAINT ck_assertion_temporal_context_position
                CHECK (kind = 'timeless' OR position IS NOT NULL)
        );
        CREATE INDEX IF NOT EXISTS ix_assertion_temporal_context_position
            ON assertion_temporal_contexts(position);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS ix_assertion_temporal_context_position;
        DROP TABLE IF EXISTS assertion_temporal_contexts;
        """
    )
