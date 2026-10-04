"""Create raw ingestion tables.

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")

    op.create_table(
        "ingestion_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_name", sa.String(length=120), nullable=False),
        sa.Column("sample_number", sa.Integer(), nullable=True),
        sa.Column("source_filename", sa.String(length=255), nullable=False),
        sa.Column("source_sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_seen", sa.BigInteger(), nullable=False),
        sa.Column("rows_accepted", sa.BigInteger(), nullable=False),
        sa.Column("rows_rejected", sa.BigInteger(), nullable=False),
        sa.Column("claim_lines_loaded", sa.BigInteger(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_sha256",
            "source_filename",
            name="uq_ingestion_source_hash_file",
        ),
        schema="raw",
    )

    op.create_table(
        "carrier_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ingestion_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_row_number", sa.BigInteger(), nullable=False),
        sa.Column("beneficiary_id", sa.String(length=32), nullable=False),
        sa.Column("claim_id", sa.String(length=32), nullable=False),
        sa.Column("claim_from_date", sa.Date(), nullable=True),
        sa.Column("claim_through_date", sa.Date(), nullable=True),
        sa.Column("diagnosis_codes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingestion_batch_id"],
            ["raw.ingestion_batches.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ingestion_batch_id",
            "source_row_number",
            name="uq_carrier_claim_batch_row",
        ),
        schema="raw",
    )
    op.create_index(
        "ix_raw_carrier_claim_id",
        "carrier_claims",
        ["claim_id"],
        schema="raw",
    )
    op.create_index(
        "ix_raw_carrier_beneficiary_id",
        "carrier_claims",
        ["beneficiary_id"],
        schema="raw",
    )

    op.create_table(
        "carrier_claim_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("claim_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("provider_npi", sa.String(length=32), nullable=True),
        sa.Column("tax_number", sa.String(length=32), nullable=True),
        sa.Column("hcpcs_code", sa.String(length=16), nullable=True),
        sa.Column("payment_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("deductible_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("primary_payer_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("coinsurance_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("allowed_charge_amount", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("processing_indicator_code", sa.String(length=8), nullable=True),
        sa.Column("diagnosis_code", sa.String(length=16), nullable=True),
        sa.ForeignKeyConstraint(
            ["claim_record_id"],
            ["raw.carrier_claims.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "claim_record_id",
            "line_number",
            name="uq_carrier_claim_line",
        ),
        schema="raw",
    )
    op.create_index(
        "ix_raw_carrier_line_provider",
        "carrier_claim_lines",
        ["provider_npi"],
        schema="raw",
    )
    op.create_index(
        "ix_raw_carrier_line_hcpcs",
        "carrier_claim_lines",
        ["hcpcs_code"],
        schema="raw",
    )

    op.create_table(
        "rejected_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ingestion_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_row_number", sa.BigInteger(), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=False),
        sa.Column("source_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["ingestion_batch_id"],
            ["raw.ingestion_batches.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="raw",
    )
    op.create_index(
        "ix_raw_rejected_batch",
        "rejected_records",
        ["ingestion_batch_id"],
        schema="raw",
    )


def downgrade() -> None:
    op.drop_index("ix_raw_rejected_batch", table_name="rejected_records", schema="raw")
    op.drop_table("rejected_records", schema="raw")
    op.drop_index("ix_raw_carrier_line_hcpcs", table_name="carrier_claim_lines", schema="raw")
    op.drop_index("ix_raw_carrier_line_provider", table_name="carrier_claim_lines", schema="raw")
    op.drop_table("carrier_claim_lines", schema="raw")
    op.drop_index("ix_raw_carrier_beneficiary_id", table_name="carrier_claims", schema="raw")
    op.drop_index("ix_raw_carrier_claim_id", table_name="carrier_claims", schema="raw")
    op.drop_table("carrier_claims", schema="raw")
    op.drop_table("ingestion_batches", schema="raw")
    op.execute("DROP SCHEMA IF EXISTS raw")
