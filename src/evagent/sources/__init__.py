from __future__ import annotations

from math import ceil

from evagent.domain import RetrievalProfile, get_profile
from evagent.config import Settings
from evagent.models import PaperRecord
from evagent.retrieval import profile_filter_and_rank
from evagent.sources.arxiv import ArxivSource
from evagent.sources.crossref import CrossrefSource
from evagent.sources.openalex import OpenAlexSource
from evagent.sources.semanticscholar import SemanticScholarSource


class MultiSourceRetriever:
    def __init__(self, settings: Settings):
        self.arxiv = ArxivSource()
        self.openalex = OpenAlexSource(api_key=settings.openalex_api_key)
        self.s2 = SemanticScholarSource(api_key=settings.s2_api_key)
        self.crossref = CrossrefSource(mailto=settings.crossref_mailto)

    @staticmethod
    def _source_limits(base_limit: int) -> dict[str, int]:
        base = max(1, base_limit)
        return {
            "arxiv": ceil(1.5 * base),
            "openalex": ceil(1.3 * base),
            "semanticscholar": base,
            "crossref": max(1, int(0.7 * base)),
        }

    def search(
        self,
        query: str,
        per_source_limit: int = 3,
        profile_name: str | None = None,
        year_from: int | None = None,
        min_score: float | None = None,
    ) -> tuple[list[PaperRecord], dict]:
        profile: RetrievalProfile = get_profile(profile_name)
        effective_year_from = year_from if year_from is not None else profile.default_year_from
        effective_min_score = min_score if min_score is not None else profile.default_min_score

        limits = self._source_limits(per_source_limit)
        all_items: list[PaperRecord] = []
        source_errors: dict[str, str] = {}

        for source_name, search_fn in [
            ("arxiv", self.arxiv.search),
            ("openalex", self.openalex.search),
            ("semanticscholar", self.s2.search),
            ("crossref", self.crossref.search),
        ]:
            try:
                all_items.extend(search_fn(query=query, limit=limits[source_name]))
            except Exception as e:
                # Keep pipeline robust when one API fails or rate-limits.
                source_errors[source_name] = str(e)
                continue

        ranked, stats = profile_filter_and_rank(
            records=all_items,
            profile=profile,
            year_from=effective_year_from,
            min_score=effective_min_score,
        )

        return ranked, {
            "profile": profile.name,
            "year_from": effective_year_from,
            "min_score": effective_min_score,
            "source_limits": limits,
            "source_errors": source_errors,
            "filter_stats": stats,
        }
