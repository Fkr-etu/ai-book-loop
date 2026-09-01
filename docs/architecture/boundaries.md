# Architecture Boundaries

The following dependency rules are intentional and should be preserved.

| Layer | May depend on | Must not depend on |
|---|---|---|
| Domain | Python standard library, domain types | Application, agents, workflow, SQLite, Gemini, CLI |
| Application | Domain, ports, application policies | Concrete SQLite/Gemini implementations |
| Agents | LLM port, domain/application DTOs as needed | CLI, persistence details |
| Workflow | Agents, workflow state, application/domain abstractions | CLI, direct database implementation |
| Infrastructure | Domain/application ports, concrete adapters | Business rules that belong in domain/use cases |
| CLI | Application use cases, composition root | SQLite APIs, provider SDKs, business rules |

## Practical review questions

Before accepting a dependency, ask:

1. Is this a business rule? If yes, it belongs in domain/application rather than an adapter.
2. Is this provider-specific? If yes, keep it in infrastructure or an adapter.
3. Can this be deterministic? If yes, implement it in Python.
4. Would replacing Gemini, SQLite, or LangGraph require changing the domain? If yes, the boundary is probably wrong.
5. Can the use case be tested without network access? It should be.
