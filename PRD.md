# ClaimGraph PI Product Requirements Document

## 1. Product Summary

ClaimGraph PI is an explainable pre-payment healthcare claims investigation and provider network intelligence platform.

The product helps payment-integrity and special-investigations teams identify suspicious claims before payment, prioritize the highest-value cases, understand why a claim or provider network was flagged, and document the evidence used for human review.

ClaimGraph PI is an investigation and decision-support system. It does not autonomously deny medical claims, replace a payer claims-adjudication platform, or make clinical decisions.

## 2. Problem

Healthcare payers process large volumes of claims with limited analyst capacity. Suspicious activity can be difficult to detect because risk may exist across several layers at once:

- individual claim anomalies
- abnormal provider billing patterns
- duplicate or near-duplicate services
- unusual procedure or diagnosis combinations
- peer-group deviations
- suspicious provider-member-facility relationships
- repeated network behavior that is difficult to see in tabular analysis

Traditional rules can detect known patterns, while machine-learning models can surface statistical anomalies. Neither is sufficient alone. Investigators need a combined view with transparent evidence, financial context, and network relationships.

## 3. Product Goal

Create a production-style investigation platform that converts claims data into prioritized, explainable cases for human review.

The product should answer five questions:

1. Which claims deserve investigation first?
2. Why was each claim flagged?
3. Is the provider behaving differently from comparable peers?
4. Are there suspicious relationships across providers, members, facilities, addresses, and procedures?
5. What payment amount is potentially exposed?

## 4. Target Users

### Primary users

#### Payment Integrity Analyst
Reviews high-risk claims, validates billing concerns, records findings, and prioritizes recovery or pre-payment intervention work.

#### Special Investigations Unit Investigator
Investigates suspected fraud, waste, abuse, collusion, and suspicious provider networks.

#### Healthcare Data Analyst
Analyzes claim trends, provider behavior, coding patterns, and operational performance.

#### Healthcare Data Scientist
Builds and monitors anomaly, classification, and graph-based risk models.

### Secondary users

#### Coding or Clinical Documentation Analyst
Reviews coding-specific issues surfaced by deterministic rules.

#### Payment Integrity Manager
Monitors case volume, risk concentration, analyst throughput, potential payment exposure, and investigation outcomes.

#### Compliance or Audit User
Reviews case evidence, decision history, and audit trails.

## 5. Initial Product Scope

The first production-quality version will focus on pre-payment investigation for professional and institutional claims represented in a claims-like public or synthetic dataset.

The system will support:

- claims ingestion and validation
- canonical claims model
- deterministic claim and billing checks
- provider peer-group analytics
- statistical and ML anomaly scoring
- graph construction and graph-risk analytics
- combined risk scoring
- investigator case queue
- claim and provider evidence views
- investigation status and disposition workflow
- audit trail
- model and rule version traceability
- operational metrics
- secure public demo with synthetic or public-safe data

## 6. Out of Scope for Initial Release

The first release will not:

- submit or adjudicate live insurance claims
- make automated claim-denial decisions
- use protected health information from real patients
- connect to a production payer or EHR
- claim regulatory or clinical certification
- provide medical advice
- replace clinical coding review
- process real payment transactions
- provide a production multi-payer clearinghouse integration
- perform fully autonomous fraud enforcement

## 7. Data Strategy

The project will use public or synthetic claims-like data suitable for software development and portfolio demonstration.

Preferred sources include public synthetic Medicare-style claims data and supporting public reference data.

No real patient PHI will be committed to the repository.

### Canonical entities

- claim
- claim line
- provider
- member
- facility
- procedure
- diagnosis
- address
- organization
- peer group
- risk signal
- investigation case
- investigation event
- model version
- rule version

## 8. Core Functional Requirements

### 8.1 Data Ingestion

The system must:

- load claims-like source data reproducibly
- validate required fields and types
- reject malformed records
- quarantine invalid records with structured reasons
- prevent duplicate ingestion
- track source file and ingestion batch
- record ingestion metrics

### 8.2 Claims Normalization

The platform must map source data into a canonical schema.

Required capabilities:

- normalize identifiers
- standardize dates
- standardize monetary fields
- normalize procedure and diagnosis representations
- preserve source lineage
- generate deterministic record identifiers
- keep raw and curated layers logically separated

### 8.3 Deterministic Risk Rules

The rule engine must support versioned rules and structured results.

Initial rule families should include:

- exact duplicate claims
- near-duplicate service patterns
- unusual repeat-service frequency
- suspicious charge deviation
- provider billing concentration
- member utilization anomalies
- procedure-frequency anomalies
- impossible or inconsistent values supported by the dataset

Every rule result must contain:

- rule identifier
- rule version
- affected entity
- severity
- evidence fields
- explanation
- timestamp

Rules must be deterministic and must not depend on an LLM to decide whether a claim is flagged.

### 8.4 Provider Peer Analytics

Providers must be compared against an explicit peer group.

Peer grouping may use:

- specialty
- geography where supported
- facility type
- procedure mix
- claim volume

The system should calculate:

- claim volume
- average paid or submitted amount
- procedure frequency
- high-cost procedure share
- repeat-service frequency
- member concentration
- deviation from peer median
- robust z-scores or comparable statistical measures

### 8.5 Machine-Learning Risk Layer

The ML layer should detect anomalous claims or providers without replacing deterministic evidence.

Initial implementation may include:

- Isolation Forest or comparable unsupervised baseline
- gradient-boosted supervised model if suitable labels can be responsibly constructed
- calibrated risk probabilities where classification is used
- feature attribution for supported models
- strict training-serving separation
- reproducible feature generation

Model outputs must include:

- model identifier
- model version
- score
- threshold
- feature attribution or contributing features where technically supported
- data snapshot identifier

### 8.6 Graph Intelligence

The graph layer must represent relationships such as:

- provider to member
- provider to facility
- provider to address
- provider to procedure
- member to procedure
- organization to provider

Initial graph capabilities should include:

- degree and weighted-degree analysis
- shared-entity relationships
- community detection
- connected component analysis
- suspicious concentration patterns
- graph-derived features for provider risk
- investigator-friendly relationship visualization

The graph must support evidence drill-down rather than decorative visualization.

### 8.7 Composite Risk Ranking

The platform must combine risk evidence in an explainable manner.

A claim or provider risk record should distinguish:

- deterministic rule signals
- statistical peer deviations
- ML score
- graph-risk signals
- financial exposure

The product must not collapse all evidence into an unexplained black-box number.

### 8.8 Investigator Workbench

The web application must provide:

- prioritized case queue
- filters and sorting
- claim summary
- provider profile
- risk-signal breakdown
- peer comparison
- graph relationship view
- evidence timeline
- potential payment exposure
- analyst notes
- investigation status
- disposition
- audit history

Suggested statuses:

- NEW
- IN_REVIEW
- NEEDS_DOCUMENTATION
- ESCALATED
- CLEARED
- CONFIRMED_ISSUE
- CLOSED

### 8.9 Search

Authorized users should be able to search by supported identifiers such as:

- claim ID
- provider ID
- member ID
- case ID

Search must enforce authorization and input validation.

### 8.10 Audit Trail

Every material action must be attributable and timestamped.

Audit events should cover:

- login
- case assignment
- case view when appropriate
- status change
- disposition
- analyst note creation
- rule execution
- model scoring run
- model version change
- data ingestion batch
- administrative configuration change

Audit logs must not expose secrets or unnecessary sensitive fields.

## 9. User Experience Requirements

The product must work across mobile, tablet, laptop, and desktop without horizontal overflow.

Required public and application behaviors include:

- mobile navigation where needed
- clickable logo
- correct titles and meta descriptions
- favicon
- clear loading, empty, success, warning, and error states
- no placeholder copy in production
- functional buttons and links
- accessible form validation
- custom 404 page
- correct footer navigation
- clickable contact details where displayed
- keyboard-accessible interactions
- meaningful focus states
- accessible color contrast
- meaningful alt text for informative images

## 10. Authentication and Authorization

If authentication is enabled in the deployed product, it must include working:

- signup or controlled user creation
- login
- logout
- email verification where signup is public
- password reset
- session expiration
- rate limiting
- resource-level authorization
- secure password hashing
- secure cookie or token handling

OAuth may be included only if it is fully implemented and tested.

The product must prevent insecure direct object reference access between users.

## 11. Security Requirements

- no credentials, API keys, private keys, database passwords, or tokens in frontend bundles
- no secrets committed to Git
- HTTPS in production
- strict input validation
- parameterized database access
- safe file handling
- rate limiting on abuse-sensitive endpoints
- structured security-relevant logging
- no sensitive values in application logs
- authorization checks at every protected resource boundary
- dependency vulnerability scanning
- secret scanning
- secure headers
- CSRF protection where applicable
- safe CORS configuration
- replay protections where relevant

## 12. AI Boundaries

AI may be used only where it adds clear user value and does not control deterministic risk decisions.

Permitted examples:

- summarizing already-derived evidence for an investigator
- generating a plain-language explanation from structured risk signals
- assisting with search over product documentation

AI must not:

- autonomously deny claims
- invent supporting evidence
- replace deterministic policy or rule evaluation
- expose PHI or secrets to external model providers
- generate SQL or code that is executed without validation
- be presented as a clinical authority

Any AI-generated explanation must be grounded in stored structured evidence.

## 13. Analytics and Product Telemetry

The deployed application should support privacy-aware:

- page-view tracking
- key workflow events
- error monitoring
- performance monitoring

Events must not contain sensitive claims content.

Example product events:

- case_opened
- case_filtered
- graph_view_opened
- case_status_changed
- case_disposition_recorded
- provider_profile_opened

## 14. Public Product Surface

If a public product site is included, it must provide as applicable:

- home or product overview
- working demo entry point
- privacy policy
- terms of service
- cookie consent where required by the configured tracking stack
- contact or support
- bug-report path
- custom 404 page

It must not contain fake customers, fake testimonials, fabricated integrations, fabricated performance claims, or non-working demos.

## 15. SEO and Discoverability

Public pages should implement where applicable:

- sitemap.xml
- robots.txt
- canonical tags
- descriptive meta titles
- meta descriptions
- one H1 per page
- correct heading hierarchy
- social preview metadata and image
- schema markup where appropriate
- internal links
- clean URL slugs
- alt text
- compressed images
- no accidental noindex directives
- HTTPS
- mobile responsiveness
- Core Web Vitals review
- llms.txt where appropriate

Search-console submission and backlink work are launch tasks and must not be falsely represented as completed unless actually performed.

## 16. Performance Requirements

Initial targets for the public demo:

- no avoidable horizontal overflow at supported breakpoints
- interactive case-list actions should feel immediate under demo-scale data
- common API reads should target sub-second response times under local/demo load
- graph views must use bounded queries and pagination or limits
- large claims tables must not be rendered fully in the browser
- images must be compressed and appropriately sized
- expensive scoring jobs should run asynchronously if they exceed request-time limits

## 17. Accessibility Requirements

Target WCAG 2.2 AA principles where practical.

Requirements include:

- sufficient contrast
- keyboard navigation
- visible focus states
- semantic headings
- descriptive labels
- accessible validation messages
- no color-only risk communication
- reduced-motion respect if motion is introduced
- responsive text sizing

## 18. Reliability and Error Handling

Every external or failure-prone operation must produce a controlled failure path.

The application must have:

- structured API errors
- user-facing error messages
- retry guidance only where retry is safe
- ingestion failure logging
- background-job status where used
- health endpoint
- readiness checks where appropriate
- no stack traces exposed to users

## 19. Testing Requirements

The project must include:

- unit tests
- integration tests
- API tests
- authorization tests
- negative-path tests
- data-quality tests
- model or scoring tests
- graph analytics tests
- frontend component or flow tests where appropriate
- end-to-end coverage for the primary investigator workflow
- broken-link checks
- responsive layout checks
- secret scanning and dependency checks in CI

## 20. Success Criteria

The initial release is successful when a reviewer can:

1. ingest the supported claims dataset reproducibly
2. generate deterministic, statistical, ML, and graph risk signals
3. open a prioritized investigation queue
4. understand exactly why a case is risky
5. compare a provider with peers
6. inspect relevant network relationships
7. record an investigation decision
8. reconstruct the evidence and audit history
9. run the system locally from documented setup steps
10. access a deployed demo that demonstrates the real workflow
11. inspect automated tests and CI that validate core behavior

## 21. Portfolio and Interview Standard

The repository should demonstrate engineering decisions rather than only final screenshots.

A technical reviewer should be able to inspect:

- why the canonical data model was chosen
- how leakage is prevented
- how graph relationships are built
- how rules and models are versioned
- why risk signals are explainable
- how human review is kept in the decision loop
- how security boundaries are enforced
- how the system fails safely
- what was deliberately scoped out

No feature should be represented as implemented unless working code and tests support the claim.
