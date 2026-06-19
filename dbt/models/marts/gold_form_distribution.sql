{{ config(materialized='table') }}

SELECT
    form,
    COUNT(*) AS total_filings
FROM {{ ref('stg_filings') }}
GROUP BY form
ORDER BY total_filings DESC