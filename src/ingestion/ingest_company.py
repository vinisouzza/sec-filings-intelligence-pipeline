import json

from pathlib import Path

from ingestion.sec_client import SECClient

from utils.logger import get_logger

from datetime import datetime, UTC

logger = get_logger()


def ingest_company(cik: str) -> None:
    """Ingest the company data for a given CIK."""

    client = SECClient()

    data = client.get_submissions(cik)

    folder = (
        Path("data/raw/sec")
        / f"ingestion_date={datetime.now(UTC).date().isoformat()}"
        / f"cik={str(cik).zfill(10)}"
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

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

    
    last_run_file = Path("data/state/last_run.json")
    with open(
        last_run_file,
        "w",
        encoding="utf-8"
    ) as f:
    
        json.dump(
            {
                "last_run": str(datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"))
            },
            f,
            ensure_ascii=False,
            indent=4
        )
    
    logger.info(
        f"File saved: {output_file}"
    )