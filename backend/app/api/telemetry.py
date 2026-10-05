from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.rate_limit import RateLimitExceeded, enforce_rate_limit
from app.auth.security import hash_identifier
from app.db.models import ProductEvent
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])

ALLOWED_EVENTS = {
    "page_view",
    "case_opened",
    "case_filtered",
    "graph_view_opened",
    "case_status_changed",
    "case_disposition_recorded",
    "provider_profile_opened",
    "support_opened",
}


class TelemetryEventRequest(BaseModel):
    event_name: str = Field(min_length=1, max_length=64)
    route: str = Field(min_length=1, max_length=256)
    properties: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
def record_product_event(
    payload: TelemetryEventRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    if payload.event_name not in ALLOWED_EVENTS:
        raise HTTPException(status_code=422, detail="Unsupported telemetry event")

    if not payload.route.startswith("/") or ".." in payload.route:
        raise HTTPException(status_code=422, detail="Invalid telemetry route")

    if len(payload.properties) > 12:
        raise HTTPException(status_code=422, detail="Too many telemetry properties")

    actor_source = request.client.host if request.client else "unknown"
    actor_hash = hash_identifier(actor_source)

    try:
        enforce_rate_limit(
            f"claimgraph:telemetry:{actor_hash}",
            limit=120,
            window_seconds=3600,
        )
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Telemetry rate limit exceeded",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    safe_properties: dict[str, Any] = {}
    for key, value in payload.properties.items():
        if len(key) > 48:
            raise HTTPException(status_code=422, detail="Telemetry property key is too long")
        if isinstance(value, str) and len(value) > 160:
            raise HTTPException(status_code=422, detail="Telemetry property value is too long")
        safe_properties[key] = value

    db.add(
        ProductEvent(
            event_name=payload.event_name,
            route=payload.route,
            actor_hash=actor_hash,
            properties=safe_properties,
            occurred_at=datetime.now(UTC),
        )
    )
    db.commit()
    return {"status": "accepted"}
