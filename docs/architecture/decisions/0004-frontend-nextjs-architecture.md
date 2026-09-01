# ADR-0004: Frontend Next.js Architecture & Design System

- Status: Accepted
- Date: 2026-09-01

## Context

The application requires a modern, responsive Web UI ("Manuscript Studio") to support authors visually across all writing steps (outlining, character psychology, world bible, intention laboratory, Linter validation loop, relationship graphs, and manuscript compilation).

## Decision

1. **Framework & Stack:** Use Next.js 16 (App Router), TypeScript, and React 19 inside a dedicated `web/` directory.
2. **Design System ("Tactile Minimalism"):** Establish tokenized styling in Tailwind CSS v4 and `globals.css` with a Parchment & Ink color palette (`#f8f5f0` canvas, `#0b1c30` UI blue, `#ffddb8` lore gold) and Playfair Display / Merriweather / Inter / Courier Prime fonts.
3. **Graph Visualization:** Use `@xyflow/react` for interactive Lore Relationship Graph rendering.
4. **Mock API Layer:** Decouple React state from data fetching via `web/src/services/api.ts` and `web/src/types/index.ts`.
5. **E2E Testing:** Use Playwright (`@playwright/test`) for interactive route coverage and screenshot verification.

## Consequences

- Full visual studio experience available for writers without tight coupling to a live backend API during frontend development.
- UI state management remains decoupled from backend communication contracts.
- Automated Playwright tests verify visual and functional regression on every build.
