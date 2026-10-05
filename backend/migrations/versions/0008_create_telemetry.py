"""Create privacy-safe product telemetry.

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS telemetry")
    op.create_table(
        "product_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_name", sa.String(length=64), nullable=False),
        sa.Column("route", sa.String(length=256), nullable=False),
        sa.Column("actor_hash", sa.String(length=64), nullable=True),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="telemetry",
    )
    op.create_index(
        "ix_telemetry_event_time",
        "product_events",
        ["event_name", "occurred_at"],
        schema="telemetry",
    )
    op.create_index(
        "ix_telemetry_route_time",
        "product_events",
        ["route", "occurred_at"],
        schema="telemetry",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_telemetry_route_time",
        table_name="product_events",
        schema="telemetry",
    )
    op.drop_index(
        "ix_telemetry_event_time",
        table_name="product_events",
        schema="telemetry",
    )
    op.drop_table("product_events", schema="telemetry")
    op.execute("DROP SCHEMA IF EXISTS telemetry")
