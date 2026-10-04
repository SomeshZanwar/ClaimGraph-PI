# ClaimGraph PI Project Memory

## Project

ClaimGraph PI

## Current Objective

Build a production-style pre-payment healthcare claims investigation and provider network intelligence platform.

The system will combine deterministic claim rules, provider peer analytics, machine-learning anomaly/risk signals, graph analytics, financial exposure, and a human investigator workflow.

## Core Product Boundary

The product is an investigation and decision-support system.

It will not autonomously deny claims, make clinical decisions, claim regulatory certification, or use real PHI in the public demo.

## Target Users

- Payment Integrity Analysts
- SIU Investigators
- Healthcare Data Analysts
- Healthcare Data Scientists
- Coding/Documentation Analysts
- Payment Integrity Managers
- Compliance/Audit users

## Planned Major Components

- reproducible claims ingestion
- canonical PostgreSQL data model
- dbt analytical layer
- deterministic risk-rule engine
- provider peer analytics
- Neo4j relationship graph
- graph risk analytics
- ML anomaly/risk layer
- MLflow experiment/model tracking
- evidence composer
- case prioritization
- secure FastAPI API
- authentication and authorization
- investigator React application
- case queue
- provider profile
- graph explorer
- audit trail
- observability
- legal/support pages
- SEO and public product surface
- deployment

## Governing Documents

### Completed

- PRD.md
- Architecture.md
- rules.md
- phases.md
- design.md
- memory.md

## Phase Status

### Phase 0: Product and Engineering Specification

Status: COMPLETE

Completed:

- PRD
- architecture
- engineering rules
- implementation phases
- design system
- project memory

### Phase 1: Repository Foundation and Local Environment

Status: COMPLETE

Completed:

- README foundation
- Apache-2.0 license
- .gitignore
- .env.example
- FastAPI backend scaffold
- typed runtime configuration
- backend health endpoints
- backend pytest harness
- React + TypeScript + Vite frontend scaffold
- IBM Plex typography foundation
- responsive application shell
- mobile navigation
- custom 404 route
- route-specific page titles
- favicon
- valid empty-state copy
- Dockerfiles
- SPA Nginx routing
- Docker Compose with PostgreSQL, Neo4j, Redis, Mailpit, backend, and frontend
- frontend unit-test harness
- ESLint configuration
- GitHub Actions baseline CI
- local setup documentation
- current frontend dependency refresh
- CI validated successfully after TypeScript configuration fix

Open Phase 1 follow-up:

- generate and commit a frontend lockfile after final dependency resolution can be materialized locally

This follow-up does not block Phase 2 because CI resolves and validates the dependency set, but it remains a repository reproducibility improvement required before final release.

## Current Phase

Phase 2: Data Source, Canonical Model, and Ingestion

Status: COMPLETE

## Next Work

Completed in Phase 2 so far:

- CMS DE-SynPUF Carrier Claims selected as the primary source
- source provenance and limitations documented
- Sample 2 source manifest added
- raw ingestion batch contract created
- PostgreSQL raw claim/claim-line/rejection models created
- initial Alembic migration added
- streaming ZIP/CSV reader implemented
- claim and line-slot parser implemented
- invalid-row quarantine path implemented
- ingestion CLI implemented
- parser and ZIP-streaming tests added

Completed validation:

- PostgreSQL service runs in CI
- Alembic migration is applied in CI
- repository-safe CMS-shaped fixture added
- end-to-end database ingestion test added
- malformed row quarantine verified
- latest Phase 2 CI is green
- ingestion commands and expected metrics documented in README

## Current File Being Worked On

secure user, session, verification, reset, rate-limit, and authorization layer

## Files/Areas Not Yet Worked On

- data source implementation
- backend database models
- Alembic migrations
- pipelines/ingest
- pipelines/validation
- dbt project
- risk_engine
- ml
- graph projection
- investigator case APIs
- authentication flows
- provider APIs
- investigator UI
- legal pages
- support/bug-report pages
- analytics tracking
- SEO launch files
- observability implementation
- deployment

## Important Engineering Decisions So Far

### Product Scope

The first version focuses on pre-payment investigation and evidence presentation rather than full claims adjudication.

### Data

The public/demo system will use public-safe or synthetic claims-like data.

No real PHI will be committed.

### Relational Store

PostgreSQL is the system of record.

### Analytics Modeling

dbt Core will provide transformation and data-quality layers.

### Graph Store

Neo4j is the primary relationship graph.

NetworkX may support offline/unit-testable graph analysis.

### API

FastAPI.

### Frontend

React + TypeScript + Vite.

### ML

scikit-learn baseline, with LightGBM/XGBoost only when justified.

MLflow for experiment/model metadata.

### Explainability

Structured rule, peer, graph, and ML evidence remains separate.

No black-box-only case score.

### AI

Any AI feature is secondary to structured evidence and cannot make enforcement decisions.

### Payments

Out of scope.

### Public UI

Must be fully responsive and follow the project-wide design, SEO, accessibility, legal, and security requirements.

## Non-Negotiable UI Rules

- no horizontal page scrolling
- no mobile overflow
- mobile menu
- favicon
- correct page titles
- meta descriptions
- working footer links
- current copyright year
- compressed images
- custom 404
- working buttons
- success and error messages
- no placeholders in shipped UI
- no dead navigation
- clickable logo
- clickable contact details where shown
- mobile/tablet/laptop/desktop optimized

## Non-Negotiable Design Avoidances

Avoid generic AI/startup-template patterns, including harsh gradients, pure white backgrounds, drop shadows, bento grids, neon palettes, generic purple/black AI branding, excessive rounded cards, fake testimonials, decorative terminals, emojis, sparkle icons, radial orbs, dot grids, liquid glass, and gratuitous motion.

Do not use Inter, Geist, or Space Grotesk.

## Non-Negotiable Security Rules

- no frontend secrets
- no secrets in Git
- HTTPS in production
- input validation
- SQL and Cypher parameterization
- secure authentication
- rate limiting
- object-level authorization
- no IDOR
- security-relevant logging
- safe error messages
- abuse protection
- dependency and secret scanning
- no PHI in public/demo data

## SEO/Public Product Requirements

As applicable:

- sitemap.xml
- robots.txt
- canonical tags
- meta titles
- meta descriptions
- one H1 per public page
- correct heading hierarchy
- alt text
- schema markup
- internal links
- clean URL slugs
- image compression
- Core Web Vitals review
- HTTPS
- llms.txt where appropriate
- social preview image
- Privacy Policy
- Terms of Service
- contact/support
- bug report

## Repository Provenance Rule

The repository must not include unnecessary AI branding, generated-by-AI language, Copilot-agent attribution, or fake development history.

Development should proceed incrementally with meaningful commits.

No false authorship claims should be added.

## Last Updated

2026-10-04

## Phase 3 Completion

Phase 3 is COMPLETE.

Implemented and validated:

- dbt source definitions for raw ingestion tables
- staging models for batches, claims, and claim lines
- canonical claim service-event intermediate model
- claim-line fact
- claim-level fact
- synthetic provider dimension
- provider operational claim metrics mart
- schema and custom date-order tests
- schema naming aligned to architecture
- dbt connection validation in CI
- dbt build and tests against PostgreSQL fixture in CI
- latest analytics CI run green

## Phase 4 Completion

Phase 4 is COMPLETE.

Implemented and validated:

- versioned YAML rule definitions
- deterministic rule loader and ruleset hashing
- persistent rule-run and risk-signal tables
- exact duplicate claim review rule
- repeated identical line review rule
- rapid repeat service review rule
- payment/allowed-charge consistency review rule
- structured evidence payloads
- deterministic risk CLI
- safe fixture signals verified in CI
- risk language explicitly avoids declaring fraud as fact

## Phase 5 Completion

Phase 5 is COMPLETE.

Implemented and validated:

- dominant HCPCS behavioral profile per synthetic provider
- explicit operational peer assignment
- volume bands
- provider peer cohort key
- peer cohort size
- peer median allowed-charge baseline
- median absolute deviation
- robust z-score only for sufficiently sized cohorts
- explicit INSUFFICIENT_COHORT and NO_VARIATION states
- dbt test preventing peer scores for undersized cohorts
- CI green

Important limitation: DE-SynPUF NPIs are synthetic. These cohorts are behavioral comparison groups, not clinical specialty classifications.

## Phase 6 Completion

Phase 6 is COMPLETE.

Implemented and validated:

- PostgreSQL graph-run metadata and provider graph-metric tables
- Neo4j constraints
- idempotent managed graph projection
- Member, Claim, Provider, and Procedure nodes
- Member-to-Claim, Claim-to-Provider, and Claim-to-Procedure relationships
- source snapshot hashing
- bounded batch projection
- NetworkX provider-member bipartite analytics
- shared-provider counts
- maximum shared-member overlap
- connected-component provider/member counts
- persisted graph metrics
- graph unit tests
- real Neo4j service in CI
- graph projection and verification green in CI

Current dataset limitation: Carrier claims do not provide reliable facility/address entities for this synthetic graph, so those node types are not fabricated.

## Phase 7 Completion

Phase 7 is COMPLETE.

Implemented and validated:

- canonical claim ML feature mart
- versioned Isolation Forest anomaly model
- source snapshot hash
- explicit feature schema
- production minimum training-row guard
- fixture-only small-data override for CI
- deterministic random seed
- persisted model-run metadata
- persisted claim anomaly scores
- anomaly threshold
- descriptive feature-deviation context
- MLflow experiment tracking using SQLite-backed tracking
- local model artifact persistence
- unit tests for reproducibility and explanation labeling
- end-to-end model training/scoring verification in CI
- no fabricated fraud labels or supervised accuracy claims

## Phase 8 Completion

Phase 8 is COMPLETE.

Implemented and validated:

- investigation case table
- immutable evidence-version table keyed by evidence hash
- rule-signal to claim mapping
- latest model signal composition
- provider peer evidence
- provider network evidence
- financial exposure
- source-file lineage
- transparent priority components
- queue priority bands
- explicit statement that priority is not a fraud probability
- idempotent evidence-version handling
- unit tests for scoring and evidence hashing
- case composition and evidence verification in CI

## Next Action

Implement secure users, roles, Argon2id passwords, opaque expiring sessions, email verification, password reset, Redis-backed abuse protection, CSRF checks, audit events, and case assignment authorization.
