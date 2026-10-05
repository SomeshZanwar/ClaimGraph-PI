# ADR-002: Keep Evidence Sources Separate From Case Priority

## Status

Accepted.

## Context

Combining deterministic rules, peer deviation, anomaly scores, graph signals, and financial exposure into one opaque score would make investigation ranking difficult to audit.

## Decision

Persist each evidence source independently, then compose an immutable evidence package and calculate a transparent workload-priority score from documented components.

The priority score is explicitly not a fraud probability.

## Consequences

Investigators can inspect why a case was prioritized and distinguish hard deterministic evidence from statistical or model-derived signals. Ranking weights can evolve without rewriting historical evidence.
