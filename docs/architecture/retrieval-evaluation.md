# Canon retrieval evaluation

Stage 8 makes retrieval quality measurable before the generation → review → correction loop.

```text
Evaluation dataset
        ↓
RetrievalEvaluator
        ↓
CanonicalKnowledgeRetriever
        ↓
ranked Canon facts
        ↓
Precision@K / Recall@K / Hit@K / MRR
```

`RetrievalEvaluationCase` is a reproducible evaluation datum: a query and the set of expected Canon fact `(id, version)` keys. The evaluator never mutates Canon and accepts any implementation of `CanonicalKnowledgeRetriever`, so lexical, semantic, and hybrid strategies can be compared on the same dataset.

For a configured `K`, the evaluator reports:

- **Precision@K**: relevant returned facts divided by returned facts in the evaluated top-K.
- **Recall@K**: relevant returned facts divided by the number of expected relevant facts.
- **Hit@K**: whether at least one expected fact was retrieved.
- **MRR**: reciprocal rank of the first relevant result, or zero when none is retrieved.

Aggregate reports use the arithmetic mean across cases. A case with no expected relevant facts has recall zero; this keeps the benchmark focused on coverage of explicitly required Canon knowledge.

Fact identity includes the Canon version, `(fact.id, fact.version)`, so historical versions cannot accidentally satisfy a case targeting a specific active fact.

The evaluation dataset should be curated from representative chapter queries and expected Canon facts. It should be versioned alongside the code and reused unchanged when comparing retrieval strategies. Unit tests verify metric arithmetic and deterministic repeated evaluation; the benchmark itself should remain independent of any embedding vendor or vector database.

Evaluation is observational only. The evaluator does not create, approve, reject, modify, deactivate, or promote Canon facts. Only the knowledge workflow remains authoritative for Canon state.
