from __future__ import annotations

from evagent.models import PaperRecord


def to_markdown_summary(paper: PaperRecord, evidence_snippets: list[str] | None = None) -> str:
    snippets = evidence_snippets or []
    highlights = "\n".join(f"- {s}" for s in snippets[:3]) or "- N/A"

    return f"""# Paper Summary: {paper.title}

**Authors**: {", ".join(paper.authors) if paper.authors else "Unknown"}
**Year**: {paper.year or "Unknown"}
**Venue**: {paper.metadata.get("venue", "Unknown")}
**DOI/URL**: {paper.doi or paper.url or "N/A"}

## Overview
This summary follows a structured research-paper analysis workflow.
The paper is captured as evidence candidate for EventVision literature QA.

## Highlights
{highlights}

## Strengths
- Clearly tied to a domain query or retrieval target.
- Captured with source metadata for traceability.

## Weaknesses
- Full methodological scoring requires deeper section-level parsing.
- Reproducibility judgement requires code/data availability checks.

## Detailed Summary
### Introduction
{(paper.abstract or "N/A")[:700]}

### Methods
N/A in baseline parser.

### Results
N/A in baseline parser.

### Discussion
N/A in baseline parser.

## Reproducibility Notes
- Metadata captured: {"yes" if paper.metadata else "partial"}
- Open-access PDF: {"yes" if paper.pdf_url else "unknown"}
"""
