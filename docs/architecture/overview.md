# Architecture Overview

## Layers

```text
Web UI (Next.js) / CLI
 │
 ▼
Application use cases / Mock API Services
 │
 ▼
Domain models + ports
 ▲
 │
Infrastructure adapters
 │
 ├── SQLite repository / localStorage
 └── Configurable LLM provider / Mock API Client
```

Workflow orchestration is isolated from the domain. Agents encapsulate LLM-facing capabilities; use cases decide when those capabilities are invoked.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books, chapters, lore, characters, and scene reviews. It must remain independent of SQLite, Gemini, LangGraph, and the CLI.

### Application

Owns business actions such as creating a book, generating an outline, approving an outline, adding a chapter, and generating a chapter. It coordinates ports and domain state.

### Frontend Studio (`web/`)

Provides the user-facing web experience ("Manuscript Studio"):
- **`src/app/`**: Next.js App Router page routes for dashboard, authentication, setup, studio desk, outline, characters, lore, lore-graph, intention-lab, validation-loop, export, and pricing.
- **`src/components/`**: Tactile Minimalism UI layout components (`Navbar`, `Sidebar`, `StudioLayout`, `Providers`).
- **`src/types/`**: Centralized TypeScript data models and API response contracts.
- **`src/services/api.ts`**: Decoupled mock API client handling CRUD operations and simulated LLM critique responses.
- **`src/lib/useProjectStore.tsx`**: React Context store providing state management and sync with `localStorage`.

### Agents

Provide focused LLM capabilities such as outline generation, writing, review, and summarization. They should not become business orchestrators.

### Workflow

Coordinates the multi-step chapter generation loop. The workflow can use LangGraph where useful, but the rest of the application must not depend on that implementation choice.

### Infrastructure

Provides concrete persistence (SQLite / `localStorage`), configuration, and LLM provider implementations and assembles them in the composition root.

### CLI

Translates command-line input into application use-case calls and presents results. It contains no business rules or infrastructure wiring beyond obtaining the composition root.

## Composition root

`infrastructure/container.py` is the application composition root. It wires settings, repository, LLM provider, agents, workflow, and use cases. New entry points should reuse this assembly rather than constructing provider-specific dependencies themselves.
