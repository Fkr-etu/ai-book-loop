# Product Strategy

This document complements the product roadmap with the strategic decisions and sequencing rules that should guide implementation. It is intentionally more opinionated than the feature roadmap: it defines what we are trying to prove, what we are deliberately not building yet, and when infrastructure changes become justified.

## 1. Strategic thesis

AI Book Loop is the first product, but the long-term opportunity is broader than AI-assisted writing.

The core asset is a **canonical knowledge engine** able to maintain a trusted, auditable representation of a long-lived corpus:

```text
Documents / content
        ↓
Extraction / analysis
        ↓
Assertions + evidence
        ↓
Contradictions / dependencies
        ↓
Human review
        ↓
Canonical state
        ↓
Impact analysis on future changes
```

The book is the wedge because it forces the system to solve persistent state, continuity, dependencies, contradictions, iterative review, and human approval in a demanding environment.

The long-term product hypothesis is a **knowledge consistency / documentation QA layer** that can sit above existing company sources of truth.

## 2. What is the moat?

The moat is not:

- a particular LLM;
- prompts;
- a vector database;
- a generic RAG pipeline;
- a knowledge graph built for its own sake;
- an editor competing with existing authoring tools.

The moat we want to prove is:

1. reliable extraction of meaningful assertions;
2. explicit evidence and provenance;
3. a clear proposed-vs-approved boundary;
4. canonical state that humans can trust;
5. dependency-aware change impact;
6. reproducible review decisions;
7. a loop that gets more useful as the corpus evolves.

If those primitives work, retrieval and infrastructure can evolve without changing the core product thesis.

## 3. Near-term priority: prove the Book loop

The immediate objective is not to build the future platform. It is to make the Book workflow sufficiently useful that real users repeatedly use it.

The product loop is:

```text
Author intent
    ↓
Outline proposal
    ↓
Chapter proposal
    ↓
AI review / linting
    ↓
Continuity + quality checks
    ↓
Human approval
    ↓
Canonical update
    ↓
Next chapter / revision
```

The canonical state must remain trustworthy as the manuscript grows. AI-generated material is a proposal until explicitly approved.

### Book success signals

We should look for evidence that:

- users complete multiple chapters or revisions;
- review findings are materially useful rather than decorative;
- continuity errors are caught that a one-shot LLM workflow would miss;
- users understand why a finding was produced;
- users trust the approved canonical state;
- the loop saves meaningful time or reduces rework.

Do not generalize the product merely because the architecture can generalize.

## 4. Canon MVP: smallest useful abstraction

The next architecture step is a **small canonical model**, not a generic knowledge platform.

The first useful primitives are:

- `SourceDocument` — where a statement originates;
- `Assertion` — a proposed statement extracted or inferred from content;
- `Evidence` — the precise support for an assertion;
- `Conflict` — incompatible assertions or constraints;
- `ReviewDecision` — human disposition of a proposal/conflict;
- `CanonicalFact` — approved knowledge used as source of truth;
- `Confidence` — signal attached to analysis, never a substitute for approval;
- `Dependency` — relation between knowledge and affected content.

The critical lifecycle is:

```text
RAW / SOURCE
    ↓
EXTRACTED / PROPOSED
    ↓
UNDER REVIEW
    ↓
APPROVED
    ↓
CANONICAL
```

Rejection must also be represented explicitly. Old versions and decisions are preserved; canonical state is never silently overwritten.

### First Book proof

A generated chapter should eventually be able to produce assertions such as:

```text
Assertion:
  Sarah learns the truth in chapter 18.

Evidence:
  chapter 18, paragraph / span reference

Compared with:
  existing canonical assertion(s)

Result:
  consistent | conflict | needs review

Decision:
  approve | reject | revise
```

This is enough to validate the canonical workflow without implementing a generalized graph or semantic-memory platform.

## 5. Database strategy: SQLite → PostgreSQL → pgvector

Database migration is a consequence of product evidence, not a milestone by itself.

### Stage A — SQLite now

SQLite is the right default while the project is proving the Book loop and the first Canon primitives.

Store structured canonical information directly:

- books and chapters;
- versions;
- assertions;
- evidence/provenance;
- conflicts;
- review decisions;
- canonical facts;
- dependencies.

Do **not** introduce embeddings merely because semantic search may be useful later.

### Stage B — PostgreSQL when production requirements justify it

Move from SQLite to PostgreSQL before introducing pgvector when one or more of these become real requirements:

- deployed production service with meaningful concurrent writes;
- multiple active users/workspaces;
- stronger transactional/concurrency requirements;
- corpus size and query patterns exceed what SQLite handles comfortably;
- operational requirements require a server database;
- backups, observability, replication, or managed database operations become important.

The migration should preserve the domain model and application ports. The persistence adapter changes; the canonical business rules do not.

### Stage C — pgvector only when retrieval becomes the bottleneck

Add pgvector only after semantic retrieval is demonstrated to improve a real workflow or becomes necessary at corpus scale.

Evidence could include:

- exact/structured retrieval no longer finds the relevant evidence reliably;
- large corpora make candidate selection expensive;
- semantic similarity materially improves continuity/conflict detection;
- retrieval quality can be measured against a representative evaluation set.

**PostgreSQL is a production/scalability decision. pgvector is a retrieval decision. They should not be coupled.**

## 6. Retrieval is not the source of truth

Even after embeddings and pgvector exist, vectors must remain a retrieval mechanism.

The source of truth remains:

```text
Canonical facts
+ evidence
+ provenance
+ review decisions
+ versions
+ dependencies
```

A semantic search result can propose relevant evidence. It cannot by itself make a fact canonical.

This distinction is essential to the long-term product: the system is a knowledge QA engine, not merely a RAG chatbot.

## 7. Parallel development strategy

Roadmap work and implementation should be parallelized by architectural ownership to avoid collisions.

While product/strategy work is being refined, the safest independent implementation stream is:

**Canon MVP domain + business rules + tests.**

That stream should:

- live primarily in domain/application layers;
- avoid changing the roadmap documents;
- avoid introducing PostgreSQL or pgvector;
- avoid building generic retrieval infrastructure;
- add invariants and tests around proposed-vs-approved knowledge;
- prove the Assertion → Evidence → Conflict → Review → CanonicalFact cycle.

Other low-collision work can include CI quality, observability, and LLM cost instrumentation, provided they do not alter the core domain contract.

## 8. What we deliberately defer

Until the relevant product evidence exists, defer:

- PostgreSQL migration for its own sake;
- pgvector and embeddings;
- generic RAG infrastructure;
- a full knowledge graph;
- broad integrations;
- enterprise governance;
- a generic documentation editor;
- complex multi-agent orchestration.

The rule is simple:

> **Do not pay platform complexity before the workflow has demonstrated the need for it.**

## 9. Strategic gates

Every major expansion should pass five gates:

### Value
Does the workflow solve a painful problem better than a generic LLM or the customer's current process?

### Trust
Can users understand and verify why the system made a finding or proposed a canonical update?

### Frequency
Does the workflow recur frequently enough to create habitual use and, later, SaaS retention?

### Integration
Can the system work above existing sources of truth rather than requiring migration?

### Economics
Does the value justify the cost of inference, storage, retrieval, and infrastructure?

Failure at any gate means we revisit the workflow or ICP before adding infrastructure.

## 10. Strategic sequence

The intended sequence is therefore:

```text
1. Prove Book loop
        ↓
2. Prove Canon primitives inside Book
        ↓
3. Prove change impact / regression
        ↓
4. Validate documentation problem with design partners
        ↓
5. Productize Documentation QA
        ↓
6. Integrate with existing company sources
        ↓
7. Add SaaS governance / collaboration
        ↓
8. Add agentic resolution
        ↓
9. Add enterprise infrastructure when commercially justified
```

Infrastructure follows evidence:

```text
SQLite
  ↓ (production / concurrency evidence)
PostgreSQL
  ↓ (semantic retrieval evidence)
pgvector
```

The strategic objective is not to build the largest AI stack. It is to build the smallest reliable system that can maintain and validate canonical knowledge, then expand only when users prove where that capability has economic value.
