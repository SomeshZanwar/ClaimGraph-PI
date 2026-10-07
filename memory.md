# ClaimGraph PI Project Memory

## Project

ClaimGraph PI

## Current Objective

Complete and release-harden an explainable pre-payment healthcare claims investigation and provider network intelligence platform.

The system combines deterministic claim rules, provider peer analytics, unsupervised anomaly detection, graph analytics, financial exposure, immutable evidence, secure investigator workflows, and auditability.

## Core Product Boundary

ClaimGraph PI is an investigation and decision-support system.

It does not autonomously deny claims, make clinical decisions, identify real providers or beneficiaries as fraudulent, claim regulatory certification, or require real PHI for its public demonstration.

## Target Users

- Payment Integrity Analysts
- SIU Investigators
- Healthcare Data Analysts
- Healthcare Data Scientists
- Coding and Documentation Analysts
- Payment Integrity Managers
- Compliance and Audit users

## Governing Documents

Complete and maintained:

- PRD.md
- Architecture.md
- rules.md
- phases.md
- design.md
- memory.md

## Current Overall Status

Repository implementation: COMPLETE AND RELEASE-READY

Release implementation validation: GREEN, [CI run 288](https://github.com/SomeshZanwar/ClaimGraph-PI/actions/runs/37570827101), including automated axe accessibility assertions. The documentation reconciliation is tracked in [PR 12](https://github.com/SomeshZanwar/ClaimGraph-PI/pull/12).

Validated CI jobs:

- Backend and Analytics: PASS
- Frontend: PASS
- Security: PASS

The latest validated pipeline includes PostgreSQL migrations, backend tests, dbt build/tests, deterministic risk rules, Neo4j projection, graph analytics, anomaly-model training/scoring, evidence/case composition, frontend lint/unit/build, Playwright browser QA, secret scanning, dependency audits, frontend secret-marker checks, and development/production Compose validation.

## Phase Status

### Phase 0: Product and Engineering Specification

Status: COMPLETE

- product requirements
- architecture
- engineering rules
- implementation phases
- design system
- living project memory

### Phase 1: Repository Foundation and Local Environment

Status: COMPLETE

- Apache-2.0 license
- .gitignore
- .env.example
- FastAPI backend
- typed runtime configuration
- React + TypeScript + Vite frontend
- Dockerfiles
- Docker Compose
- PostgreSQL
- Neo4j
- Redis
- Mailpit
- pytest
- Vitest
- Playwright
- GitHub Actions
- responsive application shell
- mobile navigation
- favicon
- custom 404
- local setup documentation

Release reproducibility:

- frontend package-lock.json is committed
- CI and frontend container installs use npm ci
- backend coverage floor is enforced
- frontend JavaScript bundle budget is enforced

### Phase 2: Data Source, Canonical Model, and Ingestion

Status: COMPLETE

- CMS DE-SynPUF Carrier Claims selected
- source provenance and limitations documented
- Sample 2 manifest
- ingestion batches and checksums
- ZIP/CSV streaming
- schema validation
- line-slot normalization
- accepted/rejected accounting
- structured quarantine records
- PostgreSQL raw models
- Alembic migration
- ingestion CLI
- PostgreSQL integration tests

### Phase 3: dbt Analytics and Data Quality

Status: COMPLETE

- raw sources
- staging models
- canonical claim service events
- claim-line fact
- claim fact
- provider dimension
- provider operational metrics
- claim ML feature mart
- schema tests
- custom date-order tests
- CI dbt connection/build/test validation

### Phase 4: Deterministic Risk Engine

Status: COMPLETE

- versioned YAML rules
- ruleset hashing
- persistent rule runs
- persistent risk signals
- duplicate-claim review rule
- repeated-service-line rule
- rapid-repeat-service rule
- payment/allowed-charge consistency rule
- structured evidence
- deterministic CLI
- synthetic fixture verification

### Phase 5: Provider Peer Intelligence

Status: COMPLETE

- dominant HCPCS behavioral profile
- explicit operational cohort assignment
- volume bands
- peer cohort key
- peer cohort size
- peer median
- median absolute deviation
- robust z-score
- insufficient-cohort handling
- no synthetic-specialty claims

### Phase 6: Graph Data Model and Network Analytics

Status: COMPLETE

- Neo4j managed projection
- Member nodes
- Claim nodes
- Provider nodes
- Procedure nodes
- Member-to-Claim relationships
- Claim-to-Provider relationships
- Claim-to-Procedure relationships
- source snapshot hashing
- bounded batch projection
- NetworkX provider-member analytics
- shared-member overlap
- connected-component metrics
- persisted graph metrics
- real Neo4j CI validation

Facility/address entities are not fabricated where the selected source cannot support them.

### Phase 7: Machine-Learning Risk Layer

Status: COMPLETE

- canonical numeric claim features
- Isolation Forest anomaly model
- deterministic random seed
- source snapshot/version tracking
- explicit feature schema
- production minimum-row guard
- fixture-only CI override
- persisted model runs
- persisted claim anomaly scores
- anomaly threshold
- descriptive feature-deviation context
- MLflow tracking
- local artifact persistence
- reproducibility tests

The anomaly score is not represented as a fraud probability.

### Phase 8: Evidence Composer and Case Prioritization

Status: COMPLETE

- investigation case table
- immutable evidence versions
- evidence hashing
- rule evidence
- model evidence
- peer evidence
- graph evidence
- financial exposure
- source lineage
- transparent priority components
- priority bands
- idempotent evidence versions
- case composition verification

### Phase 9: Authentication, Authorization, and User Model

Status: COMPLETE

- Argon2id password hashing
- users and roles
- opaque server-side sessions
- session expiry
- email verification
- password reset
- single-use token handling
- Redis-backed abuse controls
- CSRF checks
- case-level authorization
- read-only audit role
- authorization tests
- authentication lifecycle tests
- structured audit events

### Phase 10: Investigator API

Status: COMPLETE

- paginated case queue
- case detail
- case assignment
- case status
- disposition
- investigator notes
- provider profile
- provider graph endpoint
- search
- audit endpoint
- typed response models
- protected resource checks

### Phase 11: Investigator Web Application

Status: COMPLETE

- authenticated application shell
- login
- signup
- email verification flow
- password reset flow
- prioritized queue
- filtering
- case evidence view
- case assignment
- status workflow
- notes
- provider profile
- Cytoscape network view
- responsive mobile/tablet/laptop/desktop behavior
- explicit loading/success/error/empty states
- custom 404
- Playwright browser QA

### Phase 12: Public Product Surface, Legal, SEO, and Accessibility

Status: COMPLETE AT REPOSITORY LEVEL

- public product page
- methodology page
- Privacy Policy
- Terms of Service
- support/bug-report route
- consent control
- page titles
- meta descriptions
- canonical links
- Open Graph metadata
- social preview
- favicon
- sitemap generation
- robots generation
- llms.txt
- responsive layout
- keyboard-visible focus states
- non-color-only risk labels
- automated axe WCAG 2.1 A/AA assertions on desktop/mobile public and protected flows
- accessible primary-action contrast and provider-graph semantics

External search-engine submission remains a post-deployment action and is documented rather than falsely marked complete.

### Phase 13: Observability and Operations

Status: COMPLETE AT REPOSITORY LEVEL

- structured logging
- request IDs
- Prometheus-compatible request metrics
- health endpoint
- readiness endpoint
- database/Neo4j/Redis readiness behavior
- operational runbook
- deployment health checks
- safe failure responses

External alert routing depends on the chosen host and remains a deployment-environment task.

### Phase 14: Security Hardening

Status: COMPLETE

Validated controls include:

- committed-secret scan
- Python dependency audit
- frontend dependency audit
- frontend bundle scan for backend secret markers
- CSRF protection
- secure session design
- password hashing
- token expiry and single use
- rate limiting
- resource-level authorization
- case-access isolation tests
- parameterized SQL
- parameterized Cypher
- bounded graph exploration
- no public production database/graph/Redis ports
- production HTTPS topology
- security headers
- SECURITY.md

### Phase 15: Performance and Reliability

Status: COMPLETE FOR DEMO SCALE

- pagination
- bounded graph queries
- batch ingestion
- asynchronous/batch analytical workflow separation
- responsive frontend checks
- page-level overflow tests
- browser interactive-state QA
- static asset caching through production web stack
- production service health checks
- deterministic fixture/bootstrap process

A full production traffic/load benchmark is outside the portfolio-scale deployment claim.

### Phase 16: Deployment and Demo Validation

Status: IMPLEMENTATION COMPLETE, EXTERNAL LAUNCH PENDING

Repository deployment assets are complete:

- production Docker Compose
- Caddy HTTPS reverse proxy
- frontend Nginx
- backend container
- PostgreSQL
- Neo4j
- password-protected Redis
- analytics bootstrap profile
- production environment template
- deployment runbook
- production Compose validation in CI

Not yet claimed as complete:

- provisioning a real public host/domain
- production SMTP credentials
- live TLS validation
- live demo account
- live public URL

Those require external hosting/account access and are tracked in docs/launch-checklist.md.

### Phase 17: Portfolio and Interview Packaging

Status: COMPLETE AT REPOSITORY LEVEL

- production README
- architecture overview
- data dictionary
- model evaluation
- graph methodology
- responsible-use documentation
- ADRs
- operations runbook
- security policy
- deployment runbook
- known limitations
- reproducible local/demo bootstrap

A live-demo link will be added only after a real deployment exists.

### Phase 18: Final QA

Status: COMPLETE AT REPOSITORY LEVEL

Completed:

- backend CI green
- analytics CI green
- frontend CI green
- Playwright desktop/mobile workflow QA green
- security CI green
- development Compose valid
- production Compose valid
- no public database/graph/Redis ports in production topology
- no fake testimonials/customers/pricing
- no PHI requirement
- no unsupported regulatory claims
- no known broken primary workflow links in browser QA
- public internal footer routes verified by browser QA
- no page-level horizontal overflow in tested public and protected routes

Final QA also includes:

- committed frontend lockfile and npm ci reproducibility
- backend coverage floor
- frontend bundle-size budget
- dependency-aware readiness for PostgreSQL, Neo4j, and Redis
- production configuration validation that rejects unsafe production secrets/HTTP origins
- local Markdown-link validation
- SEO support-file browser checks
- analytics-consent browser checks
- viewport-independent mobile navigation tests

External hosting, live TLS/SMTP validation, search-engine submission, and a public demo URL remain launch-environment actions. They are not represented as completed inside the repository.

## Important Engineering Decisions

### Data

Use public-safe or synthetic claims only.

The public/demo path must never require real PHI.

### System of Record

PostgreSQL is authoritative.

Neo4j is a reproducible graph projection.

### Analytics

dbt provides trusted transformations and data-quality checks.

### Explainability

Deterministic, peer, anomaly, graph, financial, and lineage evidence remain distinct.

### Human Review

Priority ranking is investigation workload prioritization.

It is not an autonomous payment or fraud determination.

### Payments

Payments/subscriptions are intentionally out of scope.

### Public UI

The UI follows the project design rules and avoids generic marketing-template patterns.

## Current Work

The accessibility and dependency-lock release pass is complete on the PR 12 branch. The frontend lockfile was regenerated and clean installs pass. Axe assertions found primary-action contrast and graph-role violations; both were fixed without excluding rules. Full CI run 288 passed. Release records now reflect this validated implementation; the documentation commit receives its own CI validation on the PR.

## Last Updated

2026-10-06

## Latest Validation

GitHub Actions [run 288](https://github.com/SomeshZanwar/ClaimGraph-PI/actions/runs/37570827101) completed successfully on 2026-10-06 (America/Chicago; 2026-10-07 UTC), validating branch commit `34f6502eddfc4a4a9fb49f6f97842cf40161d730` through the PR merge checkout.

Validated jobs:

- Backend and Analytics: PASS
- Frontend: PASS
- Security: PASS

Validated release checks include migrations, backend tests and coverage floor, dbt, deterministic rules, Neo4j projection, network analytics, anomaly scoring, evidence/case composition, dependency readiness, frontend lint/unit/build, bundle budget, desktop/mobile Playwright QA with axe WCAG 2.1 A/AA assertions, secret scanning, dependency audits, documentation links, frontend secret-marker scanning, and development/production Compose validation. Browser QA: 29 passed, 1 intentional desktop skip for the mobile-only navigation test. Automated accessibility checks are fixture-based and do not establish complete WCAG conformance.

## Next Action

Review the accessibility release changes in PR 12. External live deployment remains optional and requires real hosting/domain/SMTP access. See docs/release-validation.md for release evidence and docs/launch-checklist.md for external launch actions.

Do not begin Project 2 until the user explicitly approves moving forward.
