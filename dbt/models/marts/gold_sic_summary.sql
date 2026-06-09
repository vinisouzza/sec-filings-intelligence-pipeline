{{ config(materialized='table') }}

with company_filings as (

    select
        c.sic,
        c.sic_description,
        c.cik,
        f.accession_number

    from {{ ref('stg_companies') }} c

    left join {{ ref('stg_filings') }} f
        on c.cik = f.cik

)

select

    sic,

    sic_description,

    count(distinct cik) as total_companies,

    count(accession_number) as total_filings

from company_filings

group by
    sic,
    sic_description