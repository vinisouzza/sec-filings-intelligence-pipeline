select *
from {{ ref('stg_filings') }}
where filing_date > current_date