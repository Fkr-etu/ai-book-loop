# Guide de déploiement production — GCP

Ce guide décrit le déploiement de **AI Book Loop / Manuscript Studio** sur Google Cloud. GCP héberge l'ensemble de la pile de production : frontend, API, PostgreSQL, images, secrets, migrations et observabilité.

Pour les raisons et compromis de cette architecture, voir [`gcp-architecture.md`](./gcp-architecture.md).

## 1. Architecture

- **Frontend** : Next.js sur Cloud Run.
- **Backend** : FastAPI sur Cloud Run.
- **Base** : Cloud SQL PostgreSQL.
- **Images** : Artifact Registry.
- **Secrets** : Secret Manager.
- **Migrations** : Alembic exécuté par Cloud Run Job.
- **CI/CD** : GitHub Actions pour la validation, Cloud Build pour la production.
- **Région** : `europe-west1`.

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

Créer un dépôt Artifact Registry régional pour les images API et frontend.

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

Le déploiement de production doit exécuter le Cloud Run Job de migration avant de rendre la nouvelle version applicative active.

Ne pas lancer `alembic upgrade head` dans le processus de démarrage de chaque instance Cloud Run : le scaling horizontal rendrait cette stratégie fragile et inutilement concurrente.

## 5. Déploiement

La production est déclenchée par une release explicite.

Cloud Build :

1. construit l'image API ;
2. construit l'image frontend ;
3. pousse les images dans Artifact Registry ;
4. exécute le job Alembic ;
5. déploie le service Cloud Run API ;
6. déploie le service Cloud Run frontend ;
7. effectue les vérifications de santé nécessaires.

Les Pull Requests et branches de travail exécutent uniquement le CI. Elles ne déclenchent pas le déploiement de production.

## 6. Configuration applicative

Le backend utilise PostgreSQL via `DATABASE_URL`.

Le frontend utilise l'URL publique de l'API via `NEXT_PUBLIC_API_URL`.

Comme frontend et backend sont tous deux sous GCP, la configuration n'a pas besoin de reproduire l'architecture cross-domain Vercel/Cloud Run historique. Les règles CORS et cookies restent toutefois explicites et doivent être configurées selon les domaines publics retenus.

## 7. Vérifications post-déploiement

1. Vérifier `GET /health` sur l'API Cloud Run.
2. Vérifier `/docs` sur l'API.
3. Tester register → login → `/api/auth/me` depuis le frontend.
4. Vérifier la persistance PostgreSQL.
5. Vérifier qu'une génération de chapitre peut être reprise après redémarrage du service.
6. Vérifier les logs Cloud Run et l'exécution du job de migration.

## 8. Retour arrière

Une version Cloud Run précédente peut être remise en trafic si une release applicative est défaillante.

Les migrations de schéma doivent rester compatibles avec cette stratégie : privilégier des migrations rétrocompatibles lorsque plusieurs révisions applicatives peuvent coexister pendant un déploiement.

Les migrations destructives nécessitent une procédure spécifique et ne doivent pas être ajoutées à une release standard sans stratégie de rollback des données.

## 9. Principes d'exploitation

Le MVP privilégie le coût et la simplicité :

- Cloud Run scale-to-zero ;
- petite instance Cloud SQL ;
- une seule région ;
- pas de HA initiale ;
- pas de GKE ;
- pas de Redis ;
- pas de VPC/NAT complexe ;
- montée en gamme déclenchée par l'usage réel.
