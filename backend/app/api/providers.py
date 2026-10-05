from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.schemas import ProviderProfileResponse
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.models import GraphRun, ProviderGraphMetric
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("/{provider_npi}", response_model=ProviderProfileResponse)
def get_provider_profile(
    provider_npi: str,
    _context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> ProviderProfileResponse:
    if len(provider_npi) > 32 or not provider_npi.strip():
        raise HTTPException(status_code=422, detail="Invalid provider identifier")

    peer = db.execute(
        text(
            """
            select *
            from analytics.mart_provider_peer_metrics
            where provider_npi = :provider_npi
            """
        ),
        {"provider_npi": provider_npi},
    ).mappings().first()

    aggregate = db.execute(
        text(
            """
            select
                count(distinct claim_record_id) as claim_count,
                coalesce(sum(allowed_charge_amount), 0) as total_allowed_charge
            from analytics.fact_claim_lines
            where provider_npi = :provider_npi
            """
        ),
        {"provider_npi": provider_npi},
    ).mappings().one()

    if int(aggregate["claim_count"]) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    latest_graph_run = db.scalar(
        select(GraphRun)
        .where(GraphRun.status == "COMPLETED")
        .order_by(GraphRun.started_at.desc())
        .limit(1)
    )
    graph_metric = None
    if latest_graph_run is not None:
        graph_metric = db.scalar(
            select(ProviderGraphMetric).where(
                ProviderGraphMetric.graph_run_id == latest_graph_run.id,
                ProviderGraphMetric.provider_npi == provider_npi,
            )
        )

    linked_case_count = db.execute(
        text(
            """
            select count(distinct c.id)
            from casework.cases c
            inner join analytics.fact_claim_lines l
                on l.claim_record_id = c.claim_record_id
            where l.provider_npi = :provider_npi
            """
        ),
        {"provider_npi": provider_npi},
    ).scalar_one()

    return ProviderProfileResponse(
        provider_npi=provider_npi,
        peer_metrics=dict(peer) if peer else None,
        graph_metrics=(
            {
                "member_count": graph_metric.member_count,
                "shared_provider_count": graph_metric.shared_provider_count,
                "max_shared_members_with_peer": graph_metric.max_shared_members_with_peer,
                "component_provider_count": graph_metric.component_provider_count,
                "component_member_count": graph_metric.component_member_count,
            }
            if graph_metric
            else None
        ),
        linked_case_count=int(linked_case_count),
        total_claim_count=int(aggregate["claim_count"]),
        total_allowed_charge=Decimal(str(aggregate["total_allowed_charge"] or 0)),
    )
