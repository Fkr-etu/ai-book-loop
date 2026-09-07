"""Persist Stripe customer/subscription state and webhook idempotency."""

from alembic import op

revision = "0004_stripe_billing"
down_revision = "0003_auth_rate_limits"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT;
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS subscription_status TEXT NOT NULL DEFAULT 'inactive';
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS subscription_current_period_end TIMESTAMPTZ;
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS subscription_cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE;

        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_stripe_customer_id
            ON users(stripe_customer_id)
            WHERE stripe_customer_id IS NOT NULL;
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_stripe_subscription_id
            ON users(stripe_subscription_id)
            WHERE stripe_subscription_id IS NOT NULL;

        CREATE TABLE IF NOT EXISTS stripe_webhook_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS stripe_webhook_events;
        DROP INDEX IF EXISTS ux_users_stripe_subscription_id;
        DROP INDEX IF EXISTS ux_users_stripe_customer_id;
        ALTER TABLE users DROP COLUMN IF EXISTS subscription_cancel_at_period_end;
        ALTER TABLE users DROP COLUMN IF EXISTS subscription_current_period_end;
        ALTER TABLE users DROP COLUMN IF EXISTS subscription_status;
        ALTER TABLE users DROP COLUMN IF EXISTS stripe_subscription_id;
        ALTER TABLE users DROP COLUMN IF EXISTS stripe_customer_id;
        """
    )
