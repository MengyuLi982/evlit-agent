from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PaperRecord:
    source: str
    paper_id: str
    title: str
    year: int | None = None
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    doi: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceItem:
    claim: str
    paper_id: str
    title: str
    section: str
    snippet: str
    confidence: float


def dedup_key(p: PaperRecord) -> str:
    if p.doi:
        return f"doi:{p.doi.lower()}"
    if p.paper_id.startswith("arxiv:"):
        return p.paper_id.lower()

    title = " ".join((p.title or "").lower().split())
    first_author = (p.authors[0].lower() if p.authors else "unknown")
    year = str(p.year or "na")
    return f"fallback:{title}|{first_author}|{year}"
