---
name: paper-details
description: Retrieve comprehensive details about a specific academic paper including abstract, citations, references, and related work. Use when you have a paper ID (DOI, ArXiv, etc.) and need full metadata, citation information, or want to explore a paper's connections.
allowed-tools: Bash, Read, Grep, Glob, TodoWrite
---

<objective>
Retrieve comprehensive information about a specific academic paper from Asta's scientific corpus. Given a paper identifier (DOI, ArXiv ID, title, etc.), fetch full metadata including abstract, TLDR, citation counts, and optionally explore citing papers, references, and author's other work.
</objective>

<quick_start>
To get paper details:

```
/asta:paper-details arxiv:1706.03762
```

With optional expansions:
```
/asta:paper-details "10.1038/nature14539" --include citations,references
```
</quick_start>

<success_criteria>
- Successfully resolves paper ID to full metadata
- Returns abstract and TLDR (AI-generated summary)
- Provides citation count and key metrics
- Includes links to full text when available
- Optionally expands to show citations, references, or author's other work
</success_criteria>

<context>
**Supported ID Formats:**

| Format | Example | Notes |
|--------|---------|-------|
| DOI | `10.1145/3394486.3403110` | Most reliable |
| ArXiv | `arxiv:2005.14165` | Include prefix |
| Semantic Scholar | `CorpusId:218470331` | Internal ID |
| PubMed | `PMID:29618526` | Medical literature |
| MAG | `MAG:2952589709` | Microsoft Academic |
| Title | `"Attention Is All You Need"` | Falls back to search |

**Available Fields:**
abstract, authors, citations, citationCount, fieldsOfStudy,
influentialCitationCount, isOpenAccess, journal, publicationDate,
references, tldr, url, venue, year
</context>

<workflow>
**Phase 1: Identify Paper**

1. Parse the input to determine ID type:
   - DOI pattern: `10.xxxx/xxxxx`
   - ArXiv pattern: `arxiv:XXXX.XXXXX` or `XXXX.XXXXX`
   - Semantic Scholar: `CorpusId:XXXXXXX`
   - Title: Quoted string without ID pattern

2. If title provided, use `mcp__asta__snippet_search` to find the paper first

**Phase 2: Retrieve Details**

3. Use `mcp__asta__get_paper` with:
   - `paper_id`: The resolved paper ID
   - `fields`: Request all relevant fields

4. Parse and format the response

**Phase 3: Expand (if requested)**

5. If `--include citations`: Use `mcp__asta__get_paper_citations`
6. If `--include references`: Use `mcp__asta__get_paper_references`
7. If `--include authors`: Use `mcp__asta__get_author_papers` for each author
</workflow>

<output_format>
Structure the output as:

```markdown
# {Paper Title}

## Quick Summary
**TLDR:** {AI-generated summary from Asta}

## Metadata

| Field | Value |
|-------|-------|
| Authors | {Full author list with affiliations} |
| Year | {Year} |
| Venue | {Conference or Journal} |
| Citations | {count} ({influential_count} influential) |
| Open Access | {Yes/No} |
| Fields | {fieldsOfStudy} |

## Abstract
{Full abstract text}

## Links
- **DOI:** [{doi}](https://doi.org/{doi})
- **ArXiv:** [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})
- **PDF:** {pdf_link if available}
- **Semantic Scholar:** [View on S2]({s2_url})

## Key Citations (if requested)
{Top 5 most influential papers that cite this one}

| Paper | Year | Citations |
|-------|------|-----------|
| {Title} | {Year} | {count} |

## Key References (if requested)
{Most cited references from this paper}

## Related Work by Authors (if requested)
{Other notable papers by the same authors}
```
</output_format>

<examples>
<example number="1">
<input>/asta:paper-details arxiv:1706.03762</input>
<output>
# Attention Is All You Need

## Quick Summary
**TLDR:** A new neural network architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely, achieving state-of-the-art results on machine translation.

## Metadata

| Field | Value |
|-------|-------|
| Authors | Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin |
| Year | 2017 |
| Venue | NeurIPS |
| Citations | 95,000+ (12,000+ influential) |
| Open Access | Yes |
| Fields | Computer Science, Machine Learning |

## Abstract
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely...

## Links
- **ArXiv:** [1706.03762](https://arxiv.org/abs/1706.03762)
- **PDF:** [Download](https://arxiv.org/pdf/1706.03762)
- **Semantic Scholar:** [View on S2](https://semanticscholar.org/paper/...)
</output>
</example>

<example number="2">
<input>/asta:paper-details "BERT: Pre-training of Deep Bidirectional Transformers"</input>
<output>
(Searches for the paper by title first, then retrieves details as above)
</output>
</example>
</examples>

<anti_patterns>
- **Don't guess IDs** - If ID format is unclear, ask for clarification
- **Don't fabricate metadata** - Only return data from the API
- **Don't skip the TLDR** - Include the AI-generated summary when available
- **Don't return partial data** - If a field is unavailable, note it explicitly
</anti_patterns>

<common_papers>
For testing or quick reference:
- Attention paper: `arxiv:1706.03762`
- BERT: `arxiv:1810.04805`
- GPT-3: `arxiv:2005.14165`
- AlphaFold: `DOI:10.1038/s41586-021-03819-2`
- ResNet: `arxiv:1512.03385`
</common_papers>
