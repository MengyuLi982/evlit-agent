# Skills Setup for This Codebase

Use these skills when processing links found in Markdown files (especially `*.md` under this repo).

## Installed skills
- `doc` (`~/.codex/skills/doc`)
- `playwright` (`~/.codex/skills/playwright`)
- `pdf` (`~/.codex/skills/pdf`)
- `arxiv-search` (`~/.codex/skills/arxiv-search`)
- `analyzing-research-papers` (`~/.codex/skills/analyzing-research-papers`)

## Link-to-skill routing
- For documentation links (`docs.*`, API docs, framework docs):
  - Use `doc` first.
  - Use `playwright` if the page needs dynamic rendering or interactive navigation.
- For GitHub repository links:
  - Use `doc` to gather README/docs quickly.
  - Use `playwright` only when static fetch is not enough.
- For arXiv links (`arxiv.org`):
  - Use `arxiv-search` for metadata retrieval.
  - Use `analyzing-research-papers` for structured paper analysis/summaries.
- For direct PDF links (`*.pdf`):
  - Use `pdf` for parsing/render checks.
  - Use `analyzing-research-papers` when the PDF is a research paper.

## Operating rules
- Extract links from Markdown with:
  - `rg -o "https?://[^)\\] >\\\"]+" <file>.md | sort -u`
- Cache or persist normalized results before downstream processing.
- Keep provenance: for each extracted claim, store source URL and retrieval timestamp.
