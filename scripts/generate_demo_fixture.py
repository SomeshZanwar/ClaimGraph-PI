from __future__ import annotations

import csv
import random
import zipfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

HEADER = [
    "DESYNPUF_ID",
    "CLM_ID",
    "CLM_FROM_DT",
    "CLM_THRU_DT",
    "ICD9_DGNS_CD_1",
    "PRF_PHYSN_NPI_1",
    "TAX_NUM_1",
    "HCPCS_CD_1",
    "LINE_NCH_PMT_AMT_1",
    "LINE_BENE_PTB_DDCTBL_AMT_1",
    "LINE_BENE_PRMRY_PYR_PD_AMT_1",
    "LINE_COINSRNC_AMT_1",
    "LINE_ALOWD_CHRG_AMT_1",
    "LINE_PRCSG_IND_CD_1",
    "LINE_ICD9_DGNS_CD_1",
]

HCPCS = ["99213", "99214", "93000", "80061", "85025", "97110", "71020"]
DIAGNOSIS = ["25000", "4019", "2724", "7242", "41401", "53081"]


def money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"


def generate_rows(count: int = 300, seed: int = 20261004) -> list[dict[str, str]]:
    rng = random.Random(seed)
    rows: list[dict[str, str]] = []
    start = date(2009, 1, 1)

    for index in range(count):
        beneficiary = f"DEMO_BENE_{index % 90:04d}"
        provider = f"DEMO_NPI_{index % 24:04d}"
        procedure = HCPCS[index % len(HCPCS)]
        diagnosis = DIAGNOSIS[index % len(DIAGNOSIS)]
        service_date = start + timedelta(days=index % 180)
        allowed = Decimal(str(45 + (index % 14) * 13 + rng.randint(0, 18)))
        payment = allowed * Decimal("0.78")

        if index % 47 == 0:
            allowed *= Decimal("8.5")
            payment = allowed * Decimal("0.82")

        if index % 71 == 0:
            payment = allowed * Decimal("1.12")

        row = {
            "DESYNPUF_ID": beneficiary,
            "CLM_ID": f"DEMO_CLM_{index:06d}",
            "CLM_FROM_DT": service_date.strftime("%Y%m%d"),
            "CLM_THRU_DT": service_date.strftime("%Y%m%d"),
            "ICD9_DGNS_CD_1": diagnosis,
            "PRF_PHYSN_NPI_1": provider,
            "TAX_NUM_1": f"DEMO_TAX_{index % 12:03d}",
            "HCPCS_CD_1": procedure,
            "LINE_NCH_PMT_AMT_1": money(payment),
            "LINE_BENE_PTB_DDCTBL_AMT_1": money(Decimal("0")),
            "LINE_BENE_PRMRY_PYR_PD_AMT_1": money(Decimal("0")),
            "LINE_COINSRNC_AMT_1": money(allowed - payment),
            "LINE_ALOWD_CHRG_AMT_1": money(allowed),
            "LINE_PRCSG_IND_CD_1": "A",
            "LINE_ICD9_DGNS_CD_1": diagnosis,
        }
        rows.append(row)

        if index > 0 and index % 37 == 0:
            duplicate = dict(row)
            duplicate["CLM_ID"] = f"DEMO_CLM_DUP_{index:06d}"
            rows.append(duplicate)

    return rows


def write_demo_zip(output: Path, count: int = 300) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    csv_path = output.with_suffix(".csv")
    rows = generate_rows(count=count)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(csv_path, arcname="claimgraph_demo_carrier.csv")

    csv_path.unlink()
    return output


def main() -> None:
    output = write_demo_zip(Path("data/generated/claimgraph_demo_carrier.zip"))
    print(f"Wrote deterministic demo data to {output}")


if __name__ == "__main__":
    main()
