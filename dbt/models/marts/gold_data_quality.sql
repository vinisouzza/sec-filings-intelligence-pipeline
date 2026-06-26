{{ config(materialized='table') }}

select

    current_timestamp as execution_timestamp,

    count(*) as total_filings,

    count(case when cik is null then 1 end) as null_cik,

    count(case when form is null then 1 end) as null_form,

    count(case when filing_date is null then 1 end) as null_filing_date,

    count(*) - count(distinct accession_number) as duplicate_filings,

    round(
        100.0 *
        (
            count(*) -
            (
                count(case when cik is null then 1 end)
                + count(case when form is null then 1 end)
                + count(case when filing_date is null then 1 end)
            )
        )
        /
        count(*),
        2
    ) as quality_score

from {{ ref('stg_filings') }}