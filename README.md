# ClaimGraph PI

ClaimGraph PI is a pre-payment healthcare claims investigation and provider network intelligence platform.

The project is being built as a production-style system that combines deterministic risk rules, provider peer analytics, graph intelligence, machine-learning signals, financial exposure, and a human investigator workflow.

## Current Status

Phase 1 is in progress.

The repository already contains the governing product and engineering specifications:

- [PRD.md](PRD.md)
- [Architecture.md](Architecture.md)
- [rules.md](rules.md)
- [phases.md](phases.md)
- [design.md](design.md)
- [memory.md](memory.md)

Application code is being implemented incrementally according to those documents.

## Product Boundary

ClaimGraph PI is an investigation and decision-support system.

It does not autonomously deny claims, make clinical decisions, or claim regulatory certification. The public demo will use public-safe or synthetic claims-like data only.

## Planned Stack

- Python 3.12+
- FastAPI
- PostgreSQL
- dbt Core
- Neo4j
- scikit-learn
- MLflow
- React
- TypeScript
- Vite
- Docker
- GitHub Actions

## Local Development

Local setup instructions will be completed as the Phase 1 environment is finalized.

## License

Apache-2.0
