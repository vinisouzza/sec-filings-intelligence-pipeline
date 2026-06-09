import pandas as pd

from silver import build_silver as bs


def test_build_silver_tables():
    companies_df, filings_df = bs.build_silver_tables()

    assert isinstance(companies_df, pd.DataFrame)
    assert isinstance(filings_df, pd.DataFrame)

    assert not companies_df.empty
    assert not filings_df.empty

    assert "cik" in companies_df.columns
    assert "company_name" in companies_df.columns
    assert "source_file" in companies_df.columns

    assert "cik" in filings_df.columns
    assert "accession_number" in filings_df.columns
    assert "source_file" in filings_df.columns


def test_save_silver_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(bs, "SILVER_ROOT", tmp_path / "data" / "silver")
    monkeypatch.setattr(bs, "SILVER_COMPANIES_PATH", tmp_path / "data" / "silver" / "silver_companies.parquet")
    monkeypatch.setattr(bs, "SILVER_FILINGS_PATH", tmp_path / "data" / "silver" / "silver_filings.parquet")

    companies_df = pd.DataFrame(
        [
            {
                "cik": "0000320193",
                "company_name": "Apple Inc.",
                "ticker": "AAPL",
                "exchange": "Nasdaq",
                "sic": "3571",
                "sic_description": "Electronic Computers",
                "state_of_incorporation": "CA",
                "category": "Large accelerated filer",
                "latest_ingestion_date": "2026-06-08",
                "source_file": "data/raw/sec/ingestion_date=2026-06-08/cik=0000320193/submissions.json",
            }
        ]
    )

    filings_df = pd.DataFrame(
        [
            {
                "cik": "0000320193",
                "accession_number": "0000320193-25-000108",
                "filing_date": "2025-08-01",
                "report_date": "2025-06-28",
                "acceptance_datetime": "2025-08-01 18:00:00",
                "form": "10-K",
                "file_number": "001-36743",
                "size": 12345,
                "is_xbrl": True,
                "is_inline_xbrl": True,
                "primary_document": "a10-k.htm",
                "ingestion_date": "2026-06-08",
                "source_file": "data/raw/sec/ingestion_date=2026-06-08/cik=0000320193/submissions.json",
            }
        ]
    )

    companies_path, filings_path = bs.save_silver_tables(companies_df, filings_df)

    assert companies_path.exists()
    assert filings_path.exists()