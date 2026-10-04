with assigned as (
    select *
    from {{ ref('int_provider_peer_assignment') }}
),

peer_baseline as (
    select
        peer_group_key,
        count(*) as peer_group_size,
        percentile_cont(0.5) within group (
            order by avg_claim_allowed_charge_amount
        ) as peer_median_avg_allowed
    from assigned
    where avg_claim_allowed_charge_amount is not null
    group by peer_group_key
),

absolute_deviation as (
    select
        a.provider_npi,
        a.peer_group_key,
        abs(
            a.avg_claim_allowed_charge_amount
            - b.peer_median_avg_allowed
        ) as absolute_deviation
    from assigned a
    inner join peer_baseline b
        on a.peer_group_key = b.peer_group_key
    where a.avg_claim_allowed_charge_amount is not null
),

peer_mad as (
    select
        peer_group_key,
        percentile_cont(0.5) within group (
            order by absolute_deviation
        ) as peer_mad_avg_allowed
    from absolute_deviation
    group by peer_group_key
)

select
    a.provider_npi,
    a.peer_group_key,
    a.dominant_hcpcs_code,
    a.volume_band,
    a.provider_claim_count,
    a.unique_beneficiary_count,
    a.avg_lines_per_claim,
    a.avg_claim_payment_amount,
    a.avg_claim_allowed_charge_amount,
    a.median_claim_allowed_charge_amount,
    a.max_claim_allowed_charge_amount,
    b.peer_group_size,
    b.peer_median_avg_allowed,
    m.peer_mad_avg_allowed,
    case
        when b.peer_group_size < 5 then null
        when m.peer_mad_avg_allowed is null or m.peer_mad_avg_allowed = 0 then null
        else (
            a.avg_claim_allowed_charge_amount - b.peer_median_avg_allowed
        ) / (1.4826 * m.peer_mad_avg_allowed)
    end as robust_z_avg_allowed,
    case
        when b.peer_group_size < 5 then 'INSUFFICIENT_COHORT'
        when m.peer_mad_avg_allowed is null or m.peer_mad_avg_allowed = 0
            then 'NO_VARIATION'
        else 'COMPARABLE'
    end as peer_comparison_status
from assigned a
left join peer_baseline b
    on a.peer_group_key = b.peer_group_key
left join peer_mad m
    on a.peer_group_key = m.peer_group_key
