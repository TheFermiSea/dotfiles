---
name: literature-review
description: Generate structured literature reviews on research topics by synthesizing findings from multiple papers. Use when conducting research surveys, identifying themes and gaps, or preparing academic writing on any scientific topic.
allowed-tools: Bash, Read, Grep, Glob, TodoWrite
---

<objective>
Generate comprehensive literature reviews by searching Asta's scientific corpus, synthesizing findings across multiple papers, identifying key themes, and highlighting research gaps. This skill helps researchers understand the landscape of a field efficiently.
</objective>

<quick_start>
To generate a literature review:

```
/asta:literature-review "federated learning for healthcare applications"
```

Optional depth levels:
- `--depth quick` (5-10 papers, fast overview)
- `--depth standard` (15-25 papers, balanced)
- `--depth comprehensive` (30+ papers, thorough)
</quick_start>

<success_criteria>
- Identifies and synthesizes key papers on the topic
- Groups findings into coherent themes
- Notes methodological approaches and trends
- Identifies gaps and future research directions
- Provides proper citations for all claims
</success_criteria>

<context>
**When to use:**
- Starting research in a new area
- Writing related work sections
- Identifying research opportunities
- Understanding field evolution

**Depth Guidelines:**

| Depth | Papers | Use Case |
|-------|--------|----------|
| quick | 5-10 | Initial exploration |
| standard | 15-25 | Research planning |
| comprehensive | 30+ | Thesis/publication prep |
</context>

<workflow>
**Phase 1: Discovery**

1. Use `mcp__asta__snippet_search` with the main topic to find relevant passages
2. Identify key papers from the results
3. Use `mcp__asta__get_paper` on top papers to get abstracts and TLDRs

**Phase 2: Citation Expansion**

4. For seminal papers (high citation count), use `mcp__asta__get_paper_citations` to find follow-on work
5. Use `mcp__asta__get_paper_references` on key papers to identify foundational work
6. Track the citation network to understand field structure

**Phase 3: Synthesis**

7. Group papers into thematic clusters based on:
   - Methodological approach
   - Application domain
   - Theoretical contribution
8. Identify common findings and consensus
9. Note contradictions or ongoing debates
10. Identify gaps where research is sparse

**Phase 4: Reporting**

11. Structure findings into clear sections
12. Provide citations for all claims
13. Highlight most influential papers
14. Suggest future research directions
</workflow>

<output_format>
Structure the review as:

```markdown
# Literature Review: {Topic}

## Overview
{Brief introduction to the field and scope of this review - 1-2 paragraphs}

## Key Themes

### {Theme 1 Name}
{Summary of papers and findings related to this theme}
- {Paper1} ({Year}): {Key finding}
- {Paper2} ({Year}): {Key finding}

### {Theme 2 Name}
{Summary}

## Methodological Approaches
{Common methods, datasets, evaluation metrics across the field}

## Key Findings
{Synthesized findings noting consensus and disagreements}

## Research Gaps
{Identified gaps and opportunities for future work}

## Seminal Papers
{List of most influential papers to read first, with brief justification}

## References
{Formatted citations for all papers mentioned}
```
</output_format>

<examples>
<example number="1">
<input>/asta:literature-review "explainability in deep learning" --depth quick</input>
<output>
# Literature Review: Explainability in Deep Learning

## Overview
Explainability in deep learning has emerged as a critical research area, driven by the need to understand and trust AI systems in high-stakes applications. This review covers key approaches including attention visualization, feature attribution, and concept-based explanations.

## Key Themes

### Gradient-Based Methods
Post-hoc explanation methods that compute input feature importance:
- Simonyan et al. (2014): Introduced saliency maps via gradient computation
- Sundararajan et al. (2017): Integrated Gradients with axiomatic foundations
- Selvaraju et al. (2017): Grad-CAM for visual explanations in CNNs

### Attention-Based Interpretability
Using attention weights as explanations:
- Bahdanau et al. (2015): Attention mechanism for sequence-to-sequence models
- Jain & Wallace (2019): Challenged attention as faithful explanation

## Research Gaps
- Limited work on explanations for generative models
- Lack of standardized evaluation metrics for explanation quality
- Few studies on user comprehension of explanations

## Seminal Papers
1. "Attention Is All You Need" - Foundation of attention mechanisms
2. "LIME" - Model-agnostic local explanations
3. "Integrated Gradients" - Axiomatic attribution method
</output>
</example>
</examples>

<anti_patterns>
- **Don't fabricate papers** - Only cite papers found through Asta tools
- **Don't oversimplify** - Capture nuance and disagreements in the field
- **Don't ignore recency** - Balance seminal work with recent developments
- **Don't skip citations** - Every claim should be backed by a specific paper
</anti_patterns>
