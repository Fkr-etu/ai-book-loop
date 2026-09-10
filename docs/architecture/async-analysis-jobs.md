# Async analysis jobs

Long-running analyses must not execute inside an HTTP request. The API creates a durable execution intent in PostgreSQL and returns `202 Accepted`; a separate worker claims and executes the job.

## Architecture

```text
HTTP
  -> StartConsistencyAnalysis
  -> PostgreSQL analysis_jobs
  -> worker (FOR UPDATE SKIP LOCKED)
  -> AnalyzeConsistency
  -> job result
```

The job is execution state, not canonical book state. `AnalyzeConsistency` remains unaware of HTTP, PostgreSQL and workers.

## Job lifecycle

```text
QUEUED -> RUNNING -> SUCCEEDED
                  -> FAILED
```

A `RUNNING` job carries a `lease_until`. If a worker crashes before completion, another worker can reclaim the job after the lease expires. Heartbeats renew the lease while the analysis runs.

The queue provides at-least-once execution. Exactly-once invocation of an external LLM cannot be guaranteed across a worker crash between the provider response and the durable completion write. Idempotency therefore protects job creation and any future side effects.

## PostgreSQL protocol

Claiming uses a short transaction:

```sql
SELECT ...
FROM analysis_jobs
WHERE (status = 'queued' AND available_at <= CURRENT_TIMESTAMP)
   OR (status = 'running' AND lease_until < CURRENT_TIMESTAMP)
ORDER BY created_at
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

The transaction commits immediately after assigning the lease. No database transaction is held during LLM calls or long analysis work.

## API

`POST /api/books/{book_id}/consistency/analyze`

- returns `202 Accepted`;
- accepts optional `Idempotency-Key`;
- returns `job_id` and current execution state.

`GET /api/books/{book_id}/consistency/analyses/{job_id}` returns the public execution state and the result only after successful completion.

The existing `GET /api/books/{book_id}/consistency/issues` remains the read path for currently persisted consistency issues.

## Worker

The worker is a separate process (`python -m book_loop.worker`). It polls PostgreSQL, claims one job at a time, renews the lease on a separate database connection, executes the application use case, and persists success/failure.

The same Python image can be used for API and worker workloads; the process command is different. Redis/Celery/RQ/PGMQ are intentionally not required for the MVP.

## Observability

Async analysis execution is observable through structured application logs; PostgreSQL remains the durable source for the job lifecycle itself. No second metrics database or queue is introduced.

The worker emits correlated events carrying `job_id`, `book_id`, `analysis_type`, `worker_id`, `attempt` and `status`. Completion/failure events additionally expose `queue_wait_ms`, `execution_duration_ms`, retry state and, for successful consistency analyses, `issue_count`. Claim events expose `lease_recovered` so expired-worker recovery can be counted independently from ordinary retries.

These fields support Cloud Logging queries and log-based Cloud Monitoring metrics for:

- queue wait latency;
- analysis execution latency;
- successful/failed analyses;
- retry volume;
- lease recoveries;
- detected issue volume.

The API also logs the initial `job_id -> book_id -> analysis_type` correlation when a request creates or reuses an analysis job. Logs deliberately exclude prompts, generated text, source content and other potentially sensitive book data.

The durable `analysis_jobs` timestamps remain authoritative for deeper diagnosis: `created_at -> started_at` gives queue wait and `started_at -> completed_at/failed_at` gives end-to-end execution timing.

## Future extensions

- finer-grained checkpoints for multi-stage book analyses;
- `LISTEN/NOTIFY` as a wake-up optimization without replacing durable queue state;
- dedicated result tables if result size or retention requirements justify them;
- independent worker autoscaling once production volume is known;
- OpenTelemetry/traces if cross-service latency becomes difficult to diagnose from structured logs alone.
