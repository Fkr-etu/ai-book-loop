# Infrastructure and unit economics

This document estimates the cost of running Book Loop in the **current target architecture** and connects infrastructure cost to the proposed SaaS pricing.

The goal is simple: **price the product so normal customers are profitable, while putting hard capacity controls around unusually expensive AI workloads.**

These are planning estimates, not billing guarantees. Recalculate them before launch and after real usage data is available.

## Current production architecture

Book Loop is now designed as a 100% GCP production stack:

```text
GitHub
  ↓
Cloud Build
  ↓
Artifact Registry
  ↓
Cloud Run frontend (Next.js)
Cloud Run backend (FastAPI)
Cloud Run Job migrations
  ↓
Cloud SQL PostgreSQL

Secret Manager
Cloud Logging / Monitoring

Backend → Gemini API
```

The production region is `europe-west9` (Paris). The repository documentation confirms Cloud Run, Cloud SQL PostgreSQL, Artifact Registry and Secret Manager as the production components. fileciteturn59file1L22-L46

There is no Vercel, Supabase or permanently provisioned application server in the target architecture.

## Current vendor pricing anchors

### Gemini

For `gemini-2.5-flash`, current standard paid pricing is:

- **$0.30 / 1M input tokens**;
- **$2.50 / 1M output tokens**, including thinking tokens;
- cached input: **$0.03 / 1M tokens**.

For `gemini-2.5-flash-lite`:

- **$0.10 / 1M input tokens**;
- **$0.40 / 1M output tokens**.

Source: Google Gemini API pricing. citeturn0search3

This makes output tokens substantially more expensive than input tokens. We should therefore control output length, retries and unnecessary correction loops before optimizing database costs.

### Cloud Run

Cloud Run is pay-per-use and has a monthly free tier. For Tier 1 regions including Paris, the current services pricing is approximately:

- $0.000018 / vCPU-second;
- $0.000002 / GiB-second;
- request-based billing: $0.40 / million requests.

The first monthly free tier includes 240,000 vCPU-seconds and 450,000 GiB-seconds for instance-based services; request-based services have their own free allowance. citeturn2view0

For an early Book Loop deployment with low traffic and scale-to-zero enabled, **Cloud Run should remain a small part of COGS**.

### Cloud SQL PostgreSQL

Cloud SQL is the first meaningful fixed infrastructure cost because the database runs continuously.

Current Cloud SQL pricing exposes dedicated CPU/memory pricing and also offers very small shared-core instances. `db-f1-micro` is currently around **$0.0105/hour (~$7.70/month)** before storage/backups, but Google explicitly positions shared-core `db-f1-micro` / `db-g1-small` as test/development machines without an SLA. They should therefore not be treated as the long-term production baseline. citeturn1search6turn1search5

For a real production baseline, a small dedicated instance should be budgeted instead. At the current Paris Enterprise rates of roughly $0.0413/vCPU-hour and $0.007/GiB-hour, a 1 vCPU / 2 GiB instance is approximately:

```text
CPU:    1 × $0.0413 × 730 h ≈ $30.15/month
Memory: 2 × $0.007  × 730 h ≈ $10.22/month
--------------------------------------------
Compute:                    ≈ $40.37/month
```

Storage, backups and networking are additional. Current SSD storage pricing is about $0.000465753/GiB-hour, or roughly $0.34/GiB-month. citeturn1search3

Therefore a sensible early-production Cloud SQL envelope is **~$45–60/month**, depending on storage and backup configuration. This is deliberately more conservative than assuming a shared-core development instance.

### Artifact Registry and Secret Manager

Artifact Registry has a small free storage allowance and then charges for stored artifact volume; co-locating it with Cloud Run avoids unnecessary cross-region transfer. citeturn0search0

Secret Manager provides free monthly allowances for six active secret versions and 10,000 access operations. For Book Loop's small secret set, its direct cost should be effectively negligible at early scale. citeturn0search2

## Early production fixed-cost envelope

For the current GCP-only architecture, before Gemini usage:

| Component | Early monthly planning cost |
|---|---:|
| Cloud SQL PostgreSQL | **$45–60** |
| Cloud Run frontend + backend + jobs | **$0–15** |
| Artifact Registry | **$0–2** |
| Secret Manager | **~$0** |
| Logging / Monitoring / network buffer | **$5–20** |
| **Total** | **~$50–95/month** |

This is the number that matters for the first commercial deployment. It is substantially more useful than the old generic `$20–100` estimate because it reflects the actual GCP architecture and a production-grade PostgreSQL baseline.

A reasonable planning target is therefore **~$75/month fixed infrastructure** before AI usage.

## Gemini unit cost per Book Loop workflow

The previous document used one hypothetical chapter at 100k input + 20k output tokens. That remains a useful baseline, but we should now model a range because the workflow contains multiple agents and may retry.

### Baseline workflow

Assume one completed chapter workflow consumes:

- 100k input tokens;
- 20k output tokens;
- Gemini 2.5 Flash.

Then:

```text
100k input  × $0.30/M = $0.030
20k output  × $2.50/M = $0.050
--------------------------------
AI cost                 = $0.080 / chapter
```

### Conservative workflow

Assume 250k input + 50k output:

```text
250k × $0.30/M = $0.075
 50k × $2.50/M = $0.125
-------------------------
AI cost         = $0.200 / chapter
```

### Cost-control envelope

For pricing decisions, I recommend budgeting **$0.50 per completed chapter-equivalent workflow** even when the nominal Gemini estimate is lower. This 2.5× buffer is intended to absorb retries, larger contexts, correction loops, failed generations and other workflow overhead.

It is a **commercial safety envelope**, not an assertion that Gemini will actually cost $0.50 per chapter.

## What this means for our pricing

The current pricing hypothesis is:

| Plan | Monthly | Annual | Commercial role |
|---|---:|---:|---|
| Free | €0 | — | Product discovery |
| Creator | **€19** | **€190** | Serious individual creator |
| Pro | **€39** | **€390** | Intensive creator / multiple projects |
| Studio | **€79** | **€790** | Collaboration / advanced usage |

The objective is not unlimited AI. The objective is a predictable amount of narrative work per month with enough headroom for Book Loop's workflow.

## Gross-margin safety model

For planning, target direct COGS below **25% of subscription revenue** for paid plans before general company expenses such as salaries, marketing, accounting and support.

Using the conservative **$0.50 per chapter-equivalent** envelope:

| Plan | Revenue | 25% COGS ceiling | Approx. chapter-equivalents before hitting ceiling* |
|---|---:|---:|---:|
| Creator | €19 | €4.75 | ~9 |
| Pro | €39 | €9.75 | ~19 |
| Studio | €79 | €19.75 | ~39 |

*Approximate only; USD/EUR conversion, Stripe fees and shared infrastructure are not included in this simple table.

This demonstrates why **capacity must be an entitlement**, rather than unlimited generation.

At the nominal baseline of $0.08/chapter, the same plans have considerably more headroom. The conservative $0.50 envelope is intentionally used to prevent us from building a pricing model that only works under optimistic LLM usage.

## Stripe must be included in COGS

For a French Stripe account, current standard European cards are priced at **1.5% + €0.25 per successful transaction**. International cards can cost more. citeturn3search0

Approximate standard-card processing cost:

- €19 subscription → **~€0.54**
- €39 subscription → **~€0.84**
- €79 subscription → **~€1.44**

This makes the effective revenue after payment processing approximately:

- Creator: **€18.46**
- Pro: **€38.16**
- Studio: **€77.56**

Stripe Billing pricing for recurring charges should also be checked at implementation time; Checkout itself states that recurring charges are subject to Stripe Billing pricing. citeturn3search7

## Shared infrastructure allocation

The ~$75/month fixed GCP envelope is irrelevant to a single customer's unit economics once there are enough paying customers, but it matters at low scale.

Illustrative allocation:

| Paying customers | Fixed GCP cost/customer/month |
|---:|---:|
| 10 | ~$7.50 |
| 25 | ~$3.00 |
| 50 | ~$1.50 |
| 100 | ~$0.75 |
| 500 | ~$0.15 |

Therefore the immediate economic risk is **not Cloud Run or Cloud SQL**. It is allowing an individual customer to consume unbounded Gemini capacity.

## Practical conclusion for Book Loop

The economics are favorable if we enforce four rules:

1. **No unlimited AI generation.**
2. **Bound correction/review retries.**
3. **Use Flash by default and reserve more expensive models for explicitly valuable operations.**
4. **Track usage per completed workflow and enforce monthly plan capacity.**

The current GCP architecture is cheap enough that infrastructure should not drive pricing. Gemini usage and payment processing are the meaningful variable costs.

### Recommended commercial guardrail

Use the following internal planning assumptions until real production data replaces them:

```text
Fixed GCP baseline:          ~$75/month
Nominal Gemini workflow:     ~$0.08/chapter
Conservative AI envelope:    ~$0.50/chapter-equivalent
Target direct COGS:           ≤25% of subscription revenue
```

This supports the proposed **€19 / €39 / €79** pricing strategy, provided the plans have explicit capacity limits.

## What we should measure after launch

The first real unit-economics dashboard should answer only these questions:

- Gemini cost per completed chapter;
- Gemini cost per successful full workflow;
- retry/correction rate;
- average input/output tokens per workflow;
- monthly AI cost per paying customer;
- Stripe cost per paying customer;
- gross margin by plan.

The objective is to replace the conservative assumptions above with actual Book Loop workload data, then adjust quotas—not immediately adjust prices—when a workload becomes unexpectedly expensive.
