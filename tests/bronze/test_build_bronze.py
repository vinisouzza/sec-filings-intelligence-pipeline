import json

import pandas as pd

from bronze import build_bronze as bb


def test_build_bronze(tmp_path, monkeypatch):
    raw_root = (
        tmp_path
        / "data"
        / "raw"
        / "sec"
        / "ingestion_date=2026-06-04"
        / "cik=0000320193"
    )
    raw_root.mkdir(parents=True, exist_ok=True)

    raw_file = raw_root / "submissions.json"
    raw_file.write_text(
        json.dumps(
            {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "entityType": "operating",
                "sic": "3571",
                "sicDescription": "Electronic Computers",
                "ownerOrg": "06 Technology",
                "insiderTransactionForOwnerExists": 0,
                "insiderTransactionForIssuerExists": 1,
                "tickers": ["AAPL"],
                "exchanges": ["Nasdaq"],
                "ein": "942404110",
                "lei": None,
                "category": "Large accelerated filer",
                "fiscalYearEnd": "0926",
                "stateOfIncorporation": "CA",
                "stateOfIncorporationDescription": "CA",
                "addresses": {
                    "mailing": {
                        "street1": "ONE APPLE PARK WAY",
                        "street2": None,
                        "city": "CUPERTINO",
                        "stateOrCountry": "CA",
                        "zipCode": "95014",
                    },
                    "business": {
                        "street1": "ONE APPLE PARK WAY",
                        "street2": None,
                        "city": "CUPERTINO",
                        "stateOrCountry": "CA",
                        "zipCode": "95014",
                    },
                },
                "filings": {
                    "recent": {
                        "accessionNumber": [
                            "0000320193-25-000108",
                            "0000320193-25-000080",
                        ],
                        "filingDate": ["2025-08-01", "2025-05-02"],
                        "reportDate": ["2025-06-28", "2025-03-29"],
                        "acceptanceDateTime": [
                            "2025-08-01T18:00:00.000Z",
                            "2025-05-02T18:00:00.000Z",
                        ],
                        "act": ["34", "34"],
                        "form": ["10-K", "10-Q"],
                        "fileNumber": ["001-36743", "001-36743"],
                        "filmNumber": ["251156000", "251112000"],
                        "items": [None, None],
                        "size": [12345, 6789],
                        "isXBRL": [1, 1],
                        "isInlineXBRL": [1, 1],
                        "primaryDocument": ["a10-k.htm", "a10-q.htm"],
                        "coreType": ["10-K", "10-Q"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(bb, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(bb, "RAW_ROOT", tmp_path / "data" / "raw" / "sec")
    monkeypatch.setattr(bb, "BRONZE_ROOT", tmp_path / "data" / "bronze")

    companies_df, filings_df = bb.build_bronze()

    assert isinstance(companies_df, pd.DataFrame)
    assert isinstance(filings_df, pd.DataFrame)

    assert not companies_df.empty
    assert not filings_df.empty

    assert "cik" in companies_df.columns
    assert "name" in companies_df.columns
    assert "mailing_city" in companies_df.columns

    assert "cik" in filings_df.columns
    assert "form" in filings_df.columns
    assert "primary_document" in filings_df.columns

    assert len(companies_df) == 1
    assert len(filings_df) == 2


def test_save_bronze_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(bb, "BRONZE_ROOT", tmp_path / "data" / "bronze")

    companies_df = pd.DataFrame(
        [
            {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "ingestion_date": "2026-06-04",
                "source_file": "data/raw/sec/ingestion_date=2026-06-04/cik=0000320193/submissions.json",
                "load_ts": "2026-06-04T19:22:33Z",
            }
        ]
    )

    filings_df = pd.DataFrame(
        [
            {
                "cik": "0000320193",
                "accession_number": "0000320193-25-000108",
                "form": "10-K",
                "ingestion_date": "2026-06-04",
                "source_file": "data/raw/sec/ingestion_date=2026-06-04/cik=0000320193/submissions.json",
                "load_ts": "2026-06-04T19:22:33Z",
            }
        ]
    )

    companies_path, filings_path = bb.save_bronze_tables(companies_df, filings_df)

    assert companies_path.exists()
    assert filings_path.exists()