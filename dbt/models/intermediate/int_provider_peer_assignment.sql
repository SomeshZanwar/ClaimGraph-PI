with provider_metrics as (
    select *
    from {{ ref('mart_provider_claim_metrics') }}
),

dominant_procedure as (
    select *
    from {{ ref('int_provider_hcpcs_profile') }}
),

assigned as (
    select
        p.provider_npi,
        p.provider_claim_count,
        p.unique_beneficiary_count,
        p.avg_lines_per_claim,
        p.avg_claim_payment_amount,
        p.avg_claim_allowed_charge_amount,
        p.median_claim_allowed_charge_amount,
        p.max_claim_allowed_charge_amount,
        d.dominant_hcpcs_code,
        case
            when p.provider_claim_count < 10 then 'VOLUME_LT_10'
            when p.provider_claim_count < 50 then 'VOLUME_10_49'
            when p.provider_claim_count < 200 then 'VOLUME_50_199'
            else 'VOLUME_200_PLUS'
        end as volume_band
    from provider_metrics p
    left join dominant_procedure d
        on p.provider_npi = d.provider_npi
)

select
    *,
    coalesce(dominant_hcpcs_code, 'NO_HCPCS') || ':' || volume_band
        as peer_group_key
from assigned
