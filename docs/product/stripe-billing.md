# Stripe billing

Book Loop uses Stripe Checkout for paid subscriptions and Stripe Billing Portal for self-service subscription management.

## Entitlement model

The backend owns the effective `SubscriptionPlan` (`free`, `creator`, `pro`). The browser never sends a plan that is persisted directly. Stripe webhooks update the plan after Stripe confirms the subscription lifecycle.

Paid entitlement is granted only for `active` or `trialing` subscriptions. Unknown prices and non-paid subscription states fail closed to `free`.

## Flow

```text
Pricing page
   -> authenticated checkout request
   -> backend creates/reuses Stripe customer
   -> Stripe Checkout subscription
   -> Stripe webhook
   -> backend validates signature + deduplicates event
   -> subscription state + plan persisted
   -> existing capacity policy enforces limits
```

The customer portal is exposed through `POST /api/billing/portal` and must be used for cancellation, payment-method changes and plan changes rather than implementing those operations in the frontend. Checkout refuses to create a second active subscription for a customer.

## Configuration

Required production settings:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_CREATOR_MONTHLY_PRICE_ID`
- `STRIPE_CREATOR_YEARLY_PRICE_ID`
- `STRIPE_PRO_MONTHLY_PRICE_ID`
- `STRIPE_PRO_YEARLY_PRICE_ID`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`
- `STRIPE_PORTAL_RETURN_URL`

Stripe webhook endpoint: `POST /api/billing/webhook`.

## Safety requirements

- Verify the Stripe webhook signature before processing.
- Store processed event IDs so delivery retries are idempotent.
- Never trust plan/billing-cycle values from the client as entitlement state; they are only used to select a configured Stripe Price server-side.
- Keep project ownership independent from billing metadata.
- Keep capacity enforcement server-side and atomic.
- Run the Alembic migration before relying on persisted billing metadata in production.
