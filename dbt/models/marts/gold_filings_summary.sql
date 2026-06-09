{{ config(materialized='table') }}

select
    cik,

    count(*) as total_filings,

    min(filing_date) as first_filing_date,

    max(filing_date) as latest_filing_date,

    sum(
        case
            when form = '10-K' then 1
            else 0
        end
    ) as total_10k,

    sum(
        case
            when form = '10-Q' then 1
            else 0
        end
    ) as total_10q,

    sum(
        case
            when form = '8-K' then 1
            else 0
        end
    ) as total_8k

from {{ ref('stg_filings') }}

group by cik