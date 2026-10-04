select
    id::text as claim_record_id,
    ingestion_batch_id::text as ingestion_batch_id,
    source_row_number,
    beneficiary_id,
    claim_id,
    claim_from_date,
    claim_through_date,
    diagnosis_codes
from {{ source('raw', 'carrier_claims') }}
