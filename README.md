# ClaimGraph PI

ClaimGraph PI is a pre-payment healthcare claims investigation and provider network intelligence platform.

The project is being built as a production-style system that combines deterministic risk rules, provider peer analytics, graph intelligence, machine-learning signals, financial exposure, and a human investigator workflow.

## Current Status

Phase 1 foundation is in progress.

The repository contains the governing specifications:

- [PRD.md](PRD.md)
- [Architecture.md](Architecture.md)
- [rules.md](rules.md)
- [phases.md](phases.md)
- [design.md](design.md)
- [memory.md](memory.md)

The foundation and CMS DE-SynPUF Carrier Claims ingestion path are implemented and validated in CI. The dbt analytical layer is the current phase.

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

### Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- Git

### Start the foundation stack

1. Clone the repository.

~~~bash
git clone https://github.com/SomeshZanwar/ClaimGraph-PI.git
cd ClaimGraph-PI
~~~

2. Create a local environment file.

~~~bash
cp .env.example .env
~~~

On Windows PowerShell:

~~~powershell
Copy-Item .env.example .env
~~~

3. Change the development passwords and secrets in the local .env file.

Do not use the example credentials in any public deployment.

4. Build and start the services.

~~~bash
docker compose up --build
~~~

### Local services

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health
- Neo4j Browser: http://localhost:7474
- Mailpit: http://localhost:8025

PostgreSQL and Redis are also exposed locally for development.

## Run Backend Tests Without Docker

From the repository root:

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e "./backend[dev]"
pytest backend
~~~

Windows PowerShell activation:

~~~powershell
.\.venv\Scripts\Activate.ps1
~~~

## Run Frontend Checks Without Docker

~~~bash
cd frontend
npm install
npm run lint
npm run test
npm run build
~~~

A committed lockfile will be added after dependency resolution is materialized locally.

## CMS DE-SynPUF Carrier Claims Ingestion

The initial data pipeline targets CMS DE-SynPUF Sample 2 Carrier Claims. The source files are synthetic and are not committed to this repository.

See [data/README.md](data/README.md) for source URLs, limitations, and data-use notes.

After downloading a Carrier Claims ZIP into `data/raw/sample_2/`, apply the database migration:

~~~bash
alembic -c backend/alembic.ini upgrade head
~~~

Then ingest one source archive:

~~~bash
python -m app.ingestion.cli data/raw/sample_2/DE1_0_2008_to_2010_Carrier_Claims_Sample_2A.zip
~~~

The ingestion command reports:

- rows seen
- rows accepted
- rows rejected
- normalized claim lines loaded
- final batch status

Malformed rows are preserved in `raw.rejected_records` with structured reason codes instead of being silently dropped.

The CI workflow also runs an end-to-end ingestion test against PostgreSQL using a small repository-safe fixture that mirrors the CMS Carrier schema.

## Repository Standards

ClaimGraph PI is developed against explicit engineering rules covering data quality, explainability, graph analytics, ML evaluation, authentication and authorization, security, responsive UI, accessibility, legal/public-site completeness, SEO, observability, and testing.

See [rules.md](rules.md).

## License

Apache-2.0
