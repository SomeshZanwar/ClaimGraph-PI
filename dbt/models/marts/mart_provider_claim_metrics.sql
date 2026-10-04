with provider_lines as (
    select *
    from {{ ref('int_claim_service_events') }}
    where provider_npi is not null
),

provider_claims as (
    select
        provider_npi,
        claim_record_id,
        beneficiary_id,
        min(claim_from_date) as claim_from_date,
        count(*) as line_count,
        coalesce(sum(payment_amount), 0) as claim_payment_amount,
        coalesce(sum(allowed_charge_amount), 0) as claim_allowed_charge_amount
    from provider_lines
    group by provider_npi, claim_record_id, beneficiary_id
)

select
    provider_npi,
    count(*) as provider_claim_count,
    count(distinct beneficiary_id) as unique_beneficiary_count,
    avg(line_count::numeric) as avg_lines_per_claim,
    avg(claim_payment_amount) as avg_claim_payment_amount,
    avg(claim_allowed_charge_amount) as avg_claim_allowed_charge_amount,
    percentile_cont(0.5) within group (order by claim_allowed_charge_amount)
        as median_claim_allowed_charge_amount,
    max(claim_allowed_charge_amount) as max_claim_allowed_charge_amount
from provider_claims
group by provider_npi
