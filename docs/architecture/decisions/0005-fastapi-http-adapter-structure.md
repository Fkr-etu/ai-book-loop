# ADR-0005: FastAPI HTTP Adapter Structure

- Status: Accepted
- Date: 2026-09-06

## Context

The FastAPI entry point had accumulated authentication, authorization middleware, request DTOs, HTTP error mapping, and routes for books, outlines, chapters, Canon, and document ingestion in a single `book_loop/api/app.py` module.

This made the HTTP adapter difficult to maintain and obscured the existing application/domain/infrastructure boundaries.

## Decision

Keep FastAPI as an HTTP adapter and split its routes by product responsibility:

- `api/routes/auth.py` — authentication/session endpoints;
- `api/routes/books.py` — book collection and book lifecycle endpoints;
- `api/routes/outline.py` — outline endpoints;
- `api/routes/chapters.py` — chapter endpoints and canonical context projection;
- `api/routes/canon.py` — Canon queries and assertion review;
- `api/routes/documents.py` — document ingestion endpoint.

`api/app.py` remains the composition root for FastAPI: application creation, middleware configuration, shared application state, health endpoint, and router registration.

Shared HTTP dependencies live in `api/dependencies.py`.

This is an HTTP-adapter organization change, not a new business layer. Existing application use cases remain the place where business actions are orchestrated; route modules must not absorb domain rules or provider-specific implementations.

## Consequences

- The FastAPI composition root remains small and stable.
- HTTP concerns are grouped by bounded responsibility.
- Existing application use cases and domain boundaries are preserved.
- Future interfaces can continue to reuse application use cases rather than depending on FastAPI.
- Route-level tests can target one API responsibility without navigating a monolithic module.

## Non-goals

- Do not move business rules into route modules.
- Do not introduce a service layer solely to reduce file size.
- Do not couple domain code to FastAPI.
- Do not change workflow orchestration or Canon semantics as part of this refactor.
