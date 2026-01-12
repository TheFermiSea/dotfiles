---
description: Generate a structured literature review on a research topic
argument-hint: <topic> [--depth quick|standard|comprehensive]
---

Generate structured literature reviews by synthesizing findings from multiple papers on a research topic.

## Usage

```
/asta:literature-review "federated learning in healthcare"
/asta:literature-review "quantum computing error correction" --depth comprehensive
```

## Depth Options

- `--depth quick`: 5-10 key papers, fast overview
- `--depth standard`: 15-25 papers, balanced coverage (default)
- `--depth comprehensive`: 30+ papers, thorough analysis

## What You Get

A structured review including:
- **Overview**: Summary of the research landscape
- **Key Themes**: Major research directions and approaches
- **Seminal Works**: Foundational papers in the field
- **Recent Advances**: Latest developments and trends
- **Research Gaps**: Open questions and opportunities
- **Bibliography**: Full citations for all referenced papers

## Examples

```
/asta:literature-review "transformer architectures" --depth quick
/asta:literature-review "drug discovery machine learning" --depth comprehensive
/asta:literature-review "renewable energy storage"
```

## Tips

- Be specific with your topic for better results
- Use `--depth quick` for initial exploration
- Use `--depth comprehensive` for thorough research surveys
