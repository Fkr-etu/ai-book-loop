# Product Roadmap

This roadmap is organized around **commercial validation first, product expansion second**. Dates are intentionally omitted until customer discovery establishes the pace of the work.

## North star

Build the smallest product that proves narrative teams will pay to **catch expensive content regressions before they reach QA, localization, recording, implementation, or release**.

## Phase 0 — Strategic validation

**Goal:** prove that the problem, ICP, and buying motion are real before expanding the platform.

- [ ] Interview at least 10 small-to-mid-sized narrative game teams.
- [ ] Map where canonical content lives today: Articy, Git, Notion, docs, spreadsheets, custom databases, etc.
- [ ] Identify the most expensive and frequent narrative regressions.
- [ ] Identify when those regressions are discovered: writing review, implementation, QA, localization, voice, or post-release.
- [ ] Quantify current cost in people-hours, delays, rework, or release risk.
- [ ] Recruit at least 3 teams to test with real project material.
- [ ] Secure at least 1 paid pilot or equivalent strong buying signal.
- [ ] Establish baseline time spent finding and resolving continuity issues.

**Critical falsification question:** do teams encounter narrative inconsistencies often and expensively enough to pay €100–1,500/month for prevention/QA?

**Exit criterion:** continuity/content regression is demonstrated as a recurring operational cost, not merely a nice-to-have AI feature.

## Phase 1 — Narrative QA wedge

**Goal:** deliver one compelling workflow:

> **Check new or edited content against an existing canon.**

### Canon ingestion

- [ ] Import a small set of existing source documents.
- [ ] Extract characters, locations, events, relationships, facts, rules, and timeline assertions.
- [ ] Show extracted assertions with provenance and confidence.
- [ ] Allow a human to approve the initial canon.

### Continuity / regression checking

- [ ] Submit a new chapter, dialogue file, quest, or narrative document.
- [ ] Detect contradictions against approved canon.
- [ ] Detect stale references where possible.
- [ ] Separate critical contradictions, warnings, structural risks, and uncertain findings.
- [ ] Show the source assertions behind every finding.
- [ ] Preserve evidence needed to reproduce a finding.
- [ ] Avoid presenting uncertain LLM judgments as facts.

### First UX

- [ ] Project dashboard.
- [ ] Canon browser.
- [ ] Source/content upload or paste flow.
- [ ] Continuity report.
- [ ] Finding detail with evidence.
- [ ] Human review / approval flow.

**Exit criterion:** a target team can import an existing project, check new content, understand the findings, and demonstrate meaningful time saved.

## Phase 2 — Canon graph and change impact

**Goal:** make the product valuable when the project changes.

- [ ] Introduce a canonical entity model.
- [ ] Model dependencies between facts, characters, relationships, events, locations, documents, and versions.
- [ ] Implement **`What breaks if I change this?`**.
- [ ] Show downstream affected content.
- [ ] Add timeline consistency checks.
- [ ] Add character knowledge/state checks.
- [ ] Track provenance for every canonical assertion.
- [ ] Add version history and approval audit trail.
- [ ] Add canonical health / regression metrics.

**Exit criterion:** users can safely change a canonical fact and discover affected content before shipping the change.

## Phase 3 — Team workflow

**Goal:** turn the QA engine into a recurring team SaaS.

- [ ] Multi-user projects.
- [ ] Roles and permissions.
- [ ] Review queues.
- [ ] Assign continuity issues.
- [ ] Comments and decisions on findings.
- [ ] Canon change requests.
- [ ] Activity / audit log.
- [ ] Notifications.
- [ ] Project-level usage and QA health metrics.

**Commercial milestone:** convert design partners into paid Team plans.

## Phase 4 — Workflow integrations

**Goal:** become the QA layer above the customer's existing narrative stack rather than asking them to replace it.

Prioritize based on design-partner demand:

- [ ] Markdown / JSON / CSV import and export.
- [ ] Git-based narrative repositories.
- [ ] Articy or equivalent narrative-data import.
- [ ] Game dialogue / quest data formats.
- [ ] Wiki / documentation connectors.
- [ ] API and webhooks.
- [ ] CI continuity checks.
- [ ] Issue tracker / Slack-style notifications.

**Exit criterion:** a studio can run narrative QA as part of its normal content workflow with minimal migration effort.

## Phase 5 — Assisted resolution

**Goal:** use AI to resolve issues without making generation the core product.

- [ ] Suggest minimal edits that restore continuity.
- [ ] Generate alternative resolutions with explicit trade-offs.
- [ ] Re-run checks after proposed changes.
- [ ] Produce change summaries for reviewers.
- [ ] Preserve human approval before canonical updates.

The existing chapter-generation loop can be reused here as a bounded proposal → validation → review workflow.

## Phase 6 — Narrative regression platform

**Only after repeated evidence from paid customers.**

- [ ] CI/build gating for narrative checks.
- [ ] Regression baselines across releases.
- [ ] Compare canon/content changes between versions.
- [ ] Coverage metrics for characters, quests, timelines, and dependencies.
- [ ] Automated alerts on newly introduced regressions.
- [ ] API-first checks for custom production pipelines.

**Strategic outcome:** evolve from a document checker into a narrative regression-testing layer.

## Phase 7 — Studio / enterprise readiness

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
- [ ] Building a full-featured AI authoring suite before narrative QA is validated.
- [ ] Becoming another worldbuilding / lore database.
- [ ] Replacing Articy, Twine, Ink, Yarn, Notion, or other narrative production tools.
- [ ] Large-scale vector-memory infrastructure before a concrete retrieval bottleneck exists.
- [ ] Broad enterprise knowledge management outside narrative/IP workflows.
- [ ] Large transmedia feature set before the core QA/change-impact engine has product-market evidence.

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

Every major phase should answer five questions:

1. **Pain:** does this remove a costly narrative regression?
2. **Frequency:** does the customer encounter the problem often enough to pay for an always-on product?
3. **Timing:** does catching it earlier save meaningful downstream cost?
4. **Switching:** can the product fit the customer's existing workflow without requiring a full tool migration?
5. **Willingness to pay:** does the customer pay for reduced risk / QA effort rather than AI generation tokens?

If a phase cannot produce evidence for these questions, stop and revisit the ICP or problem before adding more features.
