from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from sqlalchemy import delete

from app.db.models import IngestionBatch
from app.db.session import SessionLocal
from app.ingestion.cms_carrier import ingest_carrier_zip


def main() -> None:
    fixture = Path("data/samples/carrier_fixture.csv")
    if not fixture.exists():
        raise FileNotFoundError(fixture)

    with SessionLocal() as session:
        session.execute(
            delete(IngestionBatch).where(IngestionBatch.sample_number == 999)
        )
        session.commit()

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "carrier_fixture.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.write(fixture, arcname="carrier_fixture.csv")

            batch = ingest_carrier_zip(
                session,
                zip_path,
                sample_number=999,
                commit_interval=1,
            )

        print(
            f"Loaded fixture batch {batch.id}: "
            f"{batch.rows_accepted} accepted, {batch.rows_rejected} rejected"
        )


if __name__ == "__main__":
    main()
