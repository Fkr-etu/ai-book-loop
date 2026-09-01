# Scope

This scope describes the product direction after the Narrative Canon & Continuity pivot. Existing authoring features are retained only where they support canon management and continuity QA.

## MVP — commercial wedge

- Create a narrative project.
- Import a small set of source documents.
- Extract canonical entities and assertions: characters, locations, events, relationships, facts, rules, and timeline assertions.
- Show provenance and confidence for extracted assertions.
- Require explicit human approval before assertions become canonical.
- Submit new or edited narrative content for a continuity check.
- Detect and classify contradictions, warnings, and uncertain findings.
- Explain each finding using the conflicting canonical assertions and source material.
- Maintain canonical versions and review decisions.
- Provide a project-level continuity report.

## Post-MVP — canon and change impact

- Canonical entity graph.
- Dependencies between assertions and content.
- `What breaks if I change this?` impact analysis.
- Timeline consistency checks.
- Character state / knowledge checks.
- Stale-content detection.
- Change requests and approval workflow.
- Full provenance and audit history.

## Team SaaS

- Multi-user projects.
- Roles and permissions.
- Review queues.
- Issue assignment.
- Comments and decisions.
- Notifications.
- Usage and canon-health metrics.

## Integrations

Prioritize integrations only after the core workflow is validated with target customers:

- Markdown / JSON / CSV import and export.
- Git-based narrative repositories.
- Game dialogue / quest data.
- Wiki / documentation sources.
- API and webhooks.
- CI continuity checks.

## Assisted resolution

AI authoring remains a supporting capability:

- suggest minimal edits to resolve contradictions;
- generate alternative resolutions;
- summarize proposed changes;
- re-run continuity checks automatically.

All canonical changes require human approval.

## Existing capabilities to preserve or repurpose

The current repository already contains useful concepts that should be generalized rather than discarded:

- sequential chapter workflow;
- outline approval;
- chapter versions;
- review and linting;
- canonical summaries;
- character and lore editors;
- lore relationship graph;
- validation loop;
- bounded retries;
- replaceable LLM infrastructure.

These become implementation components of the broader canon and continuity workflow.

## Explicitly out of scope for now

- Generic AI novel / chapter generation as the primary product.
- Full authoring-suite feature parity with established writing assistants.
- Broad enterprise knowledge management.
- Transmedia production management.
- Multi-region production infrastructure before commercial validation.
- Long-term vector-memory orchestration unless a measured retrieval problem requires it.

## Product validation is part of scope

Before major engineering expansion:

- interview at least 10 target teams;
- onboard at least 3 design partners using real content;
- obtain at least 1 paid pilot or equivalent buying signal;
- measure time saved finding and resolving continuity issues.
