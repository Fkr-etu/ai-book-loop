# Infrastructure and Unit Economics

This document estimates the cost of running Book Loop in the current target architecture. These are planning estimates, not billing guarantees; real production usage must replace them before final commercial decisions.

## Current production architecture

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

The application production persistence model is PostgreSQL/Cloud SQL. Local SQLite support is not the production persistence architecture.

## Cost principles

LLM inference is the important variable cost. Control output length, retries, correction loops and unnecessary context before optimizing small fixed infrastructure costs.

Cloud Run is pay-per-use. Cloud SQL is the managed PostgreSQL service and is charged for provisioned compute/memory plus storage and backups.

The repository currently documents two Cloud SQL planning envelopes:

- lean MVP shared-core configuration: approximately **$12/month** before other platform costs, with an explicit reliability/SLA trade-off;
- small dedicated single-zone baseline: approximately **$54/month** before storage/backups at the assumptions documented here.

The wider GCP planning envelope is roughly **$20–50/month before Gemini** for the lean MVP and **$60–90/month before Gemini** for the dedicated baseline. These are planning ranges, not invoices.

## Gemini workflow model

The current provider implementation uses Gemini. A chapter workflow may include writing, validation, review, correction/retry, summary and Canon extraction.

Illustrative planning assumptions:

- nominal example: 100k input + 20k output tokens on Gemini 2.5 Flash → about **$0.08/workflow** at the documented pricing assumptions;
- conservative example: 250k input + 50k output → about **$0.20/workflow**;
- commercial safety envelope: **$0.50 per completed chapter-equivalent workflow** to absorb retries, larger contexts and workflow overhead.

The $0.50 figure is a safety envelope, not a measured Book Loop production cost.

## Current commercial grid

The working subscription model is:

| Plan | Monthly | Annual | Role |
|---|---:|---:|---|
| Free | €0 | — | Product discovery |
| Creator | €19 | €190 | Serious individual creator |
| Pro | €39 | €390 | Intensive creator / multiple projects |

There is currently no Studio plan in the implemented commercial model. A higher-capacity tier is a future experiment that requires usage evidence.

Capacity must be enforced as an entitlement rather than offering unlimited inference.

## Gross-margin planning

For planning only, target direct COGS below **25% of subscription revenue** before general company expenses.

Using the conservative $0.50 workflow safety envelope, the rough AI-only headroom is approximately:

| Plan | Revenue | 25% COGS ceiling | Chapter-equivalent envelope* |
|---|---:|---:|---:|
| Creator | €19 | €4.75 | ~9 |
| Pro | €39 | €9.75 | ~19 |

*Illustrative only. Currency conversion, Stripe fees, fixed infrastructure and actual workflow mix are excluded from this simplified calculation.

This is why the product should bound workflow capacity and correction/review retries.

## Payment processing

Stripe fees must be included in commercial COGS. The exact applicable fee depends on account, payment method and geography and must be checked against the configured Stripe account before launch.

Do not treat the illustrative card-fee figures in older planning material as contractual pricing.

## What to measure

Replace these assumptions with production evidence for:

- Gemini cost per completed chapter;
- Gemini cost per successful full workflow;
- retry/correction rate;
- average input/output tokens per workflow;
- monthly AI cost per paying customer;
- Stripe cost per paying customer;
- fixed infrastructure cost;
- gross margin by plan.

The immediate economic risk is unbounded AI consumption, not the existence of a small GCP footprint.

## Commercial guardrails

1. No unlimited AI generation.
2. Bound correction/review retries.
3. Use the current Gemini implementation by default; introduce other providers only when measured benchmarks justify them.
4. Track usage per completed workflow.
5. Enforce monthly plan capacity.
6. Tune quotas from measured usage before assuming that price increases are required.

These assumptions should be revisited after real creators use Book Loop repeatedly.
