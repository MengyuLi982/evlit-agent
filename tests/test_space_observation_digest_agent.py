from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from evagent.models import PaperRecord
from evagent.sub_agents.space_observation_digest import SpaceObservationDigestAgent


@dataclass(slots=True)
class _DummySettings:
    runs_dir: Path


class _StubRetriever:
    def __init__(self, results: dict[str, list[PaperRecord]]) -> None:
        self.results = results

    def search(
        self,
        query: str,
        per_source_limit: int = 3,
        profile_name: str | None = None,
        year_from: int | None = None,
        min_score: float | None = None,
    ) -> tuple[list[PaperRecord], dict]:
        rows = self.results.get(query, [])
        return rows, {"source_errors": {}, "filter_stats": {"after_dedup": len(rows)}}


def _paper(
    *,
    paper_id: str,
    title: str,
    source: str,
    year: int,
    published_at: str | None,
    score: float,
    doi: str | None = None,
) -> PaperRecord:
    md = {"retrieval_score": score}
    if published_at:
        md["published_at"] = published_at
    return PaperRecord(
        source=source,
        paper_id=paper_id,
        title=title,
        year=year,
        authors=["A"],
        abstract=f"{title}. This paper studies event-camera methods for space observation.",
        url=f"https://example.com/{paper_id}",
        doi=doi,
        metadata=md,
    )


def test_digest_run_once_persists_outputs_and_state(tmp_path: Path) -> None:
    queries = ("q1", "q2")
    retriever = _StubRetriever(
        {
            "q1": [
                _paper(
                    paper_id="arxiv:2501.00001",
                    title="A",
                    source="arxiv",
                    year=2025,
                    published_at="2025-01-01T00:00:00Z",
                    score=0.70,
                    doi="10.1000/shared-doi",
                ),
                _paper(
                    paper_id="openalex:W1",
                    title="A updated",
                    source="openalex",
                    year=2025,
                    published_at="2025-01-02",
                    score=0.90,
                    doi="10.1000/shared-doi",
                ),
            ],
            "q2": [
                _paper(
                    paper_id="arxiv:2502.00002",
                    title="B",
                    source="arxiv",
                    year=2025,
                    published_at="2025-02-01T00:00:00Z",
                    score=0.80,
                )
            ],
        }
    )

    settings = _DummySettings(runs_dir=tmp_path / "runs")
    agent = SpaceObservationDigestAgent(
        settings=settings,  # type: ignore[arg-type]
        retriever=retriever,
        queries=queries,
        output_dir=tmp_path / "output",
    )

    report = agent.run_once(
        max_items=2,
        per_source_limit=5,
        notify=False,
        now=datetime(2026, 3, 5, 9, 0, tzinfo=timezone.utc),
    )

    assert len(report.items) == 2
    assert report.items[0].paper_id == "arxiv:2502.00002"
    assert report.items[1].paper_id == "openalex:W1"
    assert report.output_markdown_path is not None and report.output_markdown_path.exists()
    assert report.output_json_path is not None and report.output_json_path.exists()
    assert (tmp_path / "output" / "latest.md").exists()

    state = json.loads((tmp_path / "output" / "state.json").read_text(encoding="utf-8"))
    assert "arxiv:2502.00002" in state["sent_ids"]
    assert "openalex:W1" in state["sent_ids"]


def test_digest_run_once_falls_back_when_everything_was_sent(tmp_path: Path) -> None:
    queries = ("q1",)
    retriever = _StubRetriever(
        {
            "q1": [
                _paper(
                    paper_id="arxiv:2601.00001",
                    title="Latest",
                    source="arxiv",
                    year=2026,
                    published_at="2026-01-10T00:00:00Z",
                    score=0.88,
                )
            ]
        }
    )
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "state.json").write_text(
        json.dumps({"sent_ids": ["arxiv:2601.00001"]}, indent=2),
        encoding="utf-8",
    )

    settings = _DummySettings(runs_dir=tmp_path / "runs")
    agent = SpaceObservationDigestAgent(
        settings=settings,  # type: ignore[arg-type]
        retriever=retriever,
        queries=queries,
        output_dir=output_dir,
    )
    report = agent.run_once(
        max_items=1,
        per_source_limit=3,
        notify=False,
        now=datetime(2026, 3, 5, 9, 0, tzinfo=timezone.utc),
    )

    assert report.used_fallback is True
    assert len(report.items) == 1
    assert report.items[0].paper_id == "arxiv:2601.00001"

