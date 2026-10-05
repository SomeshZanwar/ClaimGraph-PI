# ADR-004: Single-VM Container Deployment for the Public Demo

## Status

Accepted for the portfolio demonstration.

## Context

The project needs a reproducible HTTPS deployment without claiming payer-scale infrastructure.

## Decision

Provide a Docker Compose production topology with Caddy, frontend Nginx, FastAPI, PostgreSQL, Neo4j, Redis, and an optional one-shot analytics bootstrap service.

Only Caddy exposes public ports. Caddy handles TLS and reverse proxying.

## Consequences

The topology is practical for a portfolio VM and preserves realistic service boundaries. It is not presented as a multi-region, payer-scale architecture. A regulated production deployment would require additional compliance, HA, backup, access-control, and operational controls.
