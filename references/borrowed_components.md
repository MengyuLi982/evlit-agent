# Borrowed Components Map

This file records which upstream repositories were used as implementation references,
and how they map to this repo's baseline modules.

## Retrieval + Grounded Answers

- Upstream: `future-house/paper-qa`
- Local clone: `.cache/upstream/paper-qa`
- Reference points:
  - scientific RAG with grounded citations
  - metadata-aware retrieval and rerank ideas
- Applied in this repo:
  - `src/evagent/sources/` multi-source connectors
  - `src/evagent/agents/nodes.py` evidence-first extraction

## Planner/Executor Research Flow

- Upstream: `assafelovic/gpt-researcher`
- Local clone: `.cache/upstream/gpt-researcher`
- Reference points:
  - planner + execution split
  - sub-question decomposition and report-style assembly
- Applied in this repo:
  - `src/evagent/agents/nodes.py` (`plan_subquestions`, retrieval loop)
  - `src/evagent/app.py` (`ask` command and run artifact persistence)

## Citation-aware Synthesis

- Upstream: `stanford-oval/storm`
- Local clone: `.cache/upstream/storm`
- Reference points:
  - staged synthesis with citations
  - perspective-driven question expansion
- Applied in this repo:
  - `src/evagent/agents/graph.py` staged graph (`plan -> retrieve -> evidence -> critic -> draft`)
  - `src/evagent/analysis/paper_summary.py` structured synthesis template

## Index/Infra Baseline

- Upstream: `qdrant/qdrant`
- Local clone: `.cache/upstream/qdrant`
- Applied in this repo:
  - `docker-compose.yml` qdrant service
  - reserved integration points in `src/evagent/index/`

## PDF Parsing Baseline

- Upstream: `grobidOrg/grobid`
- Local clone: `.cache/upstream/grobid`
- Applied in this repo:
  - `docker-compose.yml` grobid service
  - `src/evagent/ingest/grobid.py`, `src/evagent/ingest/pipeline.py`

## Evaluation/Trustworthiness Direction

- Upstream: `truera/trulens`
- Local clone: `.cache/upstream/trulens`
- Applied in this repo:
  - `src/evagent/eval/metrics.py` baseline retrieval metrics
  - placeholder for future RAG/agent evaluation runners

## Retrieval Timestamp

- Upstream clone timestamp (UTC): `2026-03-03T15:26:00Z` (approx.)
- Markdown source URL cache: see `references/source_urls.jsonl`
