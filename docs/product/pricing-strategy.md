# Product Pricing Strategy

## Purpose

This document defines the **pricing hypothesis** for Book Loop. It is not a final public price list.

Pricing must follow the product positioning: customers pay for a reliable workflow that protects narrative coherence, not for access to a particular LLM or raw token volume.

The commercial positioning is defined in [`positioning.md`](positioning.md).

## Commercial thesis

Book Loop is a **creator SaaS** for people who build long-lived narrative universes.

The first wedge is authors. Adjacent validation targets are screenwriters and Game Masters. The common value is:

> **Keep your universe coherent, even as it grows and changes.**

The user is buying continuity protection and a trusted creation/review workflow.

### What the customer is not buying

- raw tokens;
- a particular LLM vendor;
- a generic chatbot;
- unlimited one-click book generation;
- a static story bible or wiki.

LLM usage is an internal cost driver and should remain bounded internally, but it should not become the primary customer-facing abstraction.

## Market reference

The current market spans several categories:

### AI writing assistants

- **Sudowrite**: recurring plans differentiated heavily by AI usage/credits.
- **NovelAI**: subscription tiers around writing generation and context/capability.
- **Novelcrafter**: a broader novel-writing workspace with Codex, planning, review and multiple external AI providers.
- **Squibler**: aggressive positioning around AI-assisted long-form/book generation.

These products establish that creators will pay recurring subscriptions for AI-assisted writing. They also mean that Book Loop cannot differentiate simply through "AI writing", project memory, a story bible or access to several models.

### Worldbuilding / RPG tools

- **World Anvil** and **Kanka** demonstrate willingness to pay for structured worldbuilding and campaign management.
- **Campfire** demonstrates demand for structured worldbuilding features for writers.

These tools are primarily strong at storing and organizing a world. Book Loop should differentiate by checking how new content and changes affect the trusted Canon.

### Screenwriting tools

Professional screenplay tools such as **Arc Studio** already cover authoring, formatting, collaboration and revision workflows.

Book Loop should complement these tools before attempting to replace them. The differentiation is continuity and change review.

## Pricing principles

1. **Price the outcome, not the model.**
2. **Keep the public model understandable.**
3. **Use internal quotas even if the UX feels simple.**
4. **Do not promise unlimited premium-model inference.**
5. **Do not launch a complex credit economy before users understand the product.**
6. **Do not price above established creator software without evidence of superior value.**
7. **Do not compete by being the cheapest AI writer.**
8. **Validate pricing through paid usage and retention, not competitor imitation.**

## Working launch hypothesis

Keep the initial offer deliberately simple.

### Free — €0

Purpose: let a creator experience the core loop and understand the Canon concept.

Possible envelope:

- 1 active project;
- bounded outline generation;
- bounded chapter/workflow runs;
- continuity/review demonstration;
- no expectation of generating a complete book for free.

The free tier must demonstrate the **loop**, not merely provide a crippled editor.

### Pro — approximately €19/month during paid beta

This is the preferred early commercial experiment.

Target: an author actively producing or revising a book or series.

Possible envelope:

- full Book Loop workflow;
- meaningful but bounded workflow allowance;
- Canon and continuity checks;
- version and review history;
- enough capacity for genuine recurring use;
- stronger model routing where it materially improves quality.

The €19 price is an **early-adopter experiment**, not a permanent promise.

### Mature Creator tier — approximately €12/month

If validation shows a meaningful lower-intensity audience, introduce a lighter tier.

Target: hobbyists and creators using AI regularly but at lower workflow volume.

This tier should not exist merely to add a cheaper card. It needs a clear usage/value boundary that users understand.

### Mature Pro tier — approximately €24/month

If the €19 beta demonstrates willingness to pay and healthy usage, move toward approximately €24/month for the main serious-creator plan.

The justification is the workflow and continuity value, not model access.

### Power / Studio — approximately €49/month, later

Do not launch this tier until real usage demonstrates demand for it.

Potential target:

- prolific authors;
- multiple books or series;
- very high workflow volume;
- professional creator workflows;
- future collaboration capabilities.

A higher tier should capture heavy usage without forcing the core plan to subsidize extreme inference consumption.

## Do not publish a final price list yet

The current website pricing should **not be treated as authoritative**. In particular, previously displayed €24 / €59 / €179 plans and the registration page's €29 Pro offer are historical UI hypotheses, not validated commercial decisions.

Do not advertise a 14-day free trial until the product actually implements the corresponding trial and billing lifecycle.

Do not describe unavailable features such as multi-user billing, dedicated model infrastructure or enterprise support as included paid-plan functionality while those capabilities remain outside the MVP.

## Unit economics

LLM inference is a cost input, not the customer value metric.

A single chapter workflow can involve:

```text
Writer
  ↓
Validation
  ↓
Reviewer
  ↓
Correction / retry
  ↓
Summary
  ↓
Canonical extraction
```

Internal planning must account for:

- workflow multiplication;
- retries;
- context growth over a project;
- provider/model mix;
- infrastructure;
- storage;
- extreme usage.

The existing planning assumption of roughly $0.06 per completed chapter workflow is illustrative only and must not be treated as production economics. It should be replaced by measured data when real usage exists.

### Internal commercial guardrails

- target healthy gross margin on normal paid usage;
- keep premium-model usage bounded;
- route deterministic/low-value work to inexpensive models where quality permits;
- reserve stronger models for tasks where they create measurable value;
- monitor cost per active creator and cost per completed workflow;
- use limits to protect against extreme usage without making the public pricing model feel like an API bill.

## Natural commercial units to test

Do not assume words are the best unit.

Test user comprehension and willingness to pay around:

1. **Active project** — one book, series or campaign in production.
2. **Workflow capacity** — number of meaningful creation/review cycles.
3. **Continuity capacity** — depth/frequency of Canon and review analysis.
4. **Professional capabilities** — collaboration and advanced workflows later.

The right abstraction may differ between authors, screenwriters and GMs, so the product should first validate whether a common creator plan is understandable.

## Pricing validation plan

Pricing should be validated after the core promise is clear.

### Qualitative

Ask creators:

- What is the cost of an inconsistency today?
- How much time do you spend checking continuity manually?
- What do you currently use: ChatGPT, Claude, Novelcrafter, Sudowrite, World Anvil, Kanka, Campfire, spreadsheets, notes?
- What would make you trust an automated Canon?
- Would you pay for a system that catches a contradiction before it enters the next chapter/session?
- Which pricing unit feels natural: project, workflow capacity, words, or something else?

### Quantitative

Once real product usage exists, validate:

1. free → paid conversion;
2. trial → paid conversion if a real trial exists;
3. monthly retention / churn;
4. completed workflows per paying creator;
5. percentage hitting usage limits;
6. LLM cost per paying creator;
7. gross margin;
8. upgrade/downgrade behavior;
9. repeated use across chapters, revisions or sessions;
10. willingness to pay at €12 / €19 / €24 / €49.

## Decision gates

### Gate 1 — value

Creators must clearly understand that Book Loop protects narrative coherence.

### Gate 2 — repeated use

Users must return for multiple chapters, revisions or campaign sessions.

### Gate 3 — differentiation

Users should identify a meaningful advantage over a generic LLM plus their existing notes/tools.

### Gate 4 — willingness to pay

Real creators must pay or show strong purchase intent at the tested price.

### Gate 5 — economics

Actual usage must support healthy margins after LLM and infrastructure costs.

Only after these gates should the pricing ladder become fixed.

## Strategic conclusion

The current commercial hypothesis is intentionally simple:

> **Free to understand the loop; approximately €19/month to use it seriously during the paid beta; move toward approximately €24/month for the mature core plan if the evidence supports it.**

A €12 entry tier and €49 high-capacity tier are segmentation hypotheses, not launch requirements.

The long-term pricing power should come from **trusted narrative consistency and workflow outcomes**, not from the number of tokens Book Loop can generate.
