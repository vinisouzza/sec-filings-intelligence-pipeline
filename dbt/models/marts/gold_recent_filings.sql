{{ config(materialized='table') }}

SELECT
    accession_number,
    cik,
    form,
    filing_date,
    primary_document
FROM {{ ref('stg_filings') }}
ORDER BY filing_date DESC
LIMIT 100