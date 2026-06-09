from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from silver.schemas import SILVER_COMPANIES_COLUMNS, SILVER_FILINGS_COLUMNS
from utils.logger import get_logger

logger = get_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_COMPANIES_PATH = PROJECT_ROOT / "data" / "bronze" / "bronze_companies.parquet"
BRONZE_FILINGS_PATH = PROJECT_ROOT / "data" / "bronze" / "bronze_filings_recent.parquet"
SILVER_ROOT = PROJECT_ROOT / "data" / "silver"
SILVER_COMPANIES_PATH = SILVER_ROOT / "silver_companies.parquet"
SILVER_FILINGS_PATH = SILVER_ROOT / "silver_filings.parquet"


COMPANIES_QUERY = f"""
WITH bronze AS (
    SELECT *
    FROM read_parquet('{BRONZE_COMPANIES_PATH.as_posix()}')
    WHERE regexp_matches(ingestion_date, '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$')
),
ranked AS (
    SELECT
        cik,
        name AS company_name,
        list_extract(tickers, 1) AS ticker,
        list_extract(exchanges, 1) AS exchange,
        sic,
        sic_description,
        state_of_incorporation,
        category,
        CAST(ingestion_date AS DATE) AS latest_ingestion_date,
        source_file,
        load_ts,
        ROW_NUMBER() OVER (
            PARTITION BY cik
            ORDER BY CAST(ingestion_date AS DATE) DESC, load_ts DESC
        ) AS rn
    FROM bronze
)
SELECT
    cik,
    company_name,
    ticker,
    exchange,
    sic,
    sic_description,
    state_of_incorporation,
    category,
    latest_ingestion_date,
    source_file
FROM ranked
WHERE rn = 1
ORDER BY cik
"""


FILINGS_QUERY = f"""
WITH bronze AS (
    SELECT *
    FROM read_parquet('{BRONZE_FILINGS_PATH.as_posix()}')
    WHERE regexp_matches(ingestion_date, '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$')
),
typed AS (
    SELECT
        cik,
        accession_number,
        TRY_CAST(NULLIF(CAST(filing_date AS VARCHAR), '') AS DATE) AS filing_date,
        TRY_CAST(NULLIF(CAST(report_date AS VARCHAR), '') AS DATE) AS report_date,
        COALESCE(
            try_strptime(NULLIF(CAST(acceptance_datetime AS VARCHAR), ''), '%Y-%m-%dT%H:%M:%S.%fZ'),
            try_strptime(NULLIF(CAST(acceptance_datetime AS VARCHAR), ''), '%Y-%m-%dT%H:%M:%SZ')
        ) AS acceptance_datetime,
        form,
        file_number,
        TRY_CAST(NULLIF(CAST(size AS VARCHAR), '') AS BIGINT) AS size,
        CASE
            WHEN LOWER(TRIM(CAST(is_xbrl AS VARCHAR))) IN ('1', 'true', 't', 'yes', 'y') THEN TRUE
            WHEN LOWER(TRIM(CAST(is_xbrl AS VARCHAR))) IN ('0', 'false', 'f', 'no', 'n') THEN FALSE
            ELSE NULL
        END AS is_xbrl,
        CASE
            WHEN LOWER(TRIM(CAST(is_inline_xbrl AS VARCHAR))) IN ('1', 'true', 't', 'yes', 'y') THEN TRUE
            WHEN LOWER(TRIM(CAST(is_inline_xbrl AS VARCHAR))) IN ('0', 'false', 'f', 'no', 'n') THEN FALSE
            ELSE NULL
        END AS is_inline_xbrl,
        primary_document,
        TRY_CAST(NULLIF(CAST(ingestion_date AS VARCHAR), '') AS DATE) AS ingestion_date,
        source_file,
        load_ts,
        ROW_NUMBER() OVER (
            PARTITION BY cik, accession_number
            ORDER BY TRY_CAST(NULLIF(CAST(ingestion_date AS VARCHAR), '') AS DATE) DESC, load_ts DESC
        ) AS rn
    FROM bronze
)
SELECT
    cik,
    accession_number,
    filing_date,
    report_date,
    acceptance_datetime,
    form,
    file_number,
    size,
    is_xbrl,
    is_inline_xbrl,
    primary_document,
    ingestion_date,
    source_file
FROM typed
WHERE rn = 1
ORDER BY cik, filing_date DESC NULLS LAST, accession_number
"""


def build_silver_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not BRONZE_COMPANIES_PATH.exists():
        raise FileNotFoundError(f"Bronze companies file not found: {BRONZE_COMPANIES_PATH}")
    if not BRONZE_FILINGS_PATH.exists():
        raise FileNotFoundError(f"Bronze filings file not found: {BRONZE_FILINGS_PATH}")

    con = duckdb.connect(database=":memory:")

    companies_df = con.execute(COMPANIES_QUERY).df()
    filings_df = con.execute(FILINGS_QUERY).df()

    companies_df = companies_df[SILVER_COMPANIES_COLUMNS]
    filings_df = filings_df[SILVER_FILINGS_COLUMNS]

    return companies_df, filings_df


def save_silver_tables(
    companies_df: pd.DataFrame,
    filings_df: pd.DataFrame,
) -> tuple[Path, Path]:
    SILVER_ROOT.mkdir(parents=True, exist_ok=True)

    companies_df.to_parquet(SILVER_COMPANIES_PATH, index=False)
    filings_df.to_parquet(SILVER_FILINGS_PATH, index=False)

    logger.info(
        "Saved silver companies: %s | rows=%d",
        SILVER_COMPANIES_PATH,
        len(companies_df),
    )
    logger.info(
        "Saved silver filings: %s | rows=%d",
        SILVER_FILINGS_PATH,
        len(filings_df),
    )

    return SILVER_COMPANIES_PATH, SILVER_FILINGS_PATH


def main() -> None:
    logger.info("Starting silver build")

    companies_df, filings_df = build_silver_tables()
    companies_path, filings_path = save_silver_tables(companies_df, filings_df)

    logger.info(
        "Silver build finished | companies=%d | filings=%d | companies_path=%s | filings_path=%s",
        len(companies_df),
        len(filings_df),
        companies_path,
        filings_path,
    )


if __name__ == "__main__":
    main()