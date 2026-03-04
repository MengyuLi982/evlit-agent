#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${REPO_ROOT}/.env"
START_DATE="$(date -u +%Y-%m-01)"
END_DATE="$(date -u +%Y-%m-%d)"
USAGE_UNIT="cents"

usage() {
  cat <<'EOF'
Usage: scripts/check_quota.sh [options]

Options:
  --env-file PATH           Path to env file (default: <repo>/.env)
  --start-date YYYY-MM-DD   Usage start date (default: first day of current UTC month)
  --end-date YYYY-MM-DD     Usage end date (default: today UTC)
  --usage-unit UNIT         Usage unit for usage endpoint: cents|usd (default: cents)
  -h, --help                Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      ENV_FILE="$2"
      shift 2
      ;;
    --start-date)
      START_DATE="$2"
      shift 2
      ;;
    --end-date)
      END_DATE="$2"
      shift 2
      ;;
    --usage-unit)
      USAGE_UNIT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if ! [[ "$START_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "error: invalid --start-date format (expected YYYY-MM-DD)" >&2
  exit 1
fi
if ! [[ "$END_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "error: invalid --end-date format (expected YYYY-MM-DD)" >&2
  exit 1
fi
if [[ "$USAGE_UNIT" != "cents" && "$USAGE_UNIT" != "usd" ]]; then
  echo "error: --usage-unit must be cents or usd" >&2
  exit 1
fi

API_KEY="${EVAGENT_API_KEY:-${DASHSCOPE_API_KEY:-}}"
API_BASE="${EVAGENT_API_BASE:-${DASHSCOPE_API_BASE:-}}"

if [[ -z "${API_KEY:-}" ]]; then
  echo "error: missing API key (EVAGENT_API_KEY or DASHSCOPE_API_KEY)." >&2
  exit 1
fi
if [[ -z "${API_BASE:-}" ]]; then
  echo "error: missing API base (EVAGENT_API_BASE or DASHSCOPE_API_BASE)." >&2
  exit 1
fi

API_BASE="${API_BASE%/}"

LAST_CODE=""
LAST_BODY=""

api_get() {
  local path="$1"
  local tmp
  tmp="$(mktemp)"
  LAST_CODE="$(curl -sS --max-time 20 -o "$tmp" -w "%{http_code}" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    "${API_BASE}${path}" || true)"
  LAST_BODY="$(cat "$tmp")"
  rm -f "$tmp"
}

json_ok() {
  local data="$1"
  printf '%s' "$data" | python -c 'import json,sys; json.load(sys.stdin)' >/dev/null 2>&1
}

fetch_json_first() {
  local path
  for path in "$@"; do
    api_get "$path"
    if [[ "$LAST_CODE" =~ ^2 ]] && json_ok "$LAST_BODY"; then
      echo "$LAST_BODY"
      return 0
    fi
  done
  return 1
}

CREDIT_JSON=""
if CREDIT_JSON="$(fetch_json_first \
  "/dashboard/billing/credit_grants" \
  "/v1/dashboard/billing/credit_grants")"; then
  :
fi

if ! SUB_JSON="$(fetch_json_first \
  "/dashboard/billing/subscription" \
  "/v1/dashboard/billing/subscription")"; then
  echo "error: failed to fetch subscription data from ${API_BASE}." >&2
  echo "last_status=${LAST_CODE}" >&2
  echo "last_body=$(printf '%s' "$LAST_BODY" | head -c 200)" >&2
  exit 1
fi

USAGE_QUERY="?start_date=${START_DATE}&end_date=${END_DATE}"
if ! USAGE_JSON="$(fetch_json_first \
  "/dashboard/billing/usage${USAGE_QUERY}" \
  "/v1/dashboard/billing/usage${USAGE_QUERY}")"; then
  echo "error: failed to fetch usage data from ${API_BASE}." >&2
  echo "last_status=${LAST_CODE}" >&2
  echo "last_body=$(printf '%s' "$LAST_BODY" | head -c 200)" >&2
  exit 1
fi

CREDIT_JSON="$CREDIT_JSON" \
SUB_JSON="$SUB_JSON" \
USAGE_JSON="$USAGE_JSON" \
API_BASE="$API_BASE" \
START_DATE="$START_DATE" \
END_DATE="$END_DATE" \
USAGE_UNIT="$USAGE_UNIT" \
python - <<'PY'
import json
import os


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(value):
    text = f"{value:.6f}"
    return text.rstrip("0").rstrip(".")


credit_raw = os.environ.get("CREDIT_JSON", "").strip()
sub = json.loads(os.environ["SUB_JSON"])
usage = json.loads(os.environ["USAGE_JSON"])
unit = os.environ["USAGE_UNIT"]

usage_raw = to_float(usage.get("total_usage")) or 0.0
used_usd = usage_raw / 100.0 if unit == "cents" else usage_raw

limit = to_float(sub.get("hard_limit_usd"))
if limit is None:
    limit = to_float(sub.get("soft_limit_usd"))
if limit is None:
    limit = to_float(sub.get("system_hard_limit_usd"))
if limit is None:
    limit = 0.0

remaining_est = limit - used_usd

remaining_exact = None
if credit_raw:
    try:
        credit = json.loads(credit_raw)
    except json.JSONDecodeError:
        credit = None
    if isinstance(credit, dict):
        total_available = to_float(credit.get("total_available"))
        total_granted = to_float(credit.get("total_granted"))
        total_used = to_float(credit.get("total_used"))
        if total_available is not None:
            remaining_exact = total_available
        elif total_granted is not None and total_used is not None:
            remaining_exact = total_granted - total_used

print("API Quota")
print(f"base_url: {os.environ['API_BASE']}")
print(f"period: {os.environ['START_DATE']} -> {os.environ['END_DATE']}")
print(f"usage_unit: {unit}")
print(f"limit_usd: {fmt(limit)}")
print(f"used_usd: {fmt(used_usd)}")
if remaining_exact is not None:
    print(f"remaining_usd: {fmt(remaining_exact)}")
    print("remaining_source: credit_grants")
else:
    print(f"remaining_usd: {fmt(remaining_est)}")
    print("remaining_source: subscription - usage (estimated)")
PY
