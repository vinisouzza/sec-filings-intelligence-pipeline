{{ config(materialized='table') }}

select
    cik,
    accession_number,
    filing_date,
    report_date,
    form,
    primary_document
from {{ ref('stg_filings') }}
order by
    filing_date desc,
    accession_number desc