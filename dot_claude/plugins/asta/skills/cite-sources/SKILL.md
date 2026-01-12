---
name: cite-sources
description: Find academic citations to support or verify claims by searching scientific literature. Use when fact-checking statements, finding authoritative sources for claims, or verifying research assertions with confidence scoring.
allowed-tools: Bash, Read, Grep, Glob, TodoWrite
---

<objective>
Find authoritative academic sources to support, refute, or provide context for specific claims. This skill searches Asta's scientific corpus to locate relevant passages and assesses the strength of evidence with confidence scoring.
</objective>

<quick_start>
To find citations for a claim:

```
/asta:cite-sources "Large language models can perform in-context learning without gradient updates"
```

The skill will search for supporting evidence, assess source quality, and return citations with confidence levels.
</quick_start>

<success_criteria>
- Finds relevant papers that address the claim
- Provides direct quotes supporting or refuting the claim
- Assesses confidence based on source quality and evidence strength
- Includes formatted citations ready for use
- Notes any contradicting evidence or caveats
</success_criteria>

<context>
**Confidence Levels:**

| Level | Criteria |
|-------|----------|
| HIGH | 3+ high-quality sources with direct support, no contradictions |
| MEDIUM | 1-2 quality sources or indirect support |
| LOW | Only tangential support or some contradictions |
| UNSUPPORTED | No reliable sources found |
| CONTRADICTED | Evidence primarily contradicts the claim |

**Quality Signals:**
- Citation count (higher = more vetted)
- Venue reputation (top conferences/journals)
- Recency (for fast-moving fields)
- Peer review status (vs. preprints)
</context>

<workflow>
**Phase 1: Search for Evidence**

1. Parse the claim to identify:
   - Core assertion being made
   - Key concepts and entities
   - Any implicit qualifiers

2. Use `mcp__asta__snippet_search` to find relevant passages
3. Search for both supporting AND contradicting evidence

**Phase 2: Verify Sources**

4. Use `mcp__asta__get_paper` to retrieve full details for promising papers
5. Check citation counts as quality signal
6. Note publication venue reputation
7. Check publication date for recency

**Phase 3: Assess Confidence**

8. Rate overall confidence based on:
   - Number of supporting sources
   - Quality of sources (citations, venue)
   - Directness of evidence
   - Presence of contradicting evidence

**Phase 4: Format Output**

9. Lead with the verdict
10. Provide supporting quotes with full citations
11. Note contradicting evidence if present
12. Include formatted citations for use
</workflow>

<output_format>
Structure the response as:

```markdown
## Citation Analysis: "{claim}"

### Confidence: {HIGH/MEDIUM/LOW/UNSUPPORTED/CONTRADICTED}

### Evidence Summary
{Brief summary of what the literature says about this claim}

### Supporting Evidence

**Strong Support:**
1. **{Paper Title}** ({Year}, {Venue})
   *{Authors}* — Citations: {count}
   > "{Direct quote supporting the claim}"
   DOI: {doi}

**Moderate Support:**
...

### Contradicting Evidence
{Papers that contradict or qualify the claim, if any}

### Caveats
{Important nuances, conditions, or limitations}

### Recommended Citations

**APA Format:**
{Author} ({Year}). {Title}. {Venue}. {DOI}

**BibTeX:**
@article{key,
  title={...},
  author={...},
  ...
}
```
</output_format>

<examples>
<example number="1">
<input>/asta:cite-sources "Transformers scale better than RNNs for language modeling"</input>
<output>
## Citation Analysis: "Transformers scale better than RNNs for language modeling"

### Confidence: HIGH

### Evidence Summary
Multiple high-quality papers demonstrate that Transformer architectures exhibit superior scaling properties compared to RNNs, particularly for language modeling tasks. The evidence is consistent across different scales and datasets.

### Supporting Evidence

**Strong Support:**
1. **Attention Is All You Need** (2017, NeurIPS)
   *Vaswani, Ashish et al.* — Citations: 95,000+
   > "The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours"
   arXiv:1706.03762

2. **Scaling Laws for Neural Language Models** (2020, arXiv)
   *Kaplan, Jared et al.* — Citations: 3,500+
   > "We find that the loss scales as a power-law with model size, dataset size, and compute... Transformers show consistent scaling"
   arXiv:2001.08361

### Contradicting Evidence
None found. However, some work notes RNNs may be more efficient for certain streaming applications.

### Caveats
- Scaling advantages are most pronounced for large models
- RNNs may still be preferred for resource-constrained settings

### Recommended Citations

**APA Format:**
Vaswani, A., et al. (2017). Attention Is All You Need. NeurIPS. https://arxiv.org/abs/1706.03762
</output>
</example>
</examples>

<anti_patterns>
- **Don't confirm without evidence** - If no sources found, say so
- **Don't ignore contradictions** - Report contradicting evidence honestly
- **Don't overstate confidence** - Be conservative in confidence ratings
- **Don't fabricate quotes** - Only use actual passages from the API
- **Don't skip source verification** - Always check paper quality signals
</anti_patterns>

<red_flags>
Flag sources that may be unreliable:
- Predatory journals (check venue reputation)
- Retracted papers
- Pre-prints without peer review (note this clearly)
- Claims that extend beyond the actual evidence
- Very low citation counts for older papers
</red_flags>
