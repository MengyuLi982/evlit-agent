from __future__ import annotations

import math
from dataclasses import dataclass

from evagent.domain import RetrievalProfile
from evagent.models import PaperRecord, dedup_key


@dataclass(slots=True)
class RankingStats:
    raw_count: int = 0
    after_component_filter: int = 0
    after_year_filter: int = 0
    after_score_filter: int = 0


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _normalized_text(record: PaperRecord) -> str:
    title = record.title or ""
    abstract = record.abstract or ""
    return f"{title} {abstract}".lower()


def _count_term_hits(text: str, terms: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for term in terms:
        if term in text:
            hits.append(term)
    return hits


def _score_record(record: PaperRecord, profile: RetrievalProfile, year_from: int) -> tuple[float, list[str], list[str]]:
    text = _normalized_text(record)
    pos_hits = _count_term_hits(text, profile.positive_terms)
    neg_hits = _count_term_hits(text, profile.negative_terms)

    domain_score = min(1.0, len(pos_hits) / 6.0)
    source_score = profile.source_weights.get(record.source, 0.5)
    recency_score = 1.0 if (record.year is not None and record.year >= year_from) else 0.0
    neg_penalty = min(0.5, 0.15 * len(neg_hits))

    final_score = _clamp(0.55 * domain_score + 0.25 * source_score + 0.20 * recency_score - neg_penalty)
    return final_score, pos_hits, neg_hits


def profile_filter_and_rank(
    records: list[PaperRecord],
    profile: RetrievalProfile,
    year_from: int,
    min_score: float,
) -> tuple[list[PaperRecord], dict[str, int]]:
    stats = RankingStats(raw_count=len(records))

    # Crossref component records are often supplementary artifacts; remove them first.
    non_component = [
        r
        for r in records
        if not (r.source == "crossref" and (r.metadata.get("type") or "").lower() == "component")
    ]
    stats.after_component_filter = len(non_component)

    year_filtered = [r for r in non_component if r.year is not None and r.year >= year_from]
    stats.after_year_filter = len(year_filtered)

    scored: list[PaperRecord] = []
    for record in year_filtered:
        score, pos_hits, neg_hits = _score_record(record, profile, year_from)
        if score < min_score:
            continue

        record.metadata["retrieval_score"] = round(score, 4)
        record.metadata["matched_terms"] = pos_hits[:8]
        if neg_hits:
            record.metadata["negative_terms"] = neg_hits[:4]
        scored.append(record)

    stats.after_score_filter = len(scored)

    # Dedup with best score retained.
    deduped: dict[str, PaperRecord] = {}
    for rec in scored:
        key = dedup_key(rec)
        existing = deduped.get(key)
        if existing is None:
            deduped[key] = rec
            continue

        existing_score = float(existing.metadata.get("retrieval_score", 0.0))
        current_score = float(rec.metadata.get("retrieval_score", 0.0))
        if current_score > existing_score:
            deduped[key] = rec

    ranked = list(deduped.values())
    ranked.sort(
        key=lambda r: (
            float(r.metadata.get("retrieval_score", 0.0)),
            -math.inf if r.year is None else r.year,
        ),
        reverse=True,
    )

    return ranked, {
        "raw_count": stats.raw_count,
        "after_component_filter": stats.after_component_filter,
        "after_year_filter": stats.after_year_filter,
        "after_score_filter": stats.after_score_filter,
        "after_dedup": len(ranked),
    }
