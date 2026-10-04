with provider_hcpcs as (
    select
        provider_npi,
        hcpcs_code,
        count(*) as hcpcs_line_count
    from {{ ref('int_claim_service_events') }}
    where
        provider_npi is not null
        and hcpcs_code is not null
    group by provider_npi, hcpcs_code
),

ranked as (
    select
        provider_npi,
        hcpcs_code,
        hcpcs_line_count,
        row_number() over (
            partition by provider_npi
            order by hcpcs_line_count desc, hcpcs_code
        ) as procedure_rank
    from provider_hcpcs
)

select
    provider_npi,
    hcpcs_code as dominant_hcpcs_code,
    hcpcs_line_count as dominant_hcpcs_line_count
from ranked
where procedure_rank = 1
