with claim_lines as (
    select *
    from {{ ref('int_claim_service_events') }}
),

claim_rollup as (
    select
        claim_record_id,
        ingestion_batch_id,
        source_row_number,
        beneficiary_id,
        claim_id,
        claim_from_date,
        claim_through_date,
        count(*) as line_count,
        count(distinct provider_npi) filter (where provider_npi is not null) as provider_count,
        count(distinct hcpcs_code) filter (where hcpcs_code is not null) as procedure_count,
        coalesce(sum(payment_amount), 0) as total_payment_amount,
        coalesce(sum(allowed_charge_amount), 0) as total_allowed_charge_amount,
        coalesce(sum(deductible_amount), 0) as total_deductible_amount,
        coalesce(sum(coinsurance_amount), 0) as total_coinsurance_amount
    from claim_lines
    group by
        claim_record_id,
        ingestion_batch_id,
        source_row_number,
        beneficiary_id,
        claim_id,
        claim_from_date,
        claim_through_date
)

select *
from claim_rollup
