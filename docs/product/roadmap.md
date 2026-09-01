# Product Roadmap

This roadmap is organized around **commercial validation first, product expansion second**. Dates are intentionally omitted until customer discovery establishes the pace of the work.

## North star

Build the smallest product that proves narrative teams will pay to maintain a trusted canon and detect continuity failures across evolving content.

## Phase 0 — Strategic validation

**Goal:** prove that the problem, ICP, and buying motion are real before expanding the platform.

- [ ] Interview at least 10 small game studios / narrative teams.
- [ ] Map their current canon workflow: wiki, docs, spreadsheets, DCC tools, writing tools, etc.
- [ ] Identify the highest-cost continuity failures.
- [ ] Recruit at least 3 teams to test with real project material.
- [ ] Secure at least 1 paid pilot or equivalent strong buying signal.
- [ ] Measure baseline time spent finding and resolving continuity issues.

**Exit criterion:** teams describe continuity/change-impact as a recurring business problem, not merely a nice-to-have AI feature.

## Phase 1 — Continuity QA wedge

**Goal:** deliver one compelling workflow: **check new content against an existing canon**.

### Canon ingestion

- [ ] Import a small set of source documents.
- [ ] Extract characters, locations, events, relationships, facts, rules, and timeline assertions.
- [ ] Show extracted assertions with provenance and confidence.
- [ ] Allow a human to approve the initial canon.

### Continuity checking

- [ ] Submit a new chapter, dialogue file, quest, or narrative document.
- [ ] Detect contradictions against approved canon.
- [ ] Separate critical contradictions, warnings, and uncertain findings.
- [ ] Show the source assertions behind every finding.
- [ ] Avoid presenting uncertain LLM judgments as facts.

### First UX

- [ ] Project dashboard.
- [ ] Canon browser.
- [ ] Content upload / paste flow.
- [ ] Continuity report.
- [ ] Issue review and approval flow.

**Exit criterion:** a target team can import a project, check new content, understand the findings, and say the report saves meaningful time.

## Phase 2 — Canon graph and change impact

**Goal:** make the product valuable when the project changes.

- [ ] Introduce a canonical entity model.
- [ ] Model dependencies between facts, characters, relationships, events, locations, documents, and versions.
- [ ] Implement `What breaks if I change this?`.
- [ ] Show downstream affected content.
- [ ] Add timeline consistency checks.
- [ ] Add character knowledge/state checks.
- [ ] Track provenance for every canonical assertion.
- [ ] Add version history and approval audit trail.

**Exit criterion:** users can safely change a canonical fact and discover affected content before shipping the change.

## Phase 3 — Team workflow

**Goal:** turn the continuity engine into a recurring team SaaS.

- [ ] Multi-user projects.
- [ ] Roles and permissions.
- [ ] Review queues.
- [ ] Assign continuity issues.
- [ ] Comments and decisions on findings.
- [ ] Canon change requests.
- [ ] Activity / audit log.
- [ ] Notifications.
- [ ] Project-level usage and health metrics.

**Commercial milestone:** convert design partners into paid Team plans.

## Phase 4 — Integrations and studio workflow

**Goal:** meet narrative teams inside their existing workflow rather than asking them to replace it.

Potential integrations, prioritized by customer demand:

- [ ] Git-based narrative repositories.
- [ ] Markdown / JSON / CSV import and export.
- [ ] Game dialogue / quest data formats.
- [ ] Wiki / documentation connectors.
- [ ] API and webhooks.
- [ ] CI checks for narrative content where appropriate.

**Exit criterion:** a studio can run continuity checks as part of its normal content workflow.

## Phase 5 — Assisted resolution

**Goal:** use AI to resolve issues without making generation the core product.

- [ ] Suggest minimal edits that restore continuity.
- [ ] Generate alternative resolutions with explicit trade-offs.
- [ ] Re-run checks after proposed changes.
- [ ] Produce change summaries for reviewers.
- [ ] Preserve human approval before canonical updates.

The existing chapter-generation loop can be reused here as a bounded proposal → validation → review workflow.

## Phase 6 — Studio / enterprise readiness

**Only after product-market evidence.**

- [ ] SSO / SAML.
- [ ] Advanced access controls.
- [ ] API keys and service accounts.
- [ ] Data retention controls.
- [ ] Export / deletion controls.
- [ ] Security documentation.
- [ ] Usage controls and quotas.
- [ ] Dedicated or private deployment options where commercially justified.
- [ ] Enterprise support / SLA.

## Deferred / explicitly deprioritized

- [ ] Competing directly with generic AI novel-writing assistants.
- [ ] Building a full-featured AI authoring suite before continuity QA is validated.
- [ ] Large-scale vector-memory infrastructure before a concrete retrieval bottleneck exists.
- [ ] Broad enterprise knowledge management outside narrative/IP workflows.
- [ ] Large transmedia feature set before the core canon/change-impact engine has product-market evidence.

## Current technical assets to preserve

The existing architecture already contains useful foundations for the pivot:

- explicit application use cases;
- replaceable LLM providers;
- approval gates;
- chapter versions and review decisions;
- canonical summaries for continuity;
- bounded retries;
- persistence and history;
- a web studio with lore, character, outline, validation, and export concepts.

The roadmap should **extract and generalize these capabilities**, not rewrite them prematurely.

## Commercial validation loop

Every major phase should answer four questions:

1. **Pain:** does this remove a costly continuity problem?
2. **Frequency:** does the customer encounter the problem often enough to pay for an always-on product?
3. **Switching:** can the product fit the customer's existing workflow without requiring a full tool migration?
4. **Willingness to pay:** does the customer pay for the outcome rather than for AI generation tokens?

If a phase cannot produce evidence for these questions, stop and revisit the ICP or problem before adding more features.
