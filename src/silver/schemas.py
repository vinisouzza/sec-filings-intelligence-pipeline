from __future__ import annotations

SILVER_COMPANIES_COLUMNS = [
    "cik",
    "company_name",
    "ticker",
    "exchange",
    "sic",
    "sic_description",
    "state_of_incorporation",
    "category",
    "latest_ingestion_date",
    "source_file",
]

SILVER_FILINGS_COLUMNS = [
    "cik",
    "accession_number",
    "filing_date",
    "report_date",
    "acceptance_datetime",
    "form",
    "file_number",
    "size",
    "is_xbrl",
    "is_inline_xbrl",
    "primary_document",
    "ingestion_date",
    "source_file",
]