# Change impact analysis

`ChangeImpactAnalyzer` is the first lightweight implementation of the Phase 3 change-impact capability.

## Contract

Given active `CanonicalFact` records and one changed fact, the analyzer returns the IDs of facts that may be affected through an explicit reference chain.

A dependency edge exists only when:

```text
upstream.object == downstream.subject
```

Comparison is case-insensitive and surrounding whitespace is ignored. Traversal is transitive and deterministic.

## Precision boundary

This is intentionally **not** a semantic dependency engine.

It does not:

- infer relationships from prose;
- use embeddings or an LLM;
- guess whether two names refer to the same entity;
- mutate Canon;
- declare a change contradictory.

The result is an evidence-backed candidate impact set. A later application layer can resolve each affected fact back to its assertion and source evidence and present it for human review.

## Example

```text
Alice parent_of Bob
Bob parent_of Claire
Claire lives_in Paris
```

Changing the first fact yields the explicit impact chain:

```text
Alice parent_of Bob
        |
        v
Bob parent_of Claire
        |
        v
Claire lives_in Paris
```

This establishes the reusable dependency primitive without prematurely introducing a generic knowledge graph.
