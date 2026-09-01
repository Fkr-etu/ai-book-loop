# Configuration

Runtime configuration is owned by infrastructure settings and consumed by the composition root.

## Rules

- Do not read environment variables directly from domain or use-case code.
- Provider-specific settings belong in infrastructure.
- Keep credentials out of source control.
- Tests should provide deterministic fake dependencies instead of production credentials.

## LLM provider

The MVP targets Gemini, but the provider is configurable so application behavior does not depend on Gemini-specific APIs.

## Persistence

The MVP uses SQLite. Database configuration is supplied through infrastructure settings rather than embedded in application logic.

For exact variable names and defaults, consult the current settings implementation; this document intentionally avoids duplicating implementation details that can drift.
