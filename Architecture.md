# ClaimGraph PI Architecture

## 1. Architecture Goals

ClaimGraph PI is a production-style healthcare payment-integrity investigation platform with explicit separation between source ingestion, analytical transformation, deterministic rules, statistical and ML scoring, graph analytics, case-management workflows, user-facing investigation tools, and audit/observability.

The architecture must remain explainable, testable, secure, and deployable by one developer without pretending to operate at payer production scale.

## 2. High-Level Application Flow

~~~text
Public / Synthetic Claims Data
            |
            v
    Ingestion + Validation
            |
            v
       PostgreSQL Raw
            |
            v
      dbt Transformations
            |
            v
     Canonical Claims Mart
       |       |       |
       v       v       v
 Rule Engine  ML      Graph Projection
       |       |       |
       |       v       v
       |   Risk Signals  Neo4j
       |       |       |
       +-------+-------+
               |
               v
        Evidence Composer
               |
               v
         Case Prioritizer
               |
               v
      FastAPI Application API
          |             |
          v             v
 React Investigator UI  Audit / Metrics
~~~

## 3. Core Components

### 3.1 Ingestion Service

Responsibilities:

- download or accept supported public/synthetic claims source files
- verify file type and expected schema
- calculate source checksums
- assign ingestion batch IDs
- parse records
- validate required values and types
- separate accepted and quarantined records
- load accepted raw records into PostgreSQL
- persist ingestion statistics and errors

Implementation:

- Python
- Polars preferred for file-level processing, pandas where compatibility requires it
- SQLAlchemy for controlled writes where appropriate
- optimized PostgreSQL bulk loading
- Pydantic models for request and configuration validation

No raw source file is trusted without validation.

### 3.2 PostgreSQL

PostgreSQL is the system of record for:

- ingestion metadata
- canonical claims data
- provider, member, and facility reference data
- risk signals
- model scoring results
- cases
- investigation notes
- user and account data
- audit events
- workflow state

Logical schemas:

~~~text
raw
staging
analytics
risk
casework
auth
audit
~~~

### 3.3 dbt Transformation Layer

dbt Core transforms validated raw claims into canonical analytical models.

~~~text
raw source tables
      |
      v
stg_claims
stg_claim_lines
stg_providers
stg_members
      |
      v
int_claim_service_events
int_provider_utilization
int_provider_peer_groups
      |
      v
fact_claims
fact_claim_lines
dim_provider
dim_member
dim_facility
mart_provider_peer_metrics
mart_claim_features
~~~

dbt tests validate uniqueness, not-null keys, accepted values, referential integrity, domain-specific consistency rules supported by the dataset, and source freshness where supported.

### 3.4 Deterministic Rule Engine

A Python rule engine evaluates versioned, testable rules.

Initial rule configuration:

~~~text
rules/
  duplicate_claim.yaml
  repeat_service.yaml
  charge_outlier.yaml
~~~

Each rule returns:

- rule ID
- version
- entity type
- entity ID
- severity
- evidence
- explanation template
- evaluated timestamp

Rules may call SQL or Python computations, but outcomes must remain deterministic.

### 3.5 Feature Engineering Layer

Features are created from canonical data, never directly from unvalidated source rows.

Feature groups:

- claim-level monetary features
- utilization features
- temporal features
- provider peer-deviation features
- member concentration features
- procedure mix features
- graph-derived features

Training features must preserve point-in-time correctness where future information could create leakage.

### 3.6 ML Scoring Service

Initial ML implementation:

- unsupervised anomaly baseline for sparse or no-label use cases
- supervised gradient-boosted model only if a defensible label strategy is available
- probability calibration where probabilities are exposed
- SHAP or native attribution where appropriate
- persisted feature schema
- persisted model metadata

MLflow is used for experiment tracking, parameters, metrics, artifacts, and model version references.

Production scoring results in PostgreSQL reference the exact model version and feature snapshot.

### 3.7 Graph Projection and Analytics

Neo4j is the graph store for relationship analysis.

Initial node types:

- Provider
- Member
- Facility
- Address
- Procedure
- Organization

Initial relationship types:

- TREATED
- BILLED_FOR
- PRACTICES_AT
- LOCATED_AT
- PERFORMED
- AFFILIATED_WITH

Graph data is projected from validated canonical relational data.

Initial analytics:

- connected components
- weighted degree
- shared-member concentration
- shared-address patterns
- community detection
- suspicious relationship density
- graph-derived provider features

NetworkX may be used for unit-testable algorithms or offline analysis where Neo4j Graph Data Science is unnecessary.

### 3.8 Evidence Composer

The evidence composer assembles a structured case evidence object from:

- deterministic rule signals
- peer analytics
- ML output
- graph signals
- financial exposure
- source lineage

No LLM participates in deciding whether a signal is true.

### 3.9 Case Prioritization

The prioritizer turns evidence into an investigation queue.

Ranking considers explicitly documented factors such as:

- signal severity
- signal count
- financial exposure
- graph risk
- model score
- provider history

The ranking algorithm must be inspectable and testable.

### 3.10 FastAPI Backend

FastAPI provides:

- authentication endpoints
- case queue API
- case detail API
- provider profile API
- graph exploration API
- search API
- investigation workflow mutations
- audit API for authorized users
- health and readiness endpoints
- internal or admin endpoints where needed

Backend stack:

- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- psycopg
- structured logging
- rate limiting
- Argon2id password hashing
- secure HttpOnly session or access-cookie strategy

### 3.11 Background Jobs

Long-running tasks should not block HTTP requests.

Candidates:

- dataset ingestion
- dbt execution
- ML scoring batches
- graph projection
- scheduled metric refresh

Initial implementation may use Celery and Redis. If project complexity shows Celery is unnecessary for the scoped release, a smaller durable job runner may replace it. That decision must be documented before implementation.

### 3.12 Frontend

Frontend stack:

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- accessible form utilities
- Cytoscape.js for graph visualization
- a restrained charting library only where charts add analytical value
- custom CSS or CSS Modules using design tokens

The UI will not use a generic dashboard template.

Primary screens:

- product overview and demo entry
- authentication
- investigation queue
- case detail
- provider profile
- graph explorer
- analytics and operational overview
- support and feedback
- privacy
- terms
- 404

### 3.13 Authentication

~~~text
Browser
  |
  | HTTPS
  v
FastAPI
  |
  +-- password hash verification
  +-- session or access token issuance
  +-- secure HttpOnly cookie
  +-- CSRF protection where applicable
  |
  v
PostgreSQL auth tables
~~~

Public signup is included only if verification and reset flows are implemented end to end.

Local development email flows can use Mailpit. Production email-provider integration must be environment-driven.

### 3.14 Audit

Audit records should be append-oriented.

Important events:

- authentication outcome
- case assignment
- status changes
- notes
- disposition
- rule runs
- scoring runs
- ingestion jobs
- administrative changes

Audit event payloads must avoid secrets and unnecessary sensitive values.

### 3.15 Observability

Required signals:

- structured logs
- request latency
- request count
- error count
- background-job status
- ingestion statistics
- scoring job statistics
- database health
- graph query latency

Preferred tools:

- OpenTelemetry instrumentation where practical
- Prometheus-compatible metrics
- Grafana for local observability or deployment-compatible equivalent
- frontend error reporting only if configured without sensitive data leakage

## 4. Security Architecture

Trust boundaries:

~~~text
Internet
   |
   v
Frontend
   |
   | HTTPS only
   v
API boundary
   |
   +-- validation
   +-- authentication
   +-- authorization
   +-- rate limiting
   |
   +----------+
   |          |
   v          v
Postgres    Neo4j
   |
   v
Worker
~~~

Rules:

- frontend never receives backend credentials
- browser never connects directly to PostgreSQL or Neo4j
- protected APIs perform object-level authorization
- model-provider calls, if later introduced, occur server-side
- secrets are environment-driven
- CORS is allowlisted
- production cookies are secure
- database accounts follow least privilege
- graph query inputs are parameterized
- uploaded files are type and size constrained
- no raw stack traces are returned to clients

## 5. Deployment Architecture

### Local development

Docker Compose should provide:

- PostgreSQL
- Neo4j
- Redis if background jobs require it
- Mailpit if email flows are enabled
- backend
- worker
- frontend

MLflow may run as a local service or file-backed development tracker initially.

### Public demo

~~~text
Static or edge-hosted frontend
          |
        HTTPS
          |
Containerized FastAPI service
     |              |
Managed Postgres   Managed Neo4j
     |
Worker or scheduled jobs as required
~~~

Deployment provider will be selected based on low-cost feasibility, service limits, persistent storage requirements, and operational simplicity.

The deployed demo must use only public-safe or synthetic data.

## 6. Repository Structure

Target structure:

~~~text
ClaimGraph-PI/
|
+-- PRD.md
+-- Architecture.md
+-- rules.md
+-- phases.md
+-- design.md
+-- memory.md
+-- README.md
+-- LICENSE
+-- .gitignore
+-- .env.example
+-- docker-compose.yml
|
+-- backend/
|   +-- pyproject.toml
|   +-- alembic.ini
|   +-- app/
|   +-- migrations/
|   +-- tests/
|
+-- frontend/
|   +-- package.json
|   +-- vite.config.ts
|   +-- src/
|   +-- public/
|   +-- e2e/
|
+-- data/
|   +-- README.md
|   +-- raw/
|   +-- reference/
|   +-- samples/
|
+-- pipelines/
|   +-- ingest/
|   +-- validation/
|   +-- graph_projection/
|
+-- dbt/
|   +-- dbt_project.yml
|   +-- models/
|   +-- tests/
|   +-- macros/
|   +-- seeds/
|
+-- risk_engine/
|   +-- rules/
|   +-- peer_analysis/
|   +-- scoring/
|   +-- tests/
|
+-- ml/
|   +-- features/
|   +-- training/
|   +-- evaluation/
|   +-- inference/
|   +-- tests/
|
+-- graph/
|   +-- projections/
|   +-- analytics/
|   +-- tests/
|
+-- infra/
|   +-- docker/
|   +-- deployment/
|   +-- monitoring/
|
+-- scripts/
+-- docs/
|   +-- decisions/
|   +-- diagrams/
|   +-- security/
|   +-- runbooks/
|
+-- .github/
    +-- workflows/
    +-- ISSUE_TEMPLATE/
    +-- PULL_REQUEST_TEMPLATE.md
~~~

The structure is a target. Empty directories or abstractions must not be created before they have a real responsibility.

## 7. Technology Stack

| Layer | Technology |
|---|---|
| Primary language | Python 3.12+ |
| API | FastAPI |
| Validation | Pydantic |
| Relational ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Relational database | PostgreSQL |
| Analytics transforms | dbt Core |
| Dataframe processing | Polars preferred, pandas where compatibility requires it |
| Graph database | Neo4j |
| Offline graph analytics | NetworkX where appropriate |
| ML | scikit-learn, LightGBM or XGBoost if justified |
| Explainability | SHAP where model-compatible |
| Experiment tracking | MLflow |
| Background jobs | Celery + Redis if justified |
| Frontend | React + TypeScript + Vite |
| Data fetching | TanStack Query |
| Graph UI | Cytoscape.js |
| Backend tests | pytest |
| Frontend tests | Vitest + Testing Library |
| End-to-end tests | Playwright |
| Containers | Docker and Docker Compose |
| CI | GitHub Actions |
| Observability | structured logs plus OpenTelemetry or Prometheus where appropriate |

## 8. Data Flow

Batch analytical flow:

~~~text
Source dataset
   -> checksum
   -> schema validation
   -> raw tables
   -> dbt staging
   -> canonical marts
   -> risk features
   -> rules / ML / graph
   -> risk signals
   -> case ranking
~~~

Investigator request flow:

~~~text
Browser
   -> authenticated API request
   -> authorization
   -> validated query
   -> PostgreSQL / Neo4j
   -> typed API response
   -> UI
~~~

Case mutation flow:

~~~text
Investigator action
   -> validate
   -> authorize
   -> transactional state change
   -> append audit event
   -> response
~~~

## 9. API Design Principles

- version application APIs under /api/v1
- typed request and response contracts
- consistent error envelope
- pagination for list endpoints
- bounded graph queries
- idempotency where retries could duplicate work
- explicit authorization checks
- no database implementation details exposed in response contracts
- OpenAPI generated from FastAPI and kept usable

Example endpoints:

~~~text
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/cases
GET    /api/v1/cases/{case_id}
PATCH  /api/v1/cases/{case_id}
POST   /api/v1/cases/{case_id}/notes
GET    /api/v1/providers/{provider_id}
GET    /api/v1/providers/{provider_id}/graph
GET    /api/v1/search
GET    /api/v1/health
~~~

## 10. Data and ML Boundaries

- raw data cannot feed UI or models directly
- dbt validation failures must be observable
- model features are versioned
- training code is separate from inference code
- graph projection is reproducible
- no model score is treated as a final enforcement decision
- no future outcome data may leak into a historical prediction
- evaluation data remains isolated from training

## 11. Architecture Decision Records

Material architecture changes should be documented under docs/decisions/.

Examples:

- ADR-001 graph database selection
- ADR-002 authentication strategy
- ADR-003 risk-ranking design
- ADR-004 background-job framework
- ADR-005 deployment topology

Each ADR should capture context, decision, alternatives, tradeoffs, and consequences.

## 12. Definition of Production-Style

For this project, production-style means:

- reproducible environment
- meaningful tests
- migrations
- explicit configuration
- secure defaults
- structured errors
- CI
- observability
- realistic data flow
- documented architecture
- deployable services
- real primary workflow

It does not mean claiming HIPAA certification, payer-scale throughput, or regulatory approval that the project has not earned.
