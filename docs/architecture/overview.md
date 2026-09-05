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
 ├── SQLite repository
 │
 └── Configurable LLM provider

ChapterWorkflow
 ├── durable run store
 ├── ContextBuilder
 ├── WriterAgent
 ├── ChapterLinter
 ├── linguistic validation
 ├── ReviewerAgent
 ├── CorrectorAgent
 └── SummarizerAgent
```

The architecture separates **what the application must do** from **how the multi-step AI loop is executed**. Agents expose focused LLM capabilities; application policies own deterministic rules; the workflow coordinates the sequence and persists recovery state.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books, outlines, chapters, lore, scene reviews, diagnostics, and canonical knowledge. It must remain independent of SQLite, Gemini, LangGraph, and the CLI.

The domain contains the structured `Outline`, chapter status/version/summary state, validation invariants such as sequential outline chapter numbers, and the durable `ChapterWorkflowRun` contract used for restartable chapter execution.

Canonical knowledge is represented by assertions, evidence, conflicts, review decisions, and approved canonical facts. The exact persisted schema remains documented in `data-model.md`.

### Application

Owns business actions and deterministic policies such as:

- creating a book;
- generating and approving an outline;
- adding chapters sequentially;
- building bounded generation context;
- deciding review outcomes from score/approval, threshold, attempt and retry budget;
- approving or rejecting proposed canonical knowledge.

The application is also responsible for enforcing author approval gates. An LLM response cannot approve an outline, mutate canonical state, or bypass the retry policy.

### Agents

Provide focused LLM capabilities:

- **WriterAgent** — generates a chapter draft from the chapter context;
- **ReviewerAgent** — evaluates a draft and returns a structured `SceneReview`;
- **CorrectorAgent** — proposes a revised draft from review findings;
- **SummarizerAgent** — summarizes an accepted chapter for continuity;
- extraction/reconciliation agents may propose assertions or identify conflicts, but they must not silently write Canon;
- outline generation remains a separate capability for producing the structured book outline.

Agents do not own persistence, business state transitions, retry loops, or author approvals.

### Canonical knowledge

Canon is the approved source of truth for validated project knowledge. The lifecycle is:

```text
Source documents
      ↓
   Extraction
      ↓
   Assertions
      ↓
Evidence / conflicts / confidence
      ↓
 Human review & decision
      ↓
     Canon
      ↓
Generation / QA
```

Canonical facts retain provenance and an auditable approval history. Contradictory assertions are represented explicitly rather than silently resolved by an LLM.

The current implementation already supports document ingestion, assertion extraction, conflict detection and explicit review-to-Canon transitions. Broader knowledge-graph modeling remains intentionally deferred.

### Workflow

`ChapterWorkflow` coordinates one chapter generation run. It exposes a LangGraph-compatible `build()` graph for compatibility, but the production `run()` path uses a durable, persisted stepwise state machine so that a process restart can resume an existing run.

```text
START
  -> write
  -> review
       -> retry -> correct -> review
       -> accept -> summarize -> END
       -> needs_review -> END

Each transition is checkpointed in SQLite.
```

Before LLM review, the workflow runs deterministic linting and the configured linguistic validation. Blocking diagnostics prevent the LLM reviewer from being called. Non-blocking diagnostics are passed to the reviewer as structured input. Every generated attempt is persisted before review.

Runs are identified by `(book_id, chapter_number, idempotency_key)`. A completed or terminal run is not replayed, and a persisted chapter version is reused if a restart occurs after version persistence but before the workflow checkpoint advances.

LangGraph remains an implementation detail and is not the durable execution mechanism. Domain and application code must not import LangGraph-specific APIs.

### ContextBuilder

`ContextBuilder.for_chapter()` is the boundary between persisted state and LLM prompt context. It renders bounded context containing author idea, theme, lore, structured outline, constraints, previous chapter summaries, the current chapter objective, and approved Canon context when configured.

Accepted chapter summaries and active Canon facts are continuity mechanisms. Rejected attempts and transient AI output are not canonical continuity memory.

### Infrastructure

Provides concrete persistence and provider implementations and assembles them in the composition root. The backend persists book/chapter state, generation history, reviews, Canon state, and workflow runs in SQLite and uses a configurable LLM provider.

Workflow-run persistence is provided by `SQLiteWorkflowRunStore` in production and an in-memory store for isolated tests/lightweight callers. The SQLite uniqueness constraint protects run creation for the same idempotency key.

### Frontend Studio (`web/`)

Provides the user-facing web experience ("Manuscript Studio"):
- **`src/app/`**: Next.js App Router page routes for dashboard, authentication, setup, studio desk, outline, characters, lore, lore-graph, intention-lab, validation-loop, export, and pricing.
- **`src/components/`**: Tactile Minimalism UI layout components.
- **`src/types/`**: centralized TypeScript data models and API response contracts.
- **`src/services/api.ts`**: decoupled API client boundary; mock behavior may be used while backend integration is developed.
- **`src/lib/useProjectStore.tsx`**: frontend state management and local persistence where applicable.

### CLI

Translates command-line input into application use-case calls and presents results. It contains no business rules or provider-specific orchestration.

## Composition root

`infrastructure/container.py` is the application composition root. It wires settings, repository, LLM provider, agents, `SQLiteWorkflowRunStore`, workflow, and use cases. New entry points should reuse this assembly rather than constructing provider-specific dependencies themselves.
