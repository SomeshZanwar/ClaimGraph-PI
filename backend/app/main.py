from __future__ import annotations

import re
import time
import uuid

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.audit import router as audit_router
from app.api.cases import router as cases_router
from app.api.graph import router as graph_router
from app.api.providers import router as providers_router
from app.api.search import router as search_router
from app.api.telemetry import router as telemetry_router
from app.auth.routes import router as auth_router
from app.config import get_settings
from app.observability import REQUEST_COUNT, REQUEST_LATENCY, configure_logging, logger
from app.readiness import check_dependencies

settings = get_settings()
configure_logging(settings.log_level)

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
    request_id = supplied if _REQUEST_ID_PATTERN.fullmatch(supplied) else str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed = time.perf_counter() - started
        logger.exception(
            "request_failed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            duration_seconds=round(elapsed, 6),
        )
        raise

    elapsed = time.perf_counter() - started
    route = getattr(request.scope.get("route"), "path", request.url.path)
    REQUEST_COUNT.labels(
        method=request.method,
        route=route,
        status=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, route=route).observe(elapsed)

    logger.info(
        "request_completed",
        request_id=request_id,
        method=request.method,
        route=route,
        status=response.status_code,
        duration_seconds=round(elapsed, 6),
    )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.app_env.lower() in {"production", "staging"}:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.url.path.startswith("/api/v1/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(providers_router)
app.include_router(graph_router)
app.include_router(search_router)
app.include_router(audit_router)
app.include_router(telemetry_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "claimgraph-pi-api"}


@app.get("/api/v1/health", tags=["system"])
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "claimgraph-pi-api"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/ready", tags=["system"])
def readiness(response: Response) -> dict[str, object]:
    dependencies = check_dependencies()
    if not dependencies.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if dependencies.ready else "not_ready",
        "service": "claimgraph-pi-api",
        "dependencies": dependencies.as_dict(),
    }
