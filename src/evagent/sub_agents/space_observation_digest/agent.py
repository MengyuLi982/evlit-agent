from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from evagent.config import Settings
from evagent.domain import get_profile
from evagent.index.store import append_jsonl
from evagent.models import PaperRecord, dedup_key
from evagent.observability.tracing import get_logger
from evagent.sources import MultiSourceRetriever

DEFAULT_DIGEST_QUERIES: tuple[str, ...] = (
    "event camera space observation",
    "event-based vision star tracking satellite observation",
    "neuromorphic event camera space situational awareness",
)


class RetrieverLike(Protocol):
    def search(
        self,
        query: str,
        per_source_limit: int = 3,
        profile_name: str | None = None,
        year_from: int | None = None,
        min_score: float | None = None,
    ) -> tuple[list[PaperRecord], dict]: ...


@dataclass(slots=True)
class DigestItem:
    paper_id: str
    title: str
    source: str
    year: int | None
    published_at: str | None
    url: str | None
    main_content: str
    relevance_score: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "source": self.source,
            "year": self.year,
            "published_at": self.published_at,
            "url": self.url,
            "main_content": self.main_content,
            "relevance_score": self.relevance_score,
        }


@dataclass(slots=True)
class DigestReport:
    run_date: date
    generated_at: str
    profile_name: str
    queries: tuple[str, ...]
    total_candidates: int
    used_fallback: bool
    items: list[DigestItem] = field(default_factory=list)
    query_trace: list[dict[str, Any]] = field(default_factory=list)
    output_markdown_path: Path | None = None
    output_json_path: Path | None = None
    notified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_date": self.run_date.isoformat(),
            "generated_at": self.generated_at,
            "profile_name": self.profile_name,
            "queries": list(self.queries),
            "total_candidates": self.total_candidates,
            "used_fallback": self.used_fallback,
            "items": [item.to_dict() for item in self.items],
            "query_trace": self.query_trace,
            "output_markdown_path": str(self.output_markdown_path) if self.output_markdown_path else None,
            "output_json_path": str(self.output_json_path) if self.output_json_path else None,
            "notified": self.notified,
        }


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        if len(text) == 10:
            return datetime.fromisoformat(text + "T00:00:00+00:00")
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _paper_datetime(record: PaperRecord) -> datetime:
    md = record.metadata or {}
    for key in ("published_at", "publication_date", "issued_date"):
        parsed = _parse_iso_datetime(md.get(key))
        if parsed is not None:
            return parsed

    if record.year is not None:
        return datetime(record.year, 1, 1, tzinfo=timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _score(record: PaperRecord) -> float:
    try:
        return float((record.metadata or {}).get("retrieval_score", 0.0))
    except Exception:
        return 0.0


def _record_priority(record: PaperRecord) -> tuple[datetime, int, float]:
    return (_paper_datetime(record), record.year or 0, _score(record))


def _extract_main_content(text: str | None, limit: int = 300) -> str:
    if not text:
        return "No abstract available."

    normalized = " ".join(text.split()).strip()
    if not normalized:
        return "No abstract available."

    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    summary = " ".join(sentences[:2]).strip() if sentences else normalized
    if len(summary) <= limit:
        return summary
    return summary[: limit - 3] + "..."


def send_desktop_notification(title: str, message: str) -> bool:
    system = platform.system().lower()
    try:
        if system == "linux" and shutil.which("notify-send"):
            subprocess.run(["notify-send", title, message], check=False)
            return True
        if system == "darwin" and shutil.which("osascript"):
            safe_title = title.replace('"', r"\"")
            safe_message = message.replace('"', r"\"")
            script = f'display notification "{safe_message}" with title "{safe_title}"'
            subprocess.run(["osascript", "-e", script], check=False)
            return True
    except Exception:
        return False
    return False


class SpaceObservationDigestAgent:
    def __init__(
        self,
        settings: Settings,
        *,
        retriever: RetrieverLike | None = None,
        profile_name: str = "sps_space_event_startracking",
        year_from: int | None = None,
        min_score: float | None = None,
        queries: tuple[str, ...] = DEFAULT_DIGEST_QUERIES,
        output_dir: Path | None = None,
        state_path: Path | None = None,
    ) -> None:
        profile = get_profile(profile_name)

        self.settings = settings
        self.retriever = retriever or MultiSourceRetriever(settings)
        self.profile_name = profile_name
        self.year_from = year_from if year_from is not None else profile.default_year_from
        self.min_score = min_score if min_score is not None else profile.default_min_score
        self.queries = queries
        self.output_dir = output_dir or Path("output/sub_agents/space_observation_digest")
        self.state_path = state_path or (self.output_dir / "state.json")
        self.runs_path = settings.runs_dir / "space_observation_digest_runs.jsonl"
        self.logger = get_logger("evagent.subagent.space_observation_digest")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _parse_clock(clock: str) -> tuple[int, int]:
        value = clock.strip()
        m = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", value)
        if not m:
            raise ValueError("clock must be HH:MM (24-hour format)")
        return int(m.group(1)), int(m.group(2))

    @staticmethod
    def _resolve_timezone(timezone_name: str | None) -> timezone | ZoneInfo:
        if timezone_name:
            return ZoneInfo(timezone_name)
        local_tz = datetime.now().astimezone().tzinfo
        return local_tz if local_tz is not None else timezone.utc

    def _collect_candidates(self, per_source_limit: int) -> tuple[list[PaperRecord], list[dict[str, Any]]]:
        all_records: list[PaperRecord] = []
        trace: list[dict[str, Any]] = []

        for query in self.queries:
            rows, meta = self.retriever.search(
                query=query,
                per_source_limit=per_source_limit,
                profile_name=self.profile_name,
                year_from=self.year_from,
                min_score=self.min_score,
            )
            all_records.extend(rows)
            trace.append(
                {
                    "query": query,
                    "results": len(rows),
                    "source_errors": meta.get("source_errors", {}),
                    "filter_stats": meta.get("filter_stats", {}),
                }
            )

        return all_records, trace

    @staticmethod
    def _dedup_and_rank(records: list[PaperRecord]) -> list[PaperRecord]:
        best: dict[str, PaperRecord] = {}
        for rec in records:
            key = dedup_key(rec)
            existing = best.get(key)
            if existing is None or _record_priority(rec) > _record_priority(existing):
                best[key] = rec

        ranked = list(best.values())
        ranked.sort(key=_record_priority, reverse=True)
        return ranked

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"sent_ids": []}

        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return {"sent_ids": []}

        if not isinstance(payload, dict):
            return {"sent_ids": []}
        if not isinstance(payload.get("sent_ids"), list):
            payload["sent_ids"] = []
        return payload

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _to_item(record: PaperRecord) -> DigestItem:
        published_dt = _paper_datetime(record)
        published_text = None
        if published_dt.year >= 1971:
            published_text = published_dt.date().isoformat()

        return DigestItem(
            paper_id=record.paper_id,
            title=(record.title or "").strip() or "Untitled paper",
            source=record.source,
            year=record.year,
            published_at=published_text,
            url=record.url,
            main_content=_extract_main_content(record.abstract),
            relevance_score=_score(record),
        )

    def _render_markdown(self, report: DigestReport) -> str:
        lines = [
            f"# Space Observation Digest ({report.run_date.isoformat()})",
            "",
            f"- Generated at: {report.generated_at}",
            f"- Profile: {report.profile_name}",
            f"- Queries: {', '.join(report.queries)}",
            f"- Candidate count: {report.total_candidates}",
            f"- Fallback to previous papers: {'yes' if report.used_fallback else 'no'}",
            "",
        ]

        if not report.items:
            lines.append("No matching papers found in this run.")
            return "\n".join(lines) + "\n"

        for idx, item in enumerate(report.items, start=1):
            lines.append(f"## {idx}. {item.title}")
            lines.append(f"- Source: {item.source}")
            lines.append(f"- Published: {item.published_at or item.year or 'unknown'}")
            lines.append(f"- URL: {item.url or 'N/A'}")
            lines.append(f"- Main content: {item.main_content}")
            lines.append("")

        return "\n".join(lines)

    def _persist_report(self, report: DigestReport) -> None:
        day_tag = report.run_date.isoformat()
        markdown_path = self.output_dir / f"digest_{day_tag}.md"
        json_path = self.output_dir / f"digest_{day_tag}.json"
        latest_path = self.output_dir / "latest.md"

        markdown_content = self._render_markdown(report)
        markdown_path.write_text(markdown_content, encoding="utf-8")
        latest_path.write_text(markdown_content, encoding="utf-8")
        json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

        report.output_markdown_path = markdown_path
        report.output_json_path = json_path

    def run_once(
        self,
        *,
        max_items: int = 5,
        per_source_limit: int = 6,
        notify: bool = True,
        now: datetime | None = None,
    ) -> DigestReport:
        run_time = now.astimezone() if now is not None else datetime.now().astimezone()
        all_candidates, query_trace = self._collect_candidates(per_source_limit=per_source_limit)
        ranked = self._dedup_and_rank(all_candidates)

        state = self._load_state()
        sent_ids = {item for item in state.get("sent_ids", []) if isinstance(item, str)}

        unseen = [paper for paper in ranked if paper.paper_id not in sent_ids]
        used_fallback = False
        selected = unseen[:max_items]
        if not selected:
            used_fallback = True
            selected = ranked[:max_items]

        items = [self._to_item(p) for p in selected]
        report = DigestReport(
            run_date=run_time.date(),
            generated_at=run_time.isoformat(),
            profile_name=self.profile_name,
            queries=self.queries,
            total_candidates=len(ranked),
            used_fallback=used_fallback,
            items=items,
            query_trace=query_trace,
        )

        self._persist_report(report)
        append_jsonl(self.runs_path, report.to_dict())

        history = [item for item in state.get("sent_ids", []) if isinstance(item, str)]
        for paper in selected:
            if paper.paper_id in history:
                history.remove(paper.paper_id)
            history.append(paper.paper_id)
        state["last_run"] = run_time.isoformat()
        state["sent_ids"] = history[-2000:]
        self._save_state(state)

        if notify:
            top_titles = " | ".join(item.title for item in items[:3]) if items else "No papers found today."
            report.notified = send_desktop_notification(
                "Event Camera Space Observation Digest",
                top_titles[:220],
            )

        self.logger.info(
            "space_observation_digest_done count=%s fallback=%s path=%s",
            len(report.items),
            report.used_fallback,
            str(report.output_markdown_path),
        )
        return report

    def run_daily(
        self,
        *,
        at: str = "09:00",
        timezone_name: str | None = None,
        max_items: int = 5,
        per_source_limit: int = 6,
        notify: bool = True,
    ) -> None:
        hour, minute = self._parse_clock(at)
        tzinfo = self._resolve_timezone(timezone_name)
        self.logger.info("space_observation_digest_scheduler_started at=%s tz=%s", at, str(tzinfo))

        while True:
            now = datetime.now(tzinfo)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

            sleep_seconds = max(1, int((next_run - now).total_seconds()))
            self.logger.info("next_digest_run at=%s sleep_seconds=%s", next_run.isoformat(), sleep_seconds)
            time.sleep(sleep_seconds)

            try:
                self.run_once(
                    max_items=max_items,
                    per_source_limit=per_source_limit,
                    notify=notify,
                    now=datetime.now(tzinfo),
                )
            except Exception as exc:
                self.logger.exception("scheduled_digest_run_failed error=%s", str(exc))

