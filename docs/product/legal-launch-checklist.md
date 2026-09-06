# Legal launch checklist — France / EU

This checklist is a product-launch gate, not legal advice. Before enabling paid subscriptions for consumers, have the final legal documents reviewed against the actual company, data flows, payment setup and target countries.

## Landing page

- [x] Prices are presented as a simple monthly/annual hypothesis: Free, Creator 19 €/month, Pro 39 €/month.
- [x] No unsupported promise of unlimited AI generation.
- [x] No unsupported claim about copyright ownership or absolute legal protection.
- [x] No claim that user data is never processed by providers; provider/data terms must be documented before launch.

## Mandatory site documents before commercial launch

- [ ] **Mentions légales**: legal identity, address, contact details, registration information, VAT information where applicable, and hosting information.
- [ ] **Privacy policy / RGPD notice**: controller identity, purposes, legal bases, categories of data, retention periods, recipients/processors, international transfers, user rights and contact method.
- [ ] **Cookie / tracker policy and consent mechanism** where non-exempt trackers are used.
- [ ] **Terms / CGV**: service description, prices, payment, renewal, suspension/termination, liability, intellectual property, applicable law and dispute process.
- [ ] **Consumer withdrawal flow**: document the applicable right of withdrawal and the digital-service/content exceptions or express waivers used, if any.
- [ ] **Online cancellation**: provide a clear electronic cancellation path for subscriptions where required.
- [ ] **Consumer mediation**: publish the mediator's name and contact details when consumer sales are enabled.
- [ ] **Payment/invoicing**: ensure Stripe checkout and invoices display the legally required pricing, VAT and seller information.

## Product/data specifics to document

- [ ] User manuscript and Canon data processing purposes are explicit.
- [ ] Gemini / Google processing and any applicable data transfers are documented.
- [ ] Cloud Run / Cloud SQL hosting and subprocessors are documented where required.
- [ ] Account deletion and data export/deletion behavior are implemented and documented.
- [ ] Retention periods for manuscripts, versions, reviews and logs are defined.
- [ ] Security measures and incident/contact process are documented at an appropriate level.

## Important implementation rule

Do **not** enable paid checkout merely because the pricing page is ready. The commercial launch gate is: legal identity available + legal documents published + privacy/data flows documented + cancellation/refund path implemented + Stripe/invoicing configured.
