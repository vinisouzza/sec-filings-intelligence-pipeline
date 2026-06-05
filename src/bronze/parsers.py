from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_company_row(raw: dict[str, Any], source_file: str, ingestion_date: str) -> dict[str, Any]:
    addresses = raw.get("addresses", {})
    mailing = addresses.get("mailing", {})
    business = addresses.get("business", {})

    return {
        "cik": raw.get("cik"),
        "name": raw.get("name"),
        "entity_type": raw.get("entityType"),
        "sic": raw.get("sic"),
        "sic_description": raw.get("sicDescription"),
        "owner_org": raw.get("ownerOrg"),
        "insider_transaction_for_owner_exists": raw.get("insiderTransactionForOwnerExists"),
        "insider_transaction_for_issuer_exists": raw.get("insiderTransactionForIssuerExists"),
        "tickers": raw.get("tickers"),
        "exchanges": raw.get("exchanges"),
        "ein": raw.get("ein"),
        "lei": raw.get("lei"),
        "category": raw.get("category"),
        "fiscal_year_end": raw.get("fiscalYearEnd"),
        "state_of_incorporation": raw.get("stateOfIncorporation"),
        "state_of_incorporation_description": raw.get("stateOfIncorporationDescription"),
        "mailing_street1": mailing.get("street1"),
        "mailing_street2": mailing.get("street2"),
        "mailing_city": mailing.get("city"),
        "mailing_state_or_country": mailing.get("stateOrCountry"),
        "mailing_zip_code": mailing.get("zipCode"),
        "business_street1": business.get("street1"),
        "business_street2": business.get("street2"),
        "business_city": business.get("city"),
        "business_state_or_country": business.get("stateOrCountry"),
        "business_zip_code": business.get("zipCode"),
        "ingestion_date": ingestion_date,
        "source_file": source_file,
        "load_ts": _now_iso(),
    }


def parse_recent_filings_rows(raw: dict[str, Any], source_file: str, ingestion_date: str) -> list[dict[str, Any]]:
    cik = raw.get("cik")
    filings = raw.get("filings", {})
    recent = filings.get("recent", {})

    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    acceptance_datetimes = recent.get("acceptanceDateTime", [])
    acts = recent.get("act", [])
    forms = recent.get("form", [])
    file_numbers = recent.get("fileNumber", [])
    film_numbers = recent.get("filmNumber", [])
    items = recent.get("items", [])
    sizes = recent.get("size", [])
    is_xbrl = recent.get("isXBRL", [])
    is_inline_xbrl = recent.get("isInlineXBRL", [])
    primary_documents = recent.get("primaryDocument", [])

    n = len(accession_numbers)

    rows: list[dict[str, Any]] = []
    for i in range(n):
        rows.append(
            {
                "cik": cik,
                "accession_number": accession_numbers[i] if i < len(accession_numbers) else None,
                "filing_date": filing_dates[i] if i < len(filing_dates) else None,
                "report_date": report_dates[i] if i < len(report_dates) else None,
                "acceptance_datetime": acceptance_datetimes[i] if i < len(acceptance_datetimes) else None,
                "act": acts[i] if i < len(acts) else None,
                "form": forms[i] if i < len(forms) else None,
                "file_number": file_numbers[i] if i < len(file_numbers) else None,
                "film_number": film_numbers[i] if i < len(film_numbers) else None,
                "items": items[i] if i < len(items) else None,
                "size": sizes[i] if i < len(sizes) else None,
                "is_xbrl": is_xbrl[i] if i < len(is_xbrl) else None,
                "is_inline_xbrl": is_inline_xbrl[i] if i < len(is_inline_xbrl) else None,
                "primary_document": primary_documents[i] if i < len(primary_documents) else None,
                "core_type": recent.get("coreType", [None] * n)[i] if isinstance(recent.get("coreType"), list) else None,
                "ingestion_date": ingestion_date,
                "source_file": source_file,
                "load_ts": _now_iso(),
            }
        )

    return rows