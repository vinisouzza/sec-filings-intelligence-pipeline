from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import pandas as pd

from bronze.parsers import parse_company_row, parse_recent_filings_rows
from utils.logger import get_logger

logger = get_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "sec"
BRONZE_ROOT = PROJECT_ROOT / "data" / "bronze" 


def find_submission_files() -> list[Path]:
    """
    Find all submissions.json files inside the RAW layer.
    Expected structure:
    data/raw/sec/ingestion_date=YYYY-MM-DD/cik=XXXXXXXXXX/submissions.json
    """
    return sorted(RAW_ROOT.glob("ingestion_date=*/cik=*/submissions.json"))


def load_json_file(file_path: Path) -> dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def extract_ingestion_date(file_path: Path) -> str:
    """
    Extract ingestion_date from path:
    .../ingestion_date=2026-06-04/cik=0000320193/submissions.json
    """
    ingestion_folder = file_path.parent.parent.name  # ingestion_date=YYYY-MM-DD
    return ingestion_folder.split("=", 1)[1]  # YYYY-MM-DD


def build_bronze() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build bronze_companies and bronze_filings_recent from raw SEC submissions.
    """
    submission_files = find_submission_files()

    if not submission_files:
        raise FileNotFoundError(
            f"No submissions.json files found under {RAW_ROOT}"
        )

    company_rows: list[dict[str, Any]] = []
    filing_rows: list[dict[str, Any]] = []

    logger.info("Found %d raw submission files", len(submission_files))

    for raw_file in submission_files:
        try:
            raw = load_json_file(raw_file)
            ingestion_date = extract_ingestion_date(raw_file)
            source_file = str(raw_file.relative_to(PROJECT_ROOT))

            company_rows.append(
                parse_company_row(
                    raw=raw,
                    source_file=source_file,
                    ingestion_date=ingestion_date,
                )
            )

            filing_rows.extend(
                parse_recent_filings_rows(
                    raw=raw,
                    source_file=source_file,
                    ingestion_date=ingestion_date,
                )
            )

            logger.info("Parsed raw file: %s", raw_file)

        except Exception:
            logger.exception("Failed to parse raw file: %s", raw_file)
            continue

    companies_df = pd.DataFrame(company_rows)
    filings_df = pd.DataFrame(filing_rows)

    return companies_df, filings_df


def save_bronze_tables(
    companies_df: pd.DataFrame,
    filings_df: pd.DataFrame,
) -> tuple[Path, Path]:
    """
    Save bronze tables as Parquet files.
    """
    BRONZE_ROOT.mkdir(parents=True, exist_ok=True)

    companies_path = BRONZE_ROOT / "bronze_companies.parquet"
    filings_path = BRONZE_ROOT / "bronze_filings_recent.parquet"

    companies_df.to_parquet(companies_path, index=False)
    filings_df.to_parquet(filings_path, index=False)

    logger.info("Saved bronze companies: %s | rows=%d", companies_path, len(companies_df))
    logger.info("Saved bronze filings: %s | rows=%d", filings_path, len(filings_df))

    return companies_path, filings_path


def main() -> None:
    logger.info("Starting bronze build at %s", datetime.now(UTC).isoformat())

    companies_df, filings_df = build_bronze()
    companies_path, filings_path = save_bronze_tables(companies_df, filings_df)

    logger.info(
        "Bronze build finished | companies=%d | filings=%d | companies_path=%s | filings_path=%s",
        len(companies_df),
        len(filings_df),
        companies_path,
        filings_path,
    )


if __name__ == "__main__":
    main()