{{ config(materialized='table') }}

SELECT
    c.cik,
    c.company_name,
    c.sic,
    COUNT(f.accession_number) AS total_filings,
    MIN(f.filing_date) AS first_filing_date,
    MAX(f.filing_date) AS last_filing_date
FROM {{ ref('stg_companies') }} c
LEFT JOIN {{ ref('stg_filings') }} f
    ON c.cik = f.cik
GROUP BY
    c.cik,
    c.company_name,
    c.sic