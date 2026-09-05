# Product Roadmap

This roadmap keeps the **agentic book loop** as the first product and treats broader documentation / company knowledge QA as a deliberate expansion of the same underlying engine.

## North star

Build an AI agentic workflow that can repeatedly **review → propose → validate → approve → update canonical state**, first for books and later for other high-value documentation.

The strategic asset is not a generic writing assistant. It is the reusable engine that understands a long-lived corpus, its claims and dependencies, and the effect of changes on that corpus.

## Current implementation status — September 2026

This roadmap mixes **product validation** with **technical implementation**. A technical capability being implemented does not mean the product exit criterion has been validated with users.

Implemented foundations include:

- structured book/outline/chapter domain model and explicit approval gates;
- bounded Writer → validation → Reviewer → Corrector → Summarizer chapter loop;
- deterministic chapter linting and linguistic validation before LLM review;
- immutable chapter versions and persisted reviews;
- evidence-backed Canon assertions, conflicts, review decisions and canonical facts;
- durable chapter workflow runs in SQLite with step checkpoints;
- idempotent chapter execution by `(book_id, chapter_number, idempotency_key)`;
- restart recovery that reuses a chapter version already persisted before a process crash;
- provider abstraction with Gemini as the current implementation;
- deterministic/fake-based backend test strategy.

Still requiring product evidence: author trust, repeated multi-chapter use, measurable time saved versus a generic LLM, false-positive acceptance thresholds, and willingness to pay.

Known technical follow-ups before stronger production concurrency guarantees:

- close the crash window between review persistence and workflow checkpoint persistence;
- add persistent cross-process run claiming/leases before horizontally concurrent workers;
- expose an explicit API-level idempotency key if request-level idempotency is required by external clients;
- keep frontend/backend integration and frontend CI aligned with the evolving Studio implementation.

## LLM strategy

The LLM layer is an enabling capability, not the product moat. Model quality and pricing will continue to converge and change, so Book must preserve provider replaceability and avoid business logic tied to one vendor.

### Competitive position

Current major options have different strengths:

- **Gemini:** strong cost/context economics and a good default for high-volume Book workflows.
- **OpenAI:** strong general reasoning, tool use and agentic workflows; useful as a premium or fallback provider.
- **Anthropic Claude:** strong long-form reasoning and writing quality; useful for premium writing/review tasks when quality justifies cost.
- **Mistral:** attractive European/open-weight option for cost, sovereignty and future private deployment scenarios.
- **Open-weight models generally:** potentially valuable later for controlled enterprise inference, but not an MVP priority because infrastructure and evaluation costs can dominate.

The product should therefore compete **above the model layer**. A better model can improve a proposal; it does not replace the Canon, provenance, evidence, approval history or regression logic.

### Architecture rule

Keep a provider abstraction such as:

```text
LLMProvider
├── GeminiProvider
├── OpenAIProvider
├── AnthropicProvider
└── MistralProvider
```

Business workflows should depend on capabilities/tasks rather than vendor-specific APIs.

### Model routing strategy

Do not use the most expensive model for every operation. The target architecture is quality × cost × latency optimization. Routing should only become a real product/infrastructure layer after benchmarks show that different models materially improve economics or quality.

### LLM roadmap

- [ ] Keep Gemini as the initial default provider.
- [ ] Measure token cost, latency, retry rate and task quality by workflow.
- [x] Maintain provider isolation in application/domain code.
- [ ] Build a reproducible Book benchmark set before adding several providers.
- [ ] Compare Gemini, OpenAI, Anthropic and Mistral on representative Book tasks.
- [ ] Add additional providers only where benchmarks demonstrate value.
- [ ] Introduce task-level model routing when economics or quality justify it.
- [ ] Consider open-weight/private inference for enterprise requirements only after commercial evidence.

**Strategic rule:** LLMs generate proposals; the Canon determines what is accepted as canonical knowledge through evidence and human approval.

## Phase 0 — Book product validation

**Goal:** prove that the agentic loop is genuinely useful for real book creation/revision.

- [ ] Validate author intent capture and project constraints.
- [ ] Validate outline → draft workflow.
- [ ] Validate AI review / critique.
- [ ] Validate continuity checks against canonical state.
- [ ] Validate explicit human approval gates.
- [ ] Validate canonical summaries / state updates after approval.
- [ ] Observe repeated use across multiple chapters and revisions.
- [ ] Measure where the loop saves time versus a generic LLM workflow.

**Exit criterion:** real users repeatedly use the loop and trust its reviews/canonical state enough to continue a project through multiple iterations.

## Phase 1 — Excellent agentic book loop

**Goal:** make the first product compelling without turning it into a generic writing suite.

### Agentic workflow

- [x] Intent / creative brief capture.
- [x] Context and research ingestion where useful.
- [x] Outline proposal and approval.
- [x] Chapter drafting as bounded agent proposals.
- [x] AI review with structured findings.
- [x] Continuity / quality validation foundations.
- [x] Revision proposals.
- [ ] Human approval of generated chapter revisions as a complete UX flow.
- [x] Canonical state update foundations.
- [ ] Repeatable next-chapter / revision loop validated through the full product UI.

### Book intelligence

- [ ] Characters.
- [ ] Lore / world rules.
- [ ] Relationships.
- [ ] Timeline and events.
- [x] Chapter versions.
- [x] Provenance and review history.
- [x] Canonical summaries.
- [x] Deterministic validation where possible.

**Exit criterion:** the product's main advantage over a generic LLM is the persistent, agentic, review-driven loop and its ability to maintain book coherence.

## Phase 2 — Generalize the underlying knowledge model

**Goal:** extract reusable primitives without prematurely changing the book UX.

- [ ] Define a domain-neutral entity model.
- [x] Define canonical claims / facts.
- [ ] Model relationships and dependencies.
- [ ] Model events and temporal assertions.
- [ ] Model rules / constraints.
- [x] Attach provenance and confidence to claims.
- [x] Track versions and approval decisions.
- [x] Link claims to source content.
- [ ] Separate domain-specific presentation from the underlying engine.

The current Canon implementation is deliberately book-focused. Generalization is still a future phase.

**Exit criterion:** book continuity logic can be expressed using the generalized model without degrading the book product.

## Phase 3 — Change impact / regression engine

**Goal:** make the engine answer the consequences of change.

- [ ] `What breaks if I change this?`.
- [ ] Find content affected by a changed claim.
- [ ] Detect stale assertions.
- [x] Detect contradictory assertions.
- [ ] Track dependency chains.
- [ ] Add temporal consistency checks.
- [ ] Add entity state / knowledge checks.
- [ ] Produce evidence-backed regression reports.
- [ ] Re-run analysis after proposed fixes.

For books, this is narrative continuity. The same mechanism will later power documentation regression testing.

## Phase 4 — Documentation QA design partners

**Goal:** test whether the book-derived engine solves a valuable problem outside fiction.

Initial ICP hypothesis: software / B2B SaaS companies with substantial, frequently changing documentation and multiple contributors.

- [ ] Interview at least 10 documentation-heavy teams.
- [ ] Map current sources: Git, Notion, Confluence, docs, wiki, support, etc.
- [ ] Identify costly documentation regressions.
- [ ] Identify existing review / release gates.
- [ ] Recruit at least 3 design partners.
- [ ] Run the engine on real corpora.
- [ ] Obtain at least 1 paid pilot or equivalent strong buying signal.
- [ ] Measure time saved / regressions avoided.

**Critical falsification question:**

> Do documentation inconsistencies cost enough, happen often enough, and occur early enough that companies will pay for automated knowledge regression testing?

If not, stop expansion and revisit the ICP/problem.

## Phase 5 — Documentation regression MVP

**Goal:** productize the generalized loop for company documentation.

```text
Source documents
      ↓
Claim extraction
      ↓
Canonical knowledge
      ↓
New / changed content
      ↓
Regression analysis
      ↓
Findings + evidence
      ↓
Human review
      ↓
Approved knowledge
```

- [ ] Documentation corpus ingestion.
- [ ] Claim extraction and provenance.
- [ ] Canonical knowledge approval.
- [ ] New-content checks.
- [ ] Contradiction detection.
- [ ] Stale-content detection.
- [ ] Evidence-backed findings.
- [ ] Human approval.
- [ ] Knowledge health / regression report.

## Phase 6 — Integrate with existing company workflow

**Goal:** become a QA layer rather than another documentation editor.

Prioritize based on design-partner demand:

- [ ] Git / GitHub repositories.
- [ ] Markdown / JSON / CSV.
- [ ] Notion / Confluence.
- [ ] Google Docs and similar document sources.
- [ ] Help center / support content.
- [ ] API and webhooks.
- [ ] CI checks for documentation changes.
- [ ] Slack / issue tracker notifications.

**Principle:** do not require migration from the customer's existing source of truth.

## Phase 7 — General knowledge QA SaaS

**Goal:** turn the engine into a recurring B2B product.

- [ ] Multi-user workspaces.
- [ ] Roles and permissions.
- [ ] Review queues.
- [ ] Issue assignment.
- [ ] Comments and decisions.
- [ ] Audit logs.
- [ ] Knowledge-health metrics.
- [ ] Scheduled / event-driven checks.
- [ ] Usage controls and quotas.
- [ ] Team / workspace billing.

Potential positioning:

> **Documentation QA: test knowledge changes before they become company-wide misinformation.**

## Phase 8 — Agentic resolution

**Goal:** generalize the book-writing agent loop into a documentation repair loop.

```text
Regression
   ↓
Agent investigation
   ↓
Proposed fix
   ↓
Validation
   ↓
Human approval
   ↓
Updated content / knowledge
```

- [ ] Suggest minimal documentation edits.
- [ ] Generate alternative resolutions.
- [ ] Explain trade-offs.
- [ ] Propose updates to affected documents.
- [ ] Re-run regression checks.
- [ ] Summarize approved changes.

The book product remains the reference implementation for this agentic pattern.

## Phase 9 — Enterprise / knowledge infrastructure

Only after repeated commercial evidence:

- [ ] SSO / SAML.
- [ ] Advanced access controls.
- [ ] Security / compliance documentation.
- [ ] Retention and deletion controls.
- [ ] API / service accounts.
- [ ] Private deployment where justified.
- [ ] SLA / enterprise support.
- [ ] Knowledge QA API.

The long-term hypothesis is that the engine can become a **knowledge consistency layer** consumed by multiple applications, not merely a standalone documentation UI.

## Deferred / explicitly deprioritized

- [ ] Competing directly with generic AI writing assistants.
- [ ] Replacing Notion, Confluence, Articy, or other systems of record.
- [ ] Building a full enterprise knowledge-management suite before QA value is proven.
- [ ] Broad game-specific expansion unrelated to the core loop.
- [ ] Large-scale vector-memory infrastructure before a measured retrieval bottleneck exists.
- [ ] Enterprise infrastructure before product-market evidence.

## Existing technical assets to preserve

The current project already contains foundations that map naturally to this roadmap:

- explicit application use cases;
- replaceable LLM providers;
- approval gates;
- chapter versions and review decisions;
- canonical summaries for continuity;
- bounded retries;
- persistence and history;
- lore / character / outline workflows;
- validation and linting;
- durable workflow checkpoints and idempotency.

The strategy is to **prove the loop first, extract the reusable knowledge primitives second, and only then expand the market**.

## Decision gates

Every expansion must answer:

1. **Value:** does the loop solve a painful problem?
2. **Trust:** do users trust the canonical state and evidence?
3. **Frequency:** does the workflow recur often enough to support SaaS retention?
4. **Integration:** can it fit the existing source-of-truth workflow?
5. **Willingness to pay:** does the outcome justify payment independently of token consumption?
6. **LLM economics:** does the selected model/routing deliver acceptable quality, latency and gross margin?

If a gate fails, revisit the problem/ICP before adding platform complexity.
