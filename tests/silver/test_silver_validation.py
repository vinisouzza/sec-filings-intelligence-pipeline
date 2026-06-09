from pathlib import Path

import duckdb


def test_silver_parquet_files_exist():
    companies_path = Path("data/silver/silver_companies.parquet")
    filings_path = Path("data/silver/silver_filings.parquet")

    assert companies_path.exists()
    assert filings_path.exists()


def test_silver_companies_schema_and_row_count():
    con = duckdb.connect()

    df = con.execute(
        """
        SELECT *
        FROM read_parquet('data/silver/silver_companies.parquet')
        """
    ).df()

    assert not df.empty

    required_columns = {
        "cik",
        "company_name",
        "ticker",
        "exchange",
        "latest_ingestion_date",
        "source_file",
    }

    assert required_columns.issubset(df.columns)
    assert df["cik"].isna().sum() == 0
    assert df["company_name"].isna().sum() == 0


def test_silver_filings_schema_and_row_count():
    con = duckdb.connect()

    df = con.execute(
        """
        SELECT *
        FROM read_parquet('data/silver/silver_filings.parquet')
        """
    ).df()

    assert not df.empty

    required_columns = {
        "cik",
        "accession_number",
        "filing_date",
        "form",
        "ingestion_date",
        "source_file",
    }

    assert required_columns.issubset(df.columns)
    assert df["cik"].isna().sum() == 0
    assert df["accession_number"].isna().sum() == 0


def test_each_cik_appears_once_in_silver_companies():
    con = duckdb.connect()

    result = con.execute(
        """
        SELECT cik, COUNT(*) AS n
        FROM read_parquet('data/silver/silver_companies.parquet')
        GROUP BY cik
        HAVING COUNT(*) > 1
        """
    ).df()

    assert result.empty


def test_each_accession_number_appears_once_in_silver_filings():
    con = duckdb.connect()

    result = con.execute(
        """
        SELECT cik, accession_number, COUNT(*) AS n
        FROM read_parquet('data/silver/silver_filings.parquet')
        GROUP BY cik, accession_number
        HAVING COUNT(*) > 1
        """
    ).df()

    assert result.empty


def test_silver_companies_have_latest_ingestion_date():
    con = duckdb.connect()

    result = con.execute(
        """
        SELECT *
        FROM read_parquet('data/silver/silver_companies.parquet')
        WHERE latest_ingestion_date IS NULL
        """
    ).df()

    assert result.empty


def test_silver_filings_dates_are_parsed():
    con = duckdb.connect()

    result = con.execute(
        """
        SELECT *
        FROM read_parquet('data/silver/silver_filings.parquet')
        WHERE filing_date IS NULL
           OR ingestion_date IS NULL
        """
    ).df()

    assert result.empty