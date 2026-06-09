{{ config(materialized='view') }}

with silver_filings as (

    select *
    from read_parquet('data/silver/silver_filings.parquet')

)

select
    trim(cik) as cik,
    trim(accession_number) as accession_number,
    filing_date,
    report_date,
    acceptance_datetime,
    trim(form) as form,
    nullif(trim(file_number), '') as file_number,
    size,
    is_xbrl,
    is_inline_xbrl,
    trim(primary_document) as primary_document,
    ingestion_date,
    source_file
from silver_filings