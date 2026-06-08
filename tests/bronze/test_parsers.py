from bronze.parsers import parse_company_row, parse_recent_filings_rows


def test_parse_company_row():
    raw = {
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
    }

    row = parse_company_row(
        raw=raw,
        source_file="data/raw/sec/ingestion_date=2026-06-04/cik=0000320193/submissions.json",
        ingestion_date="2026-06-04",
    )

    assert row["cik"] == "0000320193"
    assert row["name"] == "Apple Inc."
    assert row["entity_type"] == "operating"
    assert row["sic"] == "3571"
    assert row["mailing_city"] == "CUPERTINO"
    assert row["business_zip_code"] == "95014"
    assert row["ingestion_date"] == "2026-06-04"
    assert row["source_file"].endswith("submissions.json")


def test_parse_recent_filings_rows():
    raw = {
        "cik": "0000320193",
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
        }
    }

    rows = parse_recent_filings_rows(
        raw=raw,
        source_file="data/raw/sec/ingestion_date=2026-06-04/cik=0000320193/submissions.json",
        ingestion_date="2026-06-04",
    )

    assert len(rows) == 2
    assert rows[0]["cik"] == "0000320193"
    assert rows[0]["accession_number"] == "0000320193-25-000108"
    assert rows[0]["filing_date"] == "2025-08-01"
    assert rows[0]["form"] == "10-K"
    assert rows[0]["primary_document"] == "a10-k.htm"
    assert rows[0]["core_type"] == "10-K"
    assert rows[1]["form"] == "10-Q"
    assert rows[1]["core_type"] == "10-Q"