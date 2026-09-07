# Architecture Overview

## Layers

```text
Web UI (Next.js) / CLI
 │
 ▼
Application use cases + policies
 │
 ▼
Domain models + ports
 ▲
 │
Infrastructure adapters
 │
 ├── PostgreSQL repository
 │
 └── Configurable LLM provider

ChapterWorkflow
 ├── durable run store
 ├── ContextBuilder
 ├── WriterAgent
 ├── deterministic + linguistic validation
 ├── ReviewerAgent
 ├── CorrectorAgent
 └── SummarizerAgent

Consistency
 ├── assertion extraction
 ├── assertion-vs-assertion conflict detection
 ├── new-text-vs-Canon diagnostics
 └── UnifiedConsistencyEngine
```

The architecture separates **what the application must do** from **how AI capabilities are provided and workflows are executed**. Agents expose focused LLM capabilities; application policies own deterministic rules; workflows coordinate persisted execution state; the consistency layer detects and explains contradictions without silently deciding Canon truth.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books, outlines, chapters, diagnostics and canonical knowledge. It must remain independent of PostgreSQL, Gemini, LangGraph, and the CLI.

Canonical knowledge is represented by assertions, evidence, conflicts, review decisions and approved canonical facts. Author-facing consistency results are represented by `ConsistencyIssue`; this is a projection/contract, not itself Canon truth.

### Application

Owns business actions and deterministic policies such as:

- creating a book;
- generating and approving an outline;
- adding chapters sequentially;
- building bounded generation context;
- deciding review outcomes from score/approval, threshold, attempt and retry budget;
- approving or rejecting proposed canonical knowledge;
- running consistency analysis through the configured detector set.

Application services enforce author approval gates. An LLM response cannot approve an outline, mutate canonical state, or bypass retry policy.

### Agents

Provide focused LLM capabilities:

- **WriterAgent** — generates a chapter draft from chapter context;
- **ReviewerAgent** — evaluates a draft and returns a structured review;
- **CorrectorAgent** — proposes a revised draft from review findings;
- **SummarizerAgent** — summarizes an accepted chapter for continuity;
- assertion extraction may propose assertions/evidence, but cannot silently write Canon.

Agents do not own persistence, business state transitions, retry loops, or author approvals.

### Canonical knowledge and consistency

Canon is the approved source of truth for validated project knowledge. The lifecycle is:

```text
Source documents
      ↓
   Extraction
      ↓
   Assertions + Evidence
      ↓
Conflicts / Consistency analysis
      ↓
 Human review & decision
      ↓
     Canon
      ↓
Generation / QA
```

The current implementation has two complementary consistency surfaces:

- `DetectConflicts` detects persisted assertion-vs-assertion contradictions;
- `CanonDiagnosticChecker` compares newly supplied text with active Canon facts;
- `UnifiedConsistencyEngine` composes consistency detectors and deduplicates their `ConsistencyIssue` results by stable ID.

The engine currently executes detectors sequentially. Parallel execution is not assumed by the architecture and should only be introduced when expensive independent detectors justify it and their persistence/session boundaries are safe.

Detection does not decide which assertion is true. Explicit author/application review is required before Canon promotion.

### Workflow

`ChapterWorkflow` coordinates one chapter generation run. It exposes a LangGraph-compatible `build()` graph for compatibility, but the production `run()` path uses durable persisted workflow state for restartability.

```text
START
  -> write
  -> validate
  -> review
       -> retry -> correct -> review
       -> accept -> summarize -> END
       -> needs_review -> END
```

Meaningful transitions and chapter versions are persisted. Generation is bounded by application retry policy. Canon/consistency checks are inputs to review rather than autonomous truth decisions.

### ContextBuilder

`ContextBuilder.for_chapter()` is the boundary between persisted state and LLM prompt context. It renders bounded context from author intent, theme, lore, structured outline, constraints, previous accepted chapter summaries, the current chapter objective and approved Canon context when configured.

Accepted chapter summaries and active Canon facts are continuity mechanisms. Rejected attempts and transient AI output are not canonical continuity memory.

### Infrastructure

Provides concrete PostgreSQL persistence, provider implementations and composition-root wiring. PostgreSQL is the production persistence boundary; migrations are managed through Alembic. The LLM provider remains configurable.

### Frontend Studio (`web/`)

Provides the user-facing web experience. It consumes the backend API through the frontend API boundary and renders persisted backend state. Frontend state is presentation/client state; it must not duplicate backend business rules or invent Canon/consistency truth.

### CLI

Translates command-line input into application use-case calls and presents results. It contains no business rules or provider-specific orchestration.

## Composition root

`infrastructure/container.py` is the application composition root. It wires settings, PostgreSQL repository, LLM provider, agents, workflow persistence, workflow and use cases. New entry points should reuse this assembly rather than constructing provider-specific dependencies themselves.
