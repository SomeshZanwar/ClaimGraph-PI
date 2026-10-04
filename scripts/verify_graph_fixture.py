from app.config import get_settings
from app.db.models import GraphRun, ProviderGraphMetric
from app.db.session import SessionLocal
from neo4j import GraphDatabase
from sqlalchemy import select


def main() -> None:
    settings = get_settings()

    with SessionLocal() as session:
        latest_run = session.scalar(
            select(GraphRun).order_by(GraphRun.started_at.desc()).limit(1)
        )
        if latest_run is None:
            raise RuntimeError("No graph run found")
        if latest_run.status != "COMPLETED":
            raise RuntimeError(f"Graph run status is {latest_run.status}")
        if latest_run.provider_nodes < 2:
            raise RuntimeError("Expected at least two synthetic provider nodes")
        if latest_run.member_nodes < 2:
            raise RuntimeError("Expected at least two synthetic member nodes")

        metrics = session.scalars(
            select(ProviderGraphMetric).where(
                ProviderGraphMetric.graph_run_id == latest_run.id
            )
        ).all()
        if not metrics:
            raise RuntimeError("No provider graph metrics were persisted")

    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        driver.verify_connectivity()
        with driver.session() as neo_session:
            count = neo_session.run(
                "MATCH (n:ClaimGraphManaged) RETURN count(n) AS count"
            ).single(strict=True)["count"]
            if int(count) == 0:
                raise RuntimeError("Managed Neo4j graph is empty")

    print(
        f"Verified graph run {latest_run.id}: "
        f"{latest_run.provider_nodes} providers, "
        f"{latest_run.member_nodes} members, "
        f"{len(metrics)} provider metrics"
    )


if __name__ == "__main__":
    main()
