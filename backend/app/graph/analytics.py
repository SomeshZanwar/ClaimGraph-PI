from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

import networkx as nx
from neo4j import Driver
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import GraphRun, ProviderGraphMetric


@dataclass(frozen=True)
class ProviderMetric:
    provider_npi: str
    member_count: int
    shared_provider_count: int
    max_shared_members_with_peer: int
    component_provider_count: int
    component_member_count: int


def compute_provider_metrics(
    edges: Iterable[tuple[str, str]],
) -> list[ProviderMetric]:
    graph = nx.Graph()
    provider_nodes: set[str] = set()

    for provider_npi, member_id in edges:
        provider_node = f"provider:{provider_npi}"
        member_node = f"member:{member_id}"
        graph.add_node(provider_node, kind="provider", provider_npi=provider_npi)
        graph.add_node(member_node, kind="member", member_id=member_id)
        graph.add_edge(provider_node, member_node)
        provider_nodes.add(provider_node)

    if not provider_nodes:
        return []

    projection = nx.algorithms.bipartite.weighted_projected_graph(
        graph,
        provider_nodes,
    )

    component_lookup: dict[str, tuple[int, int]] = {}
    for component in nx.connected_components(graph):
        provider_count = sum(
            1 for node in component if graph.nodes[node]["kind"] == "provider"
        )
        member_count = sum(
            1 for node in component if graph.nodes[node]["kind"] == "member"
        )
        for node in component:
            component_lookup[node] = (provider_count, member_count)

    metrics: list[ProviderMetric] = []
    for provider_node in sorted(provider_nodes):
        provider_npi = str(graph.nodes[provider_node]["provider_npi"])
        member_neighbors = [
            node
            for node in graph.neighbors(provider_node)
            if graph.nodes[node]["kind"] == "member"
        ]
        peer_edges = projection[provider_node]
        weights = [
            int(data.get("weight", 0))
            for _, data in peer_edges.items()
        ]
        component_provider_count, component_member_count = component_lookup[
            provider_node
        ]

        metrics.append(
            ProviderMetric(
                provider_npi=provider_npi,
                member_count=len(member_neighbors),
                shared_provider_count=len(peer_edges),
                max_shared_members_with_peer=max(weights, default=0),
                component_provider_count=component_provider_count,
                component_member_count=component_member_count,
            )
        )

    return metrics


def fetch_provider_member_edges(driver: Driver) -> list[tuple[str, str]]:
    with driver.session() as neo_session:
        records = neo_session.run(
            """
            MATCH (provider:Provider)<-[:BILLED_BY]-(claim:Claim)
                  <-[:HAS_CLAIM]-(member:Member)
            RETURN DISTINCT
                provider.provider_npi AS provider_npi,
                member.member_id AS member_id
            ORDER BY provider_npi, member_id
            """
        )
        return [
            (str(record["provider_npi"]), str(record["member_id"]))
            for record in records
        ]


def persist_provider_metrics(
    session: Session,
    graph_run: GraphRun,
    metrics: list[ProviderMetric],
) -> None:
    session.execute(
        delete(ProviderGraphMetric).where(
            ProviderGraphMetric.graph_run_id == graph_run.id
        )
    )

    evaluated_at = datetime.now(UTC)
    for metric in metrics:
        session.add(
            ProviderGraphMetric(
                graph_run_id=graph_run.id,
                provider_npi=metric.provider_npi,
                member_count=metric.member_count,
                shared_provider_count=metric.shared_provider_count,
                max_shared_members_with_peer=metric.max_shared_members_with_peer,
                component_provider_count=metric.component_provider_count,
                component_member_count=metric.component_member_count,
                evaluated_at=evaluated_at,
            )
        )
    session.commit()


def analyze_graph(
    session: Session,
    driver: Driver,
    graph_run: GraphRun,
) -> list[ProviderMetric]:
    edges = fetch_provider_member_edges(driver)
    metrics = compute_provider_metrics(edges)
    persist_provider_metrics(session, graph_run, metrics)
    return metrics
