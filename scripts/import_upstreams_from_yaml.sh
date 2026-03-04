#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/import_upstreams_from_yaml.sh [--manifest <path>] [--prefix-root <dir>] [--mode add|pull] [--dry-run]

Defaults:
  --manifest references/imported_repos.yaml
  --prefix-root vendor
  --mode add

Behavior:
  - Reads import targets from the YAML manifest in file order.
  - Per repo supports:
      url:    required
      prefix: optional (default <prefix-root>/<repo_name>)
      branch: optional (default remote HEAD)
  - Imports each repo using scripts/import_upstream_history.sh.
USAGE
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

MANIFEST="references/imported_repos.yaml"
PREFIX_ROOT="vendor"
MODE="add"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest)
      [[ $# -ge 2 ]] || fail "--manifest requires a value"
      MANIFEST="$2"
      shift 2
      ;;
    --prefix-root)
      [[ $# -ge 2 ]] || fail "--prefix-root requires a value"
      PREFIX_ROOT="$2"
      shift 2
      ;;
    --mode)
      [[ $# -ge 2 ]] || fail "--mode requires a value"
      MODE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
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

[[ "$MODE" == "add" || "$MODE" == "pull" ]] || fail "--mode must be add or pull"
[[ -f "$MANIFEST" ]] || fail "manifest not found: $MANIFEST"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPORT_SCRIPT="$SCRIPT_DIR/import_upstream_history.sh"
[[ -x "$IMPORT_SCRIPT" ]] || fail "import script is missing or not executable: $IMPORT_SCRIPT"

mapfile -t URLS < <(
  awk '
    function trim(s) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", s)
      gsub(/["\047]/, "", s)
      return s
    }
    function flush() {
      if (url != "") {
        print url "\t" prefix "\t" branch
      }
      url = ""
      prefix = ""
      branch = ""
    }
    /^[[:space:]]*-[[:space:]]*name:[[:space:]]*/ {
      flush()
      next
    }
    /^[[:space:]]*url:[[:space:]]*https?:\/\// {
      line = $0
      sub(/^[^:]*:[[:space:]]*/, "", line)
      url = trim(line)
      next
    }
    /^[[:space:]]*prefix:[[:space:]]*/ {
      line = $0
      sub(/^[^:]*:[[:space:]]*/, "", line)
      prefix = trim(line)
      next
    }
    /^[[:space:]]*branch:[[:space:]]*/ {
      line = $0
      sub(/^[^:]*:[[:space:]]*/, "", line)
      branch = trim(line)
      next
    }
    END { flush() }
  ' "$MANIFEST"
)

[[ ${#URLS[@]} -gt 0 ]] || fail "no import targets found in $MANIFEST"

for row in "${URLS[@]}"; do
  IFS=$'\t' read -r url prefix branch <<<"$row"
  repo_name="$(basename "${url%.git}")"
  if [[ -z "$prefix" ]]; then
    prefix="${PREFIX_ROOT}/${repo_name}"
  fi

  cmd=("$IMPORT_SCRIPT" "$MODE" --repo-url "$url" --prefix "$prefix")
  if [[ -n "$branch" ]]; then
    cmd+=(--branch "$branch")
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run]'
    printf ' %q' "${cmd[@]}"
    printf '\n'
    continue
  fi

  printf 'importing %s -> %s (%s)\n' "$url" "$prefix" "$MODE"
  "${cmd[@]}"
done
