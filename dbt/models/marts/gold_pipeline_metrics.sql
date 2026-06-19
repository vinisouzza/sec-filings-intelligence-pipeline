{{ config(materialized='table') }}

select
    current_timestamp as execution_timestamp,

    (select count(*) from {{ ref('stg_companies') }})
        as total_companies,

    (select count(*) from {{ ref('stg_filings') }})
        as total_filings,

    (select count(*) from {{ ref('gold_company_activity') }})
        as companies_with_activity