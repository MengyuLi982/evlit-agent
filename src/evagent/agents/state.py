from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    query: str
    profile_name: str
    year_from: int
    min_score: float
    min_evidence: int
    per_source_limit: int
    subqueries: list[str]
    candidates: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    answer: str
    needs_more: bool
    retry_count: int
    filter_stats: dict[str, Any]
    query_filter_stats: list[dict[str, Any]]
