# Infrastructure and unit economics

This document estimates the cost of running Book Loop in the **current target architecture** and connects infrastructure cost to the proposed SaaS pricing.

The goal is simple: **price the product so normal customers are profitable, while putting hard capacity controls around unusually expensive AI workloads.**

These are planning estimates, not billing guarantees. Recalculate them before launch and after real usage data is available.

## Current production architecture

Book Loop is designed as a 100% GCP production stack:

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

The repository architecture document currently specifies `europe-west1` as the reference region and a deliberately small Cloud SQL starting point. There is no Vercel, Supabase or permanently provisioned application server in the target architecture.

## Current vendor pricing anchors

### Gemini

For `gemini-2.5-flash`, current standard paid pricing is:

- **$0.30 / 1M input tokens**;
- **$2.50 / 1M output tokens**, including thinking tokens;
- cached input: **$0.03 / 1M tokens**.

For `gemini-2.5-flash-lite`:

- **$0.10 / 1M input tokens**;
- **$0.40 / 1M output tokens**.

Source: Google Gemini API pricing.

This makes output tokens substantially more expensive than input tokens. We should therefore control output length, retries and unnecessary correction loops before optimizing database costs.

### Cloud Run

Cloud Run is pay-per-use and has a monthly free tier. For low traffic and scale-to-zero enabled, Cloud Run should remain a small part of COGS.

### Cloud SQL PostgreSQL

This is the part that needs to be distinguished carefully: **PostgreSQL itself is free/open source. Cloud SQL is the managed database service around PostgreSQL, and Google charges for the continuously provisioned compute, memory, storage and backups.**

There are two relevant starting points.

#### Option A — documented MVP instance: `db-f1-micro`

The repository's GCP architecture currently specifies `db-f1-micro` as the deliberately frugal MVP configuration.

Current Google pricing is approximately:

```text
$0.0105 / hour × 730 h ≈ $7.67 / month
```

Storage and used backups are additional. At 10 GiB of SSD and 10 GiB of used backups, using current Paris rates as a planning example:

```text
SSD:      10 GiB × $0.000465753 × 730 h ≈ $3.40
Backups:  10 GiB × $0.000109589 × 730 h ≈ $0.80
------------------------------------------------
Cloud SQL:                                ≈ $11.87/month
```

This is the **cheap MVP number**, but it comes with an important limitation: shared-core instances are not covered by the Cloud SQL SLA. Google documents them as the smallest instances suitable for trying the service. They should therefore be treated as an explicit MVP trade-off, not as the production reliability baseline.

#### Option B — small dedicated production baseline

For Cloud SQL Enterprise general-purpose dedicated-core instances, the current minimum is **1 vCPU and at least 3.75 GiB RAM**. Current list pricing is approximately $0.0413/vCPU-hour and $0.007/GiB-hour.

For a 1 vCPU / 3.75 GiB instance running continuously:

```text
CPU:       1 × $0.0413 × 730 h ≈ $30.15
Memory: 3.75 × $0.007  × 730 h ≈ $19.16
-----------------------------------------
Compute:                       ≈ $49.31/month
```

Adding the same illustrative 10 GiB SSD + 10 GiB used backups:

```text
Compute:   ≈ $49.31
SSD:        ≈ $3.40
Backups:    ≈ $0.80
--------------------
Total:      ≈ $53.51/month
```

This is the correct explanation for the previously quoted **~$45–60/month** Cloud SQL envelope: it was a conservative production-grade estimate, **not a PostgreSQL licence fee**.

High availability would roughly double the compute pricing and would therefore move this small instance to roughly **$103/month before storage/backups**. It is intentionally excluded from the MVP cost model.

Google's current documentation confirms that shared-core instances are not covered by the SLA, while SLA-covered configurations require dedicated CPU and high availability. That makes the trade-off explicit: **~$12/month for a very small MVP database versus ~\$54/month for a small dedicated single-zone database, before any HA upgrade.**

## Early production fixed-cost envelope

For the current GCP-only architecture, before Gemini usage:

| Component | MVP planning cost | Dedicated production baseline |
|---|---:|---:|
| Cloud SQL PostgreSQL | **~$12/month** | **~$54/month** |
| Cloud Run frontend + backend + jobs | **~$0–15** | **~$0–15** |
| Artifact Registry | **~$0–2** | **~$0–2** |
| Secret Manager | **~$0** | **~$0** |
| Logging / Monitoring / network buffer | **~$5–20** | **~$5–20** |
| **Total before Gemini** | **~$17–49/month** | **~$59–91/month** |

This is more useful than a single `$75/month` number because it exposes the actual decision.

**For the Book Loop MVP, the infrastructure can realistically start around $20–50/month before Gemini if we accept the `db-f1-micro` reliability trade-off.**

If we want the first commercial production database to have dedicated CPU/RAM, budget roughly **$60–90/month before Gemini** for the complete GCP platform.

The database is therefore not economically dangerous at either stage. The important variable cost remains Gemini usage.

## Gemini unit cost per Book Loop workflow

The workflow contains multiple agents and may retry, so model a range rather than a single optimistic figure.

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

For pricing decisions, budget **$0.50 per completed chapter-equivalent workflow** as a safety envelope. This 2.5× buffer is intended to absorb retries, larger contexts, correction loops, failed generations and other workflow overhead.

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

For a French Stripe account, current standard European cards are priced at **1.5% + €0.25 per successful transaction**. International cards can cost more.

Approximate standard-card processing cost:

- €19 subscription → **~€0.54**
- €39 subscription → **~€0.84**
- €79 subscription → **~€1.44**

This makes the effective revenue after payment processing approximately:

- Creator: **€18.46**
- Pro: **€38.16**
- Studio: **€77.56**

Stripe Billing pricing for recurring charges should also be checked at implementation time.

## Shared infrastructure allocation

Using the dedicated-production planning baseline of ~$75/month as a rounded commercial envelope:

| Paying customers | Fixed GCP cost/customer/month |
|---:|---:|
| 10 | ~$7.50 |
| 25 | ~$3.00 |
| 50 | ~$1.50 |
| 100 | ~$0.75 |
| 500 | ~$0.15 |

Using the lean MVP baseline of ~$35/month, the corresponding allocation is only ~$3.50/user at 10 paying users and ~$0.35/user at 100.

The immediate economic risk is therefore **not Cloud Run or Cloud SQL**. It is allowing an individual customer to consume unbounded Gemini capacity.

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
MVP GCP baseline:             ~$35/month planning midpoint
Dedicated GCP baseline:       ~$75/month planning midpoint
Cloud SQL MVP:                ~$12/month
Cloud SQL dedicated baseline: ~$54/month
Nominal Gemini workflow:      ~$0.08/chapter
Conservative AI envelope:     ~$0.50/chapter-equivalent
Target direct COGS:            ≤25% of subscription revenue
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
