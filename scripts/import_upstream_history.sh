#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/import_upstream_history.sh add  --repo-url <url> --prefix <path> [--branch <name>] [--remote <name>]
  scripts/import_upstream_history.sh pull --repo-url <url> --prefix <path> [--branch <name>] [--remote <name>]

Modes:
  add   Import an upstream repository as a subtree.
  pull  Update an existing imported subtree from the same upstream.

Notes:
  - Upstream commits keep their original author/committer timestamps.
  - A local merge commit is created at import/update time.
USAGE
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

canonicalize_url() {
  printf '%s' "$1" | sed -E 's#\.git$##; s#/$##'
}

derive_remote_name() {
  local url="$1"
  local no_git repo owner

  no_git="${url%.git}"
  repo="$(basename "$no_git")"
  owner="$(basename "$(dirname "$no_git")")"

  printf 'upstream-%s-%s' "$owner" "$repo" | tr -c '[:alnum:]._-' '-'
}

resolve_branch() {
  local remote="$1"
  local head_branch

  head_branch="$(git remote show "$remote" | sed -n 's/.*HEAD branch: //p' | head -n 1 | tr -d '[:space:]')"
  if [[ -n "$head_branch" && "$head_branch" != "(unknown)" ]]; then
    printf '%s' "$head_branch"
    return
  fi

  for candidate in main master; do
    if git rev-parse --verify --quiet "refs/remotes/${remote}/${candidate}" >/dev/null; then
      printf '%s' "$candidate"
      return
    fi
  done

  fail "could not detect default branch for remote '$remote'; pass --branch explicitly"
}

ensure_git_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "current directory is not a git repository"
}

ensure_clean_worktree() {
  git diff --quiet || fail "working tree has unstaged changes; commit/stash first"
  git diff --cached --quiet || fail "index has staged changes; commit/stash first"
}

ensure_subtree_available() {
  git subtree -h >/dev/null 2>&1 || fail "git subtree is unavailable in this Git installation"
}

MODE="add"
REPO_URL=""
PREFIX=""
BRANCH=""
REMOTE_NAME=""

if [[ $# -gt 0 ]]; then
  case "$1" in
    add|pull)
      MODE="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
  esac
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url)
      [[ $# -ge 2 ]] || fail "--repo-url requires a value"
      REPO_URL="$2"
      shift 2
      ;;
    --prefix)
      [[ $# -ge 2 ]] || fail "--prefix requires a value"
      PREFIX="$2"
      shift 2
      ;;
    --branch)
      [[ $# -ge 2 ]] || fail "--branch requires a value"
      BRANCH="$2"
      shift 2
      ;;
    --remote)
      [[ $# -ge 2 ]] || fail "--remote requires a value"
      REMOTE_NAME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown argument: $1"
      ;;
  esac
done

[[ -n "$REPO_URL" ]] || {
  usage
  fail "--repo-url is required"
}
[[ -n "$PREFIX" ]] || {
  usage
  fail "--prefix is required"
}

ensure_git_repo
ensure_clean_worktree
ensure_subtree_available

if [[ -z "$REMOTE_NAME" ]]; then
  REMOTE_NAME="$(derive_remote_name "$REPO_URL")"
fi

if git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  EXISTING_URL="$(git remote get-url "$REMOTE_NAME")"
  if [[ "$(canonicalize_url "$EXISTING_URL")" != "$(canonicalize_url "$REPO_URL")" ]]; then
    fail "remote '$REMOTE_NAME' points to '$EXISTING_URL', not '$REPO_URL'"
  fi
else
  git remote add "$REMOTE_NAME" "$REPO_URL"
fi

git fetch "$REMOTE_NAME" --tags --prune

if [[ -z "$BRANCH" ]]; then
  BRANCH="$(resolve_branch "$REMOTE_NAME")"
fi

git rev-parse --verify --quiet "refs/remotes/${REMOTE_NAME}/${BRANCH}" >/dev/null \
  || fail "branch '$BRANCH' not found on remote '$REMOTE_NAME'"

if [[ "$MODE" == "add" ]]; then
  if [[ -f "$PREFIX" ]]; then
    fail "prefix '$PREFIX' exists as a file"
  fi
  if [[ -d "$PREFIX" && -n "$(find "$PREFIX" -mindepth 1 -print -quit 2>/dev/null || true)" ]]; then
    fail "prefix '$PREFIX' already exists and is not empty; use pull mode for updates"
  fi

  git subtree add \
    --prefix="$PREFIX" \
    "$REMOTE_NAME" "$BRANCH" \
    --message "Import $REPO_URL ($BRANCH) into $PREFIX preserving upstream history"
else
  git cat-file -e "HEAD:$PREFIX" 2>/dev/null || fail "prefix '$PREFIX' does not exist in HEAD"

  git subtree pull \
    --prefix="$PREFIX" \
    "$REMOTE_NAME" "$BRANCH" \
    --message "Update $PREFIX from $REPO_URL ($BRANCH) preserving upstream history"
fi

printf 'import complete: mode=%s repo=%s branch=%s prefix=%s\n' "$MODE" "$REPO_URL" "$BRANCH" "$PREFIX"
