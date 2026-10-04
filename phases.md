# ClaimGraph PI Implementation Phases

## Guiding Principle

The project will be built in controlled phases. A phase is complete only when its required implementation, tests, documentation, and quality gates pass.

Application code must not jump ahead of unresolved foundational decisions.

## Phase 0: Product and Engineering Specification

### Goal

Lock the product boundaries, architecture, engineering rules, visual direction, and execution plan before application development.

### Deliverables

- PRD.md
- Architecture.md
- rules.md
- phases.md
- design.md
- memory.md

### Exit Criteria

- target users are explicit
- product scope is bounded
- architecture is coherent
- data strategy is defined
- AI boundaries are explicit
- security requirements are documented
- design anti-patterns are documented
- implementation phases are agreed
- repository state is tracked in memory.md

## Phase 1: Repository Foundation and Local Environment

### Goal

Create a reproducible engineering foundation.

### Deliverables

- README skeleton
- LICENSE
- .gitignore
- .env.example
- backend Python project
- frontend React/TypeScript project
- Dockerfiles
- docker-compose.yml
- PostgreSQL service
- Neo4j service
- optional Redis service
- backend health endpoint
- frontend application shell
- linting and formatting
- test harnesses
- GitHub Actions baseline CI

### Tests

- backend smoke test
- frontend smoke test
- container health checks
- CI executes successfully

### Exit Criteria

A new developer can clone the repository, follow documented setup, and start the stack locally.

## Phase 2: Data Source, Canonical Model, and Ingestion

### Goal

Create the real data foundation.

### Deliverables

- selected public/synthetic claims source
- source documentation
- ingestion batch model
- checksum handling
- schema validation
- raw PostgreSQL tables
- rejected/quarantined record handling
- ingestion CLI
- canonical identifier rules
- data source lineage
- ingestion metrics

### Tests

- valid source ingestion
- malformed record rejection
- duplicate batch handling
- required-field validation
- deterministic IDs
- checksum behavior

### Exit Criteria

The supported source can be ingested reproducibly with clear accepted/rejected counts.

## Phase 3: dbt Analytics and Data Quality

### Goal

Create trusted canonical analytical data.

### Deliverables

- dbt project
- source definitions
- staging models
- intermediate models
- fact and dimension models
- provider peer-group models
- claim feature mart
- dbt tests
- custom domain tests where appropriate
- generated dbt documentation

### Tests

- uniqueness
- not-null
- referential integrity
- accepted values
- domain consistency
- model row-count expectations where stable

### Exit Criteria

Risk logic no longer depends directly on raw source data.

## Phase 4: Deterministic Risk Engine

### Goal

Build transparent, versioned claim and provider risk rules.

### Deliverables

- rule contract
- rule registry
- versioned rule definitions
- duplicate detection
- repeat-service rules
- charge/peer deviation rules
- provider concentration rules
- structured risk-signal persistence
- risk-engine CLI

### Tests

- each rule positive case
- each rule negative case
- rule-version persistence
- deterministic repeated execution
- invalid configuration handling

### Exit Criteria

The platform can generate structured deterministic risk signals with evidence.

## Phase 5: Provider Peer Intelligence

### Goal

Build statistically grounded provider comparison.

### Deliverables

- peer-group definition
- robust comparison metrics
- provider profile features
- peer percentiles
- robust z-score or equivalent deviation measures
- historical trend support where source data permits
- peer evidence persistence

### Tests

- peer-group assignment
- edge cases for low-volume providers
- null/zero division handling
- stable ranking logic

### Exit Criteria

An investigator can understand how a provider differs from comparable peers.

## Phase 6: Graph Data Model and Network Analytics

### Goal

Expose suspicious multi-entity relationships that tabular analysis misses.

### Deliverables

- Neo4j schema/indexes
- relational-to-graph projection pipeline
- provider/member/facility/address/procedure nodes
- versioned relationships
- connected components
- weighted degree
- shared-member analysis
- shared-address analysis
- community detection
- bounded graph API

### Tests

- graph projection correctness
- duplicate-node prevention
- edge-count validation
- known network-pattern fixtures
- bounded query behavior
- Cypher injection resistance

### Exit Criteria

The system can produce explainable graph signals tied back to source records.

## Phase 7: Machine-Learning Risk Layer

### Goal

Add statistically validated anomaly/model signals without hiding deterministic evidence.

### Deliverables

- feature-generation pipeline
- point-in-time feature rules
- baseline anomaly model
- supervised model only if labels justify it
- training pipeline
- evaluation report
- MLflow tracking
- model artifact versioning
- inference module
- local explanations where supported

### Evaluation

At minimum assess:

- precision
- recall
- PR-AUC where labels exist
- score distribution
- calibration if probability is exposed
- top-k capture where meaningful
- analyst workload implications

### Tests

- feature schema
- deterministic preprocessing
- no leakage checks
- model artifact loading
- scoring contract
- threshold behavior

### Exit Criteria

ML outputs are reproducible, versioned, and clearly separated from deterministic evidence.

## Phase 8: Evidence Composer and Case Prioritization

### Goal

Turn signals into investigator-ready cases.

### Deliverables

- evidence schema
- composite case representation
- transparent prioritization logic
- financial exposure estimate
- case creation/upsert
- case status model
- audit events
- priority explanation

### Tests

- ranking determinism
- evidence-source preservation
- no black-box-only ranking
- status transitions
- audit trail

### Exit Criteria

High-risk claims/providers can be ranked without losing signal provenance.

## Phase 9: Authentication, Authorization, and User Model

### Goal

Implement secure access before exposing case data.

### Deliverables

- user model
- roles
- secure password hashing
- login
- logout
- session expiry
- public signup only if full verification flow is included
- password reset
- verification flow if signup enabled
- rate limiting
- object-level authorization
- audit logging

### Tests

- valid login
- invalid login
- brute-force/rate-limit behavior
- expired session
- password reset
- token single-use
- cross-user access denial
- role restriction

### Exit Criteria

Protected data cannot be accessed without correct authentication and authorization.

## Phase 10: Investigator API

### Goal

Provide a stable typed API for the investigator workflow.

### Deliverables

- paginated case queue
- case detail
- provider profile
- search
- graph endpoint
- notes
- status changes
- dispositions
- audit endpoint for authorized users
- consistent error responses
- OpenAPI review

### Tests

- success paths
- validation failures
- auth failures
- authorization failures
- pagination
- search abuse cases
- graph limits
- mutation audit events

### Exit Criteria

The primary product workflow is complete at the API layer.

## Phase 11: Investigator Web Application

### Goal

Create the actual working product interface.

### Deliverables

- responsive application shell
- mobile navigation
- investigation queue
- filtering/sorting
- case detail
- risk-signal breakdown
- provider peer view
- graph explorer
- notes
- status/disposition workflow
- success/error states
- analytics overview where useful
- support route
- bug-report route
- custom 404

### Required Responsive Checks

- mobile
- tablet
- laptop
- desktop
- no horizontal overflow

### Exit Criteria

An investigator can complete the end-to-end review workflow without direct database/API interaction.

## Phase 12: Public Product Surface, Legal, SEO, and Accessibility

### Goal

Make the deployed product complete and discoverable.

### Deliverables

- public overview page
- real demo entry point
- favicon
- social preview image
- page titles
- meta descriptions
- canonical tags
- sitemap.xml
- robots.txt
- llms.txt where appropriate
- schema markup where appropriate
- privacy policy
- terms of service
- cookie consent if required
- alt text
- image compression
- clean URL slugs
- footer links
- current copyright year

### Tests

- broken links
- metadata checks
- 404 behavior
- responsive checks
- contrast review
- heading hierarchy
- keyboard navigation
- no accidental noindex

### Exit Criteria

The public-facing product meets the agreed UX, SEO, accessibility, and legal-page requirements.

## Phase 13: Observability and Operations

### Goal

Make failures visible and diagnosable.

### Deliverables

- structured logging
- request correlation IDs
- application metrics
- database health
- graph health
- ingestion metrics
- scoring-job metrics
- worker health if applicable
- operational runbook
- safe error handling
- alerts supported by deployment environment where feasible

### Exit Criteria

Core application failures can be identified without exposing sensitive data.

## Phase 14: Security Hardening

### Goal

Validate the application's trust boundaries.

### Deliverables

- dependency scanning
- secret scanning
- auth abuse checks
- input validation review
- SQL/Cypher injection checks
- CORS review
- secure headers
- cookie review
- rate-limit review
- upload protections if upload exists
- authorization matrix
- frontend secret review

### Exit Criteria

Known high-risk application paths have explicit controls and negative tests.

## Phase 15: Performance and Reliability

### Goal

Ensure the demo remains responsive and stable under realistic portfolio/demo load.

### Deliverables

- query analysis
- index review
- bounded graph queries
- pagination
- API latency measurements
- frontend bundle review
- image optimization
- Core Web Vitals review
- background-job boundaries
- failure/retry behavior

### Exit Criteria

No obvious avoidable performance bottlenecks remain in primary flows.

## Phase 16: Deployment and Demo Validation

### Goal

Deploy the real product and validate it end to end.

### Deliverables

- HTTPS deployment
- production environment configuration
- managed database configuration
- public-safe demo data
- database migrations
- frontend deployment
- backend deployment
- health checks
- deployed E2E smoke test
- no frontend secrets
- real demo path

### Exit Criteria

A reviewer can use the deployed primary workflow without local setup.

## Phase 17: Portfolio and Interview Packaging

### Goal

Make the repository easy to evaluate technically.

### Deliverables

- completed README
- architecture diagram
- screenshots
- demo walkthrough
- data dictionary
- model evaluation summary
- graph methodology
- security summary
- known limitations
- roadmap
- selected ADRs
- reproducible local setup
- live demo links

### Exit Criteria

A reviewer can understand the product, architecture, evidence, tradeoffs, and limitations from the repository.

## Phase 18: Final QA

### Checklist

- no broken links
- no broken buttons
- no placeholders
- no horizontal scrolling
- mobile/tablet/laptop/desktop checked
- legal pages work
- metadata correct
- favicon works
- sitemap/robots valid
- all required tests green
- CI green
- no secrets
- no fake claims
- no dead navigation
- no stale docs
- memory.md accurate

### Final Definition of Done

The project is complete only when implementation, deployment, tests, documentation, security controls, responsive UI, and real workflow all agree with what the repository claims.
