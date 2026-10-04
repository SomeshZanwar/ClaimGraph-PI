select
    claim_record_id
from {{ ref('stg_carrier_claims') }}
where
    claim_from_date is not null
    and claim_through_date is not null
    and claim_from_date > claim_through_date
