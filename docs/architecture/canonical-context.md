# Canonical context

Stage 3 of ADR 001 makes approved knowledge available to chapter generation. Stage 4 bounds that context by retrieving only Canon facts relevant to the current chapter.

```text
CanonicalFact (active)
        ↓
 CanonicalRetriever
        ↓
   ContextBuilder
        ↓
 chapter generation
        ↓
      Writer
```

Only active `CanonicalFact` records are eligible for retrieval. Proposed, deferred, rejected, and inactive historical facts remain outside generation context.

`CanonicalRetriever` currently uses deterministic lexical overlap across the chapter title, objective, previous chapter summaries, and each fact's statement/subject/predicate/object. Results are sorted by descending overlap score, then stable fact id/version, with configurable `top_k` and `min_score`.

Each canonical entry carries its fact and assertion identifiers so downstream tooling can retain provenance. The underlying chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

The retrieval strategy is deliberately dependency-free. Embeddings, vector search, semantic ranking, and more advanced query expansion can replace or complement it later without weakening the canonical boundary.
