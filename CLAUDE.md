# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EventVision Literature Agent: A multi-agent RAG system for event-camera and AI-imaging literature research. Uses LangGraph for orchestration, LiteLLM for LLM calls, Qdrant for vector storage, and GROBID for PDF parsing.

## Development Commands

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Configure API keys and service URLs
```

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_nodes.py  # Run specific test file
pytest -v                 # Verbose output
pytest --cov              # With coverage
```

### Linting
```bash
ruff check .              # Check for issues
ruff check --fix .        # Auto-fix issues
ruff format .             # Format code
```

### CLI Commands
```bash
evagent profiles          # List retrieval profiles
evagent search "<query>" --profile <name> --year-from 2021 --min-score 0.55 --limit 5
evagent ask "<query>" --profile <name> --year-from 2021 --min-score 0.55 --min-evidence 3 --limit 6
evagent ingest --pdf <path-or-url>
```

### Optional Services
```bash
docker compose up -d qdrant grobid  # Start Qdrant (port 6333) and GROBID (port 8070)
```

## Architecture

### Multi-Agent Graph Flow
The system uses LangGraph to orchestrate a multi-agent workflow:
1. **Planner** (`plan_subquestions`): Decomposes user query into sub-questions
2. **Retriever** (`retrieve_candidates`): Fetches papers from multiple academic sources
3. **Evidence** (`extract_evidence`): Extracts relevant snippets from candidates
4. **Critic** (`critic_and_fix`): Evaluates evidence quality, may trigger re-retrieval
5. **Draft** (`draft_answer`): Generates final grounded answer with citations

Graph definition: `src/evagent/agents/graph.py`
Node implementations: `src/evagent/agents/nodes.py`
State schema: `src/evagent/agents/state.py`

### Multi-Source Retrieval
Academic search connectors in `src/evagent/sources/`:
- `arxiv.py`: arXiv API
- `semanticscholar.py`: Semantic Scholar API (requires S2_API_KEY)
- `openalex.py`: OpenAlex API (optional OPENALEX_API_KEY)
- `crossref.py`: Crossref API (requires CROSSREF_MAILTO)

Deduplication strategy: `DOI > arXiv_id > normalized(title + first_author + year)`

### Profile-Based Retrieval
Profiles define domain-specific query expansion and filtering rules.
- Profiles: `src/evagent/domain/profiles.py`
- Default profile: `sps_space_event_startracking`
- Profiles include: query expansion terms, year filters, score thresholds, evidence requirements

### Configuration
Settings loaded from `.env` file via `src/evagent/config.py`:
- `EVAGENT_CHAT_MODEL`: LLM model (default: qwen3-max)
- `EVAGENT_EMBED_MODEL`: Embedding model (default: text-embedding-v3)
- `EVAGENT_API_KEY` / `DASHSCOPE_API_KEY`: LLM API key
- `EVAGENT_API_BASE` / `DASHSCOPE_API_BASE`: LLM API base URL
- `S2_API_KEY`, `OPENALEX_API_KEY`, `CROSSREF_MAILTO`: Academic API credentials
- `QDRANT_URL`: Qdrant vector DB URL (default: http://localhost:6333)
- `GROBID_URL`: GROBID PDF parser URL (default: http://localhost:8070)

### Key Modules
- `src/evagent/app.py`: CLI entrypoint (Typer)
- `src/evagent/llm/`: LLM client wrapper (LiteLLM)
- `src/evagent/ingest/`: PDF ingestion pipeline (GROBID)
- `src/evagent/index/`: Vector store operations (Qdrant)
- `src/evagent/eval/`: Evaluation metrics (recall@k, MRR, NDCG)
- `src/evagent/observability/`: Logging and tracing (structlog)

## Development Philosophy

**Borrow-first, then extend**: This project references upstream patterns from PaperQA2, GPT-Researcher, STORM, and LangGraph. Upstream repos are cloned to `.cache/upstream/` for reference (not imported as dependencies).

Original contributions focus on:
- Event-domain query expansion (event camera, DVS, DAVIS, jitter, centroiding)
- Citation-hop retrieval with diversity constraints
- Contextual-bandit retrieval policy selection

## Testing Notes

- Tests use pytest with minimal fixtures
- Mock external API calls (academic sources, LLM)
- Test files mirror source structure: `tests/test_<module>.py`
- Profile-based tests: `tests/test_profile_ranking.py`
- CLI tests: `tests/test_cli_profile_options.py`

## Run Artifacts

Query runs are logged to JSONL files in `runs/` directory:
- `runs/ask_runs.jsonl`: Multi-agent workflow runs with evidence and filter stats
- Each run includes: query, profile, answer, evidence, candidates, filter statistics
