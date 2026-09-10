# ADR 0009 — PostgreSQL-backed asynchronous analysis jobs

- Status: Accepted
- Date: 2026-09-10

## Context

Consistency and other book analyses can involve multiple repository reads and LLM calls. Running them synchronously inside FastAPI requests creates timeout and availability risk as book size grows.

The application already uses PostgreSQL as its durable state store and already relies on PostgreSQL transactions and advisory locks for concurrency-sensitive operations. Introducing a second infrastructure such as Redis or Celery would add operational complexity before the workload justifies it.

## Decision

Use PostgreSQL as the durable queue for long-running analyses.

Jobs are persisted in `analysis_jobs` and claimed by workers with `SELECT ... FOR UPDATE SKIP LOCKED`. A short transaction assigns a worker lease; long-running analysis executes after that transaction commits. A `lease_until` timestamp is renewed by heartbeats and allows another worker to reclaim work after a crash.

The HTTP layer creates a job and returns `202 Accepted`. Application use cases remain independent of HTTP and worker mechanics. The worker is a separate process using the same application container and infrastructure adapters.

The system guarantees durable job state and prevents concurrent claims of the same queue row. It intentionally provides at-least-once execution semantics rather than promising exactly-once LLM invocation.

## Consequences

### Positive

- no long HTTP request is required for analysis;
- PostgreSQL remains the single durable coordination system;
- multiple workers can consume concurrently without an external broker;
- crashed workers can be recovered through leases;
- Clean Architecture boundaries remain explicit.

### Negative

- PostgreSQL now carries queue workload in addition to business persistence;
- polling introduces a small scheduling delay and database queries;
- exactly-once external side effects remain impossible without additional idempotent protocols;
- very high queue volume may eventually justify a dedicated queue system.

## Rejected alternatives

- **FastAPI `BackgroundTasks`**: not durable across process/container termination.
- **Redis/Celery/RQ**: unnecessary operational dependency for the current scale and deployment model.
- **PGMQ**: technically viable, but the application needs only a small queue/lease protocol and does not yet benefit from another abstraction layer.
- **HTTP timeout increases**: treats the symptom rather than decoupling execution from transport.
