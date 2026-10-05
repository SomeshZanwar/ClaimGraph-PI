# ClaimGraph PI Data Dictionary

## Raw Layer

### raw.ingestion_batches
One row per ingested source archive.

Key fields:
- id: ingestion batch UUID
- dataset_name: logical source dataset
- source_filename: original archive filename
- source_sha256: immutable source checksum
- status: STARTED, COMPLETED, or FAILED
- rows_seen / rows_accepted / rows_rejected: ingestion quality metrics
- claim_lines_loaded: normalized long-form line count

### raw.carrier_claims
One row per accepted synthetic Carrier claim source row.

Key fields:
- claim_record_id: internal UUID
- beneficiary_id: synthetic DE-SynPUF beneficiary identifier
- claim_id: synthetic claim identifier
- claim_from_date / claim_through_date
- diagnosis_codes
- ingestion_batch_id / source_row_number: lineage

### raw.carrier_claim_lines
One row per non-empty repeated Carrier line slot.

Key fields:
- claim_record_id
- line_number
- provider_npi: synthetic/disclosure-treated provider identifier
- hcpcs_code
- diagnosis_code
- payment_amount
- allowed_charge_amount
- deductible_amount
- coinsurance_amount

### raw.rejected_records
Quarantined source rows with structured reason codes and original payload.

## Analytics Layer

### analytics.fact_claim_lines
Canonical long-form service lines used by rule, peer, graph, and ML layers.

### analytics.fact_claims
Claim-level rollup with line/provider/procedure counts and financial totals.

### analytics.dim_provider
Synthetic provider-level operational aggregate.

### analytics.mart_provider_peer_metrics
Behavioral peer-cohort statistics. Peer groups are based on observable procedure mix and volume, not clinical specialty.

### analytics.mart_claim_ml_features
Numeric claim features used by the unsupervised Isolation Forest model.

## Risk Layer

### risk.rule_runs
Versioned deterministic rule executions with a ruleset hash.

### risk.risk_signals
Structured deterministic evidence containing rule ID/version, entity, severity, explanation, evidence payload, observed value, and threshold.

## Graph Metadata

### graph_meta.graph_runs
Tracks each Neo4j projection and its source snapshot.

### graph_meta.provider_graph_metrics
Provider-member connectivity metrics calculated from the projected graph.

## ML Metadata

### ml_meta.model_runs
Model type, version, source snapshot, feature list, contamination setting, threshold, metrics, and artifact path.

### ml_meta.claim_model_scores
One anomaly score per claim/model run with descriptive feature-deviation context.

## Casework

### casework.cases
Investigation queue records with status, priority, financial exposure, assignment, disposition, and current evidence hash.

### casework.case_evidence
Immutable evidence versions keyed by evidence hash.

### casework.case_notes
Investigator notes with author and timestamp.

## Authentication and Audit

### auth.users
Account identity, role, password hash, verification state, and lifecycle timestamps.

### auth.sessions
Opaque session-token hashes, CSRF token hashes, expiry, revocation, and privacy-safe client metadata.

### auth.auth_tokens
Single-use email verification and password-reset token hashes.

### audit.events
Append-oriented product/security audit events.

## Telemetry

### telemetry.product_events
First-party privacy-safe product events. Claims payloads and synthetic beneficiary identifiers are intentionally excluded.
