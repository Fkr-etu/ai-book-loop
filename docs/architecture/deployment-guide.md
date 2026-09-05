# Guide de déploiement production — GCP uniquement

Ce guide décrit le déploiement cible de **AI Book Loop / Manuscript Studio** sur une seule plateforme : Google Cloud.

## 1. Architecture cible

```text
GitHub
  │
  ▼
Cloud Build
  ├── Artifact Registry
  │     ├── book-loop-api
  │     └── book-loop-web
  │
  ├── Cloud Run
  │     ├── book-loop-api (FastAPI)
  │     └── book-loop-web (Next.js)
  │
  └── Cloud Run Job
        └── book-loop-migrate (Alembic)

Cloud SQL PostgreSQL
Secret Manager
Cloud Logging
```

Les composants sont volontairement regroupés en `europe-west1` afin de limiter la complexité et les coûts réseau.

## 2. Choix MVP pragmatiques

- Cloud Run avec `min=0` pour API et frontend.
- `max=3` instances au départ pour éviter une dérive accidentelle des coûts.
- 512 MiB et 1 vCPU par service au départ.
- Cloud SQL PostgreSQL en petite instance shared-core, sans haute disponibilité.
- Pas de Load Balancer, GKE, Memorystore, Cloud NAT ou architecture réseau complexe au MVP.
- Artifact Registry dans la même région que Cloud Run.
- Secrets dans Secret Manager ; aucun secret dans Git.
- Alembic exécuté par un Cloud Run Job **avant** le déploiement applicatif.

La capacité pourra être augmentée sans changer l'architecture applicative.

## 3. Préparer le projet GCP

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

Créer le dépôt Artifact Registry :

```bash
gcloud artifacts repositories create book-loop \
  --repository-format=docker \
  --location=europe-west1 \
  --description="AI Book Loop container images"
```

## 4. Cloud SQL PostgreSQL

Créer une petite instance PostgreSQL dans `europe-west1` adaptée au MVP, sans HA.

Créer ensuite la base et l'utilisateur applicatif. La valeur complète de connexion doit être stockée dans Secret Manager sous `book-loop-database-url`.

Pour une connexion Cloud Run via Cloud SQL, la valeur recommandée est une URL PostgreSQL utilisant le socket Cloud SQL, par exemple :

```text
postgresql+psycopg://BOOK_USER:BOOK_PASSWORD@/book_loop?host=/cloudsql/PROJECT_ID:europe-west1:INSTANCE_NAME
```

Le compte de service d'exécution Cloud Run doit disposer de `roles/cloudsql.client`.

## 5. Secrets

Créer au minimum :

- `book-loop-database-url`
- `book-loop-gemini-api-key`
- `book-loop-jwt-secret`

Puis donner au compte de service d'exécution le rôle `roles/secretmanager.secretAccessor` sur ces secrets.

Le compte de service utilisé par Cloud Build doit également pouvoir déployer Cloud Run, écrire dans Artifact Registry et exécuter le job de migration.

## 6. Déploiement automatisé

`cloudbuild.yaml` construit les deux images, pousse les images dans Artifact Registry, exécute les migrations Alembic puis déploie les services Cloud Run.

Ordre :

1. build API ;
2. push API ;
3. migration Alembic ;
4. déploiement API ;
5. récupération de l'URL API ;
6. build frontend avec `NEXT_PUBLIC_API_URL` ;
7. push frontend ;
8. déploiement frontend ;
9. mise à jour de `CORS_ORIGINS` avec l'URL Cloud Run du frontend.

Les migrations ne sont donc pas lancées au démarrage de chaque instance Cloud Run.

## 7. Déclenchement recommandé

Pour conserver le comportement de livraison défini précédemment :

- branches de fonctionnalité : CI uniquement ;
- Pull Requests : CI uniquement ;
- `main` : CI uniquement ;
- branche `release` : Cloud Build → production.

Configurer dans Cloud Build un trigger GitHub sur `release` pointant vers `cloudbuild.yaml`.

## 8. Vérification post-déploiement

```bash
gcloud run services describe book-loop-api --region=europe-west1
gcloud run services describe book-loop-web --region=europe-west1
```

Vérifier ensuite :

- `GET /health` de l'API retourne HTTP 200 ;
- `/docs` est accessible sur l'API ;
- le frontend charge correctement ;
- register → login → `/api/auth/me` fonctionne ;
- la création d'un livre persiste dans Cloud SQL ;
- une migration Alembic est bien enregistrée dans `alembic_version`.

## 9. Sécurité et coûts

Ne jamais placer `DATABASE_URL`, `GEMINI_API_KEY` ou `JWT_SECRET_KEY` dans `cloudbuild.yaml`, `.env` committé ou les images.

Le pipeline est conçu pour un projet sans client : aucune instance Cloud Run minimale, aucune HA PostgreSQL et aucun composant réseau coûteux ne sont activés par défaut.

Le principal coût fixe est Cloud SQL. Cloud Run, Artifact Registry et Cloud Build restent proportionnels à l'utilisation pour un trafic faible.

## 10. Évolution future

Lorsque Book aura de la traction :

1. augmenter la taille Cloud SQL ;
2. activer les backups/PITR et la HA si nécessaire ;
3. augmenter les limites Cloud Run ;
4. ajouter un domaine personnalisé et HTTPS applicatif ;
5. ajouter monitoring/alerting plus poussé ;
6. uniquement si nécessaire, introduire des composants réseau ou de scaling supplémentaires.

Cette migration d'infrastructure ne modifie pas la roadmap fonctionnelle de Book.
