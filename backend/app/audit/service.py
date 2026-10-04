from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import AuditEvent


def record_audit_event(
    session: Session,
    *,
    event_type: str,
    user_id: UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata or {},
        request_id=request_id,
        occurred_at=datetime.now(UTC),
    )
    session.add(event)
    return event
