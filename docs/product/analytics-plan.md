# Book Loop — Analytics Plan

## Goal

Measure product activation, workflow usage and subscription conversion without collecting manuscript content, Canon content, prompts, model responses, imported documents, or other writing data.

## Principles

- Analytics is product telemetry, not content surveillance.
- No manuscript, Canon, prompt, AI response or imported document content is sent to analytics.
- Analytics is disabled until the user explicitly accepts non-essential tracking.
- The application uses an internal analytics abstraction so the provider can be changed without rewriting product code.
- Events use stable names and small, documented property sets.
- Business-critical state remains in the Book Loop backend; analytics is never the source of truth.

## Initial event taxonomy

| Event | Trigger | Allowed properties |
| --- | --- | --- |
| `landing_viewed` | Landing page viewed | none |
| `signup_started` | Registration flow started | none |
| `signup_completed` | Registration completed | `plan` |
| `book_created` | Book created | `plan` |
| `canon_configured` | Initial Canon configuration completed | `plan` |
| `chapter_generation_started` | Chapter generation requested | `plan`, `chapter_number` |
| `chapter_generation_completed` | Chapter generation completed | `plan`, `chapter_number`, `generation_status` |
| `chapter_reviewed` | Chapter review completed | `plan`, `chapter_number` |
| `chapter_approved` | Human approval completed | `plan`, `chapter_number` |
| `chapter_correction_requested` | Human requests correction | `plan`, `chapter_number` |
| `subscription_checkout_started` | Paid checkout started | `plan` |
| `subscription_started` | Paid subscription confirmed | `plan` |
| `subscription_cancelled` | Subscription cancellation confirmed | `plan` |

## Data that must never be tracked

- Manuscript text or excerpts
- Canon facts, characters, locations, events or relationships
- Prompts or LLM responses
- Uploaded/imported source documents or their content
- API keys, authentication tokens, emails or other direct identifiers
- Free-form user-entered text

## Consent

The cookie-consent boundary stores an explicit `accepted`/`rejected` choice. Google Analytics is initialized only after `accepted`. Rejecting consent prevents analytics initialization and event dispatch. The current consent banner also avoids sending analytics data before a choice is made.

Final production deployment must validate the selected analytics provider, cookie/traceur classification and legal wording against the actual Book Loop stack and applicable French/EU requirements.

## Provider strategy

Book Loop currently uses Google Analytics 4 through a small provider-neutral client. The GA4 measurement ID is supplied as the public `NEXT_PUBLIC_GA4_MEASUREMENT_ID` build variable; it is not a secret. The identifier is injected at Next.js build time so the deployed client bundle has an explicit production configuration.

The application does not send manuscript text, Canon data, prompts, model responses, emails or authentication data as event properties. GA4 is configured with `send_page_view: false`; Book Loop controls the product events explicitly through `track()`.
