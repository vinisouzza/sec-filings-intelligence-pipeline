{{ config(materialized='view') }}

with silver_companies as (

    select *
    from read_parquet('data/silver/silver_companies.parquet')

)

select
    trim(cik) as cik,
    trim(company_name) as company_name,
    nullif(trim(ticker), '') as ticker,
    nullif(trim(exchange), '') as exchange,
    trim(sic) as sic,
    nullif(trim(sic_description), '') as sic_description,
    nullif(trim(state_of_incorporation), '') as state_of_incorporation,
    nullif(trim(category), '') as category,
    latest_ingestion_date,
    source_file
from silver_companies