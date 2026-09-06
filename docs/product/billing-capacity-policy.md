# Billing & capacity policy

The customer-facing plans are **Free / Creator / Pro**. Capacity is enforced server-side; the frontend is never authoritative for entitlement checks.

| Plan | Price | Active projects | Workflow runs / month |
|---|---:|---:|---:|
| Free | €0 | 1 | 5 |
| Creator | €19/month or €190/year | 3 | 50 |
| Pro | €39/month or €390/year | 10 | 200 |

These workflow limits are an initial safety envelope, not a promise of unlimited inference. They can be tuned from measured cost and retention data without exposing model/token units to customers.

## Security rules

- Plan state is stored and evaluated by the backend.
- A client must never be able to select or override its own plan.
- Project ownership remains independent from billing metadata.
- Usage counters must be enforced atomically before a billable workflow starts.
- Stripe webhooks will be the source of truth for paid subscription lifecycle state once billing is integrated.
- Failed, invalid, or replayed billing events must fail closed and be idempotent.
