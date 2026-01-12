---
description: Find academic citations to support or verify a claim
argument-hint: <claim>
---

Find authoritative academic sources to support, refute, or provide context for specific claims.

## Usage

```
/asta:cite-sources "Large language models exhibit emergent capabilities at scale"
/asta:cite-sources "CRISPR can edit genes with high precision"
```

## What You Get

For each claim, returns:
- **Supporting sources**: Papers that provide evidence for the claim
- **Confidence score**: How well the literature supports the claim
- **Key quotes**: Relevant passages from the papers
- **Caveats**: Any nuances or limitations mentioned in the literature
- **Citations**: Properly formatted references

## Confidence Levels

- **Strong**: Multiple high-quality sources directly support the claim
- **Moderate**: Some support, but with caveats or limited evidence
- **Weak**: Little direct support, claim may be overstated
- **Contested**: Literature shows disagreement on this topic

## Examples

```
/asta:cite-sources "Transformer models outperform RNNs on long sequences"
/asta:cite-sources "Exercise reduces risk of cardiovascular disease"
/asta:cite-sources "Quantum computers can break RSA encryption"
```

## Use Cases

- Fact-checking research claims
- Finding citations for academic writing
- Verifying statements before publication
- Understanding scientific consensus on a topic
