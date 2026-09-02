# Infrastructure cost analysis

This document turns infrastructure into an explicit product/strategy decision. The objective is to keep fixed costs low while the product hypothesis is still being validated, and to scale infrastructure only when usage or reliability requirements justify it.

## Executive conclusion

Infrastructure should be treated as a **variable-cost optimization problem**, not as a platform-building objective.

For the current Book MVP, SQLite plus a single application runtime is sufficient. The dominant cost is expected to be LLM usage, not the database or application server.

The recommended progression is:

```text
Local / MVP
SQLite + one API/runtime
        ↓
Production Book
managed PostgreSQL + serverless/container runtime
        ↓
Knowledge QA at scale
PostgreSQL + object storage + observability
        ↓
Semantic retrieval bottleneck proven
PostgreSQL + pgvector (or another measured retrieval layer)
```

PostgreSQL and pgvector are separate decisions. PostgreSQL solves operational/database requirements; pgvector solves a demonstrated semantic-retrieval requirement.

## Cost drivers

The main infrastructure cost categories are:

1. **LLM inference** — likely the largest variable cost.
2. **Application compute** — API, background jobs, workers.
3. **Database** — initially small; becomes a meaningful fixed cost with managed PostgreSQL.
4. **Storage** — documents, versions, exports, logs and eventually embeddings.
5. **Observability / networking** — initially minor, but can grow with traffic and retained logs.
6. **Operational overhead** — not directly visible on the cloud bill, but important when choosing managed services.

Gemini 2.5 Flash currently lists $0.30 / 1M input tokens and $2.50 / 1M output tokens on the standard paid tier. Gemini 2.5 Flash-Lite lists $0.10 / 1M input and $0.40 / 1M output. These prices make model selection and prompt/output discipline much more important than early database optimization. See the current provider pricing before committing to a commercial unit economics model.

## Scenario A — Local / development

### Architecture

- SQLite
- local API / CLI
- local or developer-provided LLM credentials
- no always-on cloud infrastructure

### Expected fixed infrastructure cost

**~$0/month**, excluding developer machines and LLM usage.

This should remain the default for development and CI where practical.

## Scenario B — Early production Book

### Hypothesis

A small number of real authors use the product, but traffic is intermittent and the corpus is still modest.

### Architecture

- serverless/container application runtime;
- managed PostgreSQL only when persistence/concurrency requires it;
- object storage for larger files if needed;
- basic logging and monitoring;
- no vector database.

Cloud Run is an example of a serverless runtime that bills for resources actually used and automatically scales instances, making it a reasonable early-production model when traffic is bursty.

### Order-of-magnitude planning budget

**~$20–100/month excluding LLM usage** is a reasonable planning envelope for a small production deployment, but this is not a vendor quote. The actual amount depends strongly on region, minimum instances, database size, backups, network traffic and observability retention.

The important decision is not to run a large always-on cluster before traffic exists.

## Scenario C — Product with hundreds of active users

### Hypothesis

The Book workflow has product-market evidence and there are hundreds of active users, with concurrent requests and background jobs.

### Architecture

- managed PostgreSQL;
- one or more serverless/container application services;
- background workers/jobs for long-running generation and analysis;
- object storage for documents and exports;
- centralized logs/metrics;
- backups and recovery procedures.

### Order-of-magnitude planning budget

**~$100–500/month excluding LLM usage** is a useful planning range for the application/infrastructure layer before high availability or enterprise requirements. This is intentionally a range rather than a forecast: managed PostgreSQL pricing is driven by CPU, memory, storage and networking, while serverless compute is usage-dependent.

At this stage, LLM spend can easily exceed infrastructure spend if users generate and review substantial amounts of content.

## Scenario D — Documentation QA pilot

### Hypothesis

Three to ten B2B design partners provide real documentation corpora. Usage is periodic but corpus sizes are substantially larger than a book project.

### Architecture

- managed PostgreSQL;
- object storage for source documents and immutable versions;
- asynchronous ingestion/extraction jobs;
- application API;
- basic queue/job mechanism;
- observability;
- no mandatory pgvector yet.

### Order-of-magnitude planning budget

**~$200–1,000/month excluding LLM usage** is a reasonable planning envelope for a small pilot environment with several corpora. This should be validated against the selected cloud, region, retention policy and ingestion frequency.

The major new cost is not necessarily PostgreSQL itself. It is the combination of repeated ingestion, extraction, analysis and retained source/version data.

## Scenario E — Knowledge QA SaaS at meaningful scale

### Hypothesis

Hundreds to thousands of organizations/users, continuous document changes, automated regression checks and customer-facing SLAs.

### Architecture

- highly available managed PostgreSQL;
- object storage;
- asynchronous workers/queues;
- caching where measured useful;
- centralized observability;
- rate limits and quotas;
- tenant isolation and backup/recovery strategy;
- semantic retrieval only where benchmarks show it is necessary.

### Order-of-magnitude planning budget

**~$1,000–5,000+/month excluding LLM usage** becomes plausible depending on availability, traffic, retention, background processing and enterprise requirements.

This range is deliberately broad. At this stage, architecture should be driven by measured workload and gross margin targets rather than a generic startup stack.

## LLM cost model

LLM usage should be modeled separately from infrastructure.

For Gemini 2.5 Flash standard pricing, a simple planning formula is:

```text
monthly LLM cost
= input_tokens / 1,000,000 × $0.30
+ output_tokens / 1,000,000 × $2.50
```

For Gemini 2.5 Flash-Lite:

```text
monthly LLM cost
= input_tokens / 1,000,000 × $0.10
+ output_tokens / 1,000,000 × $0.40
```

### Example: one chapter workflow

Assume, purely as a planning hypothesis:

- 100k input tokens across context, lore, outline, previous summaries and review calls;
- 20k output tokens across draft, review and summary.

Then Flash would cost approximately:

```text
100k × $0.30/M = $0.03
20k × $2.50/M  = $0.05
Total           = $0.08 / chapter
```

At 20 chapters, that is about **$1.60 per book** under these assumptions.

The actual cost may be materially higher or lower depending on retries, reasoning tokens, context size, model choice and workflow design. This example is a unit-economics model, not a measured application cost.

## Why pgvector should not be added for cost reasons

pgvector is not a cost-saving technology by itself. It introduces another retrieval dimension and can increase database CPU, memory and storage requirements.

Its value should be demonstrated by a retrieval benchmark such as:

- exact/structured retrieval misses relevant evidence;
- semantic retrieval materially improves recall/precision;
- corpus size makes brute-force or application-side retrieval too expensive;
- retrieval latency becomes a user-visible bottleneck.

Until then, structured PostgreSQL queries and simple deterministic retrieval are preferable.

## PostgreSQL migration trigger

Move from SQLite when one or more of these become true:

- multiple users write concurrently;
- deployed production API requires robust concurrent persistence;
- background workers need transactional coordination;
- backups/recovery requirements exceed the local SQLite setup;
- dataset size or operational needs justify managed database infrastructure;
- team operations benefit from a managed database.

Do **not** migrate simply because PostgreSQL is more scalable in theory.

## Infrastructure guardrails

- Keep infrastructure minimal until product usage justifies it.
- Prefer managed services over self-hosted databases for production.
- Separate compute, persistence, object storage and retrieval concerns.
- Keep repository ports/adapters so SQLite and PostgreSQL remain interchangeable at the application boundary.
- Measure LLM cost per completed workflow, not only tokens per request.
- Add quotas before runaway agentic workflows become a billing risk.
- Track retry rates: bounded retries are a direct cost-control mechanism.
- Store provenance and review history, but define retention policies before the corpus becomes large.
- Do not introduce a vector database or knowledge graph without a benchmark showing the need.

## Decision table

| Stage | Database | Compute | Vector search | Planning budget, excl. LLM |
|---|---|---|---|---:|
| Development | SQLite | Local | No | ~$0 |
| Early Book production | PostgreSQL when needed | Serverless/container | No | ~$20–100/mo |
| Hundreds of users | Managed PostgreSQL | Serverless + jobs | No by default | ~$100–500/mo |
| Documentation pilot | Managed PostgreSQL + object storage | API + async jobs | Only if proven | ~$200–1,000/mo |
| Scaled Knowledge QA | HA PostgreSQL + object storage | Services + workers | Benchmark-driven | ~$1,000–5,000+/mo |

These are **planning envelopes**, not commitments or vendor quotes. Re-estimate before each infrastructure transition using real workload measurements and current provider prices.

## Strategic conclusion

The project should optimize in this order:

```text
1. Prove user value
2. Measure workflow cost
3. Optimize prompts / model routing / retries
4. Introduce managed PostgreSQL when operationally justified
5. Add semantic retrieval only when retrieval quality or scale requires it
6. Add enterprise infrastructure only when customers pay for it
```

The moat remains the canonical knowledge model and evidence-backed validation loop. Infrastructure exists to support that moat; it should not become the product strategy.
