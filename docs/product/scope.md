# Scope

This scope describes the product direction after the Narrative Content QA & Canon Engine pivot. Existing authoring features are retained only where they support canon management, continuity QA, or assisted resolution.

## MVP — commercial wedge

The MVP must prove one workflow:

> **Import an existing project, then check new or edited content against its approved canon.**

### Source ingestion

- Create a narrative project.
- Import a small set of source documents.
- Support simple source formats first; avoid requiring migration from an existing narrative stack.
- Extract canonical entities and assertions: characters, locations, events, relationships, facts, rules, and timeline assertions.
- Show provenance and confidence for extracted assertions.
- Require explicit human approval before assertions become canonical.

### Narrative QA

- Submit new or edited narrative content for a continuity check.
- Detect and classify contradictions, stale information, structural risks, and uncertain findings.
- Explain each finding using the conflicting canonical assertions and source material.
- Identify affected entities and content where possible.
- Keep deterministic checks separate from probabilistic LLM findings.
- Provide a project-level continuity / regression report.
- Preserve the evidence needed to reproduce a finding.

### First UX

- Project dashboard.
- Canon browser.
- Source/content import flow.
- Continuity report.
- Issue detail with evidence.
- Human review / approval flow.

## Post-MVP — canon graph and change impact

- Canonical entity graph.
- Dependencies between assertions and content.
- `What breaks if I change this?` impact analysis.
- Timeline consistency checks.
- Character state / knowledge checks.
- Stale-content detection.
- Change requests and approval workflow.
- Full provenance and audit history.
- Canon health metrics.

## Team SaaS

- Multi-user projects.
- Roles and permissions.
- Review queues.
- Issue assignment.
- Comments and decisions.
- Notifications.
- Project usage and QA metrics.
- Team-level audit history.

## Integrations

Prioritize integrations only after the core workflow is validated with target customers. The product should integrate with existing systems rather than require migration.

Potential integrations:

- Markdown / JSON / CSV import and export.
- Git-based narrative repositories.
- Articy or equivalent narrative data exports.
- Game dialogue / quest data.
- Wiki / documentation sources.
- API and webhooks.
- CI continuity checks.
- Issue trackers / team notifications.

## Assisted resolution

AI authoring remains a supporting capability:

- suggest minimal edits to resolve contradictions;
- generate alternative resolutions;
- summarize proposed changes and trade-offs;
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

These become implementation components of the broader canon and QA workflow.

## Explicitly out of scope for now

- Generic AI novel / chapter generation as the primary product.
- Full authoring-suite feature parity with established writing assistants.
- Replacing Articy, Twine, Ink, Yarn, Notion, or other production tools.
- Full worldbuilding database parity with established products.
- Broad enterprise knowledge management.
- Transmedia production management.
- Multi-region production infrastructure before commercial validation.
- Long-term vector-memory orchestration unless a measured retrieval problem requires it.

## Product validation is part of scope

Before major engineering expansion:

- interview at least 10 target teams;
- onboard at least 3 design partners using real content;
- obtain at least 1 paid pilot or equivalent buying signal;
- measure time spent finding and resolving narrative regressions before and after the product;
- verify that integration with an existing workflow is possible without a full migration.
