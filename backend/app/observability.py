from __future__ import annotations

import logging
import sys

import structlog
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "claimgraph_http_requests_total",
    "HTTP requests handled by ClaimGraph PI.",
    ["method", "route", "status"],
)
REQUEST_LATENCY = Histogram(
    "claimgraph_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
)


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger("claimgraph")
