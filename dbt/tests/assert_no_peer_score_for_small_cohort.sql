select
    provider_npi
from {{ ref('mart_provider_peer_metrics') }}
where
    peer_group_size < 5
    and robust_z_avg_allowed is not null
