from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class BronzeCompaniesSchema:
    table_name: ClassVar[str] = "bronze_companies"

    columns: ClassVar[list[str]] = [
        "cik",
        "name",
        "entity_type",
        "sic",
        "sic_description",
        "owner_org",
        "insider_transaction_for_owner_exists",
        "insider_transaction_for_issuer_exists",
        "tickers",
        "exchanges",
        "ein",
        "lei",
        "category",
        "fiscal_year_end",
        "state_of_incorporation",
        "state_of_incorporation_description",
        "mailing_street1",
        "mailing_street2",
        "mailing_city",
        "mailing_state_or_country",
        "mailing_zip_code",
        "business_street1",
        "business_street2",
        "business_city",
        "business_state_or_country",
        "business_zip_code",
        "ingestion_date",
        "source_file",
        "load_ts",
    ]


@dataclass(frozen=True)
class BronzeFilingsRecentSchema:
    table_name: ClassVar[str] = "bronze_filings_recent"

    columns: ClassVar[list[str]] = [
        "cik",
        "accession_number",
        "filing_date",
        "report_date",
        "acceptance_datetime",
        "act",
        "form",
        "file_number",
        "film_number",
        "items",
        "size",
        "is_xbrl",
        "is_inline_xbrl",
        "primary_document",
        "core_type",
        "ingestion_date",
        "source_file",
        "load_ts",
    ]