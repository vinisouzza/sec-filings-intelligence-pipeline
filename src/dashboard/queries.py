from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

DB_PATH = Path("data/warehouse/sec_filings.duckdb")


def _get_connection() -> duckdb.DuckDBPyConnection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found at: {DB_PATH}. "
            "Run dbt run before opening the dashboard."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)


def load_kpis() -> dict[str, object]:
    query = """
    SELECT
        (SELECT COUNT(*) FROM analytics.gold_companies_latest) AS total_companies,
        (SELECT COUNT(*) FROM analytics.gold_filings_summary) AS total_companies_with_filings,
        (SELECT SUM(total_filings) FROM analytics.gold_filings_summary) AS total_filings,
        (SELECT MAX(latest_filing_date) FROM analytics.gold_filings_summary) AS latest_filing_date
    """
    with _get_connection() as con:
        row = con.execute(query).fetchone()

    return {
        "total_companies": row[0],
        "total_companies_with_filings": row[1],
        "total_filings": row[2],
        "latest_filing_date": row[3],
    }


def load_filings_by_form() -> pd.DataFrame:
    query = """
    SELECT
        form,
        COUNT(*) AS filings_count
    FROM analytics.stg_filings
    GROUP BY form
    ORDER BY filings_count DESC, form
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_top_companies() -> pd.DataFrame:
    query = """
    SELECT
        c.company_name,
        c.ticker,
        c.exchange,
        f.total_filings,
        f.first_filing_date,
        f.latest_filing_date
    FROM analytics.gold_filings_summary f
    JOIN analytics.gold_companies_latest c
        ON c.cik = f.cik
    ORDER BY f.total_filings DESC, c.company_name
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_recent_filings(limit: int = 10) -> pd.DataFrame:
    query = f"""
    SELECT
        cik,
        accession_number,
        filing_date,
        report_date,
        form,
        primary_document
    FROM analytics.stg_filings
    ORDER BY filing_date DESC NULLS LAST, accession_number DESC
    LIMIT {int(limit)}
    """
    with _get_connection() as con:
        return con.execute(query).df()
    
def load_filings_timeline():
    query = """
    SELECT
        filing_date,
        COUNT(*) AS filings
    FROM analytics.stg_filings
    WHERE filing_date IS NOT NULL
    GROUP BY filing_date
    ORDER BY filing_date
    """

    with _get_connection() as con:
        return con.execute(query).df()
    
def load_companies():
    query = """
    SELECT
        company_name,
        cik
    FROM analytics.gold_companies_latest
    ORDER BY company_name
    """

    with _get_connection() as con:
        return con.execute(query).df()
    
def load_company_detail(cik: str):
    query = f"""
    SELECT *
    FROM analytics.gold_companies_latest
    WHERE cik = '{cik}'
    """

    with _get_connection() as con:
        return con.execute(query).df()
    
def load_company_filings(cik: str):
    query = f"""
    SELECT
        filing_date,
        form,
        accession_number
    FROM analytics.stg_filings
    WHERE cik = '{cik}'
    ORDER BY filing_date DESC
    """

    with _get_connection() as con:
        return con.execute(query).df()