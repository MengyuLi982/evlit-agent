#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required to run this script. Install with: pip install pyyaml"
    ) from exc


@dataclass
class CommitEntry:
    timestamp: str
    message: str
    paths: list[str]


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        joined = " ".join(cmd)
        raise RuntimeError(
            f"command failed ({proc.returncode}): {joined}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc.stdout.strip()


def git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    return run(["git", *args], cwd=cwd, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite repository history into gradual backdated commits from a manifest."
    )
    parser.add_argument("--source-ref", default="origin/main", help="Reference for final snapshot")
    parser.add_argument(
        "--work-branch", default="gradual-main", help="Branch to create for rewritten history"
    )
    parser.add_argument(
        "--manifest",
        default="references/rewrite_timeline_2025_06_to_2026_03.yaml",
        help="YAML file with commit timeline",
    )
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--author-email", required=True)
    parser.add_argument("--committer-name", default=None)
    parser.add_argument("--committer-email", default=None)
    parser.add_argument("--push-remote", default=None)
    parser.add_argument("--push-ref", default=None)
    parser.add_argument("--force-with-lease-sha", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def ensure_git_repo() -> None:
    git("rev-parse", "--is-inside-work-tree")


def ensure_clean_worktree() -> None:
    dirty = git("status", "--porcelain")
    if dirty:
        raise RuntimeError(
            "working tree is not clean; run this in a clean clone/branch.\n"
            f"status:\n{dirty}"
        )


def load_manifest(path: Path) -> list[CommitEntry]:
    if not path.exists():
        raise RuntimeError(f"manifest not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("manifest root must be a map")

    commits = data.get("commits")
    if not isinstance(commits, list) or not commits:
        raise RuntimeError("manifest must contain non-empty 'commits' list")

    entries: list[CommitEntry] = []
    for idx, raw in enumerate(commits, start=1):
        if not isinstance(raw, dict):
            raise RuntimeError(f"commit #{idx}: entry must be a map")
        ts = raw.get("timestamp")
        msg = raw.get("message")
        paths = raw.get("paths")

        if not isinstance(ts, str) or not ts:
            raise RuntimeError(f"commit #{idx}: invalid timestamp")
        if not isinstance(msg, str) or not msg:
            raise RuntimeError(f"commit #{idx}: invalid message")
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
            raise RuntimeError(f"commit #{idx}: invalid paths list")

        _parse_iso8601(ts, where=f"commit #{idx}")
        entries.append(CommitEntry(timestamp=ts, message=msg, paths=paths))

    return entries


def _parse_iso8601(value: str, *, where: str) -> dt.datetime:
    txt = value
    if txt.endswith("Z"):
        txt = txt[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(txt)
    except ValueError as exc:
        raise RuntimeError(f"{where}: invalid ISO-8601 timestamp '{value}'") from exc
    if parsed.tzinfo is None:
        raise RuntimeError(f"{where}: timestamp must include timezone offset: '{value}'")
    return parsed


def load_source_paths(source_ref: str) -> list[str]:
    out = git("-c", "core.quotePath=false", "ls-tree", "-r", "--name-only", source_ref)
    paths = [line for line in out.splitlines() if line.strip()]
    if not paths:
        raise RuntimeError(f"source ref has no files: {source_ref}")
    return paths


def validate_coverage(entries: list[CommitEntry], source_paths: list[str]) -> None:
    source_set = set(source_paths)
    seen: dict[str, int] = {}

    for idx, entry in enumerate(entries, start=1):
        for path in entry.paths:
            if path in seen:
                raise RuntimeError(
                    f"path duplicated across commits: '{path}' in commit #{seen[path]} and #{idx}"
                )
            seen[path] = idx
            if path not in source_set:
                raise RuntimeError(f"manifest path not found in source snapshot: {path}")

    manifest_set = set(seen)
    missing = sorted(source_set - manifest_set)
    extra = sorted(manifest_set - source_set)
    if missing or extra:
        msg = []
        if missing:
            msg.append("missing from manifest:\n" + "\n".join(missing[:50]))
        if extra:
            msg.append("extra in manifest:\n" + "\n".join(extra[:50]))
        raise RuntimeError("manifest coverage mismatch\n" + "\n\n".join(msg))


def ensure_monotonic(entries: list[CommitEntry]) -> None:
    parsed = [_parse_iso8601(e.timestamp, where=f"message='{e.message}'") for e in entries]
    for i in range(1, len(parsed)):
        if parsed[i] <= parsed[i - 1]:
            raise RuntimeError(
                "manifest timestamps must be strictly increasing: "
                f"#{i} '{entries[i - 1].timestamp}' then #{i + 1} '{entries[i].timestamp}'"
            )


def chunked(values: list[str], size: int = 128) -> Iterable[list[str]]:
    for i in range(0, len(values), size):
        yield values[i : i + size]


def setup_orphan_branch(source_ref: str, branch: str) -> None:
    current = git("rev-parse", "--abbrev-ref", "HEAD")
    if current == branch:
        git("checkout", "--detach", source_ref)
    existing = git("branch", "--list", branch)
    if existing.strip():
        git("branch", "-D", branch)

    git("checkout", "--orphan", branch)
    # Make the orphan branch truly empty before staged restore operations.
    git("rm", "-rf", "--ignore-unmatch", ".")
    git("clean", "-fdx")


def apply_commits(
    entries: list[CommitEntry],
    source_ref: str,
    author_name: str,
    author_email: str,
    committer_name: str,
    committer_email: str,
) -> None:
    for idx, entry in enumerate(entries, start=1):
        for batch in chunked(entry.paths):
            git("restore", "--source", source_ref, "--", *batch)
            git("add", "--", *batch)

        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = entry.timestamp
        env["GIT_COMMITTER_DATE"] = entry.timestamp
        env["GIT_AUTHOR_NAME"] = author_name
        env["GIT_AUTHOR_EMAIL"] = author_email
        env["GIT_COMMITTER_NAME"] = committer_name
        env["GIT_COMMITTER_EMAIL"] = committer_email

        git(
            "commit",
            "-m",
            entry.message,
            "--author",
            f"{author_name} <{author_email}>",
            env=env,
        )
        print(f"[{idx:02d}/{len(entries)}] {entry.timestamp}  {entry.message}")


def verify_result(source_ref: str, branch: str, expected_count: int) -> None:
    git("diff", "--name-status", "--exit-code", source_ref, branch)

    source_tree = git("rev-parse", f"{source_ref}^{{tree}}")
    branch_tree = git("rev-parse", f"{branch}^{{tree}}")
    if source_tree != branch_tree:
        raise RuntimeError(f"tree mismatch: source={source_tree} branch={branch_tree}")

    count = int(git("rev-list", "--count", branch))
    if count != expected_count:
        raise RuntimeError(f"unexpected commit count: got={count} expected={expected_count}")

    dates = git("log", "--reverse", "--format=%aI", branch).splitlines()
    parsed = [_parse_iso8601(d, where="rewritten log") for d in dates]
    for i in range(1, len(parsed)):
        if parsed[i] <= parsed[i - 1]:
            raise RuntimeError("rewritten commit dates are not strictly increasing")


def maybe_push(
    branch: str,
    push_remote: str | None,
    push_ref: str | None,
    lease_sha: str | None,
) -> None:
    if not push_remote and not push_ref and not lease_sha:
        print("skip push: no push arguments provided")
        return

    if not push_remote or not push_ref or not lease_sha:
        raise RuntimeError(
            "push requires --push-remote, --push-ref, and --force-with-lease-sha together"
        )

    git(
        "push",
        f"--force-with-lease={push_ref}:{lease_sha}",
        push_remote,
        f"{branch}:{push_ref}",
    )
    print(f"push complete: {push_remote} {branch}:{push_ref}")


def print_plan(entries: list[CommitEntry], source_ref: str, branch: str) -> None:
    print("dry-run plan")
    print(f"source_ref: {source_ref}")
    print(f"work_branch: {branch}")
    print(f"commits: {len(entries)}")
    for idx, entry in enumerate(entries, start=1):
        print(f"{idx:02d}. {entry.timestamp}  {entry.message}  ({len(entry.paths)} paths)")


def main() -> int:
    args = parse_args()

    committer_name = args.committer_name or args.author_name
    committer_email = args.committer_email or args.author_email

    ensure_git_repo()
    ensure_clean_worktree()

    entries = load_manifest(Path(args.manifest))
    ensure_monotonic(entries)

    source_paths = load_source_paths(args.source_ref)
    validate_coverage(entries, source_paths)

    if args.dry_run:
        print_plan(entries, args.source_ref, args.work_branch)
        return 0

    setup_orphan_branch(args.source_ref, args.work_branch)
    apply_commits(
        entries,
        args.source_ref,
        args.author_name,
        args.author_email,
        committer_name,
        committer_email,
    )
    verify_result(args.source_ref, args.work_branch, len(entries))

    maybe_push(args.work_branch, args.push_remote, args.push_ref, args.force_with_lease_sha)

    print("rewrite complete")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
