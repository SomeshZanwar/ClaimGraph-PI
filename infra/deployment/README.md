# Production Deployment

ClaimGraph PI ships with a Docker Compose production topology intended for a small portfolio/demo VM.

## Topology

- Caddy: public HTTPS endpoint and automatic TLS
- frontend: Nginx serving the built React application
- backend: FastAPI application with automatic Alembic migrations
- PostgreSQL: application, analytics, audit, and telemetry state
- Neo4j: managed investigation graph
- Redis: rate limiting and abuse protection
- analytics bootstrap: optional one-shot service for deterministic public-safe demo data

PostgreSQL, Neo4j, and Redis have no public host ports in the production compose file.

## Requirements

- Linux VM with Docker Engine and Docker Compose
- DNS A/AAAA record for the application domain pointing to the VM
- ports 80 and 443 reachable from the internet
- SMTP credentials for real email verification and password reset delivery
- at least 4 GB RAM recommended for the complete demonstration stack

## Configure

Copy the template outside version control:

~~~bash
cp infra/deployment/production.env.example .env.production
~~~

Replace every example credential. Generate independent random values for database, graph, Redis, and session secrets.

The production environment file must never be committed.

## Start the application

~~~bash
docker compose \
  --env-file .env.production \
  -f docker-compose.production.yml \
  up -d --build
~~~

Caddy requests and renews TLS certificates automatically after DNS resolves to the host.

## Bootstrap public-safe demonstration data

The optional bootstrap profile generates 300 deterministic CMS-shaped synthetic Carrier claims, runs dbt, deterministic rules, Neo4j projection, network analytics, the unsupervised anomaly model, MLflow tracking, and case composition.

The generated rows are demonstration data. They are not actual Medicare beneficiaries or providers.

~~~bash
docker compose \
  --env-file .env.production \
  -f docker-compose.production.yml \
  --profile bootstrap \
  run --rm analytics
~~~

The bootstrap is intentionally separate from normal application startup so model/data processing does not silently run when the API restarts.

## Real CMS DE-SynPUF ingestion

For analysis beyond the deterministic live demo, use the CMS DE-SynPUF Carrier Claims source documented in data/README.md.

Large CMS archives are intentionally excluded from Git history.

## Verify

~~~bash
curl -fsS https://YOUR_DOMAIN/api/v1/health
curl -fsS https://YOUR_DOMAIN/ready
~~~

The readiness response should report `database`, `neo4j`, and `redis` as `ok`. A failed dependency returns HTTP 503 rather than advertising the service as ready.

Also verify:

- signup delivers a real verification email
- the verification link activates the account
- login sets Secure/HttpOnly session state
- password reset email is delivered and the token is single-use
- the queue opens only after authentication
- /metrics is not publicly reachable through Caddy
- HTTP redirects to HTTPS
- database, Neo4j, and Redis ports are not exposed externally

## Backups

Back up these named volumes or move them to managed services before using the stack for anything beyond a portfolio demonstration:

- claimgraph_postgres
- claimgraph_neo4j
- claimgraph_redis
- claimgraph_artifacts
- claimgraph_caddy_data

## Production data boundary

The public demonstration must not accept or ingest real PHI. ClaimGraph PI has not been certified for HIPAA-regulated production use and makes no such claim.
