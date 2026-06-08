from pathlib import Path

import duckdb


def test_bronze_parquet_files_exist():
    companies_path = Path("data/bronze/bronze_companies.parquet")
    filings_path = Path("data/bronze/bronze_filings_recent.parquet")

    assert companies_path.exists()
    assert filings_path.exists()


def test_bronze_companies_schema_and_row_count():
    con = duckdb.connect()

    df = con.execute(
        """
        SELECT *
        FROM read_parquet('data/bronze/bronze_companies.parquet')
        """
    ).df()

    assert not df.empty

    required_columns = {
        "cik",
        "name",
        "entity_type",
        "ingestion_date",
        "source_file",
        "load_ts",
    }

    assert required_columns.issubset(df.columns)

    assert df["cik"].isna().sum() == 0
    assert df["name"].isna().sum() == 0


def test_bronze_filings_schema_and_row_count():
    con = duckdb.connect()

    df = con.execute(
        """
        SELECT *
        FROM read_parquet('data/bronze/bronze_filings_recent.parquet')
        """
    ).df()

    assert not df.empty

    required_columns = {
        "cik",
        "accession_number",
        "form",
        "ingestion_date",
        "source_file",
        "load_ts",
    }

    assert required_columns.issubset(df.columns)

    assert df["cik"].isna().sum() == 0
    assert df["accession_number"].isna().sum() == 0


def test_each_company_snapshot_appears_once():
    """
    Bronze is historical.

    The same CIK can appear multiple times with different ingestion dates.

    What should be unique is:
        (cik, ingestion_date)
    """

    con = duckdb.connect()

    result = con.execute(
        """
        SELECT
            cik,
            ingestion_date,
            COUNT(*) AS n
        FROM read_parquet('data/bronze/bronze_companies.parquet')
        GROUP BY cik, ingestion_date
        HAVING COUNT(*) > 1
        """
    ).df()

    assert result.empty


def test_each_source_file_generates_one_company_row():
    """
    Each submissions.json file should generate exactly
    one row in bronze_companies.
    """

    con = duckdb.connect()

    result = con.execute(
        """
        SELECT
            source_file,
            COUNT(*) AS n
        FROM read_parquet('data/bronze/bronze_companies.parquet')
        GROUP BY source_file
        HAVING COUNT(*) > 1
        """
    ).df()

    assert result.empty


def test_filings_count_is_reasonable():
    con = duckdb.connect()

    result = con.execute(
        """
        SELECT
            cik,
            COUNT(*) AS filings_count
        FROM read_parquet('data/bronze/bronze_filings_recent.parquet')
        GROUP BY cik
        ORDER BY filings_count DESC
        """
    ).df()

    assert not result.empty
    assert result["filings_count"].min() > 0


def test_filings_ciks_exist_in_companies():
    """
    Basic referential integrity:
    every CIK present in filings
    must exist in companies.
    """

    con = duckdb.connect()

    result = con.execute(
        """
        WITH companies AS (
            SELECT DISTINCT cik
            FROM read_parquet('data/bronze/bronze_companies.parquet')
        ),
        filings AS (
            SELECT DISTINCT cik
            FROM read_parquet('data/bronze/bronze_filings_recent.parquet')
        )
        SELECT f.cik
        FROM filings f
        LEFT JOIN companies c
            ON f.cik = c.cik
        WHERE c.cik IS NULL
        """
    ).df()

    assert result.empty


def test_ingestion_dates_have_valid_format():
    """
    Ensure that all loaded partitions follow the pattern YYYY-MM-DD.
    """

    con = duckdb.connect()

    result = con.execute(
        """
        SELECT DISTINCT ingestion_date
        FROM read_parquet('data/bronze/bronze_companies.parquet')
        WHERE regexp_matches(
            ingestion_date,
            '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
        ) = FALSE
        """
    ).df()

    assert result.empty