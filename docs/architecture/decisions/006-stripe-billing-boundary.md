# ADR 006 — Stripe billing boundary

## Status
Accepted

## Context

Book Loop already had backend-authoritative subscription plans and capacity limits, but no payment provider was connected. The pricing UI existed without a real checkout lifecycle.

## Decision

Use Stripe Checkout for initial paid subscription creation and Stripe Billing Portal for customer self-service. Keep Stripe-specific API calls in infrastructure, expose billing actions through explicit API routes, and treat verified Stripe webhooks as the source of truth for paid subscription lifecycle state.

The domain keeps the provider-neutral `SubscriptionPlan` enum. Stripe customer IDs, subscription IDs, lifecycle status and webhook event IDs remain persistence/infrastructure concerns. Capacity enforcement remains in the existing backend policy and workflow reservation path.

The frontend may select a desired plan and billing cadence for checkout, but it never becomes the authority for entitlement.

## Consequences

- Paid checkout can be enabled without coupling domain models to Stripe SDK types.
- Webhook retries are idempotent through persisted event IDs.
- Subscription cancellation and payment-method changes remain in Stripe Billing Portal rather than being reimplemented in the frontend.
- Production requires Stripe Price IDs, API/webhook secrets, legal/commercial readiness and end-to-end webhook validation.
