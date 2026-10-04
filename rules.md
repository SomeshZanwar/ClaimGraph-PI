# ClaimGraph PI Engineering Rules

## 1. Purpose

This file defines the non-negotiable engineering, product, security, design, and operational rules for ClaimGraph PI.

If implementation decisions conflict with this file, this file wins unless the change is documented through an architecture decision record and reflected here.

## 2. Product Boundaries

ClaimGraph PI is an investigation and decision-support system for pre-payment healthcare claims analysis.

It must not:

- autonomously deny or approve healthcare claims
- present itself as a clinical decision system
- claim HIPAA certification or regulatory approval
- process real PHI in the public demo
- fabricate provider, payer, customer, testimonial, or performance claims
- imply production payer integrations that do not exist
- present synthetic labels as real fraud ground truth

Human review remains mandatory for investigation disposition.

## 3. Approved Core Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- psycopg

### Analytics

- dbt Core
- Polars preferred
- pandas only where library compatibility or established tooling makes it more practical
- NumPy
- SciPy where statistically justified

### Machine Learning

- scikit-learn
- LightGBM or XGBoost only where justified by data and evaluation
- SHAP where compatible and useful
- MLflow for experiment tracking and model-version metadata

### Graph

- Neo4j
- NetworkX for local/offline algorithm validation where appropriate
- Cytoscape.js for investigator-facing graph visualization

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- CSS Modules or carefully scoped custom CSS
- semantic HTML

### Testing

- pytest
- pytest-cov
- Vitest
- Testing Library
- Playwright

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- OpenTelemetry and Prometheus-compatible metrics where practical

## 4. Libraries and Dependency Rules

- use the smallest dependency that solves the real requirement
- do not add libraries for trivial utility functions
- pin production dependencies through an appropriate lockfile
- do not use abandoned packages
- do not add duplicate libraries that solve the same problem without a documented reason
- evaluate licenses before adding uncommon dependencies
- avoid framework churn during a phase unless a real blocker exists
- do not use large UI component frameworks by default
- do not use a generic admin/dashboard theme

## 5. Coding Standards

### Python

- use type hints on public functions and application boundaries
- prefer small, cohesive modules
- separate domain logic from framework glue
- use Pydantic models at API/config boundaries
- keep database access in repository/service layers rather than directly inside route handlers
- use context managers for resources
- use timezone-aware datetimes
- use Decimal or database numeric types for financial values where precision matters
- do not silently coerce invalid healthcare identifiers or money values
- do not swallow exceptions

### TypeScript

- strict TypeScript
- no implicit any
- typed API clients
- feature-level separation
- no business logic hidden inside presentational components
- accessible interactive elements
- no duplicated API request logic across pages

### SQL

- explicit grain for every analytical model
- parameterized application queries
- no SELECT * in production application queries
- aliases must be readable
- indexes must be justified by query patterns
- no business-critical metric without a documented definition

## 6. Error Handling

All errors must be intentional and observable.

### Backend

Use a consistent error envelope with:

- machine-readable code
- human-readable message
- request/correlation ID
- optional field-level details

Never expose:

- stack traces
- SQL statements containing sensitive values
- environment values
- secrets
- internal hostnames
- authentication tokens

### Frontend

Every asynchronous flow must account for:

- loading
- success
- empty state
- validation error
- authorization failure
- network failure
- server failure

Do not use generic messages such as "Something went wrong" where a safer, more useful explanation is available.

### Data Pipelines

Bad records must be quarantined or rejected with explicit reasons.

Do not silently drop rows.

## 7. Security Rules

### Secrets

- no secrets in frontend code
- no secrets committed to Git
- no real credentials in examples
- use environment variables or a deployment secret manager
- provide only placeholder variable names in .env.example
- secret values must never appear in logs

### Authentication

If public authentication is enabled:

- use Argon2id or a current secure password-hashing standard
- use expiring sessions or tokens
- secure cookies in production
- HttpOnly where applicable
- SameSite configured deliberately
- CSRF protection where the auth/session design requires it
- login rate limiting
- reset-token expiration and single use
- email verification if public signup is enabled
- generic login/reset responses where user-enumeration risk exists

### Authorization

- authorization must occur server-side
- object-level authorization is mandatory
- never trust user-supplied ownership identifiers
- test cross-user access explicitly
- administrative actions must require explicit role checks

### API Security

- validate all request payloads
- validate query/path parameters
- use bounded pagination
- rate limit abuse-sensitive endpoints
- restrict CORS
- enforce HTTPS in production
- use secure headers
- validate content type
- set upload size limits
- reject unexpected file extensions and MIME types
- use parameterized Cypher and SQL

### Logging

Log:

- authentication failures
- authorization failures
- rate-limit events
- application errors
- data ingestion failures
- suspicious request patterns

Do not log:

- passwords
- reset tokens
- access tokens
- raw secrets
- unnecessary claims payloads
- unnecessary personal identifiers

## 8. Healthcare Data Rules

- public demo must use public-safe or synthetic data only
- do not commit PHI
- identifiers in demo data must not correspond to real patients
- source lineage must be preserved
- raw data is immutable after successful ingestion
- transformed data must be reproducible
- domain assumptions must be documented
- synthetic labels must be labeled synthetic
- coding-rule claims must be limited to what the implemented data and logic support

## 9. Data Quality Rules

Every critical dataset must define:

- grain
- primary or natural key
- required fields
- accepted ranges or values where appropriate
- freshness expectation where relevant
- referential integrity expectations

Quality failures must be visible.

Do not allow known failed quality checks to disappear from reports without an explicit resolution record.

## 10. ML Rules

### Training

- split strategy must reflect the temporal nature of the task where applicable
- prevent target leakage
- prevent future-data leakage
- keep training and evaluation sets isolated
- record model configuration
- record feature schema
- record data snapshot/version
- record evaluation metrics

### Evaluation

Do not optimize on accuracy alone.

Use metrics appropriate for highly imbalanced risk detection, such as:

- precision
- recall
- PR-AUC
- ROC-AUC where useful
- calibration
- top-k capture
- cost-sensitive metrics
- analyst workload impact

### Explainability

- model explanation must reference actual model inputs
- do not invent explanations
- distinguish global and local importance
- do not present SHAP values as causal evidence
- preserve deterministic risk signals separately from ML signals

### Model Governance

- every production/demo score must reference a model version
- thresholds must be versioned
- model changes require evaluation evidence
- no model may automatically deny a claim
- model output is advisory evidence

## 11. Graph Rules

- graph relationships must be derived from source/canonical data, not invented
- bound all interactive graph queries
- cap node/edge counts in UI responses
- parameterize Cypher
- distinguish direct relationships from inferred relationships
- graph risk must be explainable
- community membership is not proof of fraud
- centrality is not proof of fraud
- network patterns must be presented as investigation signals

## 12. AI Usage Boundaries

AI features are optional and subordinate to structured evidence.

Allowed:

- plain-language summarization of structured evidence
- investigator-facing explanation of rule/model/graph signals
- documentation assistance inside the product if grounded in approved sources

Not allowed:

- deciding whether a claim is fraudulent
- denying a claim
- inventing missing evidence
- generating unvalidated SQL or Cypher and executing it
- sending PHI, credentials, or secrets to external model providers
- modifying risk evidence without an auditable deterministic source

If an AI explanation is shown:

- the underlying evidence must be viewable
- generated text must be labeled as an explanation, not primary evidence
- failures must degrade gracefully to the structured evidence view

## 13. Frontend and UX Rules

Required:

- no horizontal scrolling at supported breakpoints
- mobile menu where navigation collapses
- clickable logo
- clickable contact information where displayed
- correct page titles
- meta descriptions
- favicon
- responsive layouts
- accessible contrast
- visible focus states
- custom 404 page
- working footer links
- current copyright year
- success states
- error states
- form validation
- no placeholder text in shipped surfaces
- no unused navigation
- no broken buttons
- no broken links
- compressed images
- descriptive alt text

Every page must be usable on:

- mobile
- tablet
- laptop
- desktop

## 14. Design Anti-Patterns

Avoid:

- harsh gradients
- Lucide-heavy icon-driven layouts
- pure white backgrounds
- rainbow coloring
- drop shadows
- repetitive three-feature-card rows
- emojis in product UI
- liquid-glass effects
- em dashes in product copy
- Inter
- Geist
- Space Grotesk
- colored left stripes
- fake testimonials
- bento grids
- decorative terminal windows
- "it's not X, it's Y" copy
- checkmark-bullet marketing sections
- generic three-tier pricing
- fake product demos
- excessively soft corner radii
- purple-and-black AI branding
- skeleton loaders as a substitute for fast interactions
- radial orbs
- dot grids
- sparkle icons
- animated arrows
- missing terms
- missing privacy policy
- gratuitous hover animations
- neon colors
- generic pastel palettes

## 15. CTA Rule

Use a single primary CTA color across the product.

Secondary and tertiary actions must not compete visually with the primary action.

## 16. SEO and Public-Site Rules

For public pages where applicable:

- sitemap.xml
- robots.txt
- canonical tags
- meta titles
- meta descriptions
- exactly one meaningful H1 per page
- valid heading hierarchy
- alt text
- schema markup where useful
- internal linking
- broken-link checks
- compressed images
- Core Web Vitals review
- mobile responsiveness
- HTTPS
- clean URL slugs
- llms.txt where appropriate
- no accidental noindex directives
- social preview image and metadata

Search-engine submission is a launch task and must not be marked complete unless actually performed.

## 17. Legal and Compliance Pages

Public deployment must include as applicable:

- Privacy Policy
- Terms of Service
- cookie consent when the configured analytics/tracking and jurisdiction require it
- contact/support route
- bug-report route

Legal pages must describe the actual deployed behavior.

Do not paste irrelevant generic clauses.

## 18. Analytics and Tracking

If analytics are enabled:

Track only necessary events.

Do not send claim content or sensitive identifiers to analytics vendors.

Include:

- page views
- major workflow actions
- error monitoring
- performance metrics

Respect consent requirements.

## 19. Payments

Payments are out of scope for the initial ClaimGraph PI release.

Do not add pricing, Stripe, subscriptions, upgrades, downgrades, or cancellation flows simply to make the project look like a SaaS product.

If payments are added later, they require a new PRD scope decision and full lifecycle testing.

## 20. Performance Rules

- paginate large tables
- bound graph queries
- avoid N+1 database access
- add indexes based on observed query patterns
- compress images
- lazy-load expensive visualizations only when useful
- do not fetch entire claim datasets into the browser
- asynchronous jobs for long-running scoring/ingestion
- measure before optimizing

## 21. Testing Rules

A feature is not complete without appropriate tests.

Required categories:

- unit
- integration
- API
- auth
- authorization
- negative path
- data quality
- rule-engine
- ML scoring
- graph analytics
- frontend
- end-to-end
- broken links
- responsive behavior
- security checks

CI must block merges on required test failures.

## 22. Git and Repository Rules

- small, meaningful commits
- descriptive commit messages
- no giant one-shot implementation commit
- no generated-by-AI language
- no Copilot-agent authored commits
- no secrets in history
- no committed local environments
- no generated large datasets
- no commented-out dead code
- no TODO graveyard
- no fake issue/PR history
- do not claim features before they exist

## 23. Documentation Rules

Documentation must be accurate.

Update:

- README when public capabilities change
- Architecture.md when architecture changes
- rules.md when constraints change
- phases.md when phase scope changes
- memory.md after meaningful implementation milestones
- ADRs for material technical choices

## 24. Completion Standard

A feature is complete only when:

1. implementation exists
2. tests pass
3. errors are handled
4. security boundaries are enforced
5. documentation is updated
6. responsive behavior is checked if UI-facing
7. no placeholder content remains
8. memory.md reflects the current state
