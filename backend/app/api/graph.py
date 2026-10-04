from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from neo4j import GraphDatabase

from app.api.schemas import GraphEdge, GraphNode, ProviderGraphResponse
from app.auth.dependencies import AuthContext, get_auth_context
from app.config import get_settings

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/providers/{provider_npi}", response_model=ProviderGraphResponse)
def provider_graph(
    provider_npi: str,
    _context: Annotated[AuthContext, Depends(get_auth_context)],
    limit: int = Query(default=50, ge=10, le=100),
) -> ProviderGraphResponse:
    if len(provider_npi) > 32 or not provider_npi.strip():
        raise HTTPException(status_code=422, detail="Invalid provider identifier")

    settings = get_settings()
    query = """
    MATCH (provider:Provider {provider_npi: $provider_npi})
    OPTIONAL MATCH (provider)<-[:BILLED_BY]-(claim:Claim)<-[:HAS_CLAIM]-(member:Member)
    WITH provider, collect(DISTINCT claim)[0..$limit] AS claims,
         collect(DISTINCT member)[0..$limit] AS members
    RETURN provider, claims, members
    """

    with GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    ) as driver:
        with driver.session() as session:
            record = session.run(
                query,
                provider_npi=provider_npi,
                limit=limit,
            ).single()

    if record is None or record["provider"] is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    nodes = [
        GraphNode(
            id=f"provider:{provider_npi}",
            type="provider",
            label=provider_npi,
        )
    ]
    edges: list[GraphEdge] = []

    seen_claims: set[str] = set()
    for claim in record["claims"]:
        claim_id = str(claim["claim_record_id"])
        seen_claims.add(claim_id)
        nodes.append(
            GraphNode(
                id=f"claim:{claim_id}",
                type="claim",
                label=str(claim.get("claim_id") or claim_id),
            )
        )
        edges.append(
            GraphEdge(
                source=f"claim:{claim_id}",
                target=f"provider:{provider_npi}",
                type="BILLED_BY",
            )
        )

    for member in record["members"]:
        member_id = str(member["member_id"])
        node_id = f"member:{member_id}"
        nodes.append(GraphNode(id=node_id, type="member", label=member_id))

    if seen_claims:
        with GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        ) as driver:
            with driver.session() as session:
                rels = session.run(
                    """
                    MATCH (member:Member)-[:HAS_CLAIM]->(claim:Claim)
                    WHERE claim.claim_record_id IN $claim_ids
                    RETURN DISTINCT member.member_id AS member_id,
                                    claim.claim_record_id AS claim_record_id
                    LIMIT $limit
                    """,
                    claim_ids=sorted(seen_claims),
                    limit=limit,
                )
                for rel in rels:
                    edges.append(
                        GraphEdge(
                            source=f"member:{rel['member_id']}",
                            target=f"claim:{rel['claim_record_id']}",
                            type="HAS_CLAIM",
                        )
                    )

    unique_nodes = {node.id: node for node in nodes}
    truncated = len(record["claims"]) >= limit or len(record["members"]) >= limit
    return ProviderGraphResponse(
        provider_npi=provider_npi,
        nodes=list(unique_nodes.values())[: 2 * limit + 1],
        edges=edges[: 3 * limit],
        truncated=truncated,
    )
