from pathlib import Path
from datetime import datetime, UTC
import json 

from ingestion.ingest_company import ingest_company
from ingestion.sec_client import SECClient
from utils.logger import get_logger

logger = get_logger()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_FILE = PROJECT_ROOT / "data" / "watchlist.txt"
STATE_DIR = PROJECT_ROOT / "data" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_watchlist() -> list[str]:
    """Load the watchlist"""
    if not WATCHLIST_FILE.exists():
        raise FileNotFoundError(f"Watchlist not found: {WATCHLIST_FILE}")
    
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
    

def save_last_run() -> Path:
    """Save the last run timestamp"""
    last_run_file = STATE_DIR / "last_run.json"
    
    payload = {
        "last_run": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    }
    
    with open(last_run_file, "w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=4
        )

    return last_run_file


def main() -> None:
    watchlist = load_watchlist()
    client = SECClient()

    logger.info(f"Loaded {len(watchlist)} CIKs from watchlist")

    success_count = 0
    failed_count = 0
    
    for cik in watchlist:
        try:
            ingest_company(cik, client=client)
            success_count += 1
        except Exception as e:
            logger.error(f"Error ingesting CIK {cik}: {e}")
            failed_count += 1
    
    last_run_file = save_last_run()

    logger.info(
        "Run finished | success=%d | failed=%d | last_run_file=%s",
        success_count,
        failed_count,
        last_run_file
    )

if __name__ == "__main__":
    main()