---
description: Search for academic papers using Asta's semantic search across 225M+ papers
argument-hint: <query> [--limit N] [--venue]
---

Search for academic papers using natural language queries via Allen AI's Asta semantic search.

## Usage

```
/asta:paper-search "transformer architectures for vision"
/asta:paper-search "federated learning healthcare" --limit 20
```

## How It Works

Uses the `mcp__asta__snippet_search` tool to search 285M+ passages from 225M+ scientific papers. Returns ranked results with:
- Paper title and authors
- Year and venue
- Relevant snippet showing why it matched
- DOI/ArXiv ID for verification

## Options

- `--limit N`: Number of results (default: 10, max: 100)
- `--venue`: Filter by venue (e.g., "NeurIPS", "Nature")

## Examples

```
/asta:paper-search "attention mechanisms in transformers"
/asta:paper-search "CRISPR gene editing" --limit 5
/asta:paper-search "climate change models" --venue Nature
```
