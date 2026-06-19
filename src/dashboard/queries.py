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
        (SELECT COUNT(*) FROM analytics.gold_filings_summary) AS companies_with_filings,
        (SELECT COALESCE(SUM(total_filings), 0) FROM analytics.gold_filings_summary) AS total_filings,
        (SELECT MAX(latest_filing_date) FROM analytics.gold_filings_summary) AS latest_filing_date
    """
    with _get_connection() as con:
        row = con.execute(query).fetchone()

    return {
        "total_companies": row[0],
        "companies_with_filings": row[1],
        "total_filings": row[2],
        "latest_filing_date": row[3],
    }


def load_filings_by_form() -> pd.DataFrame:
    query = """
    SELECT
        form,
        total_filings
    FROM analytics.gold_form_distribution
    ORDER BY total_filings DESC, form
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_top_companies() -> pd.DataFrame:
    query = """
    SELECT
        c.company_name,
        c.ticker,
        c.exchange,
        a.total_filings,
        a.first_filing_date,
        a.last_filing_date
    FROM analytics.gold_company_activity a
    JOIN analytics.gold_companies_latest c
        ON c.cik = a.cik
    ORDER BY a.total_filings DESC, c.company_name
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
    FROM analytics.gold_recent_filings
    ORDER BY filing_date DESC NULLS LAST, accession_number DESC
    LIMIT {int(limit)}
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_filings_timeline() -> pd.DataFrame:
    query = """
    SELECT
        filing_month,
        total_filings
    FROM analytics.gold_filing_trends
    ORDER BY filing_month
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_companies() -> pd.DataFrame:
    query = """
    SELECT
        cik,
        company_name
    FROM analytics.gold_companies_latest
    ORDER BY company_name
    """
    with _get_connection() as con:
        return con.execute(query).df()


def load_company_detail(cik: str) -> pd.DataFrame:
    query = """
    SELECT *
    FROM analytics.gold_companies_latest
    WHERE cik = ?
    """
    with _get_connection() as con:
        return con.execute(query, [cik]).df()


def load_company_filings(cik: str) -> pd.DataFrame:
    query = """
    SELECT
        accession_number,
        filing_date,
        report_date,
        form,
        primary_document
    FROM analytics.gold_company_filings
    WHERE cik = ?
    ORDER BY filing_date DESC NULLS LAST, accession_number DESC
    """
    with _get_connection() as con:
        return con.execute(query, [cik]).df()


def load_sic_summary() -> pd.DataFrame:
    query = """
    SELECT
        sic,
        sic_description,
        total_companies,
        total_filings
    FROM analytics.gold_sic_summary
    ORDER BY total_filings DESC, total_companies DESC, sic
    """
    with _get_connection() as con:
        return con.execute(query).df()