# Canonical context

Stage 3 of ADR 001 makes approved knowledge available to chapter generation. Stage 4 bounds that context by retrieving only Canon facts relevant to the current chapter. Stage 5 separates the retrieval contract from its lexical implementation. Stage 6 adds an embedding-backed implementation without making embeddings the source of truth. Stage 7 adds deterministic hybrid fusion of lexical and semantic rankings.

```text
CanonicalFact (active)
        ↓
CanonicalKnowledgeRetriever
        ↓
HybridCanonicalRetriever
      ↙       ↘
 lexical    semantic
      \       /
       RRF fusion
          ↓
    ContextBuilder
          ↓
   chapter generation
          ↓
        Writer
```

Only active `CanonicalFact` records are eligible for retrieval. Proposed, deferred, rejected, and inactive historical facts remain outside generation context.

`CanonicalKnowledgeRetriever` is the domain-level retrieval contract. `CanonicalRetriever` is the default dependency-free implementation and uses deterministic lexical overlap. `EmbeddingCanonicalRetriever` is an optional semantic implementation that ranks facts by cosine similarity between query and fact embeddings.

`HybridCanonicalRetriever` composes two implementations of the same retrieval contract and fuses their ranked candidate lists with Reciprocal Rank Fusion (RRF). RRF avoids calibrating incompatible lexical and cosine score scales: each occurrence contributes `1 / (rrf_k + rank)`. The fused results use deterministic descending fused score, then stable fact id/version ordering, with configurable `top_k` and `rrf_k`.

The hybrid retriever is an injectable strategy rather than a mandatory default because an embedding provider is not part of the repository's infrastructure. This keeps the dependency-free lexical path available while allowing application wiring to opt into semantic or hybrid retrieval when an `EmbeddingProvider` is available.

The embedding boundary is `EmbeddingProvider` in the domain protocols. A provider can wrap a local model or external embedding API without coupling Canon retrieval to a vendor or vector database. Neither semantic nor hybrid retrieval persists embeddings or mutates Canon.

`ContextBuilder` depends on the `CanonicalKnowledgeRetriever` protocol rather than any concrete implementation. Lexical, embedding, hybrid, or future retrieval strategies can therefore be selected without modifying context assembly or knowledge storage.

Each canonical entry carries its fact and assertion identifiers so downstream tooling can retain provenance. The underlying chain remains:

`CanonicalFact → ReviewDecision → Assertion → Evidence → SourceDocument`

The retrieval strategy must remain read-only with respect to Canon: retrieval cannot create, approve, modify, deactivate, or promote canonical facts. A vector index, when introduced, remains an optimization layer and never becomes the canonical source of truth.
