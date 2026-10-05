from __future__ import annotations

import subprocess
from pathlib import Path

from app.casework.composer import compose_cases
from app.config import get_settings
from app.db.models import IngestionBatch
from app.db.session import SessionLocal
from app.graph.analytics import analyze_graph
from app.graph.projection import project_graph
from app.ingestion.cms_carrier import ingest_carrier_zip, sha256_file
from app.ml.claim_anomaly import train_and_score_claims
from app.risk.engine import load_rule_definitions, run_rules
from generate_demo_fixture import write_demo_zip
from neo4j import GraphDatabase
from sqlalchemy import select


def run_dbt() -> None:
    subprocess.run(
        [
            "dbt",
            "build",
            "--project-dir",
            "dbt",
            "--profiles-dir",
            "dbt",
        ],
        check=True,
    )


def ensure_demo_ingested(zip_path: Path) -> None:
    digest = sha256_file(zip_path)
    with SessionLocal() as session:
        existing = session.scalar(
            select(IngestionBatch).where(
                IngestionBatch.source_sha256 == digest,
                IngestionBatch.source_filename == zip_path.name,
                IngestionBatch.status == "COMPLETED",
            )
        )
        if existing is not None:
            print(f"Demo batch already ingested: {existing.id}")
            return

        batch = ingest_carrier_zip(
            session,
            zip_path,
            sample_number=998,
            commit_interval=100,
        )
        print(
            f"Ingested demo batch {batch.id}: "
            f"{batch.rows_accepted} accepted, {batch.rows_rejected} rejected"
        )


def main() -> None:
    settings = get_settings()
    zip_path = write_demo_zip(Path("/tmp/claimgraph_demo_carrier.zip"), count=300)
    ensure_demo_ingested(zip_path)

    run_dbt()

    with SessionLocal() as session:
        rule_run = run_rules(session, load_rule_definitions())
        print(f"Generated {rule_run.signal_count} deterministic signals")

    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        driver.verify_connectivity()
        with SessionLocal() as session:
            graph_run = project_graph(session, driver, replace=True)
            metrics = analyze_graph(session, driver, graph_run)
            print(f"Projected graph with {len(metrics)} provider metric rows")

    with SessionLocal() as session:
        model_run = train_and_score_claims(
            session,
            contamination=0.05,
            min_training_rows=50,
        )
        print(
            f"Trained {model_run.model_version} on "
            f"{model_run.training_row_count} claim rows"
        )

    with SessionLocal() as session:
        cases = compose_cases(session)
        print(f"Composed {len(cases)} investigation cases")

    print("ClaimGraph PI demonstration bootstrap completed.")


if __name__ == "__main__":
    main()
