import requests

from tenacity import retry, stop_after_attempt, wait_exponential

from utils.config import settings


class SECClient:
    """Client for interacting with the SEC EDGAR API."""

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": settings.SEC_USER_AGENT
        })

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1)
    )
    
    def get_json(self, url: str) -> dict:
        """Make a GET request to the specified URL and return the JSON response."""

        response = self.session.get(
            url,
            timeout=settings.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()
    
    def get_submissions(self, cik: str) -> dict:
        """Get the submissions for a given CIK."""

        cik = str(cik).zfill(10)

        url = (
            f"https://data.sec.gov/submissions/"
            f"CIK{cik}.json"
        )

        return self.get_json(url)