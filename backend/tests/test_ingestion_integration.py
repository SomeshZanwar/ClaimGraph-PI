import zipfile
from pathlib import Path

from sqlalchemy import select

from app.db.models import IngestionBatch, RawCarrierClaim, RejectedRecord
from app.db.session import SessionLocal
from app.ingestion.cms_carrier import ingest_carrier_zip


def test_ingest_carrier_zip_persists_claims_and_rejections(tmp_path: Path) -> None:
    fixture = Path("data/samples/carrier_fixture.csv")
    zip_path = tmp_path / "carrier_fixture.zip"

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(fixture, arcname="carrier_fixture.csv")

    with SessionLocal() as session:
        batch = ingest_carrier_zip(
            session,
            zip_path,
            sample_number=999,
            commit_interval=1,
        )

        assert batch.status == "COMPLETED"
        assert batch.rows_seen == 3
        assert batch.rows_accepted == 2
        assert batch.rows_rejected == 1
        assert batch.claim_lines_loaded == 2

        claims = session.scalars(
            select(RawCarrierClaim).where(
                RawCarrierClaim.ingestion_batch_id == batch.id
            )
        ).all()
        rejected = session.scalars(
            select(RejectedRecord).where(
                RejectedRecord.ingestion_batch_id == batch.id
            )
        ).all()

        assert {claim.claim_id for claim in claims} == {"SYNCLM001", "SYNCLM002"}
        assert len(rejected) == 1
        assert rejected[0].reason_code == "INVALID_DATE_RANGE"

        session.delete(session.get(IngestionBatch, batch.id))
        session.commit()
