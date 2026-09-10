"""Add durable PostgreSQL-backed analysis jobs.

Revision ID: 0009_analysis_jobs
Revises: 0008_assertion_temporal_contexts
"""

from alembic import op
import sqlalchemy as sa


revision = "0009_analysis_jobs"
down_revision = "0008_assertion_temporal_contexts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("book_id", sa.Text(), nullable=False),
        sa.Column("owner_id", sa.Text(), nullable=False),
        sa.Column("analysis_type", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_step", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("available_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("failed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("lease_until", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("worker_id", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("book_id", "analysis_type", "idempotency_key", name="uq_analysis_job_idempotency"),
    )
    op.create_index(
        "idx_analysis_jobs_claim",
        "analysis_jobs",
        ["status", "available_at", "created_at"],
    )
    op.create_index(
        "idx_analysis_jobs_owner_created",
        "analysis_jobs",
        ["owner_id", "created_at"],
    )
    op.create_index(
        "idx_analysis_jobs_book_created",
        "analysis_jobs",
        ["book_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_analysis_jobs_book_created", table_name="analysis_jobs")
    op.drop_index("idx_analysis_jobs_owner_created", table_name="analysis_jobs")
    op.drop_index("idx_analysis_jobs_claim", table_name="analysis_jobs")
    op.drop_table("analysis_jobs")
