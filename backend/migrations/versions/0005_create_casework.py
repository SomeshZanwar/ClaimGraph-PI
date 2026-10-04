"""Create investigation case and evidence tables.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS casework")

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_key", sa.String(length=128), nullable=False),
        sa.Column("claim_record_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority_score", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("priority_band", sa.String(length=16), nullable=False),
        sa.Column("financial_exposure", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("strongest_signal", sa.String(length=160), nullable=True),
        sa.Column("current_evidence_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_key", name="uq_casework_case_key"),
        schema="casework",
    )
    op.create_index(
        "ix_casework_claim",
        "cases",
        ["claim_record_id"],
        schema="casework",
    )
    op.create_index(
        "ix_casework_status_priority",
        "cases",
        ["status", "priority_score"],
        schema="casework",
    )

    op.create_table(
        "case_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["casework.cases.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "case_id",
            "evidence_hash",
            name="uq_casework_case_evidence_hash",
        ),
        schema="casework",
    )
    op.create_index(
        "ix_casework_evidence_case",
        "case_evidence",
        ["case_id"],
        schema="casework",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_casework_evidence_case",
        table_name="case_evidence",
        schema="casework",
    )
    op.drop_table("case_evidence", schema="casework")
    op.drop_index(
        "ix_casework_status_priority",
        table_name="cases",
        schema="casework",
    )
    op.drop_index(
        "ix_casework_claim",
        table_name="cases",
        schema="casework",
    )
    op.drop_table("cases", schema="casework")
    op.execute("DROP SCHEMA IF EXISTS casework")
