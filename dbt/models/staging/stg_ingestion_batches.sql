select
    id::text as ingestion_batch_id,
    dataset_name,
    sample_number,
    source_filename,
    source_sha256,
    status,
    started_at,
    completed_at,
    rows_seen,
    rows_accepted,
    rows_rejected,
    claim_lines_loaded
from {{ source('raw', 'ingestion_batches') }}
