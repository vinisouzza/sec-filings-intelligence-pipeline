{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('month', filing_date) AS filing_month,
    COUNT(*) AS total_filings
FROM {{ ref('stg_filings') }}
GROUP BY 1
ORDER BY 1