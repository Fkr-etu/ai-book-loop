"""Add persistent authentication rate-limit events.

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
        CREATE TABLE IF NOT EXISTS auth_rate_limit_events (
            id BIGSERIAL PRIMARY KEY,
            rate_key TEXT NOT NULL,
            attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS ix_auth_rate_limit_events_key_time
            ON auth_rate_limit_events(rate_key, attempted_at);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS auth_rate_limit_events;")
