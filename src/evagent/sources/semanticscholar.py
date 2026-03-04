from __future__ import annotations

from evagent.models import PaperRecord
from evagent.sources.base import APIClient


class SemanticScholarSource:
    def __init__(self, api_key: str | None = None):
        self.client = APIClient("https://api.semanticscholar.org/graph/v1")
        self.api_key = api_key

    def search(self, query: str, limit: int = 5) -> list[PaperRecord]:
        headers = {"x-api-key": self.api_key} if self.api_key else None
        data = self.client.get_json(
            "paper/search",
            params={
                "query": query,
                "limit": limit,
                "fields": "title,abstract,year,authors,url,openAccessPdf,externalIds",
            },
            headers=headers,
        )

        out: list[PaperRecord] = []
        for item in data.get("data", []):
            external_ids = item.get("externalIds", {}) or {}
            doi = external_ids.get("DOI")
            arxiv = external_ids.get("ArXiv")
            paper_id = arxiv or item.get("paperId", "unknown")
            out.append(
                PaperRecord(
                    source="semanticscholar",
                    paper_id=f"s2:{paper_id}",
                    title=item.get("title", ""),
                    year=item.get("year"),
                    authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
                    abstract=item.get("abstract"),
                    url=item.get("url"),
                    pdf_url=(item.get("openAccessPdf", {}) or {}).get("url"),
                    doi=doi,
                    metadata={"external_ids": external_ids},
                )
            )
        return out
