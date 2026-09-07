# Product Strategy

This document complements the product roadmap with strategic decisions and sequencing rules. It defines what we are trying to prove, what we deliberately defer, and when infrastructure changes become justified.

## 1. Strategic thesis

AI Book Loop is the first product and the Book is the proving ground. The core asset is a **consistency engine** able to maintain a trusted, auditable representation of a long-lived corpus and evaluate proposed changes against that state.

```text
Documents / content
        ↓
Extraction / analysis
        ↓
Assertions + evidence
        ↓
Consistency detection
        ↓
Human review
        ↓
Canonical state
        ↓
Change impact / regression analysis
```

The strategic objective is not to build a generic knowledge platform before the Book use case is validated. It is to prove that creators repeatedly obtain value from evidence-backed consistency checks and an explicit approval loop.

## 2. What is the moat?

The moat is not a particular LLM, prompt, vector database, generic RAG pipeline, or editor.

The moat we want to prove is:

1. reliable extraction of meaningful assertions;
2. explicit evidence and provenance;
3. a clear proposed-vs-approved boundary;
4. canonical state that humans can trust;
5. deterministic and eventually semantic consistency detection;
6. dependency-aware change impact;
7. reproducible review decisions;
8. a loop that becomes more useful as the corpus evolves.

If those primitives work, retrieval and infrastructure can evolve without changing the core product thesis.

## 3. Near-term priority: prove the Book consistency loop

The immediate objective is product validation, not platform expansion.

```text
Author intent
    ↓
Outline / proposal
    ↓
New content
    ↓
Consistency + quality checks
    ↓
Evidence-backed findings
    ↓
Human decision
    ↓
Approved Canon
    ↓
Next chapter / revision
```

The current implementation already provides the foundations: assertions, evidence, conflicts, CanonicalFacts, review decisions, Canon diagnostics and the composable `UnifiedConsistencyEngine`. The next value to prove is whether authors trust and repeatedly use those capabilities.

### Book success signals

- users complete multiple chapters or revisions;
- findings catch useful continuity errors;
- evidence makes findings understandable and verifiable;
- users trust the approved canonical state;
- the loop saves meaningful time or reduces rework;
- users return because the growing corpus makes consistency protection increasingly valuable.

Do not generalize the product merely because the architecture can generalize.

## 4. Canon and consistency: smallest useful abstraction

The current useful primitives are:

- `SourceDocument` — where source material originates;
- `Assertion` — a proposed structured statement;
- `Evidence` — support and provenance for an assertion;
- `Conflict` — persisted incompatible assertions;
- `ReviewDecision` — explicit disposition of proposed knowledge;
- `CanonicalFact` — approved knowledge used as source of truth;
- `ConsistencyIssue` — author-facing consistency finding;
- `ConsistencyDetector` implementations — independent detection capabilities composed by the consistency engine.

Current ownership is deliberately separated:

- `ExtractChapterAssertions` extracts proposals;
- `DetectConflicts` handles persisted assertion-vs-assertion conflicts;
- `CanonDiagnosticChecker` checks new text against active Canon;
- `UnifiedConsistencyEngine` composes detectors and deduplicates stable issues;
- author/application review remains authoritative for Canon mutation.

The principle is: **L’IA propose, l’auteur décide.**

## 5. Database strategy

Database choice follows operational evidence. It is not a product milestone by itself.

### Current state — PostgreSQL

PostgreSQL/Cloud SQL is the current production persistence layer. It supports the deployed multi-user backend, durable workflow runs, Canon state, chapter history and transactional persistence requirements.

The domain and application ports remain persistence-agnostic. PostgreSQL is an infrastructure choice, not the definition of the Canon model.

### Retrieval — only when needed

Do not add pgvector or embeddings merely because semantic retrieval may become useful.

Add semantic retrieval when measured evidence shows that structured retrieval/candidate selection is no longer sufficient, for example:

- relevant evidence is systematically missed by deterministic candidate selection;
- corpus size makes candidate generation too expensive;
- semantic similarity materially improves consistency detection;
- retrieval quality can be measured against a representative evaluation set.

**PostgreSQL is a persistence/scalability decision. pgvector is a retrieval decision. They are independent.**

## 6. Retrieval is not the source of truth

Even when embeddings exist, vectors remain a retrieval mechanism.

The source of truth remains:

```text
Canonical facts
+ evidence
+ provenance
+ review decisions
+ versions
+ dependencies
```

A retrieval result can propose relevant evidence. It cannot make a fact canonical.

## 7. What we deliberately defer

Until product evidence exists, defer:

- pgvector and embeddings;
- generic RAG infrastructure;
- a full knowledge graph;
- broad external integrations;
- enterprise governance;
- a generic documentation editor;
- complex multi-agent orchestration;
- automatic unsupervised Canon mutation;
- adjacent vertical-specific UX before the common consistency problem is validated.

The rule is simple:

> **Do not pay platform complexity before the workflow has demonstrated the need for it.**

## 8. Strategic gates

Every major expansion should pass five gates:

### Value
Does the workflow solve a painful problem better than a generic LLM or the customer's current process?

### Trust
Can users understand and verify why the system made a finding or proposed a canonical update?

### Frequency
Does the workflow recur often enough to create habitual use and retention?

### Integration
Can the system work above existing sources of truth rather than requiring unnecessary migration?

### Economics
Does the value justify inference, storage, retrieval and infrastructure cost?

Failure at any gate means revisiting the workflow or ICP before adding complexity.

## 9. Strategic sequence

```text
1. Prove Book loop with real authors
        ↓
2. Prove repeated value of Consistency Engine / Corpus Intelligence
        ↓
3. Add change-impact and regression capabilities
        ↓
4. Validate adjacent creator segments
        ↓
5. Add integrations and creator SaaS capabilities from observed demand
        ↓
6. Test Documentation QA as a separate market
        ↓
7. Add agentic resolution only after trust/value evidence
        ↓
8. Add enterprise governance only when commercially justified
```

Infrastructure evolves independently from product phases:

```text
PostgreSQL / Cloud SQL
        ↓
semantic retrieval evidence
        ↓
optional pgvector / embeddings
```

The strategic objective is to build the smallest reliable system that can maintain and validate canonical knowledge, then expand only when users prove where that capability has economic value.
