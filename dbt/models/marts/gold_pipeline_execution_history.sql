{{ config(materialized='incremental') }}

select
    current_timestamp as execution_timestamp,

    count(distinct cik) as total_companies,

    count(*) as total_filings,

    count(distinct case
        when filing_date >= current_date - interval '30 days'
        then cik
    end) as active_companies

from {{ ref('stg_filings') }}

{% if is_incremental() %}
where current_timestamp >
(
    select max(execution_timestamp)
    from {{ this }}
)
{% endif %}