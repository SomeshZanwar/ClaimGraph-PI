"""Create graph projection metadata tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS graph_meta")

    op.create_table(
        "graph_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("projected_rows", sa.BigInteger(), nullable=False),
        sa.Column("provider_nodes", sa.BigInteger(), nullable=False),
        sa.Column("member_nodes", sa.BigInteger(), nullable=False),
        sa.Column("claim_nodes", sa.BigInteger(), nullable=False),
        sa.Column("procedure_nodes", sa.BigInteger(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="graph_meta",
    )
    op.create_index(
        "ix_graph_meta_run_status",
        "graph_runs",
        ["status"],
        schema="graph_meta",
    )

    op.create_table(
        "provider_graph_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("graph_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_npi", sa.String(length=32), nullable=False),
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column("shared_provider_count", sa.Integer(), nullable=False),
        sa.Column("max_shared_members_with_peer", sa.Integer(), nullable=False),
        sa.Column("component_provider_count", sa.Integer(), nullable=False),
        sa.Column("component_member_count", sa.Integer(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["graph_run_id"],
            ["graph_meta.graph_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "graph_run_id",
            "provider_npi",
            name="uq_provider_graph_metric_run_provider",
        ),
        schema="graph_meta",
    )
    op.create_index(
        "ix_graph_metric_provider",
        "provider_graph_metrics",
        ["provider_npi"],
        schema="graph_meta",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_graph_metric_provider",
        table_name="provider_graph_metrics",
        schema="graph_meta",
    )
    op.drop_table("provider_graph_metrics", schema="graph_meta")
    op.drop_index(
        "ix_graph_meta_run_status",
        table_name="graph_runs",
        schema="graph_meta",
    )
    op.drop_table("graph_runs", schema="graph_meta")
    op.execute("DROP SCHEMA IF EXISTS graph_meta")
