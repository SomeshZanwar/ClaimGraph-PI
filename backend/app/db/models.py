from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IngestionBatch(Base):
    __tablename__ = "ingestion_batches"
    __table_args__ = (
        UniqueConstraint(
            "source_sha256",
            "source_filename",
            name="uq_ingestion_source_hash_file",
        ),
        {"schema": "raw"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    dataset_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sample_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="STARTED")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    rows_seen: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    rows_accepted: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    claim_lines_loaded: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    claims: Mapped[list[RawCarrierClaim]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class RawCarrierClaim(Base):
    __tablename__ = "carrier_claims"
    __table_args__ = (
        UniqueConstraint(
            "ingestion_batch_id",
            "source_row_number",
            name="uq_carrier_claim_batch_row",
        ),
        Index("ix_raw_carrier_claim_id", "claim_id"),
        Index("ix_raw_carrier_beneficiary_id", "beneficiary_id"),
        {"schema": "raw"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ingestion_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw.ingestion_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_row_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    beneficiary_id: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_id: Mapped[str] = mapped_column(String(32), nullable=False)
    claim_from_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    claim_through_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    diagnosis_codes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    batch: Mapped[IngestionBatch] = relationship(back_populates="claims")
    lines: Mapped[list[RawCarrierClaimLine]] = relationship(
        back_populates="claim",
        cascade="all, delete-orphan",
    )


class RawCarrierClaimLine(Base):
    __tablename__ = "carrier_claim_lines"
    __table_args__ = (
        UniqueConstraint(
            "claim_record_id",
            "line_number",
            name="uq_carrier_claim_line",
        ),
        Index("ix_raw_carrier_line_provider", "provider_npi"),
        Index("ix_raw_carrier_line_hcpcs", "hcpcs_code"),
        {"schema": "raw"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    claim_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw.carrier_claims.id", ondelete="CASCADE"),
        nullable=False,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    provider_npi: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tax_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    hcpcs_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    payment_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    deductible_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    primary_payer_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    coinsurance_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    allowed_charge_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    processing_indicator_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    diagnosis_code: Mapped[str | None] = mapped_column(String(16), nullable=True)

    claim: Mapped[RawCarrierClaim] = relationship(back_populates="lines")


class RejectedRecord(Base):
    __tablename__ = "rejected_records"
    __table_args__ = (
        Index("ix_raw_rejected_batch", "ingestion_batch_id"),
        {"schema": "raw"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ingestion_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("raw.ingestion_batches.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_row_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_detail: Mapped[str] = mapped_column(Text, nullable=False)
    source_payload: Mapped[dict[str, str | None]] = mapped_column(JSONB, nullable=False)


class RuleRun(Base):
    __tablename__ = "rule_runs"
    __table_args__ = (
        Index("ix_risk_rule_run_status", "status"),
        {"schema": "risk"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ruleset_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="STARTED")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    signal_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    signals: Mapped[list[RiskSignal]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class RiskSignal(Base):
    __tablename__ = "risk_signals"
    __table_args__ = (
        Index("ix_risk_signal_rule", "rule_id", "rule_version"),
        Index("ix_risk_signal_entity", "entity_type", "entity_id"),
        Index("ix_risk_signal_severity", "severity"),
        {"schema": "risk"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    rule_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk.rule_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(160), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    observed_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    threshold_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    run: Mapped[RuleRun] = relationship(back_populates="signals")


class GraphRun(Base):
    __tablename__ = "graph_runs"
    __table_args__ = (
        Index("ix_graph_meta_run_status", "status"),
        {"schema": "graph_meta"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="STARTED")
    source_snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    projected_rows: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    provider_nodes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    member_nodes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    claim_nodes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    procedure_nodes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider_metrics: Mapped[list[ProviderGraphMetric]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class ProviderGraphMetric(Base):
    __tablename__ = "provider_graph_metrics"
    __table_args__ = (
        UniqueConstraint(
            "graph_run_id",
            "provider_npi",
            name="uq_provider_graph_metric_run_provider",
        ),
        Index("ix_graph_metric_provider", "provider_npi"),
        {"schema": "graph_meta"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    graph_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("graph_meta.graph_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_npi: Mapped[str] = mapped_column(String(32), nullable=False)
    member_count: Mapped[int] = mapped_column(Integer, nullable=False)
    shared_provider_count: Mapped[int] = mapped_column(Integer, nullable=False)
    max_shared_members_with_peer: Mapped[int] = mapped_column(Integer, nullable=False)
    component_provider_count: Mapped[int] = mapped_column(Integer, nullable=False)
    component_member_count: Mapped[int] = mapped_column(Integer, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    run: Mapped[GraphRun] = relationship(back_populates="provider_metrics")
