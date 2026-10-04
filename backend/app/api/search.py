from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.schemas import SearchResponse, SearchResult
from app.auth.dependencies import AuthContext, get_auth_context
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    _context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
    q: str = Query(min_length=2, max_length=64),
) -> SearchResponse:
    term = q.strip()
    if not term:
        return SearchResponse(items=[])

    rows = db.execute(
        text(
            """
            with matches as (
                select
                    'claim'::text as type,
                    claim_record_id as id,
                    claim_id as label,
                    beneficiary_id as secondary,
                    1 as rank
                from analytics.fact_claims
                where claim_id = :term or claim_record_id = :term

                union all

                select
                    'provider'::text as type,
                    provider_npi as id,
                    provider_npi as label,
                    'Synthetic provider identifier'::text as secondary,
                    2 as rank
                from analytics.dim_provider
                where provider_npi = :term

                union all

                select
                    'case'::text as type,
                    id::text as id,
                    case_key as label,
                    status as secondary,
                    3 as rank
                from casework.cases
                where id::text = :term or case_key = :term
            )
            select type, id, label, secondary
            from matches
            order by rank
            limit 20
            """
        ),
        {"term": term},
    ).mappings()

    return SearchResponse(
        items=[
            SearchResult(
                type=str(row["type"]),
                id=str(row["id"]),
                label=str(row["label"]),
                secondary=str(row["secondary"]) if row["secondary"] is not None else None,
            )
            for row in rows
        ]
    )
