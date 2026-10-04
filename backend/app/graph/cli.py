from __future__ import annotations

import argparse

from neo4j import GraphDatabase

from app.config import get_settings
from app.db.session import SessionLocal
from app.graph.analytics import analyze_graph
from app.graph.projection import project_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Project canonical ClaimGraph PI data into Neo4j."
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete ClaimGraph-managed nodes before rebuilding the graph.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()

    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        driver.verify_connectivity()

        with SessionLocal() as session:
            graph_run = project_graph(session, driver, replace=args.replace)
            metrics = analyze_graph(session, driver, graph_run)

    print(f"Graph run: {graph_run.id}")
    print(f"Status: {graph_run.status}")
    print(f"Projected rows: {graph_run.projected_rows}")
    print(f"Provider nodes: {graph_run.provider_nodes}")
    print(f"Member nodes: {graph_run.member_nodes}")
    print(f"Claim nodes: {graph_run.claim_nodes}")
    print(f"Procedure nodes: {graph_run.procedure_nodes}")
    print(f"Provider metrics: {len(metrics)}")


if __name__ == "__main__":
    main()
