select
    id::text as claim_line_record_id,
    claim_record_id::text as claim_record_id,
    line_number,
    nullif(trim(provider_npi), '') as provider_npi,
    nullif(trim(tax_number), '') as tax_number,
    nullif(trim(hcpcs_code), '') as hcpcs_code,
    payment_amount,
    deductible_amount,
    primary_payer_amount,
    coinsurance_amount,
    allowed_charge_amount,
    nullif(trim(processing_indicator_code), '') as processing_indicator_code,
    nullif(trim(diagnosis_code), '') as diagnosis_code
from {{ source('raw', 'carrier_claim_lines') }}
