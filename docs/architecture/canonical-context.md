# Canonical context

Stage 3 of ADR 001 makes approved knowledge available to chapter generation. Stage 4 bounds that context by retrieving only Canon facts relevant to the current chapter. Stage 5 separates the retrieval contract from its lexical implementation. Stage 6 adds an embedding-backed implementation without making embeddings the source of truth.

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

`CanonicalKnowledgeRetriever` is the domain-level retrieval contract. `CanonicalRetriever` is the default dependency-free implementation and uses deterministic lexical overlap. `EmbeddingCanonicalRetriever` is an optional semantic implementation that ranks facts by cosine similarity between query and fact embeddings.

The embedding boundary is `EmbeddingProvider` in the domain protocols. A provider can wrap a local model or external embedding API without coupling Canon retrieval to a vendor or vector database. The semantic retriever only consumes active facts supplied by the knowledge repository; it does not persist embeddings or mutate Canon.

Semantic retrieval validates non-empty finite vectors, rejects dimension mismatches, supports configurable `top_k` and `min_score`, and uses stable fact id/version ordering for equal similarity scores. A zero query vector produces no results.

`ContextBuilder` depends on the `CanonicalKnowledgeRetriever` protocol rather than any concrete implementation. Lexical, embedding, or future hybrid strategies can therefore be selected without modifying context assembly or knowledge storage.

Each canonical entry carries its fact and assertion identifiers so downstream tooling can retain provenance. The underlying chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

The retrieval strategy must remain read-only with respect to Canon: retrieval cannot create, approve, modify, deactivate, or promote canonical facts. A vector index, when introduced, remains an optimization layer and never becomes the canonical source of truth.
