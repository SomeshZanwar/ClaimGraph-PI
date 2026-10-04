from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int


class CaseSummary(BaseModel):
    id: UUID
    claim_record_id: str
    status: str
    priority_score: Decimal
    priority_band: str
    financial_exposure: Decimal
    strongest_signal: str | None
    disposition: str | None
    assigned_user_id: UUID | None
    updated_at: datetime


class CaseListResponse(BaseModel):
    items: list[CaseSummary]
    meta: PageMeta


class CaseDetail(CaseSummary):
    evidence_hash: str
    evidence: dict[str, Any]
    created_at: datetime


class CaseUpdateRequest(BaseModel):
    status: str | None = None
    disposition: str | None = Field(default=None, max_length=64)
    assign_to_self: bool = False


class CaseNoteRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class CaseNoteResponse(BaseModel):
    id: UUID
    case_id: UUID
    author_user_id: UUID
    body: str
    created_at: datetime


class ProviderProfileResponse(BaseModel):
    provider_npi: str
    peer_metrics: dict[str, Any] | None
    graph_metrics: dict[str, Any] | None
    linked_case_count: int
    total_claim_count: int
    total_allowed_charge: Decimal


class SearchResult(BaseModel):
    type: str
    id: str
    label: str
    secondary: str | None = None


class SearchResponse(BaseModel):
    items: list[SearchResult]


class GraphNode(BaseModel):
    id: str
    type: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class ProviderGraphResponse(BaseModel):
    provider_npi: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    truncated: bool


class AuditEventResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    event_type: str
    resource_type: str | None
    resource_id: str | None
    metadata: dict[str, Any]
    request_id: str | None
    occurred_at: datetime


class AuditListResponse(BaseModel):
    items: list[AuditEventResponse]
    meta: PageMeta
