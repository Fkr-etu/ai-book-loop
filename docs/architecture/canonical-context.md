# Canonical context

Stage 3 of ADR 001 makes approved knowledge available to chapter generation. Stage 4 bounds that context by retrieving only Canon facts relevant to the current chapter. Stage 5 separates the retrieval contract from its lexical implementation so semantic retrieval can be introduced without changing chapter generation or the Canon boundary.

```text
CanonicalFact (active)
        ↓
CanonicalKnowledgeRetriever
        ↓
   ContextBuilder
        ↓
 chapter generation
        ↓
      Writer
```

Only active `CanonicalFact` records are eligible for retrieval. Proposed, deferred, rejected, and inactive historical facts remain outside generation context.

`CanonicalKnowledgeRetriever` is the domain-level retrieval contract. `CanonicalRetriever` is the default dependency-free implementation and currently uses deterministic lexical overlap across the chapter title, objective, previous chapter summaries, and each fact's statement/subject/predicate/object. Results are sorted by descending overlap score, then stable fact id/version, with configurable `top_k` and `min_score`.

`ContextBuilder` depends on the `CanonicalKnowledgeRetriever` protocol rather than the concrete implementation. This makes the retrieval strategy replaceable: a future embedding/vector or hybrid retriever can be injected without modifying context assembly or knowledge storage.

Each canonical entry carries its fact and assertion identifiers so downstream tooling can retain provenance. The underlying chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

The retrieval strategy must remain read-only with respect to Canon: retrieval cannot create, approve, modify, deactivate, or promote canonical facts. Embeddings, vector search, semantic ranking, and more advanced query expansion remain optional implementations behind the same contract.
