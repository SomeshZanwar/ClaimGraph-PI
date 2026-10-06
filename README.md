# ClaimGraph PI

ClaimGraph PI is an explainable pre-payment healthcare claims investigation and provider network intelligence platform.

It combines validated claims ingestion, deterministic billing signals, provider peer analysis, unsupervised anomaly detection, relationship-graph analytics, financial exposure, immutable evidence versions, and a secure human investigator workflow.

## Product Boundary

ClaimGraph PI is an investigation and decision-support system.

It does not:

- automatically approve or deny healthcare claims
- make clinical decisions
- identify a real person or provider as fraudulent
- represent anomaly scores as fraud probabilities
- claim HIPAA certification or regulatory approval
- require real PHI for the public demonstration

The public/demo data path uses synthetic CMS DE-SynPUF-style claims.

## What the System Implements

### Claims and Data Quality

- CMS DE-SynPUF Carrier Claims ingestion
- ZIP/CSV streaming
- source SHA-256 lineage
- accepted/rejected record accounting
- structured quarantine reasons
- normalized claim-line representation
- PostgreSQL migrations
- dbt staging, facts, dimensions, and quality tests

### Explainable Risk Signals

- versioned deterministic rule definitions
- duplicate-claim review signals
- repeated-line signals
- rapid repeat-service signals
- payment/allowed-charge consistency signals
- provider behavioral cohorts
- robust peer comparison with small-cohort protection
- Isolation Forest claim anomaly scoring
- versioned model metadata and MLflow tracking
- descriptive, non-causal feature-deviation context

### Provider Network Intelligence

- Neo4j projection from canonical relational data
- Member, Claim, Provider, and Procedure nodes
- bounded provider network exploration
- NetworkX provider-member analytics
- shared-member overlap
- connected-component metrics
- graph-run/source-snapshot provenance

### Investigation Workflow

- transparent case priority components
- immutable evidence versions
- financial exposure
- source lineage
- case assignment
- case status
- investigator notes
- disposition
- audit events
- provider profile
- network graph
- role-restricted audit access

### Authentication and Security

- Argon2id passwords
- email verification
- password reset
- opaque expiring server-side sessions
- CSRF protection
- Redis-backed abuse controls
- case-level authorization
- read-only audit role
- request IDs
- structured logs
- secure production headers
- committed-secret scanning
- Python and Node dependency audits

### Public Product Surface

- responsive mobile/tablet/laptop/desktop UI
- mobile navigation
- custom 404
- Privacy Policy
- Terms of Service
- support/bug-report route
- consented first-party page telemetry
- route titles and meta descriptions
- canonical links
- Open Graph metadata
- schema markup
- favicon and social preview
- sitemap and robots generation
- llms.txt

## Architecture

~~~text
CMS synthetic claims / deterministic demo generator
                         |
                         v
              Ingestion + validation
                         |
                         v
               PostgreSQL raw layer
                         |
                         v
                    dbt Core
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
       Rule engine   ML features   Graph projection
             |       Isolation      Neo4j
             |        Forest          |
             |           |        NetworkX
             +-----------+-----------+
                         |
                         v
               Evidence composition
                         |
                         v
                Case prioritization
                         |
                         v
                    FastAPI
                         |
              Authentication / RBAC
                         |
                         v
                React investigator UI
~~~

PostgreSQL remains the system of record. Neo4j is a reproducible projection, not a separate source of truth.

See [Architecture.md](Architecture.md) and the [architecture decisions](docs/decisions/).

## Technology Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI, Pydantic |
| Relational data | PostgreSQL, SQLAlchemy, Alembic |
| Analytics | dbt Core |
| Graph | Neo4j, NetworkX, Cytoscape.js |
| ML | scikit-learn Isolation Forest, MLflow |
| Abuse controls | Redis |
| Frontend | React, TypeScript, Vite, TanStack Query |
| Testing | pytest, Vitest, Playwright |
| Observability | structlog, Prometheus-compatible metrics |
| Containers | Docker, Docker Compose |
| HTTPS | Caddy |
| CI | GitHub Actions |

## Data

The primary public development source is CMS DE-SynPUF Carrier Claims.

See [data/README.md](data/README.md) for:

- official source links
- source limitations
- local file placement
- synthetic-data interpretation boundaries

Large CMS archives are intentionally excluded from Git history.

A deterministic repository generator is also available for the hosted demo workflow. It produces CMS-shaped synthetic records that are not actual CMS beneficiaries or providers.

## Local Development

### Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- Git

### Start the stack

~~~bash
git clone https://github.com/SomeshZanwar/ClaimGraph-PI.git
cd ClaimGraph-PI
cp .env.example .env
docker compose up --build
~~~

Windows PowerShell:

~~~powershell
Copy-Item .env.example .env
docker compose up --build
~~~

Change example local secrets before starting the stack.

### Local Services

- Frontend: http://localhost:5173
- API: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Neo4j Browser: http://localhost:7474
- Mailpit: http://localhost:8025

Local database and graph ports are exposed for development. The production topology does not expose them publicly.

## Claims Pipeline

Apply migrations:

~~~bash
alembic -c backend/alembic.ini upgrade head
~~~

Ingest a supported DE-SynPUF Carrier archive:

~~~bash
python -m app.ingestion.cli data/raw/sample_2/DE1_0_2008_to_2010_Carrier_Claims_Sample_2A.zip
~~~

Build canonical analytics:

~~~bash
dbt build --project-dir dbt --profiles-dir dbt
~~~

Run deterministic risk rules:

~~~bash
python -m app.risk.cli
~~~

Project and analyze the graph:

~~~bash
python -m app.graph.cli --replace
~~~

Train and score the anomaly model:

~~~bash
python -m app.ml.cli
~~~

Compose investigation cases:

~~~bash
python -m app.casework.cli
~~~

## Deterministic Demo Bootstrap

For a public-safe demonstration without downloading a large CMS archive:

~~~bash
python scripts/generate_demo_fixture.py
~~~

The production deployment includes an optional one-shot analytics bootstrap container that runs the complete data, rules, graph, ML, and case-composition pipeline.

See [infra/deployment/README.md](infra/deployment/README.md).

## Testing

Backend:

~~~bash
pip install -e "./backend[dev]"
pytest backend
~~~

Frontend:

~~~bash
cd frontend
npm ci
npm run lint
npm run test
npm run build
npm run e2e
~~~

The CI pipeline validates:

- Python linting
- PostgreSQL migrations
- backend unit/integration/auth/authorization tests
- CMS-shaped ingestion
- dbt build and data-quality tests
- deterministic risk signals
- real Neo4j projection
- graph analytics
- anomaly training/scoring
- evidence/case composition
- frontend lint/unit/build
- desktop and mobile browser QA
- secret-pattern scanning
- Python dependency audit
- npm dependency audit
- frontend bundle secret-marker checks
- committed local documentation links
- minimum backend coverage threshold
- frontend JavaScript bundle budget
- PostgreSQL, Neo4j, and Redis readiness
- development and production Compose validation

## Production Deployment

The repository includes a production Docker Compose topology with:

- Caddy HTTPS reverse proxy
- frontend Nginx
- FastAPI backend
- PostgreSQL
- Neo4j
- password-protected Redis
- optional analytics bootstrap

Only ports 80/443 are intended to be public.

See the [production deployment runbook](infra/deployment/README.md).

A public host/domain is an external launch step and is not represented as completed until a real environment is provisioned.

## Security

Read [SECURITY.md](SECURITY.md).

Important design choices include:

- server-side resource authorization
- cross-user case access prevention
- CSRF-protected mutations
- no frontend secrets
- no production credentials in Git
- no public database/graph/Redis ports in the documented production topology
- no PHI requirement for the public demonstration

## Methodology and Technical Notes

- [Product requirements](PRD.md)
- [Architecture](Architecture.md)
- [Engineering rules](rules.md)
- [Implementation phases](phases.md)
- [Design system](design.md)
- [Data dictionary](docs/data-dictionary.md)
- [Model evaluation](docs/model-evaluation.md)
- [Graph methodology](docs/graph-methodology.md)
- [Responsible use](docs/responsible-use.md)
- [Operations runbook](docs/runbooks/operations.md)
- [Public launch checklist](docs/launch-checklist.md)

## Known Limitations

- DE-SynPUF is synthetic and has limited inferential value for real Medicare behavior.
- Synthetic provider identifiers are not real NPIs.
- Provider peer groups are behavioral cohorts, not clinical specialty classifications.
- The anomaly model is unsupervised and is not a fraud classifier.
- Graph connectivity is an investigation signal, not proof of misconduct.
- The repository deployment is sized for a portfolio/demo environment, not payer-scale regulated production.

## License

Apache-2.0
