from __future__ import annotations

from xml.etree import ElementTree as ET

from evagent.models import PaperRecord
from evagent.sources.base import APIClient


class ArxivSource:
    def __init__(self) -> None:
        self.client = APIClient("http://export.arxiv.org/api/query")

    def search(self, query: str, limit: int = 5) -> list[PaperRecord]:
        text = self.client.get_text(params={"search_query": f"all:{query}", "start": 0, "max_results": limit})
        root = ET.fromstring(text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        out: list[PaperRecord] = []

        for entry in root.findall("atom:entry", ns):
            entry_id = entry.findtext("atom:id", default="", namespaces=ns)
            arxiv_id = entry_id.rstrip("/").split("/")[-1]
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip().replace("\n", " ")
            abstract = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip().replace("\n", " ")
            published = entry.findtext("atom:published", default="", namespaces=ns)
            updated = entry.findtext("atom:updated", default="", namespaces=ns)
            year = int(published[:4]) if len(published) >= 4 and published[:4].isdigit() else None
            authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]

            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href")
                    break

            out.append(
                PaperRecord(
                    source="arxiv",
                    paper_id=f"arxiv:{arxiv_id}",
                    title=title,
                    year=year,
                    authors=[a for a in authors if a],
                    abstract=abstract,
                    url=entry_id,
                    pdf_url=pdf_url,
                    metadata={
                        "published_at": published or None,
                        "updated_at": updated or None,
                    },
                )
            )

        return out
