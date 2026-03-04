from __future__ import annotations

from dataclasses import dataclass

import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class APIClient:
    base_url: str
    timeout: int = 20

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def get_json(self, path: str = "", *, params: dict | None = None, headers: dict | None = None) -> dict:
        url = self.base_url.rstrip("/") + ("/" + path.lstrip("/") if path else "")
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def get_text(self, path: str = "", *, params: dict | None = None, headers: dict | None = None) -> str:
        url = self.base_url.rstrip("/") + ("/" + path.lstrip("/") if path else "")
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text
