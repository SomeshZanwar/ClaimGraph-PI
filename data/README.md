# ClaimGraph PI Data

## Primary Development Dataset

ClaimGraph PI uses the CMS 2008-2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF) as its initial claims-development source.

CMS created DE-SynPUF to provide a realistic Medicare claims structure for software development, training, and safe data-mining work while protecting beneficiary privacy.

Official source:

https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf

## Initial Claim Type

The first ingestion pipeline targets the Carrier Claims DE-SynPUF.

Carrier records represent synthetic physician/supplier claims and contain:

- synthetic beneficiary identifier
- claim identifier
- claim from/through dates
- up to 8 claim diagnosis codes
- up to 13 provider NPI line slots
- up to 13 provider tax-number line slots
- up to 13 HCPCS line slots
- line payment amounts
- line beneficiary deductible amounts
- line primary-payer amounts
- line coinsurance amounts
- line allowed-charge amounts
- line processing-indicator codes
- line diagnosis codes

The project converts the 13 repeated line slots into a long-form raw claim-line table.

## Development Sample

The initial supported download target is DE-SynPUF Sample 2.

CMS Sample 2 download page:

https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf/de10-sample-2

Carrier files:

- https://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_2A.zip
- https://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_2B.zip

Beneficiary summary file for the first year:

- https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_2.zip

The two Carrier files are parts of the same sample and should be ingested under the same logical dataset version.

## Why This Dataset

The source is suitable for this project because:

- it uses claims-like structures and variable names modeled after CMS data
- it supports linking synthetic claims to synthetic beneficiaries
- it contains provider, procedure, diagnosis, and payment fields useful for risk analytics
- it is explicitly intended for software/application development
- no record represents an actual Medicare beneficiary

## Critical Limitation

DE-SynPUF is synthetic.

CMS warns that the synthetic process alters interdependence and covariance among variables. The data has limited inferential value for drawing conclusions about actual Medicare beneficiaries.

Therefore ClaimGraph PI will not claim:

- real fraud prevalence
- real provider misconduct
- production model performance on Medicare claims
- population-level Medicare conclusions
- real-world savings estimates derived from the synthetic sample

Any suspicious patterns detected in the public demo are demonstration signals within synthetic data.

## Provider Identifier Limitation

Provider NPI values in DE-SynPUF were generated or disclosure-treated and do not identify real providers.

Graph relationships based on these values are used to demonstrate investigation methodology only.

## Repository Data Policy

Large CMS source files are not committed to Git.

Expected local layout:

~~~text
data/
  raw/
    sample_2/
      DE1_0_2008_to_2010_Carrier_Claims_Sample_2A.zip
      DE1_0_2008_to_2010_Carrier_Claims_Sample_2B.zip
~~~

The data/raw directory is ignored except for its .gitkeep marker.

## Data Lineage

Every ingested record will carry:

- ingestion batch ID
- source filename
- source row number
- source checksum
- ingestion timestamp

This allows a risk signal to be traced back to the exact source batch that produced it.

## Source Documentation

CMS DE-SynPUF overview:

https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files

CMS DE-SynPUF codebook:

https://www.cms.gov/files/document/cms08-10desynpufcodebookpdf

CMS DE-SynPUF user documentation:

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/synpuf_dug.pdf
