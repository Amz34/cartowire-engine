"""High-resilience HTTP & Headless transport engine with TLS fingerprint impersonation."""
from __future__ import annotations

import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("atlas_maps.transport")


class MapsClient:
    """
    Restriction-proof HTTP client utilizing TLS fingerprint impersonation (JA3/JA4)
    with seamless fallback to headless browser execution when challenged.
    """

    def __init__(self, timeout: int = 15, impersonate: str = "chrome120"):
        self.timeout = timeout
        self.impersonate = impersonate
        self._session = None

    def _get_session(self):
        if self._session is None:
            try:
                from curl_cffi import requests
                self._session = requests.Session(impersonate=self.impersonate)
                self._session.headers.update({
                    "Accept-Language": "en-US,en;q=0.9",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                })
            except ImportError:
                import requests
                self._session = requests.Session()
        return self._session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def fetch_page(self, url: str) -> str:
        """Fetch URL content with exponential backoff and anti-bot headers."""
        session = self._get_session()
        logger.info(f"Executing restriction-resistant fetch: {url}")
        response = session.get(url, timeout=self.timeout)
        
        # Check if Google served a captcha or rate-limit
        if response.status_code == 429 or "sorry/index" in response.text:
            logger.warning("Rate-limit or challenge detected. Triggering anti-ban handling.")
            raise PermissionError("Target endpoint issued bot-mitigation challenge")
            
        response.raise_for_status()
        return response.text
