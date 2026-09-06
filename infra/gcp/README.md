# GCP deployment

AI Book Loop uses Cloud Run for the API and frontend, Cloud SQL PostgreSQL for persistence, Artifact Registry for container images, Secret Manager for runtime secrets, and Alembic for schema migrations.

## Production region

`europe-west9` (Paris), matching the existing Cloud SQL instance `book-loop-postgres`.

## Required resources

- Artifact Registry: `book-loop-api`, `book-loop-web`
- Cloud SQL PostgreSQL: `book-loop-postgres`
- Secrets: `DATABASE_URL`, `GEMINI_API_KEY`, `AUTH_SECRET_KEY`
- Service accounts: `book-loop-api`, `book-loop-migrations`

## Deployment

`cloudbuild.yaml` builds and pushes both images, runs Alembic through a dedicated Cloud Run Job, then deploys the API and frontend services.

The pipeline is intentionally conservative: API max 3 instances, frontend max 2, and both services scale to zero.

## First deployment

Run from the repository root after configuring the GCP project and granting Cloud Build permission to deploy Cloud Run services/jobs and impersonate the runtime service accounts:

```bash
gcloud builds submit --config=cloudbuild.yaml
```

By default the frontend image is built with `NEXT_PUBLIC_USE_REAL_API=false`. This keeps CI and a fresh infrastructure deployment deterministic until the real API URL and authenticated journey have been validated.

## Enable the real API

`NEXT_PUBLIC_*` variables are consumed by the Next.js client bundle at **image build time**. Setting them only with Cloud Run runtime environment variables is therefore insufficient.

Once the API service is ready, obtain its Cloud Run URL:

```bash
gcloud run services describe book-loop-api \
  --region=europe-west9 \
  --format='value(status.url)'
```

Then build and deploy the frontend with the real API enabled:

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_API_URL=https://YOUR-API-URL,_USE_REAL_API=true
```

The frontend uses the API's existing HttpOnly session cookie. The real API client therefore sends `credentials: include`; do not move authentication secrets into `NEXT_PUBLIC_*` variables.

## Authentication / IAM

The application API has its own user authentication and book authorization. Cloud Run's `--allow-unauthenticated` controls access to the HTTP service itself; it does not replace application authentication. During the integration phase the API can remain publicly reachable at the transport layer while `/api/books/*` stays protected by the application's session.

If Cloud Build reports that it cannot set the `allUsers` invoker policy for `book-loop-api`, grant the Cloud Build service account the required Cloud Run/IAM permissions rather than weakening application authentication. The API must still reject unauthenticated book requests with HTTP 401.

## Important

Do not run database migrations from the API container startup command. Migrations are an explicit deployment step so application instances never race to mutate the schema.
