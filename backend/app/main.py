from __future__ import annotations

import re
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit import router as audit_router
from app.api.cases import router as cases_router
from app.api.graph import router as graph_router
from app.api.providers import router as providers_router
from app.api.search import router as search_router
from app.auth.routes import router as auth_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="ClaimGraph PI API",
    version="0.1.0",
    description="Backend API for the ClaimGraph PI investigation platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "X-CSRF-Token"],
)

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    request_id = (
        supplied
        if _REQUEST_ID_PATTERN.fullmatch(supplied)
        else str(uuid.uuid4())
    )
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(providers_router)
app.include_router(graph_router)
app.include_router(search_router)
app.include_router(audit_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "claimgraph-pi-api"}


@app.get("/api/v1/health", tags=["system"])
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "claimgraph-pi-api"}
