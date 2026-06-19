select count(*) as total_rows
from {{ ref('gold_filings_summary') }}
having count(*) = 0