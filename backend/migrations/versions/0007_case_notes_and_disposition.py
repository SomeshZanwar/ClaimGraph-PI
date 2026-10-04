"""Add investigator case notes and dispositions.

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column("disposition", sa.String(length=64), nullable=True),
        schema="casework",
    )

    op.create_table(
        "case_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["casework.cases.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["author_user_id"],
            ["auth.users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="casework",
    )
    op.create_index(
        "ix_casework_note_case_time",
        "case_notes",
        ["case_id", "created_at"],
        schema="casework",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_casework_note_case_time",
        table_name="case_notes",
        schema="casework",
    )
    op.drop_table("case_notes", schema="casework")
    op.drop_column("cases", "disposition", schema="casework")
