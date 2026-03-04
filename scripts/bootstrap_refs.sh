#!/usr/bin/env bash
set -euo pipefail

mkdir -p .cache/upstream

repos=(
  "https://github.com/future-house/paper-qa.git"
  "https://github.com/assafelovic/gpt-researcher.git"
  "https://github.com/stanford-oval/storm.git"
  "https://github.com/qdrant/qdrant.git"
  "https://github.com/grobidOrg/grobid.git"
  "https://github.com/truera/trulens.git"
)

for repo in "${repos[@]}"; do
  name="$(basename -s .git "$repo")"
  target=".cache/upstream/$name"
  if [[ -d "$target/.git" ]]; then
    echo "skip $name (already exists)"
    continue
  fi
  echo "cloning $repo -> $target"
  git clone --depth 1 "$repo" "$target"
done
