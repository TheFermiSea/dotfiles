# Asta Plugin for Claude Code

Scientific research tools powered by [Allen AI's Asta framework](https://allenai.org/asta). Search 225M+ academic papers, synthesize literature, and verify citations directly from Claude Code.

## Features

| Skill | Description |
|-------|-------------|
| `/asta:paper-search` | Semantic search across 285M+ passages |
| `/asta:literature-review` | Synthesize research into themes |
| `/asta:cite-sources` | Find citations with confidence scoring |
| `/asta:paper-details` | Get full paper info by DOI/ArXiv |

**Subagents:**
- `research-assistant` - Multi-turn deep research exploration
- `citation-verifier` - Fact-check claims against literature

## Setup

### Step 1: Get an Asta API Key

1. Visit the [Asta API Key Request Form](https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm)
2. Fill out the form with your information
3. You'll receive an API key via email (typically 24-48 hours)

### Step 2: Set Environment Variable

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export ASTA_API_KEY="your-api-key-here"
```

Then reload: `source ~/.zshrc` (or restart terminal)

### Step 3: Add Asta MCP Server

Add the Asta MCP server to Claude Code using the CLI:

```bash
claude mcp add --transport http --scope user asta \
  --header "x-api-key: \${ASTA_API_KEY}" \
  https://asta-tools.allen.ai/mcp/v1
```

**Alternative: Manual JSON configuration**

Add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "asta": {
      "type": "http",
      "url": "https://asta-tools.allen.ai/mcp/v1",
      "headers": {
        "x-api-key": "${ASTA_API_KEY}"
      }
    }
  }
}
```

### Step 4: Verify Installation

Restart Claude Code, then test:

```
/asta:paper-search "attention mechanisms"
```

## Usage Examples

### Search for Papers

```
/asta:paper-search "transformer architectures for vision" --limit 10
```

### Generate Literature Review

```
/asta:literature-review "federated learning in healthcare" --depth standard
```

Depth options: `quick` (5-10 papers), `standard` (15-25), `comprehensive` (30+)

### Find Citations for a Claim

```
/asta:cite-sources "Large language models exhibit emergent capabilities at scale"
```

### Get Paper Details

```
/asta:paper-details arxiv:1706.03762
/asta:paper-details "10.1038/nature14539" --include citations
```

Supported ID formats: DOI, ArXiv, CorpusId, PMID, MAG, or title search.

## Data Coverage

The Asta corpus includes:

| Metric | Value |
|--------|-------|
| Papers | 225M+ |
| Authors | 80M+ |
| Citation edges | 550M+ |
| Full-text papers | 12M+ |
| Searchable passages | 285M+ |

**Sources:** Semantic Scholar, arXiv, PubMed, ACL, NeurIPS, ICML, and major journals.

## MCP Tools Available

Once configured, these tools are available:

| Tool | Description |
|------|-------------|
| `get_paper` | Get paper details by ID |
| `snippet_search` | Semantic search across passages |
| `paper_search` | Search by metadata |
| `get_paper_citations` | Get citing papers |
| `get_paper_references` | Get referenced papers |
| `get_author_papers` | Get papers by author |

## Troubleshooting

### "MCP server not found"

1. Verify the MCP server is configured: `claude mcp list`
2. Check API key is set: `echo $ASTA_API_KEY`
3. Restart Claude Code after configuration changes

### "API key not found"

1. Ensure `ASTA_API_KEY` is exported in your shell profile
2. Restart terminal or run `source ~/.zshrc`
3. Verify: `echo $ASTA_API_KEY`

### "Rate limit exceeded"

- Wait a few minutes before retrying
- API key provides higher limits than anonymous access
- Contact Allen AI for enterprise access

### "No results found"

- Try broader search terms
- Check if topic is covered in scientific literature
- Very recent papers may not be indexed yet

## Resources

- [Asta Documentation](https://allenai.org/asta)
- [Asta MCP API Reference](https://allenai.org/asta/resources/mcp)
- [AstaBench GitHub](https://github.com/allenai/asta-bench)
- [API Key Request](https://share.hsforms.com/1L4hUh20oT3mu8iXJQMV77w3ioxm)

## License

This plugin is provided for research purposes. The Asta API is provided by Allen Institute for AI under their terms of service.
