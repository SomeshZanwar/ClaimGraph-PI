select
    l.claim_line_record_id,
    c.claim_record_id,
    c.ingestion_batch_id,
    c.source_row_number,
    c.beneficiary_id,
    c.claim_id,
    c.claim_from_date,
    c.claim_through_date,
    l.line_number,
    l.provider_npi,
    l.tax_number,
    l.hcpcs_code,
    l.payment_amount,
    l.deductible_amount,
    l.primary_payer_amount,
    l.coinsurance_amount,
    l.allowed_charge_amount,
    l.processing_indicator_code,
    l.diagnosis_code
from {{ ref('stg_carrier_claim_lines') }} l
inner join {{ ref('stg_carrier_claims') }} c
    on l.claim_record_id = c.claim_record_id
