#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="${1:-AI agent项目步骤.md}"
OUT_TXT="references/source_urls.txt"
OUT_JSONL="references/source_urls.jsonl"

mkdir -p references

rg -o "https?://[^)\\] >\"]+" "$INPUT_FILE" | sort -u > "$OUT_TXT"

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
awk -v ts="$TS" '{printf("{\"url\":\"%s\",\"retrieved_at\":\"%s\"}\n", $0, ts)}' "$OUT_TXT" > "$OUT_JSONL"

echo "Wrote $OUT_TXT and $OUT_JSONL"
