from __future__ import annotations

from evagent.models import PaperRecord
from evagent.sources.base import APIClient


class OpenAlexSource:
    def __init__(self, api_key: str | None = None):
        self.client = APIClient("https://api.openalex.org")
        self.api_key = api_key

    def search(self, query: str, limit: int = 5) -> list[PaperRecord]:
        params = {"search": query, "per-page": limit}
        if self.api_key:
            params["api_key"] = self.api_key

        data = self.client.get_json("works", params=params)
        out: list[PaperRecord] = []

        for w in data.get("results", []):
            ids = w.get("ids", {})
            doi = ids.get("doi", "").replace("https://doi.org/", "") or None
            paper_id = ids.get("openalex", w.get("id", "openalex:unknown")).replace("https://openalex.org/", "")
            authors = [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])]
            abstract = None
            abstract_inv = w.get("abstract_inverted_index")
            if isinstance(abstract_inv, dict) and abstract_inv:
                # Reconstruct rough abstract text from inverted index.
                pairs = []
                for token, positions in abstract_inv.items():
                    for pos in positions:
                        pairs.append((pos, token))
                abstract = " ".join(token for _, token in sorted(pairs))

            out.append(
                PaperRecord(
                    source="openalex",
                    paper_id=f"openalex:{paper_id}",
                    title=w.get("title", ""),
                    year=w.get("publication_year"),
                    authors=[a for a in authors if a],
                    abstract=abstract,
                    url=w.get("primary_location", {}).get("landing_page_url") or w.get("id"),
                    pdf_url=w.get("primary_location", {}).get("pdf_url"),
                    doi=doi,
                    metadata={
                        "referenced_works": w.get("referenced_works", []),
                        "cited_by_count": w.get("cited_by_count"),
                    },
                )
            )

        return out
