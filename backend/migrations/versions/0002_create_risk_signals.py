"""Create deterministic risk rule tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS risk")

    op.create_table(
        "rule_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ruleset_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signal_count", sa.BigInteger(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="risk",
    )
    op.create_index(
        "ix_risk_rule_run_status",
        "rule_runs",
        ["status"],
        schema="risk",
    )

    op.create_table(
        "risk_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("rule_version", sa.String(length=32), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", sa.String(length=160), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("threshold_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["rule_run_id"],
            ["risk.rule_runs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="risk",
    )
    op.create_index(
        "ix_risk_signal_rule",
        "risk_signals",
        ["rule_id", "rule_version"],
        schema="risk",
    )
    op.create_index(
        "ix_risk_signal_entity",
        "risk_signals",
        ["entity_type", "entity_id"],
        schema="risk",
    )
    op.create_index(
        "ix_risk_signal_severity",
        "risk_signals",
        ["severity"],
        schema="risk",
    )


def downgrade() -> None:
    op.drop_index("ix_risk_signal_severity", table_name="risk_signals", schema="risk")
    op.drop_index("ix_risk_signal_entity", table_name="risk_signals", schema="risk")
    op.drop_index("ix_risk_signal_rule", table_name="risk_signals", schema="risk")
    op.drop_table("risk_signals", schema="risk")
    op.drop_index("ix_risk_rule_run_status", table_name="rule_runs", schema="risk")
    op.drop_table("rule_runs", schema="risk")
    op.execute("DROP SCHEMA IF EXISTS risk")
