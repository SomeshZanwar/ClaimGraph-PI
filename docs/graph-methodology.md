# Graph Methodology

## Purpose

The graph layer surfaces relationships that are difficult to inspect in claim tables while preserving traceability back to canonical claims.

## Graph Projection

Neo4j nodes currently include:

- Member
- Claim
- Provider
- Procedure

Relationships include:

- Member HAS_CLAIM Claim
- Claim BILLED_BY Provider
- Claim CONTAINS_PROCEDURE Procedure

Every graph entity originates from validated canonical data. Facility/address nodes are not fabricated because the selected Carrier source does not reliably support them.

## Projection Safety

- uniqueness constraints prevent duplicate managed nodes
- Cypher inputs are parameterized
- projections are source-snapshot tracked
- ClaimGraph-managed nodes can be rebuilt idempotently
- interactive graph queries are bounded

## Network Analytics

NetworkX creates a provider-member bipartite graph and derives:

- provider member count
- number of providers sharing at least one member
- maximum shared-member overlap with another provider
- connected-component provider count
- connected-component member count

These metrics are persisted with the graph-run ID.

## Interpretation Boundary

A shared member, high degree, large component, or community relationship is an investigation signal only.

Connectivity is not proof of collusion, fraud, waste, abuse, or provider misconduct.

## Investigator View

The UI limits node/edge expansion and exposes entity type, relationship type, and truncation status. This prevents an unbounded graph query from becoming a browser or database denial-of-service path.
