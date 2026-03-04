from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from evagent.agents.state import AgentState
from evagent.domain import get_profile

if TYPE_CHECKING:  # pragma: no cover
    from evagent.llm.client import LLMClient
    from evagent.sources import MultiSourceRetriever


def plan_subquestions(state: AgentState) -> AgentState:
    query = state["query"]
    profile = get_profile(state.get("profile_name"))

    if profile.name == "sps_space_event_startracking":
        subqueries = [
            query,
            f"{query} event camera star tracking spacecraft jitter dataset benchmark",
            f"{query} attitude determination event-based vision method limitations",
            f"{query} satellite detection space situational awareness event camera",
            f"{query} open-source code reproducibility event star tracker",
        ]
    else:
        subqueries = [
            query,
            f"{query} dataset benchmark",
            f"{query} method limitations",
            f"{query} open-source code",
        ]

    return {"subqueries": subqueries}


def _focused_retry_subqueries(state: AgentState) -> list[str]:
    query = state["query"]
    return [
        f"{query} event camera star tracking dataset",
        f"{query} event camera attitude determination spacecraft jitter",
        f"{query} star tracker benchmark satellite operation",
    ]


def _merge_filter_stats(all_stats: list[dict[str, Any]]) -> dict[str, Any]:
    merged = {
        "raw_count": 0,
        "after_component_filter": 0,
        "after_year_filter": 0,
        "after_score_filter": 0,
        "after_dedup": 0,
        "query_count": len(all_stats),
    }
    for item in all_stats:
        filter_stats = item.get("filter_stats", {})
        for key in [
            "raw_count",
            "after_component_filter",
            "after_year_filter",
            "after_score_filter",
            "after_dedup",
        ]:
            merged[key] += int(filter_stats.get(key, 0))
    return merged


def retrieve_candidates(state: AgentState, retriever: MultiSourceRetriever) -> AgentState:
    per_source = state.get("per_source_limit", 2)
    retry_count = state.get("retry_count", 0)
    profile_name = state.get("profile_name")
    year_from = state.get("year_from")
    min_score = state.get("min_score")

    if retry_count > 0:
        per_source += 1
        subqueries = _focused_retry_subqueries(state)
    else:
        subqueries = state.get("subqueries", [state["query"]])

    seen: dict[str, dict[str, Any]] = {}
    query_filter_stats: list[dict[str, Any]] = []

    for sq in subqueries:
        papers, meta = retriever.search(
            query=sq,
            per_source_limit=per_source,
            profile_name=profile_name,
            year_from=year_from,
            min_score=min_score,
        )

        query_filter_stats.append(
            {
                "query": sq,
                "profile": meta.get("profile"),
                "source_limits": meta.get("source_limits", {}),
                "source_errors": meta.get("source_errors", {}),
                "filter_stats": meta.get("filter_stats", {}),
            }
        )

        for paper in papers:
            row = asdict(paper)
            key = row.get("paper_id", "")
            score = float((row.get("metadata") or {}).get("retrieval_score", 0.0))
            existing = seen.get(key)
            if existing is None:
                seen[key] = row
                continue

            old_score = float((existing.get("metadata") or {}).get("retrieval_score", 0.0))
            if score > old_score:
                seen[key] = row

    rows = list(seen.values())
    rows.sort(
        key=lambda r: (
            float((r.get("metadata") or {}).get("retrieval_score", 0.0)),
            r.get("year") or 0,
        ),
        reverse=True,
    )

    return {
        "candidates": rows,
        "query_filter_stats": query_filter_stats,
        "filter_stats": _merge_filter_stats(query_filter_stats),
    }


def extract_evidence(state: AgentState) -> AgentState:
    query = state["query"]
    evidence = []
    for p in state.get("candidates", [])[:12]:
        snippet = (p.get("abstract") or "").strip()
        if not snippet:
            continue
        metadata = p.get("metadata") or {}
        evidence.append(
            {
                "claim": query,
                "paper_id": p.get("paper_id", "unknown"),
                "title": p.get("title", "unknown"),
                "section": "abstract",
                "snippet": snippet[:480],
                "confidence": float(metadata.get("retrieval_score", 0.70)),
                "matched_terms": metadata.get("matched_terms", []),
            }
        )
    return {"evidence": evidence}


def critic_and_fix(state: AgentState) -> AgentState:
    evidence = state.get("evidence", [])
    retry_count = state.get("retry_count", 0)
    min_evidence = state.get("min_evidence", 3)
    needs_more = len(evidence) < min_evidence and retry_count < 1
    return {"needs_more": needs_more, "retry_count": retry_count + (1 if needs_more else 0)}


def draft_answer(state: AgentState, llm: LLMClient) -> AgentState:
    evidence = state.get("evidence", [])
    min_evidence = state.get("min_evidence", 3)
    profile_name = state.get("profile_name", "default")
    if len(evidence) < min_evidence:
        return {
            "answer": (
                f"Evidence is insufficient under profile '{profile_name}' "
                f"(found {len(evidence)} < required {min_evidence}). "
                "Please broaden the query or lower filtering constraints."
            )
        }

    answer = llm.summarize_evidence(state["query"], evidence)
    return {"answer": answer}
