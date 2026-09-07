# Assertion normalization

## Purpose

Book Loop uses books as its current product wedge, but consistency primitives must not encode assumptions about characters, chapters, or narrative structure. Assertion normalization is the boundary that turns language-dependent extraction output into stable semantic predicates before consistency analysis.

The intended flow is:

```text
source text
    ↓
AssertionExtractor
    ↓
ExtractedAssertion
    ↓
PredicateNormalizer
    ↓
normalized claim
    ↓
consistency detectors
```

## Contract

`PredicateNormalizer` is a domain-level protocol:

```python
normalize(*, predicate: str, language: str = "fr") -> str
```

The protocol does not prescribe a particular NLP implementation. The current implementation is deterministic and rule-based so that normalization is testable, reproducible, and independent from an LLM provider.

## V1 vocabulary

The first controlled vocabulary deliberately stays small. Examples include:

- `habite`, `vit`, `réside` → `lives_in`
- `métier`, `profession` → `occupation`
- `père de`, `mère de`, `parent de` → `parent_of`
- `époux de`, `épouse de`, `marié à` → `spouse_of`
- `situé à` → `located_in`
- `créé par` → `created_by`
- `appartient à` → `belongs_to`

English equivalents are included for the same semantic predicates.

Unknown predicates are normalized to a stable `snake_case` representation rather than being assigned invented semantics. This makes the vocabulary extensible without silently changing meaning.

## Provenance invariant

Normalization changes semantic fields only. The original `statement` remains the exact source excerpt and offsets continue to point into the original chunk. This preserves evidence traceability while allowing detectors to compare equivalent predicates across languages or extraction phrasings.

## Why this boundary matters

The consistency engine should consume claims, not linguistic surface forms. A future documentation source might express `lives_in` as an API or configuration relationship instead of a narrative fact. The engine can remain domain-neutral as long as extraction and normalization provide stable claim semantics.

This is intentionally not a generic knowledge graph, embedding pipeline, or documentation product. Those are future experiments; the current MVP validates the architecture through the book use case first.
