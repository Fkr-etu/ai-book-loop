# France B2C commercial readiness

This checklist records the minimum product, legal and operational work to complete before commercial launch of Book Loop to consumers in France.

It is a project checklist, not legal advice. Final legal texts and implementation must be validated against the actual company identity, offer, pricing, payment provider, hosting, analytics and data flows.

## Launch gate

The product must not be considered B2C-production-ready until the following are implemented, published where required, and tested end-to-end.

### 1. Mentions légales

- [ ] Complete French legal notices.
- [ ] Identify the publisher/operator and required company/contact information.
- [ ] Identify hosting information as required.
- [ ] Make the legal-notice page permanently accessible from the website.

### 2. Privacy / RGPD

- [ ] Publish a GDPR-compliant privacy policy.
- [ ] Inventory personal-data processing purposes and legal bases.
- [ ] Document categories of data, recipients/processors, retention periods and user rights.
- [ ] Define data-subject request handling.
- [ ] Document international transfers if any third-party service creates them.
- [ ] Document AI/LLM provider data flows and retention; do not assume prompts are exempt from personal-data rules.
- [ ] Ensure the product's actual implementation matches the published policy.

### 3. Cookies and trackers

- [ ] Inventory cookies, SDKs, pixels, analytics and other trackers actually used.
- [ ] Classify strictly necessary vs consent-required technologies.
- [ ] Implement consent collection where required.
- [ ] Do not load consent-required trackers before valid consent.
- [ ] Provide an accessible way to change/withdraw consent.
- [ ] Keep the cookie/traceur policy synchronized with the production stack.

### 4. CGV / subscription

- [ ] Publish French consumer terms and conditions (CGV) appropriate to the actual subscription offer.
- [ ] Clearly describe service, price, billing frequency, renewal and applicable limits.
- [ ] Clearly describe suspension/cancellation rules and consequences.
- [ ] Provide required pre-contractual information before checkout.
- [ ] Preserve proof of contractual acceptance and the applicable version of the CGV.

### 5. Digital-service right of withdrawal

- [ ] Determine the exact withdrawal regime applicable to the Book Loop digital service and subscription.
- [ ] Implement the required withdrawal information and process.
- [ ] If immediate performance starts before the withdrawal period ends, implement the required consumer acknowledgement/consent flow and evidence.
- [ ] Handle refunds and termination consistently with the applicable legal regime.
- [ ] Test the full withdrawal flow from checkout through refund/account state.

### 6. Electronic subscription termination

- [ ] Implement an easily accessible electronic termination flow for eligible consumer subscriptions.
- [ ] Make the termination path as clear and usable as the applicable French rules require.
- [ ] Record the request, timestamp and resulting subscription state.
- [ ] Send a durable confirmation of termination where required.
- [ ] Test cancellation from a normal consumer account without support intervention.

### 7. Consumer mediation

- [ ] Select the competent consumer mediator(s) for the business activity.
- [ ] Enter the required mediation arrangement before launch.
- [ ] Publish the mediator information in the required contractual/site locations.
- [ ] Keep the information synchronized with the current business entity and activity.

### 8. Invoicing / payment records

- [ ] Implement compliant invoices/receipts for consumer subscriptions.
- [ ] Include the required seller, customer, transaction, price and tax information.
- [ ] Handle VAT/tax rules applicable to the actual business setup and customer location.
- [ ] Define invoice numbering, storage and retrieval rules.
- [ ] Ensure payment provider records reconcile with Book Loop subscription state.
- [ ] Test successful payment, failed payment, renewal, refund and cancellation scenarios.

## Product implementation dependencies

These legal requirements are not only documentation tasks. The application will need supporting capabilities:

- public legal pages and stable links;
- consent state and consent history where required;
- account/subscription lifecycle state;
- checkout acceptance/versioning records;
- withdrawal/cancellation workflows;
- durable transaction and invoice records;
- transactional email for confirmations;
- privacy/data-request operational procedures;
- auditability of important consumer actions.

## Recommended implementation order

1. Define the legal/business model and exact subscription offer.
2. Select payment/billing provider and establish the tax/invoicing model.
3. Map personal-data and tracker flows from the real production architecture.
4. Implement subscription, cancellation, withdrawal and billing state transitions.
5. Publish and integrate legal pages.
6. Implement consent management according to the actual tracker inventory.
7. Run a complete consumer checkout → service → cancellation/refund test matrix.
8. Obtain final legal review before opening paid B2C access.

## Important scope boundary

The existing GCP deployment is an infrastructure concern and should remain independently deployable on demand. Deployment readiness is not a substitute for B2C legal/commercial readiness.
