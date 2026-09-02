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

Workflow orchestration (LangGraph implementation)
 ├── ContextBuilder
 ├── WriterAgent
 ├── ChapterLinter
 ├── ReviewerAgent
 └── SummarizerAgent
```

The architecture separates **what the application must do** from **how the multi-step AI loop is executed**. Agents expose focused LLM capabilities; application policies own deterministic rules; the workflow coordinates the sequence.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books, outlines, chapters, lore, and scene reviews. It must remain independent of SQLite, Gemini, LangGraph, and the CLI.

The domain contains the structured `Outline`, chapter status/version/summary state, and validation invariants such as sequential outline chapter numbers.

### Application

Owns business actions and deterministic policies such as:

- creating a book;
- generating and approving an outline;
- adding chapters sequentially;
- building bounded generation context;
- deciding review outcomes from score/approval, threshold, attempt and retry budget.

The application is also responsible for enforcing author approval gates. An LLM response cannot approve an outline or bypass the retry policy.

### Agents

Provide focused LLM capabilities:

- **WriterAgent** — generates a chapter draft from the chapter context;
- **ReviewerAgent** — evaluates a draft and returns a structured `SceneReview`;
- **SummarizerAgent** — summarizes an accepted chapter for continuity;
- outline generation remains a separate capability for producing the structured book outline.

Agents do not own persistence, business state transitions, retry loops, or author approvals.

### Workflow

`ChapterWorkflow` coordinates one chapter generation run. The current implementation uses LangGraph as the state-machine executor, with these stages:

```text
START
  -> write
  -> review
       -> retry -> write
       -> accept -> summarize -> END
       -> needs_review -> END
```

Before LLM review, the workflow runs a deterministic `ChapterLinter`. Every generated attempt is persisted; every LLM review is persisted; only an accepted chapter produces the persisted summary used for later continuity.

LangGraph is an implementation detail. Domain and application code must not import LangGraph-specific APIs so the orchestration engine can be replaced later.

### ContextBuilder

`ContextBuilder.for_chapter()` is the boundary between persisted state and LLM prompt context. It renders a bounded context containing author idea, theme, lore, structured outline, constraints, previous chapter summaries, and the current chapter objective.

The canonical continuity mechanism is the accepted summary of each previous chapter, not the raw history of all drafts.

### Infrastructure

Provides concrete persistence and provider implementations and assembles them in the composition root. The current backend persists book/chapter state and generation history in SQLite and uses a configurable LLM provider.

### Frontend Studio (`web/`)

Provides the user-facing web experience ("Manuscript Studio"):
- **`src/app/`**: Next.js App Router page routes for dashboard, authentication, setup, studio desk, outline, characters, lore, lore-graph, intention-lab, validation-loop, export, and pricing.
- **`src/components/`**: Tactile Minimalism UI layout components (`Navbar`, `Sidebar`, `StudioLayout`, `Providers`).
- **`src/types/`**: Centralized TypeScript data models and API response contracts.
- **`src/services/api.ts`**: Decoupled API client boundary; mock behavior may be used by the frontend while backend integration is developed.
- **`src/lib/useProjectStore.tsx`**: React Context store providing frontend state management and local persistence where applicable.

### CLI

Translates command-line input into application use-case calls and presents results. It contains no business rules or provider-specific orchestration.

## Composition root

`infrastructure/container.py` is the application composition root. It wires settings, repository, LLM provider, agents, workflow, and use cases. New entry points should reuse this assembly rather than constructing provider-specific dependencies themselves.
