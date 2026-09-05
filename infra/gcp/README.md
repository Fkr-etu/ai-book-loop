# GCP deployment

AI Book Loop uses a GCP-only production stack:

- Cloud Run: FastAPI API (`book-loop-api`)
- Cloud Run: Next.js web (`book-loop-web`)
- Cloud Run Job: Alembic migrations (`book-loop-migrations`)
- Cloud SQL PostgreSQL: `book-loop-postgres`
- Artifact Registry: `book-loop-api` and `book-loop-web`
- Secret Manager: `DATABASE_URL`, `GEMINI_API_KEY`, `AUTH_SECRET_KEY`
- Cloud Build: `cloudbuild.yaml`

The deployment region is **`europe-west9` (Paris)** to match the existing Cloud SQL instance.

## One-time GCP setup

The project and billing account must be configured first. Then enable:

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com
```

Create the Artifact Registry repositories if they do not exist:

```bash
gcloud artifacts repositories create book-loop-api \
  --repository-format=docker \
  --location=europe-west9

gcloud artifacts repositories create book-loop-web \
  --repository-format=docker \
  --location=europe-west9
```

The following service accounts are used by the pipeline:

- `book-loop-api`: Cloud SQL Client + Secret Manager Secret Accessor
- `book-loop-migrations`: Cloud SQL Client + Secret Manager Secret Accessor for `DATABASE_URL`

The Cloud Build service account also needs permission to deploy Cloud Run services/jobs and push to Artifact Registry.

## Secrets

Create these secrets before the first deployment:

```text
DATABASE_URL
GEMINI_API_KEY
AUTH_SECRET_KEY
```

Do not commit secret values. The Cloud Build pipeline references secret version `1` explicitly.

`DATABASE_URL` must use the Cloud SQL Unix socket used by Cloud Run, for example:

```text
postgresql+psycopg://postgres:PASSWORD@/book_loop?host=/cloudsql/PROJECT_ID:europe-west9:book-loop-postgres
```

## Deployment pipeline

`cloudbuild.yaml` performs the following sequence:

1. Build and push the backend image.
2. Deploy/update the API Cloud Run service.
3. Deploy/update the Alembic Cloud Run Job.
4. Execute `alembic upgrade head` and wait for completion.
5. Build the Next.js image with the API URL.
6. Deploy/update the web Cloud Run service.
7. Read the web URL and configure API CORS.

Migrations deliberately run as a dedicated Cloud Run Job rather than during API startup. A failed migration therefore blocks the deployment before the frontend is updated.

## Cost controls

Initial Cloud Run settings are intentionally conservative:

- API: min 0 / max 3, 1 vCPU, 1 GiB, concurrency 8
- Web: min 0 / max 2, 1 vCPU, 512 MiB, concurrency 40
- Cloud SQL: small single-zone instance, no HA
- one region: `europe-west9`

Do not add a load balancer, Kubernetes, Redis/Memorystore, NAT gateway or multi-region infrastructure until actual traffic requires it.

## Frontend API integration

The frontend currently supports both `MockBookApi` and `RealBookApi`. The Cloud Build pipeline keeps `NEXT_PUBLIC_USE_REAL_API=false` by default until the production API integration is validated end-to-end. Set the substitution to `true` only after the frontend integration checks are complete.
