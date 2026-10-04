from __future__ import annotations

import csv
import hashlib
import io
import uuid
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    IngestionBatch,
    RawCarrierClaim,
    RawCarrierClaimLine,
    RejectedRecord,
)

REQUIRED_COLUMNS = {
    "DESYNPUF_ID",
    "CLM_ID",
    "CLM_FROM_DT",
    "CLM_THRU_DT",
}

LINE_COUNT = 13


@dataclass(frozen=True)
class ParsedLine:
    line_number: int
    provider_npi: str | None
    tax_number: str | None
    hcpcs_code: str | None
    payment_amount: Decimal | None
    deductible_amount: Decimal | None
    primary_payer_amount: Decimal | None
    coinsurance_amount: Decimal | None
    allowed_charge_amount: Decimal | None
    processing_indicator_code: str | None
    diagnosis_code: str | None


@dataclass(frozen=True)
class ParsedClaim:
    beneficiary_id: str
    claim_id: str
    claim_from_date: date | None
    claim_through_date: date | None
    diagnosis_codes: list[str]
    lines: list[ParsedLine]


class CarrierRowError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def parse_date(value: str | None, field_name: str) -> date | None:
    normalized = normalize_text(value)
    if normalized is None:
        return None

    try:
        return datetime.strptime(normalized, "%Y%m%d").date()
    except ValueError as exc:
        raise CarrierRowError(
            "INVALID_DATE",
            f"{field_name} must use YYYYMMDD format: {normalized}",
        ) from exc


def parse_decimal(value: str | None, field_name: str) -> Decimal | None:
    normalized = normalize_text(value)
    if normalized is None:
        return None

    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise CarrierRowError(
            "INVALID_DECIMAL",
            f"{field_name} is not a valid decimal: {normalized}",
        ) from exc


def parse_carrier_row(row: dict[str, str | None]) -> ParsedClaim:
    missing_columns = REQUIRED_COLUMNS.difference(row.keys())
    if missing_columns:
        raise CarrierRowError(
            "MISSING_COLUMNS",
            f"Missing required columns: {', '.join(sorted(missing_columns))}",
        )

    beneficiary_id = normalize_text(row.get("DESYNPUF_ID"))
    claim_id = normalize_text(row.get("CLM_ID"))

    if beneficiary_id is None:
        raise CarrierRowError("MISSING_BENEFICIARY_ID", "DESYNPUF_ID is required")

    if claim_id is None:
        raise CarrierRowError("MISSING_CLAIM_ID", "CLM_ID is required")

    claim_from_date = parse_date(row.get("CLM_FROM_DT"), "CLM_FROM_DT")
    claim_through_date = parse_date(row.get("CLM_THRU_DT"), "CLM_THRU_DT")

    if (
        claim_from_date is not None
        and claim_through_date is not None
        and claim_from_date > claim_through_date
    ):
        raise CarrierRowError(
            "INVALID_DATE_RANGE",
            "CLM_FROM_DT cannot be after CLM_THRU_DT",
        )

    diagnosis_codes = [
        code
        for index in range(1, 9)
        if (code := normalize_text(row.get(f"ICD9_DGNS_CD_{index}"))) is not None
    ]

    lines: list[ParsedLine] = []
    for index in range(1, LINE_COUNT + 1):
        line = ParsedLine(
            line_number=index,
            provider_npi=normalize_text(row.get(f"PRF_PHYSN_NPI_{index}")),
            tax_number=normalize_text(row.get(f"TAX_NUM_{index}")),
            hcpcs_code=normalize_text(row.get(f"HCPCS_CD_{index}")),
            payment_amount=parse_decimal(
                row.get(f"LINE_NCH_PMT_AMT_{index}"),
                f"LINE_NCH_PMT_AMT_{index}",
            ),
            deductible_amount=parse_decimal(
                row.get(f"LINE_BENE_PTB_DDCTBL_AMT_{index}"),
                f"LINE_BENE_PTB_DDCTBL_AMT_{index}",
            ),
            primary_payer_amount=parse_decimal(
                row.get(f"LINE_BENE_PRMRY_PYR_PD_AMT_{index}"),
                f"LINE_BENE_PRMRY_PYR_PD_AMT_{index}",
            ),
            coinsurance_amount=parse_decimal(
                row.get(f"LINE_COINSRNC_AMT_{index}"),
                f"LINE_COINSRNC_AMT_{index}",
            ),
            allowed_charge_amount=parse_decimal(
                row.get(f"LINE_ALOWD_CHRG_AMT_{index}"),
                f"LINE_ALOWD_CHRG_AMT_{index}",
            ),
            processing_indicator_code=normalize_text(
                row.get(f"LINE_PRCSG_IND_CD_{index}")
            ),
            diagnosis_code=normalize_text(row.get(f"LINE_ICD9_DGNS_CD_{index}")),
        )

        if any(
            value is not None
            for value in (
                line.provider_npi,
                line.tax_number,
                line.hcpcs_code,
                line.payment_amount,
                line.deductible_amount,
                line.primary_payer_amount,
                line.coinsurance_amount,
                line.allowed_charge_amount,
                line.processing_indicator_code,
                line.diagnosis_code,
            )
        ):
            lines.append(line)

    return ParsedClaim(
        beneficiary_id=beneficiary_id,
        claim_id=claim_id,
        claim_from_date=claim_from_date,
        claim_through_date=claim_through_date,
        diagnosis_codes=diagnosis_codes,
        lines=lines,
    )


def _select_csv_member(archive: zipfile.ZipFile) -> str:
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.lower().endswith(".csv")
    ]

    if not candidates:
        candidates = [
            name
            for name in archive.namelist()
            if not name.endswith("/")
        ]

    if len(candidates) != 1:
        raise ValueError(
            f"Expected exactly one data file in ZIP archive, found {len(candidates)}"
        )

    return candidates[0]


def iter_carrier_rows(zip_path: Path) -> Iterator[tuple[int, dict[str, str | None]]]:
    with zipfile.ZipFile(zip_path) as archive:
        member = _select_csv_member(archive)

        with archive.open(member, "r") as raw_handle:
            with io.TextIOWrapper(raw_handle, encoding="utf-8-sig", newline="") as text_handle:
                reader = csv.DictReader(text_handle)

                if reader.fieldnames is None:
                    raise ValueError("Carrier CSV is missing a header row")

                missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames)
                if missing_columns:
                    raise ValueError(
                        "Carrier CSV missing required columns: "
                        + ", ".join(sorted(missing_columns))
                    )

                for source_row_number, row in enumerate(reader, start=2):
                    yield source_row_number, row


def ingest_carrier_zip(
    session: Session,
    zip_path: Path,
    *,
    sample_number: int = 2,
    commit_interval: int = 500,
) -> IngestionBatch:
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)

    source_hash = sha256_file(zip_path)
    existing = session.scalar(
        select(IngestionBatch).where(
            IngestionBatch.source_sha256 == source_hash,
            IngestionBatch.source_filename == zip_path.name,
        )
    )
    if existing is not None:
        raise ValueError(
            f"Source file already ingested as batch {existing.id}: {zip_path.name}"
        )

    batch = IngestionBatch(
        dataset_name="CMS DE-SynPUF Carrier Claims",
        sample_number=sample_number,
        source_filename=zip_path.name,
        source_sha256=source_hash,
        status="STARTED",
        started_at=datetime.now(timezone.utc),
    )
    session.add(batch)
    session.commit()

    rows_since_commit = 0

    try:
        for source_row_number, row in iter_carrier_rows(zip_path):
            batch.rows_seen += 1

            try:
                parsed = parse_carrier_row(row)
            except CarrierRowError as exc:
                session.add(
                    RejectedRecord(
                        ingestion_batch_id=batch.id,
                        source_row_number=source_row_number,
                        reason_code=exc.code,
                        reason_detail=exc.detail,
                        source_payload=row,
                    )
                )
                batch.rows_rejected += 1
            else:
                claim_record_id = uuid.uuid4()
                claim = RawCarrierClaim(
                    id=claim_record_id,
                    ingestion_batch_id=batch.id,
                    source_row_number=source_row_number,
                    beneficiary_id=parsed.beneficiary_id,
                    claim_id=parsed.claim_id,
                    claim_from_date=parsed.claim_from_date,
                    claim_through_date=parsed.claim_through_date,
                    diagnosis_codes=parsed.diagnosis_codes,
                )
                session.add(claim)

                for line in parsed.lines:
                    session.add(
                        RawCarrierClaimLine(
                            claim_record_id=claim_record_id,
                            line_number=line.line_number,
                            provider_npi=line.provider_npi,
                            tax_number=line.tax_number,
                            hcpcs_code=line.hcpcs_code,
                            payment_amount=line.payment_amount,
                            deductible_amount=line.deductible_amount,
                            primary_payer_amount=line.primary_payer_amount,
                            coinsurance_amount=line.coinsurance_amount,
                            allowed_charge_amount=line.allowed_charge_amount,
                            processing_indicator_code=line.processing_indicator_code,
                            diagnosis_code=line.diagnosis_code,
                        )
                    )

                batch.rows_accepted += 1
                batch.claim_lines_loaded += len(parsed.lines)

            rows_since_commit += 1
            if rows_since_commit >= commit_interval:
                session.commit()
                rows_since_commit = 0

        batch.status = "COMPLETED"
        batch.completed_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(batch)
        return batch
    except Exception as exc:
        session.rollback()

        failed_batch = session.get(IngestionBatch, batch.id)
        if failed_batch is not None:
            failed_batch.status = "FAILED"
            failed_batch.completed_at = datetime.now(timezone.utc)
            failed_batch.error_message = str(exc)[:2000]
            session.commit()
        raise
