from __future__ import annotations

import argparse

from app.db.session import SessionLocal
from app.ml.claim_anomaly import train_and_score_claims


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train and score the ClaimGraph PI claim anomaly model."
    )
    parser.add_argument(
        "--contamination",
        type=float,
        default=0.05,
        help="Expected anomaly fraction for Isolation Forest.",
    )
    parser.add_argument(
        "--fixture-mode",
        action="store_true",
        help="Allow the tiny CI fixture to exercise the model pipeline.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    minimum_rows = 2 if args.fixture_mode else 50

    with SessionLocal() as session:
        run = train_and_score_claims(
            session,
            contamination=args.contamination,
            min_training_rows=minimum_rows,
        )

    print(f"Model run: {run.id}")
    print(f"Version: {run.model_version}")
    print(f"Status: {run.status}")
    print(f"Training rows: {run.training_row_count}")
    print(f"Anomaly threshold: {run.anomaly_threshold}")
    print(f"Artifact: {run.artifact_path}")


if __name__ == "__main__":
    main()
