"""Create authentication, audit, and case assignment tables.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email_normalized", name="uq_auth_user_email"),
        schema="auth",
    )
    op.create_index(
        "ix_auth_user_role",
        "users",
        ["role"],
        schema="auth",
    )

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_auth_session_token_hash"),
        schema="auth",
    )
    op.create_index(
        "ix_auth_session_user",
        "sessions",
        ["user_id"],
        schema="auth",
    )
    op.create_index(
        "ix_auth_session_expiry",
        "sessions",
        ["expires_at"],
        schema="auth",
    )

    op.create_table(
        "auth_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash", name="uq_auth_token_hash"),
        schema="auth",
    )
    op.create_index(
        "ix_auth_token_user_type",
        "auth_tokens",
        ["user_id", "token_type"],
        schema="auth",
    )
    op.create_index(
        "ix_auth_token_expiry",
        "auth_tokens",
        ["expires_at"],
        schema="auth",
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=96), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(length=160), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="audit",
    )
    op.create_index(
        "ix_audit_event_type_time",
        "events",
        ["event_type", "occurred_at"],
        schema="audit",
    )
    op.create_index(
        "ix_audit_resource",
        "events",
        ["resource_type", "resource_id"],
        schema="audit",
    )

    op.add_column(
        "cases",
        sa.Column(
            "assigned_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="casework",
    )
    op.create_foreign_key(
        "fk_casework_case_assigned_user",
        "cases",
        "users",
        ["assigned_user_id"],
        ["id"],
        source_schema="casework",
        referent_schema="auth",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_casework_case_assigned_user",
        "cases",
        schema="casework",
        type_="foreignkey",
    )
    op.drop_column("cases", "assigned_user_id", schema="casework")

    op.drop_index("ix_audit_resource", table_name="events", schema="audit")
    op.drop_index("ix_audit_event_type_time", table_name="events", schema="audit")
    op.drop_table("events", schema="audit")

    op.drop_index("ix_auth_token_expiry", table_name="auth_tokens", schema="auth")
    op.drop_index("ix_auth_token_user_type", table_name="auth_tokens", schema="auth")
    op.drop_table("auth_tokens", schema="auth")

    op.drop_index("ix_auth_session_expiry", table_name="sessions", schema="auth")
    op.drop_index("ix_auth_session_user", table_name="sessions", schema="auth")
    op.drop_table("sessions", schema="auth")

    op.drop_index("ix_auth_user_role", table_name="users", schema="auth")
    op.drop_table("users", schema="auth")

    op.execute("DROP SCHEMA IF EXISTS audit")
    op.execute("DROP SCHEMA IF EXISTS auth")
