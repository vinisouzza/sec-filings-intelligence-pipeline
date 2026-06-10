from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.config import get_settings


@dataclass
class SECClient:
    session: requests.Session
    timeout: int

    def __init__(
        self,
        user_agent: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        settings = get_settings()

        resolved_user_agent = user_agent or settings.SEC_USER_AGENT
        if not resolved_user_agent:
            raise ValueError(
                "SEC_USER_AGENT is required. Set it in .env, environment variables, "
                "or pass it explicitly to SECClient."
            )

        self.session = requests.Session()
        self.timeout = timeout or settings.REQUEST_TIMEOUT

        retries = Retry(
            total=max_retries or settings.MAX_RETRIES,
            connect=max_retries or settings.MAX_RETRIES,
            read=max_retries or settings.MAX_RETRIES,
            status=max_retries or settings.MAX_RETRIES,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update(
            {
                "User-Agent": resolved_user_agent,
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

    @staticmethod
    def _normalize_cik(cik: str) -> str:
        cik_str = str(cik).strip()
        if not cik_str.isdigit():
            raise ValueError(f"Invalid CIK: {cik!r}")
        return cik_str.zfill(10)

    def get_json(self, url: str) -> dict[str, Any]:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as exc:
            raise ValueError(f"Response from SEC is not valid JSON: {url}") from exc

    def get_submissions(self, cik: str) -> dict[str, Any]:
        cik_padded = self._normalize_cik(cik)
        url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        return self.get_json(url)

    def get_companyfacts(self, cik: str) -> dict[str, Any]:
        cik_padded = self._normalize_cik(cik)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
        return self.get_json(url)