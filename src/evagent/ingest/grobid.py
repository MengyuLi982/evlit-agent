from __future__ import annotations

from pathlib import Path

import requests


def parse_pdf_with_grobid(grobid_url: str, pdf_path: Path) -> str:
    endpoint = grobid_url.rstrip("/") + "/api/processFulltextDocument"
    with pdf_path.open("rb") as f:
        files = {"input": (pdf_path.name, f, "application/pdf")}
        resp = requests.post(endpoint, files=files, timeout=90)
    resp.raise_for_status()
    return resp.text
