from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from evagent.agents.graph import build_graph
from evagent.config import get_settings
from evagent.domain import get_profile, list_profiles
from evagent.index.store import append_jsonl
from evagent.ingest.pipeline import ingest_pdf
from evagent.llm.client import LLMClient
from evagent.observability.tracing import configure_logging, get_logger
from evagent.sources import MultiSourceRetriever
from evagent.sub_agents.space_observation_digest import SpaceObservationDigestAgent

app = typer.Typer(help="EventVision literature multi-agent CLI")
console = Console()


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _short(text: str | None, limit: int = 320) -> str:
    value = (text or "").replace("\n", " ").strip()
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _compact_main_papers(candidates: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
    rows = []
    for c in candidates[:top_k]:
        md = c.get("metadata") or {}
        rows.append(
            {
                "paper_id": c.get("paper_id"),
                "title": c.get("title"),
                "year": c.get("year"),
                "source": c.get("source"),
                "relevance_score": md.get("retrieval_score"),
                "matched_terms": md.get("matched_terms", [])[:5],
                "authors": (c.get("authors") or [])[:4],
                "doi": c.get("doi"),
                "url": c.get("url"),
                "main_content": _short(c.get("abstract"), 240),
            }
        )
    return rows


def _compact_evidence(evidence: list[dict[str, Any]], top_k: int = 5) -> list[dict[str, Any]]:
    rows = []
    for e in evidence[:top_k]:
        rows.append(
            {
                "paper_id": e.get("paper_id"),
                "title": e.get("title"),
                "confidence": e.get("confidence"),
                "matched_terms": (e.get("matched_terms") or [])[:5],
                "snippet": _short(e.get("snippet"), 200),
            }
        )
    return rows


def _compact_query_trace(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for t in trace:
        fs = t.get("filter_stats", {})
        rows.append(
            {
                "query": t.get("query"),
                "raw_count": fs.get("raw_count", 0),
                "after_year_filter": fs.get("after_year_filter", 0),
                "after_score_filter": fs.get("after_score_filter", 0),
                "after_dedup": fs.get("after_dedup", 0),
                "source_errors": t.get("source_errors", {}),
            }
        )
    return rows


@app.command()
def search(
    query: str,
    limit: int = typer.Option(3, min=1, max=10),
    profile: str = typer.Option("sps_space_event_startracking", help="Retrieval profile name"),
    year_from: int = typer.Option(2021, min=1900, max=2100),
    min_score: float = typer.Option(0.55, min=0.0, max=1.0),
) -> None:
    """Search papers with profile-based filtering and reranking."""
    settings = get_settings()
    configure_logging(settings.log_level)
    retriever = MultiSourceRetriever(settings)

    rows, meta = retriever.search(
        query,
        per_source_limit=limit,
        profile_name=profile,
        year_from=year_from,
        min_score=min_score,
    )

    table = Table(title=f"Search results for: {query}")
    table.add_column("paper_id")
    table.add_column("year")
    table.add_column("source")
    table.add_column("score")
    table.add_column("matched_terms")
    table.add_column("title")

    for p in rows[:30]:
        md = p.metadata or {}
        table.add_row(
            p.paper_id,
            str(p.year or ""),
            p.source,
            str(md.get("retrieval_score", "")),
            ", ".join(md.get("matched_terms", [])[:3]),
            p.title[:70],
        )

    console.print(table)

    fstats = meta.get("filter_stats", {})
    console.print(
        "Filter stats:",
        {
            "profile": meta.get("profile"),
            "year_from": meta.get("year_from"),
            "min_score": meta.get("min_score"),
            **fstats,
        },
    )


@app.command()
def ask(
    query: str,
    limit: int = typer.Option(2, min=1, max=5),
    profile: str = typer.Option("sps_space_event_startracking", help="Retrieval profile name"),
    year_from: int = typer.Option(2021, min=1900, max=2100),
    min_score: float = typer.Option(0.55, min=0.0, max=1.0),
    min_evidence: int = typer.Option(3, min=1, max=10),
) -> None:
    """Run multi-agent workflow and generate a grounded answer."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("evagent.ask")

    retriever = MultiSourceRetriever(settings)
    llm = LLMClient(settings)
    graph = build_graph(retriever, llm)

    # If the caller passes an unknown profile, fall back to default profile.
    profile_obj = get_profile(profile)

    state = {
        "query": query,
        "profile_name": profile_obj.name,
        "year_from": year_from,
        "min_score": min_score,
        "min_evidence": min_evidence,
        "per_source_limit": limit,
        "retry_count": 0,
    }
    final_state = graph.invoke(state)

    answer = final_state.get("answer", "No answer")
    evidence = final_state.get("evidence", [])
    candidates = final_state.get("candidates", [])

    console.print("\n[bold]Answer[/bold]")
    console.print(answer)

    e_table = Table(title="Evidence")
    e_table.add_column("paper_id")
    e_table.add_column("title")
    e_table.add_column("confidence")
    e_table.add_column("matched_terms")
    for e in evidence[:8]:
        e_table.add_row(
            e.get("paper_id", ""),
            e.get("title", "")[:64],
            str(e.get("confidence", "")),
            ", ".join((e.get("matched_terms") or [])[:3]),
        )
    console.print(e_table)

    record = {
        "ts": _ts(),
        "query": query,
        "profile": profile_obj.name,
        "year_from": year_from,
        "min_score": min_score,
        "min_evidence": min_evidence,
        "answer": _short(answer, 900),
        "answer_excerpt": _short(answer, 420),
        "evidence_count": len(evidence),
        "candidate_count": len(candidates),
        "filter_stats": final_state.get("filter_stats", {}),
        "query_trace": _compact_query_trace(final_state.get("query_filter_stats", [])),
        "main_papers": _compact_main_papers(candidates, top_k=3),
        "evidence": _compact_evidence(evidence, top_k=5),
    }
    append_jsonl(settings.runs_dir / "ask_runs.jsonl", record)
    logger.info("run_saved path=%s query=%s", str(settings.runs_dir / "ask_runs.jsonl"), query)


@app.command()
def profiles() -> None:
    """List retrieval profiles."""
    table = Table(title="Retrieval Profiles")
    table.add_column("name")
    table.add_column("year_from")
    table.add_column("min_score")
    table.add_column("min_evidence")
    table.add_column("description")

    for p in list_profiles():
        table.add_row(
            p.name,
            str(p.default_year_from),
            str(p.default_min_score),
            str(p.default_min_evidence),
            p.description,
        )

    console.print(table)


@app.command()
def ingest(pdf: str = typer.Option(..., help="Local PDF path or URL")) -> None:
    """Parse a PDF via GROBID and store ingest run metadata."""
    settings = get_settings()
    configure_logging(settings.log_level)
    rec = ingest_pdf(settings, pdf)
    console.print(rec)


@app.command("cache-links")
def cache_links(markdown: str = typer.Argument("AI agent项目步骤.md")) -> None:
    """Cache markdown URLs with retrieval timestamps."""
    import subprocess

    script = Path("scripts/cache_links.sh")
    if not script.exists():
        raise typer.BadParameter("scripts/cache_links.sh not found")
    subprocess.run(["bash", str(script), markdown], check=True)
    console.print("Wrote references/source_urls.txt and references/source_urls.jsonl")


@app.command("space-observation-push")
def space_observation_push(
    schedule: bool = typer.Option(False, "--schedule", help="Run continuously and trigger once per day."),
    at: str = typer.Option("09:00", help="Daily trigger time in HH:MM."),
    timezone_name: str | None = typer.Option(None, "--tz", help="IANA timezone, e.g. Europe/Berlin."),
    max_items: int = typer.Option(5, min=1, max=20),
    per_source_limit: int = typer.Option(6, min=1, max=40),
    notify: bool = typer.Option(True, "--notify/--no-notify"),
) -> None:
    """Push latest event-camera papers in space observation domain."""
    settings = get_settings()
    configure_logging(settings.log_level)
    agent = SpaceObservationDigestAgent(settings=settings)

    if schedule:
        console.print(
            {
                "status": "scheduler_started",
                "daily_at": at,
                "timezone": timezone_name or "local",
                "max_items": max_items,
                "per_source_limit": per_source_limit,
            }
        )
        try:
            agent.run_daily(
                at=at,
                timezone_name=timezone_name,
                max_items=max_items,
                per_source_limit=per_source_limit,
                notify=notify,
            )
        except KeyboardInterrupt:
            console.print("Scheduler stopped.")
        return

    report = agent.run_once(
        max_items=max_items,
        per_source_limit=per_source_limit,
        notify=notify,
    )

    table = Table(title=f"Space Observation Digest ({report.run_date.isoformat()})")
    table.add_column("title")
    table.add_column("main_content")
    table.add_column("source")
    table.add_column("published")
    for item in report.items:
        table.add_row(
            item.title[:72],
            _short(item.main_content, 200),
            item.source,
            item.published_at or str(item.year or ""),
        )
    console.print(table)

    console.print(
        {
            "count": len(report.items),
            "fallback_to_seen": report.used_fallback,
            "notified": report.notified,
            "markdown": str(report.output_markdown_path) if report.output_markdown_path else None,
            "json": str(report.output_json_path) if report.output_json_path else None,
        }
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
