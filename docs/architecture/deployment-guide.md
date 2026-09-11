# Guide de déploiement production — GCP

Ce guide décrit le déploiement de **AI Book Loop / Manuscript Studio** sur Google Cloud. GCP héberge l'ensemble de la pile de production : frontend, API, worker d'analyse, PostgreSQL, images, secrets, migrations et observabilité.

Pour les raisons et compromis de cette architecture, voir [`gcp-architecture.md`](./gcp-architecture.md). Pour la conception de la queue, voir [`async-analysis-jobs.md`](./async-analysis-jobs.md).

## 1. Architecture

- **Frontend** : Next.js sur Cloud Run.
- **Backend** : FastAPI sur Cloud Run.
- **Analysis worker** : même image applicative sur Cloud Run, avec `python -m book_loop.worker`.
- **Base** : Cloud SQL PostgreSQL.
- **Images** : Artifact Registry.
- **Secrets** : Secret Manager.
- **Migrations** : Alembic exécuté par Cloud Run Job.
- **CI/CD** : GitHub Actions pour la validation, Cloud Build pour la production.
- **Région** : `europe-west9` (Paris).

En production, le navigateur utilise le frontend comme origine unique. Les appels `/api/*` sont relayés par Next.js vers l'API Cloud Run. Le worker n'est pas exposé au navigateur.

## 2. Pré-requis GCP

Créer ou sélectionner un projet GCP puis activer au minimum :

```bash
gcloud auth login
gcloud config set project [PROJECT_ID]
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  secretmanager.googleapis.com
```

Créer un dépôt Artifact Registry régional pour l'image applicative API/web.

Créer une instance Cloud SQL PostgreSQL adaptée au stade MVP. La configuration de référence est une petite instance partagée, sans haute disponibilité.

## 3. Secrets

Créer dans Secret Manager les secrets nécessaires à l'environnement :

- `DATABASE_URL` ;
- `GEMINI_API_KEY` ;
- `AUTH_SECRET_KEY`.

Les workloads Cloud Run et le job de migration reçoivent uniquement les secrets dont ils ont besoin via leurs comptes de service.

Aucune valeur secrète ne doit être commitée dans Git.

## 4. Migrations PostgreSQL

Les migrations sont versionnées dans Alembic.

Le déploiement de production exécute le Cloud Run Job de migration avant de déployer les services applicatifs. Ne pas lancer `alembic upgrade head` au démarrage de chaque instance Cloud Run.

## 5. Déploiement

Cloud Build :

1. construit l'image API ;
2. pousse l'image dans Artifact Registry ;
3. déploie/exécute le job Alembic ;
4. déploie le service Cloud Run API ;
5. déploie le service Cloud Run `book-loop-analysis-worker` avec la même image et `python -m book_loop.worker` ;
6. résout l'URL API comme cible serveur du proxy Next.js ;
7. construit et déploie le frontend ;
8. vérifie IAM public et CORS.

Le worker reçoit `ANALYSIS_JOB_POLL_SECONDS` et `ANALYSIS_JOB_LEASE_SECONDS` et doit rester non public. Sa concurrence Cloud Run est fixée à `1` pour isoler les jobs longs.

Les Pull Requests et branches de travail exécutent uniquement le CI. Elles ne déclenchent pas le déploiement de production.

## 6. Configuration applicative

Le backend utilise PostgreSQL via `DATABASE_URL`.

Le frontend n'expose pas l'URL de l'API au navigateur. `API_INTERNAL_URL` est utilisé lors du build Next.js pour configurer le proxy `/api/*`. Le client appelle toujours des chemins relatifs (`/api/...`) sur l'origine du frontend.

Les analyses longues utilisent la queue PostgreSQL `analysis_jobs` : l'API retourne `202 Accepted`, puis le worker traite le job et renouvelle son lease jusqu'à terminaison.

## 7. Vérifications post-déploiement

1. Vérifier `GET /health` sur l'API Cloud Run.
2. Vérifier `/docs` sur l'API.
3. Tester register → login → `/api/auth/me` depuis le frontend.
4. Vérifier la persistance PostgreSQL.
5. Créer une analyse longue et vérifier le `202 Accepted`, puis son passage à un état terminal.
6. Vérifier que le worker apparaît sain dans Cloud Run et que ses logs montrent le polling/traitement des jobs.
7. Vérifier les logs Cloud Run et l'exécution du job de migration.

## 8. Retour arrière

Une version Cloud Run précédente peut être remise en trafic si une release applicative est défaillante.

Les migrations de schéma doivent rester compatibles avec cette stratégie. Les migrations destructives nécessitent une procédure spécifique et ne doivent pas être ajoutées à une release standard sans stratégie de rollback des données.

## 9. Principes d'exploitation

Le MVP privilégie le coût et la simplicité : Cloud Run scale-to-zero pour les services qui peuvent l'utiliser, capacité minimale du worker pour garantir le traitement des analyses, petite instance Cloud SQL, une seule région, pas de GKE, pas de Redis et pas de réseau complexe. La montée en gamme est déclenchée par l'usage réel.
