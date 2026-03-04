# EventVision Literature Agent

A practical starter codebase to build an **agentic RAG system** for event-camera / AI-imaging literature.

## Upstream-first Strategy

The project tracks upstream references in `references/upstream_repos.yaml` (use/reference only).
Actual code-import targets are tracked separately in `references/imported_repos.yaml`.
Implementation mapping is documented in `references/borrowed_components.md`.

Current primary references:
- PaperQA2: scientific grounded-answer baseline
- GPT-Researcher: sub-question decomposition workflow
- STORM: citation-aware synthesis style
- LangGraph: explicit multi-agent graph orchestration
- Qdrant + GROBID: vector index and scientific PDF parsing foundation

## What Is Implemented (Baseline)

- CLI entrypoints:
  - `evagent search "<query>"`
  - `evagent ask "<query>"`
  - `evagent ingest --pdf <path-or-url>`
  - `evagent profiles`
- Multi-source academic search connectors:
  - arXiv, Semantic Scholar, OpenAlex, Crossref
- Dedup strategy:
  - `DOI > arXiv_id > normalized(title + first_author + year)`
- Multi-agent graph (LangGraph):
  - `Planner -> Retriever -> Evidence -> Critic -> Draft`
- Provenance cache for Markdown links with retrieval timestamp
- Starter eval metrics (`recall_at_k`, `mrr_at_k`, `ndcg_at_k`)

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Optional services:

```bash
docker compose up -d qdrant grobid
```

Run commands:

```bash
evagent profiles
evagent search "event camera star tracking" --profile sps_space_event_startracking --year-from 2021 --min-score 0.55 --limit 5
evagent ask "What datasets are used for event-camera star tracking?" --profile sps_space_event_startracking --year-from 2021 --min-score 0.55 --min-evidence 3 --limit 6
evagent ingest --pdf "https://arxiv.org/pdf/2505.12588.pdf"
```

## Provenance Workflow

Extract URLs and cache retrieval timestamp:

```bash
bash scripts/cache_links.sh "AI agent项目步骤.md"
```

Output:
- `references/source_urls.txt`
- `references/source_urls.jsonl`

## Borrowed-vs-Original Boundary

Borrowed (upstream-inspired):
- search/retrieval APIs, citation-aware synthesis patterns, graph orchestration style

Original (to implement next):
- event-domain query expansion (`event camera`, `DVS`, `DAVIS`, `jitter`, `centroiding`)
- citation-hop retrieval (`referenced_works`, `cited_by`) with diversity constraints
- contextual-bandit retrieval policy selection loop

## Project Layout

```text
src/evagent/
  app.py
  config.py
  agents/
  analysis/
  sources/
  ingest/
  index/
  eval/
  observability/
```

## Reference Bootstrap

To clone selected upstream repositories locally for inspection:

```bash
bash scripts/bootstrap_refs.sh
```

Clones are placed in `.cache/upstream/`.

## Import Upstream Repos With Original Commit Dates

If you want imported code to keep upstream commit history and timestamps on GitHub, use subtree import (not copy/paste, squash, or cherry-pick).

Single repository import:

```bash
bash scripts/import_upstream_history.sh add \
  --repo-url https://github.com/future-house/paper-qa.git \
  --prefix vendor/paper-qa
```

Update an existing imported subtree:

```bash
bash scripts/import_upstream_history.sh pull \
  --repo-url https://github.com/future-house/paper-qa.git \
  --prefix vendor/paper-qa
```

Batch import from `references/imported_repos.yaml`:

```bash
bash scripts/import_upstreams_from_yaml.sh --mode add
```

Dry-run batch mode:

```bash
bash scripts/import_upstreams_from_yaml.sh --mode add --dry-run
```

Notes:
- Keep your working tree clean before running imports.
- Upstream commits preserve original timestamps; each import/update adds one new local merge commit with current time.
- Keep "use/reference only" repos in `references/upstream_repos.yaml`; only put real code-import repos in `references/imported_repos.yaml`.
