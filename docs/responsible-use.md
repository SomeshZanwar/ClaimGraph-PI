# Responsible Use

ClaimGraph PI supports human investigation of suspicious synthetic claims patterns.

## The System May

- prioritize cases for review
- show deterministic billing-rule evidence
- compare synthetic providers with transparent behavioral cohorts
- surface unsupervised anomaly scores
- show provider/member/claim network relationships
- estimate financial exposure from source claim fields
- preserve evidence and investigator workflow history

## The System Must Not

- automatically deny or approve a healthcare claim
- make a clinical decision
- label a person or provider fraudulent from a model score or graph pattern
- use DE-SynPUF results to claim real Medicare fraud prevalence
- process real PHI in the public demonstration
- invent evidence that does not exist in canonical data
- represent an anomaly score as a fraud probability

## Human Review

A case priority is a workload-ranking signal. Investigators remain responsible for interpreting context, obtaining documentation, and recording a final disposition under the procedures of the organization using the system.

## Synthetic Data

CMS DE-SynPUF is synthetic and designed for safe development. Its statistical relationships do not reproduce all properties of real Medicare claims. Public demo findings therefore demonstrate system behavior rather than real provider or beneficiary behavior.
