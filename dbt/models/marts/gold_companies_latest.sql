{{ config(materialized='table') }}

select
    cik,
    company_name,
    ticker,
    exchange,
    sic,
    sic_description,
    state_of_incorporation,
    category,
    latest_ingestion_date
from {{ ref('stg_companies') }}