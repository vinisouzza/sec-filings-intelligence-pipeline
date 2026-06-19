select count(*) as total_rows
from {{ ref('stg_filings') }}
having count(*) < 100