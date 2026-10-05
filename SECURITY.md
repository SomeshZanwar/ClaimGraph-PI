# Security Policy

## Scope

ClaimGraph PI is a portfolio-grade investigation platform that uses public-safe or synthetic claims data. It is not certified for processing production PHI.

## Reporting a Vulnerability

Do not publish exploitable credentials, tokens, sensitive records, or working attack payloads in a public issue.

Use GitHub's private vulnerability reporting feature for this repository when available. For non-sensitive product bugs, use the public issue tracker.

## Security Controls

The application implements:

- Argon2id password hashing
- opaque server-side sessions
- expiring sessions and single-use verification/reset tokens
- CSRF protection for authenticated mutations
- Redis-backed rate limiting
- resource-level authorization for case access
- role-based read/write restrictions
- parameterized SQL and Cypher
- bounded graph exploration
- request IDs and structured security-relevant audit events
- secure production cookies
- HTTPS termination with HSTS in the production topology
- restricted production database, graph, and Redis network exposure
- dependency auditing
- committed-secret pattern scanning
- frontend bundle checks for backend secret markers

## Data Boundary

Never submit real patient PHI, payer credentials, production claims, private keys, API keys, or other confidential material to the public demonstration.

CMS DE-SynPUF and the repository-generated demo dataset are synthetic. They must not be used to make claims about real beneficiaries or providers.

## Supported Configuration

Security claims in this repository apply to the documented deployment topology and current main branch. Deployments that disable HTTPS, expose database ports, weaken authentication configuration, or alter authorization checks are outside that boundary.
