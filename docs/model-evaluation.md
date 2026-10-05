# Claim Anomaly Model Evaluation

## Model

ClaimGraph PI uses an Isolation Forest as an unsupervised claim-anomaly signal.

The model is deliberately not presented as a fraud classifier because the development dataset does not provide defensible real fraud labels.

## Features

The model uses versioned claim-level features including:

- line count
- provider count
- procedure count
- payment total
- allowed-charge total
- deductible and coinsurance totals
- payment-to-allowed ratio
- payment and allowed charge per line
- service span

The exact feature list is persisted with each model run.

## Reproducibility

Each model run records:

- model version
- deterministic random seed
- source snapshot hash
- training-row count
- feature schema
- contamination setting
- anomaly threshold
- score distribution metrics
- local artifact location
- MLflow experiment metadata

## Evaluation Approach

Without valid outcome labels, precision, recall, and fraud-capture metrics would be misleading. The project therefore evaluates:

- deterministic reproducibility
- feature-schema stability
- score distribution
- threshold behavior
- anomaly fraction
- model artifact reloadability
- source-snapshot traceability

## Explanation Boundary

Feature-deviation context shows which input values differ most from training medians using robust deviation statistics.

It is descriptive context only. It is not a causal explanation and is not evidence that a claim is fraudulent.

## Production Guard

Normal training requires a minimum number of claim rows. The smaller override exists only to exercise the complete model pipeline in CI.

## Limitations

Synthetic DE-SynPUF covariance and relationships differ from real Medicare claims. The model therefore demonstrates production engineering and investigation methodology, not expected real-world fraud performance.
