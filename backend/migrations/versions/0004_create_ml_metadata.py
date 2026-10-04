"""Create ML model run and claim score tables.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ml_meta")

    op.create_table(
        "model_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_version", sa.String(length=96), nullable=False),
        sa.Column("model_type", sa.String(length=64), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_row_count", sa.BigInteger(), nullable=False),
        sa.Column("contamination", sa.Numeric(precision=8, scale=6), nullable=False),
        sa.Column("anomaly_threshold", sa.Numeric(precision=18, scale=8), nullable=True),
        sa.Column("feature_names", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("artifact_path", sa.String(length=512), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_version", name="uq_ml_model_version"),
        schema="ml_meta",
    )
    op.create_index(
        "ix_ml_model_run_status",
        "model_runs",
        ["status"],
        schema="ml_meta",
    )

    op.create_table(
        "claim_model_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("claim_record_id", sa.String(length=64), nullable=False),
        sa.Column("anomaly_score", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("is_anomaly", sa.Boolean(), nullable=False),
        sa.Column(
            "feature_deviation_context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["model_run_id"],
            ["ml_meta.model_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "model_run_id",
            "claim_record_id",
            name="uq_ml_score_run_claim",
        ),
        schema="ml_meta",
    )
    op.create_index(
        "ix_ml_score_claim",
        "claim_model_scores",
        ["claim_record_id"],
        schema="ml_meta",
    )
    op.create_index(
        "ix_ml_score_anomaly",
        "claim_model_scores",
        ["is_anomaly"],
        schema="ml_meta",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ml_score_anomaly",
        table_name="claim_model_scores",
        schema="ml_meta",
    )
    op.drop_index(
        "ix_ml_score_claim",
        table_name="claim_model_scores",
        schema="ml_meta",
    )
    op.drop_table("claim_model_scores", schema="ml_meta")
    op.drop_index(
        "ix_ml_model_run_status",
        table_name="model_runs",
        schema="ml_meta",
    )
    op.drop_table("model_runs", schema="ml_meta")
    op.execute("DROP SCHEMA IF EXISTS ml_meta")
