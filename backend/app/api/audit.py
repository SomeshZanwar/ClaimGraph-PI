from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import AuditEventResponse, AuditListResponse, PageMeta
from app.auth.dependencies import AuthContext, require_roles
from app.db.models import AuditEvent
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("", response_model=AuditListResponse)
def list_audit_events(
    _context: Annotated[
        AuthContext,
        Depends(require_roles("MANAGER", "ADMIN", "AUDITOR")),
    ],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
) -> AuditListResponse:
    total = db.scalar(select(func.count()).select_from(AuditEvent)) or 0
    events = list(
        db.scalars(
            select(AuditEvent)
            .order_by(AuditEvent.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return AuditListResponse(
        items=[
            AuditEventResponse(
                id=event.id,
                user_id=event.user_id,
                event_type=event.event_type,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                metadata=event.metadata_json,
                request_id=event.request_id,
                occurred_at=event.occurred_at,
            )
            for event in events
        ],
        meta=PageMeta(page=page, page_size=page_size, total=int(total)),
    )
