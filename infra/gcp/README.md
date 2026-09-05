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

The frontend currently deploys with `NEXT_PUBLIC_USE_REAL_API=false`. This is deliberate: the frontend integration must be completed and tested before production traffic is switched to the real API.

## Important

Do not run database migrations from the API container startup command. Migrations are an explicit deployment step so application instances never race to mutate the schema.
