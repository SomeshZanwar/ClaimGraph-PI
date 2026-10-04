import csv
import io
import zipfile
from pathlib import Path

from app.ingestion.cms_carrier import iter_carrier_rows


def test_iter_carrier_rows_reads_single_csv_from_zip(tmp_path: Path) -> None:
    zip_path = tmp_path / "carrier.zip"

    csv_buffer = io.StringIO()
    writer = csv.DictWriter(
        csv_buffer,
        fieldnames=[
            "DESYNPUF_ID",
            "CLM_ID",
            "CLM_FROM_DT",
            "CLM_THRU_DT",
        ],
    )
    writer.writeheader()
    writer.writerow(
        {
            "DESYNPUF_ID": "BENE001",
            "CLM_ID": "CLAIM001",
            "CLM_FROM_DT": "20090101",
            "CLM_THRU_DT": "20090103",
        }
    )

    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("carrier.csv", csv_buffer.getvalue())

    rows = list(iter_carrier_rows(zip_path))

    assert len(rows) == 1
    row_number, row = rows[0]
    assert row_number == 2
    assert row["CLM_ID"] == "CLAIM001"
