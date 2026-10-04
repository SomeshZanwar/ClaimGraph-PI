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

### Pending Application/Repository Foundation

- README.md
- LICENSE
- .gitignore
- .env.example
- docker-compose.yml
- backend project scaffold
- frontend project scaffold
- CI workflows

## Current Phase

Phase 0: Product and Engineering Specification

Status: COMPLETE after this file is committed.

## Next Phase

Phase 1: Repository Foundation and Local Environment

Immediate next work:

1. choose license
2. create root repository hygiene files
3. scaffold backend
4. scaffold frontend
5. add Docker services
6. add baseline tests
7. add baseline GitHub Actions CI
8. document local setup

## Current File Being Worked On

memory.md

## Files Not Yet Worked On

Application implementation files have not been created yet.

The following planned areas remain untouched:

- backend/
- frontend/
- data/
- pipelines/
- dbt/
- risk_engine/
- ml/
- graph/
- infra/
- scripts/
- docs/decisions/
- docs/security/
- docs/runbooks/
- .github/workflows/

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

Must be fully responsive and follow the project-wide design/SEO/security requirements.

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

## Completion Tracking

### Phase 0

- [x] PRD
- [x] architecture
- [x] engineering rules
- [x] phase plan
- [x] design system
- [x] project memory

### Phase 1

- [ ] root repo files
- [ ] backend scaffold
- [ ] frontend scaffold
- [ ] Docker
- [ ] test harness
- [ ] baseline CI
- [ ] local setup documentation

### Phase 2+

Not started.

## Last Updated

2026-10-04

## Next Action

Begin Phase 1 only after verifying all six governing documents are committed and internally consistent.
