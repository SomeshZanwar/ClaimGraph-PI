with provider_events as (
    select *
    from {{ ref('int_claim_service_events') }}
    where provider_npi is not null
),

provider_rollup as (
    select
        provider_npi,
        min(claim_from_date) as first_claim_date,
        max(claim_through_date) as last_claim_date,
        count(distinct claim_record_id) as claim_count,
        count(*) as line_count,
        count(distinct beneficiary_id) as beneficiary_count,
        count(distinct hcpcs_code) filter (where hcpcs_code is not null) as procedure_count,
        coalesce(sum(payment_amount), 0) as total_payment_amount,
        coalesce(sum(allowed_charge_amount), 0) as total_allowed_charge_amount,
        avg(allowed_charge_amount) filter (where allowed_charge_amount is not null)
            as avg_allowed_charge_amount
    from provider_events
    group by provider_npi
)

select *
from provider_rollup
