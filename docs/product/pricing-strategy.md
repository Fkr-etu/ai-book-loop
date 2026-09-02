# Product Pricing Strategy

## Purpose

This document defines a **starting pricing hypothesis** for Book. It is not a final price list. Pricing must be validated against real usage, retention, perceived value and LLM economics.

## Market reference

The current AI writing market already supports meaningful recurring subscriptions:

- Sudowrite: $10/month annual for Hobby & Student, $22/month annual for Professional, and $44/month annual for Max. The plans primarily differentiate by monthly AI credits. citeturn0search0turn0search1
- NovelAI: $10, $15 and $25/month tiers, with the higher tiers increasing capabilities/context. citeturn0search3turn0search7
- Novelcrafter positions itself as a broader novel-writing workspace with Codex, planning, review and access to multiple external AI providers; its site currently advertises plans starting at $4/month. citeturn1search0

The implication is that Book should not try to win by being the cheapest AI writing interface. The defensible value proposition is the **persistent agentic loop + continuity + review + canonical knowledge**, rather than raw generation volume.

## Pricing thesis

The user should pay for the **workflow and outcome**, not for the underlying tokens.

Do not expose provider token pricing as the primary commercial unit. LLMs are an infrastructure input that we can optimize through routing and provider selection.

The commercial metric should therefore be something understandable to an author:

- active projects / books;
- AI-assisted chapters or workflow runs;
- advanced review / continuity capacity;
- later, collaboration and publishing-oriented features.

## Recommended initial price architecture

### Free — €0

Purpose: acquisition and product discovery.

Suggested limits:

- 1 project;
- limited outline generation;
- limited chapter workflow runs per month;
- basic continuity/review demonstration;
- no expectation of producing a complete book for free.

The free tier should demonstrate the **loop**, not provide unlimited AI generation.

### Creator — €12/month

Target: hobbyists and authors testing an AI-assisted workflow.

Suggested envelope:

- several active projects;
- enough AI usage for meaningful weekly writing;
- outline + drafting + review + continuity;
- standard model routing;
- chapter/version history.

Annual target: approximately €120/year.

### Pro — €24/month

**Recommended primary plan.**

Target: authors seriously writing and revising a book or series.

Suggested envelope:

- higher AI workflow allowance;
- deeper context and continuity checks;
- more revision/review cycles;
- priority access to stronger models where justified;
- richer canonical state;
- export and project management capabilities.

Annual target: approximately €240/year.

### Power / Studio — €49/month, later

Do not launch this tier until usage patterns justify it.

Target:

- prolific authors;
- multiple books / series;
- very high workflow volume;
- advanced model routing;
- collaboration or professional workflow features.

This tier exists to capture high willingness-to-pay without forcing the core Pro plan to subsidize extreme usage.

## Why €24/month is the current anchor

The current competitive range for serious AI-assisted writing is broadly around $10–$60/month depending on usage and positioning. Sudowrite's Professional plan is $22/month on annual billing and $29/month monthly, while its Max plan reaches $44/$59. citeturn0search1

Book should therefore initially sit around **€24/month** rather than attempting either extreme:

- below €10 would communicate commodity / lightweight AI assistance;
- €40–60+ would be difficult to justify before Book has demonstrated a substantially superior workflow;
- ~€24 gives enough room for infrastructure and premium model usage while remaining inside the established author-software subscription range.

The price should be validated by willingness-to-pay interviews and, more importantly, paid conversion rather than competitor imitation.

## LLM economics and gross-margin guardrail

The current internal cost model uses Gemini 2.5 Flash as an example: 100k input tokens + 20k output tokens is approximately $0.08 for one generation pass under the documented pricing assumptions.

However, Book is not a single LLM call. A chapter may trigger:

```text
Writer
  ↓
Linter
  ↓
Reviewer
  ↓
Retry / revision
  ↓
Summary
  ↓
Canonical extraction
```

Therefore the commercial model must budget for a **workflow multiplier**, retries, context growth and premium-model routing.

For planning purposes, use three internal cost envelopes until production telemetry exists:

| Usage profile | Indicative LLM cost target / month | Commercial implication |
|---|---:|---|
| Light author | < €2 | €12 plan has large margin headroom |
| Regular author | €2–€8 | €24 plan is attractive |
| Heavy author | €8–€20+ | needs quotas/routing or higher tier |

These are planning envelopes, not measured production costs. Actual economics must come from telemetry.

### Guardrails

- Target at least ~70% gross margin on normal paid usage once infrastructure is mature.
- Do not promise unlimited premium-model usage at launch.
- Use quotas or credits internally even if the UX presents a simple workflow allowance.
- Route cheap deterministic/extraction tasks to inexpensive models where quality is sufficient.
- Reserve premium models for writing/review tasks where they create measurable user value.
- Monitor cost per active user, cost per book, cost per accepted chapter and retry rate.

## Recommended launch offer

For an early paid beta, simplify the public offer instead of launching four tiers immediately:

**Free** → experience the loop.

**Pro €19/month** → full Book workflow with a generous but bounded usage allowance.

Then move toward the mature structure:

**Creator €12 → Pro €24 → Power €49** once actual usage supports segmentation.

The €19 beta price is deliberately positioned as an early-adopter offer, not as the permanent anchor.

## What we should NOT sell yet

- raw token packages as the main product;
- unlimited premium model usage;
- per-word pricing;
- enterprise contracts for the Book MVP;
- complex credit systems before users understand the product;
- artificially cheap pricing intended to compete with generic LLM chat products.

## Validation plan

Pricing is validated only when users pay and continue using the product.

Track:

1. Free → paid conversion.
2. Trial → paid conversion.
3. Monthly retention / churn.
4. Chapters completed per paying user.
5. AI workflow runs per paying user.
6. LLM cost per paying user.
7. Gross margin per plan.
8. Percentage of users hitting usage limits.
9. Upgrade/downgrade behavior.
10. Qualitative willingness-to-pay feedback.

### Pricing decision gates

- If most users never approach limits, increase value/features before reducing price.
- If many users hit limits and retention is strong, add a higher tier rather than making the base plan unlimited.
- If users refuse €19 despite strong product engagement, investigate value proposition before immediately lowering price.
- If users happily pay €24–49 and ask for more capacity, pricing power exists.
- If LLM cost threatens margins, improve routing/prompt efficiency before redesigning the entire product around cost.

## Strategic conclusion

The initial hypothesis is:

> **Book Pro should eventually cost around €24/month, with a €19/month early-adopter beta and a €12/month entry tier.**

This is deliberately above commodity AI-chat pricing and below the most expensive author-focused AI subscriptions. The justification is not access to a particular LLM; it is the persistent **agentic writing → review → continuity → approval → canonical state** workflow.

As the Canon and regression engine become more valuable, pricing should increasingly reflect **knowledge integrity and workflow outcomes**, not tokens or raw text generation volume.
