"""Persist subscription plans and atomic workflow usage reservations.

Revision ID: 0002_billing_capacity
Revises: 0001_initial_postgresql
"""

from alembic import op

revision = "0002_billing_capacity"
down_revision = "0001_initial_postgresql"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS plan TEXT NOT NULL DEFAULT 'free';

        CREATE TABLE IF NOT EXISTS workflow_usage (
            user_id TEXT NOT NULL,
            period_start DATE NOT NULL,
            idempotency_key TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, period_start, idempotency_key)
        );

        CREATE INDEX IF NOT EXISTS ix_workflow_usage_user_period
            ON workflow_usage(user_id, period_start);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS workflow_usage;
        ALTER TABLE users DROP COLUMN IF EXISTS plan;
        """
    )
