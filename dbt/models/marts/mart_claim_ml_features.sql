select
    claim_record_id,
    line_count::double precision as line_count,
    provider_count::double precision as provider_count,
    procedure_count::double precision as procedure_count,
    total_payment_amount::double precision as total_payment_amount,
    total_allowed_charge_amount::double precision as total_allowed_charge_amount,
    total_deductible_amount::double precision as total_deductible_amount,
    total_coinsurance_amount::double precision as total_coinsurance_amount,
    case
        when total_allowed_charge_amount > 0
            then total_payment_amount::double precision
                / total_allowed_charge_amount::double precision
        else null
    end as payment_to_allowed_ratio,
    case
        when line_count > 0
            then total_allowed_charge_amount::double precision
                / line_count::double precision
        else null
    end as allowed_charge_per_line,
    case
        when line_count > 0
            then total_payment_amount::double precision
                / line_count::double precision
        else null
    end as payment_per_line,
    case
        when claim_from_date is not null and claim_through_date is not null
            then (claim_through_date - claim_from_date)::double precision
        else null
    end as service_span_days
from {{ ref('fact_claims') }}
