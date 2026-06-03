import json
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional

from ingestion.sec_client import SECClient
from utils.logger import get_logger


logger = get_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def ingest_company(cik: str, client: Optional[SECClient] = None) -> Path:
    """
    Ingest the SEC submissions data for a given CIK and save it locally.
    
    Parameters
    ----------
    cik : str
        Company CIK.
    client : Optional[SECClient]
        Reusable SEC client instance. If None, a new one is created.
    
    Returns
    -------
    Path
        Path to the saved JSON file.
    """
    
    if client is None:
        client = SECClient()

    cik_str = str(cik).strip().zfill(10)
    ingestion_date = datetime.now(UTC).date().isoformat()

    logger.info(f"Starting ingestion for CIK={cik_str}")

    data = client.get_submissions(cik_str)

    folder = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "sec"
        / f"ingestion_date={ingestion_date}"
        / f"cik={cik_str}"
    )
    folder.mkdir(parents=True, exist_ok=True)

    output_file = folder / "submissions.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    
    logger.info(
        f"File saved: {output_file}"
    )

    return output_file