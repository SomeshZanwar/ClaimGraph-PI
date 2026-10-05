# ADR-001: Split Relational, Graph, and Analytical Responsibilities

## Status

Accepted.

## Context

ClaimGraph PI needs transactional casework, reproducible analytical transformations, relationship exploration, and model/rule provenance. Forcing all responsibilities into one storage or application layer would weaken either query ergonomics or operational clarity.

## Decision

Use:

- PostgreSQL as the system of record
- dbt Core for canonical analytical transformations and data-quality tests
- Neo4j for interactive relationship traversal
- NetworkX for deterministic/offline graph metric computation
- FastAPI as the application boundary

## Consequences

The system has more services than a single-database prototype, but each service has a clear responsibility. Graph data is reproducibly projected from PostgreSQL rather than becoming an independent source of truth.
