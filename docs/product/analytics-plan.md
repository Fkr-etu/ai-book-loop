# Book Loop — Analytics Plan

## Goal

Measure product activation, workflow usage and subscription conversion without collecting manuscript content, Canon content, prompts, model responses, imported documents, or other writing data.

The first production objective is to instrument the launch funnel well enough to learn from the first author pilots. Analytics is diagnostic telemetry, not the source of truth for product state.

## Principles

- Analytics is product telemetry, not content surveillance.
- No manuscript, Canon, prompt, AI response or imported document content is sent to analytics.
- Analytics is disabled until the user explicitly accepts non-essential tracking.
- The application uses an internal analytics abstraction so the provider can be changed without rewriting product code.
- Events use stable names and small, documented property sets.
- Business-critical state remains in the Book Loop backend; analytics is never the source of truth.
- Do not introduce identifiers such as email, user ID, book ID or free-form text into event properties.

## Launch funnel

The initial pilot funnel is intentionally small:

```text
Landing
  ↓
Signup completed
  ↓
Book created
  ├── New project → Studio
  └── Existing manuscript → Import started → Document ingested
  ↓
Consistency analysis started
  ↓
Analysis completed
  ↓
Analysis result viewed
  ↓
Author says whether the result was useful
  ↓
Critical Eye opened / used
  ↓
Return visit
```

The primary learning signal is not the number of clicks. During the pilot, the most important question is whether an author reaches a result they consider genuinely useful, especially a problem they had not noticed themselves. The result UI therefore offers a binary usefulness signal without collecting free-form feedback or manuscript content.

## Initial event taxonomy

| Event | Trigger | Allowed properties |
| --- | --- | --- |
| `landing_viewed` | Landing page viewed | none |
| `signup_started` | Registration flow started | none |
| `signup_completed` | Registration completed | `plan` |
| `book_created` | Project successfully created | `plan` |
| `manuscript_import_started` | User submits an existing manuscript for import | none |
| `document_ingested` | Existing manuscript ingestion completed | none |
| `canon_configured` | Initial Canon configuration completed | `plan` |
| `analysis_started` | Consistency analysis job accepted | none |
| `analysis_completed` | Consistency analysis job succeeded | `issue_count` |
| `analysis_result_viewed` | Successful analysis result rendered | `issue_count` |
| `analysis_finding_feedback` | Author marks analysis results useful or not useful | `feedback`, `issue_count` |
| `critical_eye_opened` | First Critical Eye request in a chapter session succeeds | none |
| `critical_eye_message_sent` | Author submits an answer to Critical Eye | none |
| `critical_eye_completed` | Critical Eye session reaches its terminal response | none |
| `chapter_generation_started` | Chapter generation requested | `plan`, `chapter_number` |
| `chapter_generation_completed` | Chapter generation completed | `plan`, `chapter_number`, `generation_status` |
| `chapter_reviewed` | Chapter review completed | `plan`, `chapter_number` |
| `chapter_approved` | Human approval completed | `plan`, `chapter_number` |
| `chapter_correction_requested` | Human requests correction | `plan`, `chapter_number` |
| `subscription_checkout_started` | Paid checkout started | `plan` |
| `subscription_started` | Paid subscription confirmed | `plan` |
| `subscription_cancelled` | Subscription cancellation confirmed | `plan` |

## Pilot metrics

For the first author cohort, monitor:

- signup → book creation rate;
- new-project vs existing-manuscript path completion;
- manuscript import completion rate;
- book → first consistency analysis start rate;
- analysis start → completion rate;
- analysis completion → result viewed rate;
- distribution of `issue_count`;
- **analysis usefulness rate** among authors who submit feedback;
- Critical Eye usage after entering the Studio;
- return visits after the first analysis.

The usefulness rate is the proportion of `analysis_finding_feedback` events marked `useful`. It is a directional pilot signal, not a product-quality score: interpret it alongside interviews, observed usage and the actual examples authors found valuable or incorrect.

Do not optimize these numbers in isolation. Pair funnel data with direct author interviews and the qualitative value signal.

## Data that must never be tracked

- Manuscript text or excerpts
- Canon facts, characters, locations, events or relationships
- Prompts or LLM responses
- Uploaded/imported source documents or their content
- API keys, authentication tokens, emails or other direct identifiers
- Free-form user-entered text
- Internal identifiers that can be used to reconstruct a user's writing project

## Consent

The cookie-consent boundary stores an explicit `accepted`/`rejected` choice. Google Analytics is initialized only after `accepted`. Rejecting consent prevents analytics initialization and event dispatch. The current consent banner also avoids sending analytics data before a choice is made.

Final production deployment must validate the selected analytics provider, cookie/tracker classification and legal wording against the actual Book Loop stack and applicable French/EU requirements.

## Provider strategy

Book Loop currently uses Google Analytics 4 through a small provider-neutral client. The GA4 measurement ID is supplied as the public `NEXT_PUBLIC_GA4_MEASUREMENT_ID` build variable; it is not a secret. The identifier is injected at Next.js build time so the deployed client bundle has an explicit production configuration.

The application does not send manuscript text, Canon data, prompts, model responses, emails or authentication data as event properties. GA4 is configured with `send_page_view: false`; Book Loop controls the product events explicitly through `track()`.
