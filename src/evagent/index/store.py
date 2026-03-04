from __future__ import annotations

import json
from pathlib import Path

try:
    import orjson
except Exception:  # pragma: no cover - optional dependency fallback
    orjson = None  # type: ignore[assignment]


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as f:
        if orjson is not None:
            payload = orjson.dumps(record)
        else:
            payload = json.dumps(record, ensure_ascii=False).encode("utf-8")
        f.write(payload)
        f.write(b"\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if orjson is not None:
                rows.append(orjson.loads(line))
            else:
                rows.append(json.loads(line.decode("utf-8")))
    return rows
