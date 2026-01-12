---
name: paper-search
description: Search for academic papers using natural language queries via Asta's semantic search across 225M+ papers. Use when finding research papers, exploring literature, or discovering relevant academic work on any scientific topic.
allowed-tools: Bash, Read, Grep, Glob, TodoWrite
---

<objective>
Search for academic papers matching natural language queries using the Asta MCP server's semantic search capabilities. This skill leverages Allen AI's scientific corpus containing 225M+ papers and 285M+ searchable passages to find relevant research.
</objective>

<quick_start>
To search for papers:

```
/asta:paper-search "transformer architectures for computer vision"
```

The skill will use the `mcp__asta__snippet_search` tool to find relevant passages, then format results with titles, authors, venues, and relevance snippets.
</quick_start>

<success_criteria>
- Returns ranked list of relevant papers with metadata
- Each result includes: title, authors, year, venue, and relevance snippet
- Results are ordered by semantic relevance to the query
- Paper IDs (DOI/ArXiv) are included for verification
</success_criteria>

<context>
**Prerequisites:**
- Asta MCP server must be configured (see plugin README)
- API key required for higher rate limits

**Data Coverage:**
- 225M+ papers from all scientific disciplines
- 12M+ full-text papers (285M+ passages)
- Sources: Semantic Scholar, arXiv, PubMed, major conferences
</context>

<workflow>
**Step 1: Parse Query**
Extract the user's search intent and any filters:
- Main search terms
- Venue filters (e.g., "ACL", "NeurIPS")
- Date range (e.g., "2023-2024")
- Result limit (default: 10)

**Step 2: Execute Search**
Use `mcp__asta__snippet_search` with parameters:
- `query`: The search query
- `limit`: Number of results (default 10, max 100)
- `venues`: Comma-separated venue filter (optional)

**Step 3: Format Results**
For each result, extract and display:
- Paper title (bold)
- Authors (first 3 + "et al." if more)
- Year and venue
- Relevance snippet (the matching passage)
- Paper link and citation count

**Step 4: Offer Follow-up**
If user wants more details on a specific paper, use `mcp__asta__get_paper` to fetch full metadata.
</workflow>

<output_format>
Present results in this structure:

```markdown
## Paper Search Results for: "{query}"

**Found {n} relevant papers:**

1. **{Title}** ({Year})
   *{Author1}, {Author2}, et al.* — {Venue}
   > "{Relevant snippet from the paper...}"
   DOI: {doi} | Citations: {count}

2. **{Title}** ({Year})
   ...
```
</output_format>

<examples>
<example number="1">
<input>/asta:paper-search "attention mechanisms in large language models" --limit 5</input>
<output>
## Paper Search Results for: "attention mechanisms in large language models"

**Found 5 relevant papers:**

1. **Attention Is All You Need** (2017)
   *Vaswani, Ashish et al.* — NeurIPS
   > "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms..."
   arXiv:1706.03762 | Citations: 95,000+

2. **BERT: Pre-training of Deep Bidirectional Transformers** (2019)
   *Devlin, Jacob et al.* — NAACL
   > "BERT uses a multi-head self-attention mechanism that allows the model to jointly attend to information..."
   arXiv:1810.04805 | Citations: 78,000+
</output>
</example>
</examples>

<anti_patterns>
- **Don't guess paper details** - Always use MCP tools to retrieve actual data
- **Don't return too many results** - Default to 10, respect user limits
- **Don't omit paper IDs** - Always include DOI/ArXiv for verification
- **Don't fabricate citations** - Only report actual citation counts from the API
</anti_patterns>
