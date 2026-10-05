# Operations Runbook

## Health

Public application health:

- `/api/v1/health`: API process health
- `/ready`: readiness endpoint used by the production container health check
- `/metrics`: Prometheus metrics, intentionally blocked from the public Caddy route

## Primary Metrics

Monitor:

- HTTP request count by route template/status
- request latency by route template
- authentication failures
- rate-limit events
- database connection failures
- Neo4j connectivity failures
- ingestion accepted/rejected counts
- deterministic rule-run status
- graph-run status
- model-run status
- case-composition status

Never label metrics with claim IDs, case IDs, beneficiary IDs, provider IDs, emails, tokens, or other high-cardinality/sensitive values.

## Logs

Backend logs are JSON-structured and include request IDs.

Logs must not contain:

- passwords
- raw session/reset/verification tokens
- database credentials
- raw secrets
- full claims payloads
- unnecessary synthetic beneficiary identifiers

Use the `X-Request-ID` response header to correlate a user-visible failure with server logs.

## Common Failure: Database Unavailable

Symptoms:

- readiness fails
- API endpoints return server errors
- migrations cannot start

Actions:

1. verify PostgreSQL container/service health
2. verify the database URL and secret injection
3. verify network reachability from the backend service
4. review PostgreSQL logs
5. do not bypass migrations to restore traffic

## Common Failure: Neo4j Unavailable

The core case queue remains relational, but provider network views may fail.

Actions:

1. verify Neo4j health
2. verify Bolt URI and credentials
3. verify graph projection completed successfully
4. rerun the graph projection only after the source snapshot is available

## Common Failure: Redis Unavailable

Authentication/telemetry abuse-control paths may fail closed or reject operations depending on the route.

Actions:

1. restore Redis
2. verify password and connection string
3. do not disable rate limiting as a production workaround

## Authentication Email Failure

Signup/reset must not pretend delivery succeeded if SMTP cannot send the required message.

Actions:

1. check SMTP host/port/TLS configuration
2. verify sender identity
3. inspect mail-provider delivery events
4. never log the raw verification/reset token

## Rebuilding Demo Analytics

Use the one-shot production bootstrap profile documented under `infra/deployment/README.md`.

The bootstrap is separate from API startup and may be rerun after clearing/replacing the intended demo dataset. Review duplicate ingestion checks before rerunning against the same archive.

## Backups

Back up PostgreSQL, Neo4j, and artifact volumes before destructive migrations or data replacement.

The portfolio deployment is not advertised as high availability. Restore procedures should be rehearsed before any non-demo use.
