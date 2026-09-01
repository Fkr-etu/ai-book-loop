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
 ├── SQLite repository / localStorage
 └── Configurable LLM provider / Mock API Client
```

Workflow orchestration is isolated from the domain. Agents encapsulate LLM-facing capabilities; use cases decide when those capabilities are invoked.

## Main responsibilities

### Domain

Owns book state and domain concepts such as books, chapters, lore, characters, and scene reviews. It remains independent of persistence engines and LLM providers.

### Application

Owns business actions such as creating a book, generating an outline, approving an outline, adding a chapter, and generating a chapter.

### Frontend Studio (`web/`)

Provides the user-facing web experience ("Manuscript Studio"):
- **`src/app/`**: Next.js App Router page routes for dashboard, authentication, setup, studio desk, outline, characters, lore, lore-graph, intention-lab, validation-loop, export, and pricing.
- **`src/components/`**: Tactile Minimalism UI layout components (`Navbar`, `Sidebar`, `StudioLayout`, `Providers`).
- **`src/types/`**: Centralized TypeScript data models and API response contracts.
- **`src/services/api.ts`**: Decoupled mock API client handling CRUD operations and simulated LLM critique responses.
- **`src/lib/useProjectStore.tsx`**: React Context store providing state management and sync with `localStorage`.

### Agents

Provide focused LLM capabilities such as outline generation, writing, review, and summarization.

### Infrastructure

Provides concrete persistence (SQLite / `localStorage`), configuration, and LLM provider implementations.
