# EVLIT-Agent (EventVision Literature Agent)

EVLIT-Agent is a practical multi-agent literature assistant for event-camera research.

Current core abilities:
- multi-source paper search and ranking (`arXiv`, `OpenAlex`, `Semantic Scholar`, `Crossref`)
- grounded Q&A workflow with a LangGraph-style agent pipeline
- PDF ingest through GROBID
- daily sub-agent push for new space-observation papers (title + main content)

## Current Architecture

Main retrieval-answer flow:
- `Planner -> Retriever -> Evidence -> Critic -> Draft`

Specialized automation:
- `sub_agents/space_observation_digest` for scheduled daily paper digest and desktop notification

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Optional local services:

```bash
docker compose up -d qdrant grobid
```

## Configuration

Environment variables are in `.env.example`.

Common fields:
- `EVAGENT_API_KEY`, `EVAGENT_API_BASE`, `EVAGENT_CHAT_MODEL`, `EVAGENT_EMBED_MODEL`
- `S2_API_KEY`, `OPENALEX_API_KEY`, `CROSSREF_MAILTO`
- `QDRANT_URL`, `GROBID_URL`
- `EVAGENT_RUNS_DIR`, `EVAGENT_CACHE_DIR`, `EVAGENT_LOG_LEVEL`

## CLI Commands

After `pip install -e ".[dev]"`, use `evagent ...`.
If entrypoint is not available, use `PYTHONPATH=src python -m evagent.app ...`.

```bash
# list retrieval profiles
evagent profiles

# search papers
evagent search "event camera star tracking" \
  --profile sps_space_event_startracking \
  --year-from 2021 --min-score 0.55 --limit 5

# ask a grounded question
evagent ask "What datasets are used for event-camera star tracking?" \
  --profile sps_space_event_startracking \
  --year-from 2021 --min-score 0.55 --min-evidence 3 --limit 6

# ingest a local or remote PDF
evagent ingest --pdf "https://arxiv.org/pdf/2505.12588.pdf"

# run digest push once now
evagent space-observation-push --max-items 5 --notify

# run digest scheduler every day at 09:00 (local timezone)
evagent space-observation-push --schedule --at 09:00 --notify

# run with explicit timezone
evagent space-observation-push --schedule --at 09:00 --tz Asia/Shanghai --notify
```

Note:
- `cache-links` command in CLI expects `scripts/cache_links.sh`.
- If that script is removed in your local branch, `cache-links` will not run.

## Daily Digest Output

Space-observation sub-agent outputs:
- `output/sub_agents/space_observation_digest/digest_YYYY-MM-DD.md`
- `output/sub_agents/space_observation_digest/digest_YYYY-MM-DD.json`
- `output/sub_agents/space_observation_digest/latest.md`
- `output/sub_agents/space_observation_digest/state.json`
- run logs in `runs/space_observation_digest_runs.jsonl`

<!-- ## Project Layout

```text
src/evagent/
  app.py
  config.py
  models.py
  agents/
    graph.py
    nodes.py
    state.py
  analysis/
  domain/
  eval/
  index/
  ingest/
  llm/
  observability/
  retrieval/
  sources/
  sub_agents/
    space_observation_digest/
      agent.py
      README.md
```

Other key directories:
- `tests/` unit tests including digest-agent tests
- `scripts/` repo utility scripts (upstream import, diagram/pdf helpers)
- `output/` generated reports/diagrams/pdfs/sub-agent outputs
- `references/` upstream mapping and source URL tracking files

## Development

```bash
ruff check src tests
PYTHONPATH=src pytest -q
``` -->

## Upstream References and Import

Reference tracking files:
- `references/upstream_repos.yaml`
- `references/imported_repos.yaml`
- `references/borrowed_components.md`

Clone reference repos:

```bash
bash scripts/bootstrap_refs.sh
```

Import upstream history via subtree:

```bash
# add
bash scripts/import_upstream_history.sh add \
  --repo-url https://github.com/future-house/paper-qa.git \
  --prefix vendor/paper-qa

# update
bash scripts/import_upstream_history.sh pull \
  --repo-url https://github.com/future-house/paper-qa.git \
  --prefix vendor/paper-qa

# batch add from references/imported_repos.yaml
bash scripts/import_upstreams_from_yaml.sh --mode add
```
