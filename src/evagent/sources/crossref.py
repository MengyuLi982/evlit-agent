from __future__ import annotations

from evagent.models import PaperRecord
from evagent.sources.base import APIClient


class CrossrefSource:
    def __init__(self, mailto: str | None = None):
        self.client = APIClient("https://api.crossref.org")
        self.mailto = mailto

    def search(self, query: str, limit: int = 5) -> list[PaperRecord]:
        params = {"query": query, "rows": limit}
        if self.mailto:
            params["mailto"] = self.mailto

        data = self.client.get_json("works", params=params)
        out: list[PaperRecord] = []

        for item in data.get("message", {}).get("items", []):
            doi = item.get("DOI")
            title = (item.get("title") or [""])[0]
            year = None
            parts = (item.get("published-print") or item.get("published-online") or {}).get("date-parts")
            published_at = None
            if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                maybe_year = parts[0][0]
                year = int(maybe_year) if isinstance(maybe_year, int) else None
                if year is not None:
                    month = parts[0][1] if len(parts[0]) > 1 and isinstance(parts[0][1], int) else 1
                    day = parts[0][2] if len(parts[0]) > 2 and isinstance(parts[0][2], int) else 1
                    month = min(12, max(1, month))
                    day = min(31, max(1, day))
                    published_at = f"{year:04d}-{month:02d}-{day:02d}"

            authors = []
            for a in item.get("author", []) or []:
                full = " ".join(x for x in [a.get("given", ""), a.get("family", "")] if x).strip()
                if full:
                    authors.append(full)

            out.append(
                PaperRecord(
                    source="crossref",
                    paper_id=f"crossref:{doi or item.get('URL', 'unknown')}",
                    title=title,
                    year=year,
                    authors=authors,
                    abstract=item.get("abstract"),
                    url=item.get("URL"),
                    doi=doi,
                    metadata={
                        "publisher": item.get("publisher"),
                        "type": item.get("type"),
                        "published_at": published_at,
                    },
                )
            )

        return out
