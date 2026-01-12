---
description: Get detailed information about a specific academic paper by ID
argument-hint: <paper-id> [--include citations|references]
---

Retrieve comprehensive details about a specific academic paper including abstract, citations, references, and metadata.

## Usage

```
/asta:paper-details arxiv:1706.03762
/asta:paper-details "10.1038/nature14539"
/asta:paper-details "Attention Is All You Need"
```

## Supported ID Formats

- **ArXiv**: `arxiv:1706.03762` or `ARXIV:1706.03762`
- **DOI**: `DOI:10.1038/nature14539` or just the DOI string
- **Semantic Scholar**: `CorpusId:215416146`
- **PubMed**: `PMID:19872477`
- **Title search**: Just provide the paper title in quotes

## Options

- `--include citations`: Also fetch papers that cite this one
- `--include references`: Also fetch papers this one references

## What You Get

- Full title and abstract
- Complete author list with affiliations
- Publication date, venue, and journal
- Citation count
- TLDR summary (when available)
- Fields of study
- Open access status and links

## Examples

```
/asta:paper-details arxiv:2005.14165 --include citations
/asta:paper-details "BERT: Pre-training of Deep Bidirectional Transformers"
```
