{{ config(
    materialized='incremental',
    unique_key='accession_number'
) }}

select
    cik,
    accession_number,
    filing_date,
    report_date,
    form,
    primary_document
from {{ ref('stg_filings') }}

{% if is_incremental() %}

where filing_date >
(
    select max(filing_date)
    from {{ this }}
)

{% endif %}