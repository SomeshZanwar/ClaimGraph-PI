from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from neo4j import Driver
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import GraphRun

CONSTRAINTS = (
    "CREATE CONSTRAINT claimgraph_member_id IF NOT EXISTS "
    "FOR (n:Member) REQUIRE n.member_id IS UNIQUE",
    "CREATE CONSTRAINT claimgraph_claim_id IF NOT EXISTS "
    "FOR (n:Claim) REQUIRE n.claim_record_id IS UNIQUE",
    "CREATE CONSTRAINT claimgraph_provider_id IF NOT EXISTS "
    "FOR (n:Provider) REQUIRE n.provider_npi IS UNIQUE",
    "CREATE CONSTRAINT claimgraph_procedure_id IF NOT EXISTS "
    "FOR (n:Procedure) REQUIRE n.hcpcs_code IS UNIQUE",
)

PROJECT_BATCH = """
UNWIND $rows AS row

MERGE (member:ClaimGraphManaged:Member {member_id: row.beneficiary_id})
MERGE (claim:ClaimGraphManaged:Claim {claim_record_id: row.claim_record_id})
SET claim.claim_id = row.claim_id,
    claim.claim_from_date = row.claim_from_date,
    claim.claim_through_date = row.claim_through_date
MERGE (member)-[:HAS_CLAIM]->(claim)

FOREACH (_ IN CASE WHEN row.provider_npi IS NULL THEN [] ELSE [1] END |
    MERGE (provider:ClaimGraphManaged:Provider {provider_npi: row.provider_npi})
    MERGE (claim)-[:BILLED_BY]->(provider)
)

FOREACH (_ IN CASE WHEN row.hcpcs_code IS NULL THEN [] ELSE [1] END |
    MERGE (procedure:ClaimGraphManaged:Procedure {hcpcs_code: row.hcpcs_code})
    MERGE (claim)-[:CONTAINS_PROCEDURE]->(procedure)
)
"""

SOURCE_ROWS_SQL = """
select
    claim_record_id,
    beneficiary_id,
    claim_id,
    claim_from_date,
    claim_through_date,
    provider_npi,
    hcpcs_code
from analytics.fact_claim_lines
order by claim_record_id, line_number
"""


def source_snapshot_hash(session: Session) -> str:
    rows = session.execute(
        text(
            """
            select source_sha256
            from raw.ingestion_batches
            where status = 'COMPLETED'
            order by source_sha256
            """
        )
    ).scalars()

    source_hashes = list(rows)
    if not source_hashes:
        raise RuntimeError("No completed ingestion batches are available for graph projection")

    digest = hashlib.sha256()
    for value in source_hashes:
        digest.update(value.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _neo4j_value(value: Any) -> Any:
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def ensure_graph_constraints(driver: Driver) -> None:
    with driver.session() as neo_session:
        for statement in CONSTRAINTS:
            neo_session.run(statement).consume()


def clear_managed_graph(driver: Driver) -> None:
    with driver.session() as neo_session:
        neo_session.run(
            "MATCH (n:ClaimGraphManaged) DETACH DELETE n"
        ).consume()


def project_graph(
    session: Session,
    driver: Driver,
    *,
    replace: bool = False,
    batch_size: int = 1000,
) -> GraphRun:
    snapshot_hash = source_snapshot_hash(session)
    run = GraphRun(
        status="STARTED",
        source_snapshot_hash=snapshot_hash,
        started_at=datetime.now(UTC),
    )
    session.add(run)
    session.commit()

    try:
        ensure_graph_constraints(driver)
        if replace:
            clear_managed_graph(driver)

        result = session.execute(text(SOURCE_ROWS_SQL))
        projected_rows = 0

        with driver.session() as neo_session:
            for partition in result.mappings().partitions(batch_size):
                payload = [
                    {key: _neo4j_value(value) for key, value in dict(row).items()}
                    for row in partition
                ]
                if not payload:
                    continue
                neo_session.run(PROJECT_BATCH, rows=payload).consume()
                projected_rows += len(payload)

        with driver.session() as neo_session:
            counts = neo_session.run(
                """
                MATCH (n:ClaimGraphManaged)
                RETURN
                    count(CASE WHEN n:Provider THEN 1 END) AS providers,
                    count(CASE WHEN n:Member THEN 1 END) AS members,
                    count(CASE WHEN n:Claim THEN 1 END) AS claims,
                    count(CASE WHEN n:Procedure THEN 1 END) AS procedures
                """
            ).single(strict=True)

        run.projected_rows = projected_rows
        run.provider_nodes = int(counts["providers"])
        run.member_nodes = int(counts["members"])
        run.claim_nodes = int(counts["claims"])
        run.procedure_nodes = int(counts["procedures"])
        run.status = "COMPLETED"
        run.completed_at = datetime.now(UTC)
        session.commit()
        session.refresh(run)
        return run
    except Exception as exc:
        session.rollback()
        failed_run = session.get(GraphRun, run.id)
        if failed_run is not None:
            failed_run.status = "FAILED"
            failed_run.completed_at = datetime.now(UTC)
            failed_run.error_message = str(exc)[:2000]
            session.commit()
        raise
