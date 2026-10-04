from __future__ import annotations

import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.ingestion.cms_carrier import ingest_carrier_zip


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest a CMS DE-SynPUF Carrier Claims ZIP file."
    )
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--sample-number", type=int, default=2)
    parser.add_argument("--commit-interval", type=int, default=500)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    with SessionLocal() as session:
        batch = ingest_carrier_zip(
            session,
            args.zip_path,
            sample_number=args.sample_number,
            commit_interval=args.commit_interval,
        )

    print(f"Batch: {batch.id}")
    print(f"Status: {batch.status}")
    print(f"Rows seen: {batch.rows_seen}")
    print(f"Rows accepted: {batch.rows_accepted}")
    print(f"Rows rejected: {batch.rows_rejected}")
    print(f"Claim lines loaded: {batch.claim_lines_loaded}")


if __name__ == "__main__":
    main()
