from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    CaseDetail,
    CaseListResponse,
    CaseNoteRequest,
    CaseNoteResponse,
    CaseSummary,
    CaseUpdateRequest,
    PageMeta,
)
from app.audit.service import record_audit_event
from app.auth.dependencies import AuthContext, enforce_csrf, get_auth_context
from app.db.models import CaseEvidence, CaseNote, InvestigationCase
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

VALID_STATUSES = {
    "NEW",
    "IN_REVIEW",
    "NEEDS_DOCUMENTATION",
    "ESCALATED",
    "CLEARED",
    "CONFIRMED_ISSUE",
    "CLOSED",
}
MANAGER_ROLES = {"MANAGER", "ADMIN"}
GLOBAL_READ_ROLES = {"MANAGER", "ADMIN", "AUDITOR"}


def _visible_clause(context: AuthContext):
    if context.user.role in GLOBAL_READ_ROLES:
        return True
    return or_(
        InvestigationCase.assigned_user_id.is_(None),
        InvestigationCase.assigned_user_id == context.user.id,
    )


def _get_case_or_404(
    db: Session,
    context: AuthContext,
    case_id: UUID,
) -> InvestigationCase:
    case = db.scalar(
        select(InvestigationCase).where(
            InvestigationCase.id == case_id,
            _visible_clause(context),
        )
    )
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def _summary(case: InvestigationCase) -> CaseSummary:
    return CaseSummary(
        id=case.id,
        claim_record_id=case.claim_record_id,
        status=case.status,
        priority_score=case.priority_score,
        priority_band=case.priority_band,
        financial_exposure=case.financial_exposure,
        strongest_signal=case.strongest_signal,
        disposition=case.disposition,
        assigned_user_id=case.assigned_user_id,
        updated_at=case.updated_at,
    )


@router.get("", response_model=CaseListResponse)
def list_cases(
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    case_status: str | None = Query(default=None, alias="status"),
    priority_band: str | None = Query(default=None),
) -> CaseListResponse:
    filters = [_visible_clause(context)]
    if case_status:
        filters.append(InvestigationCase.status == case_status)
    if priority_band:
        filters.append(InvestigationCase.priority_band == priority_band)

    total = db.scalar(
        select(func.count()).select_from(InvestigationCase).where(*filters)
    ) or 0
    cases = list(
        db.scalars(
            select(InvestigationCase)
            .where(*filters)
            .order_by(
                InvestigationCase.priority_score.desc(),
                InvestigationCase.updated_at.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return CaseListResponse(
        items=[_summary(case) for case in cases],
        meta=PageMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(
    case_id: UUID,
    request: Request,
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> CaseDetail:
    case = _get_case_or_404(db, context, case_id)
    evidence = db.scalar(
        select(CaseEvidence).where(
            CaseEvidence.case_id == case.id,
            CaseEvidence.evidence_hash == case.current_evidence_hash,
        )
    )
    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Current case evidence is unavailable",
        )

    record_audit_event(
        db,
        event_type="CASE_VIEWED",
        user_id=context.user.id,
        resource_type="CASE",
        resource_id=str(case.id),
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()

    return CaseDetail(
        **_summary(case).model_dump(),
        evidence_hash=evidence.evidence_hash,
        evidence=evidence.payload,
        created_at=case.created_at,
    )


@router.patch("/{case_id}", response_model=CaseSummary)
def update_case(
    case_id: UUID,
    payload: CaseUpdateRequest,
    request: Request,
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> CaseSummary:
    enforce_csrf(request, context)
    case = _get_case_or_404(db, context, case_id)

    if context.user.role == "AUDITOR":
        raise HTTPException(status_code=403, detail="Audit role is read-only")

    changes: dict[str, object] = {}
    if payload.assign_to_self:
        if (
            case.assigned_user_id not in {None, context.user.id}
            and context.user.role not in MANAGER_ROLES
        ):
            raise HTTPException(
                status_code=403,
                detail="Case is assigned to another investigator",
            )
        case.assigned_user_id = context.user.id
        changes["assigned_user_id"] = str(context.user.id)

    if payload.status is not None:
        if payload.status not in VALID_STATUSES:
            raise HTTPException(status_code=422, detail="Invalid case status")
        if (
            case.assigned_user_id not in {context.user.id}
            and context.user.role not in MANAGER_ROLES
        ):
            raise HTTPException(status_code=403, detail="Assign the case before changing status")
        case.status = payload.status
        changes["status"] = payload.status

    if payload.disposition is not None:
        if (
            case.assigned_user_id not in {context.user.id}
            and context.user.role not in MANAGER_ROLES
        ):
            raise HTTPException(
                status_code=403,
                detail="Assign the case before recording disposition",
            )
        case.disposition = payload.disposition.strip() or None
        changes["disposition"] = case.disposition

    if not changes:
        return _summary(case)

    case.updated_at = datetime.now(UTC)
    record_audit_event(
        db,
        event_type="CASE_UPDATED",
        user_id=context.user.id,
        resource_type="CASE",
        resource_id=str(case.id),
        metadata={"changes": changes},
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()
    db.refresh(case)
    return _summary(case)


@router.get("/{case_id}/notes", response_model=list[CaseNoteResponse])
def list_case_notes(
    case_id: UUID,
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> list[CaseNoteResponse]:
    case = _get_case_or_404(db, context, case_id)
    notes = list(
        db.scalars(
            select(CaseNote)
            .where(CaseNote.case_id == case.id)
            .order_by(CaseNote.created_at.asc())
        )
    )
    return [CaseNoteResponse.model_validate(note, from_attributes=True) for note in notes]


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=201)
def add_case_note(
    case_id: UUID,
    payload: CaseNoteRequest,
    request: Request,
    context: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[Session, Depends(get_db)],
) -> CaseNoteResponse:
    enforce_csrf(request, context)
    case = _get_case_or_404(db, context, case_id)
    if context.user.role == "AUDITOR":
        raise HTTPException(status_code=403, detail="Audit role is read-only")
    if (
        case.assigned_user_id not in {context.user.id}
        and context.user.role not in MANAGER_ROLES
    ):
        raise HTTPException(
            status_code=403,
            detail="Assign the case before adding notes",
        )

    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Note cannot be empty")

    note = CaseNote(
        case_id=case.id,
        author_user_id=context.user.id,
        body=body,
        created_at=datetime.now(UTC),
    )
    db.add(note)
    db.flush()
    record_audit_event(
        db,
        event_type="CASE_NOTE_CREATED",
        user_id=context.user.id,
        resource_type="CASE",
        resource_id=str(case.id),
        metadata={"note_id": str(note.id)},
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()
    db.refresh(note)
    return CaseNoteResponse.model_validate(note, from_attributes=True)
