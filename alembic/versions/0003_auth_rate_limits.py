"""Add persistent authentication rate-limit buckets.

Revision ID: 0003_auth_rate_limits
Revises: 0002_billing_capacity
"""

from alembic import op

revision = "0003_auth_rate_limits"
down_revision = "0002_billing_capacity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_rate_limits (
            rate_key TEXT PRIMARY KEY,
            window_start TIMESTAMPTZ NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_rate_limits;")
