from __future__ import annotations

from pathlib import Path

import requests

from evagent.config import Settings
from evagent.index.store import append_jsonl
from evagent.ingest.grobid import parse_pdf_with_grobid


def _download_pdf(url: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=90)
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    return out_path


def ingest_pdf(settings: Settings, pdf: str) -> dict:
    cache_dir = settings.cache_dir / "pdf"
    if pdf.startswith("http://") or pdf.startswith("https://"):
        filename = pdf.rstrip("/").split("/")[-1] or "paper.pdf"
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        pdf_path = _download_pdf(pdf, cache_dir / filename)
    else:
        pdf_path = Path(pdf)

    tei_xml = parse_pdf_with_grobid(settings.grobid_url, pdf_path)
    record = {
        "pdf": str(pdf_path),
        "tei_length": len(tei_xml),
        "status": "parsed",
    }
    append_jsonl(settings.runs_dir / "ingest.jsonl", record)
    return record
