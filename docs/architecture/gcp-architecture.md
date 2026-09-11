# Architecture de déploiement GCP

## 1. Décision

AI Book Loop adopte **Google Cloud comme plateforme d'hébergement unique pour la production**.

La cible de référence est :

```text
GitHub
  │
  └── Cloud Build (déploiement sur release)
        ├── Artifact Registry
        │     ├── book-loop-api
        │     └── book-loop-web
        │
        ├── Cloud Run — API FastAPI
        ├── Cloud Run — Analysis Worker
        ├── Cloud Run — Frontend Next.js
        │
        └── Cloud Run Job — migrations Alembic
                    │
                    ▼
              Cloud SQL PostgreSQL

Secret Manager ──► Cloud Run / Cloud Run Job
Cloud Logging / Monitoring ──► observabilité
```

Cette décision remplace la cible historique **Vercel + Cloud Run + Supabase**. Le produit reste toutefois indépendant du fournisseur : la séparation frontend/backend, la persistance PostgreSQL et les interfaces applicatives ne dépendent pas d'un service GCP spécifique.

## 2. Pourquoi GCP uniquement ?

Le choix est principalement pragmatique : réduire le nombre de plateformes à administrer, conserver backend, frontend, base de données, secrets, images et déploiement dans un même environnement, simplifier l'authentification et le diagnostic, et disposer d'une trajectoire de montée en charge sans réarchitecturer l'application.

## 3. Composants retenus

### 3.1 Cloud Run — Backend

FastAPI est déployé comme un service Cloud Run stateless.

Principes :

- scale-to-zero (`min instances = 0`) pour limiter le coût fixe ;
- aucune donnée durable dans le filesystem du conteneur ;
- endpoint `/health` indépendant de Gemini et d'une session utilisateur ;
- secrets injectés depuis Secret Manager ;
- PostgreSQL comme persistance applicative.

### 3.2 Cloud Run — Analysis Worker

Les analyses longues ne s'exécutent pas dans le cycle de vie d'une requête HTTP. L'API crée une entrée durable dans PostgreSQL et retourne `202 Accepted`. Un service Cloud Run séparé exécute `python -m book_loop.worker` et consomme la queue `analysis_jobs`.

Le worker est configuré avec une concurrence de `1` afin qu'une instance traite un job à la fois. Les jobs sont revendiqués transactionnellement avec `FOR UPDATE SKIP LOCKED`, protégés par un lease renouvelé par heartbeat, puis récupérables après expiration du lease.

Le worker n'est pas une seconde source de vérité : il orchestre l'exécution de jobs durables en utilisant les mêmes use cases et adaptateurs que l'API.

Voir [`async-analysis-jobs.md`](./async-analysis-jobs.md) et l'ADR 0009 pour les invariants de la queue.

### 3.3 Cloud Run — Frontend

Le frontend Next.js est conteneurisé et déployé sur Cloud Run.

En production, le navigateur appelle des chemins relatifs `/api/*` sur l'origine frontend. Next.js relaie ces requêtes vers `API_INTERNAL_URL`, ce qui évite de faire dépendre la session web d'un appel cross-origin direct à l'API.

### 3.4 Cloud SQL — PostgreSQL

Cloud SQL PostgreSQL est la base de production et le stockage durable des workflows, des jobs d'analyse et des données métier.

Configuration initiale volontairement frugale : petite instance partagée, une seule zone, pas de haute disponibilité au démarrage et stockage SSD minimal. Cette configuration est un point de départ, pas une cible de charge.

### 3.5 Artifact Registry

Deux images sont conservées dans Artifact Registry : `book-loop-api` et `book-loop-web`. Le worker utilise l'image API avec une commande d'entrée différente ; il n'a donc pas besoin d'une troisième image applicative.

### 3.6 Secret Manager

Les secrets applicatifs ne sont pas stockés dans Git. Les valeurs sensibles typiques sont `DATABASE_URL`, `GEMINI_API_KEY` et `AUTH_SECRET_KEY`.

### 3.7 Alembic / migrations

Les changements de schéma PostgreSQL sont gérés par Alembic. Les migrations sont exécutées comme une étape explicite du déploiement via un Cloud Run Job avant le déploiement des services applicatifs.

## 4. Stratégie de déploiement

La production est déclenchée par une release explicite. Cloud Build construit et pousse l'image API, exécute les migrations, déploie l'API et le worker, construit et déploie le frontend, puis vérifie les IAM publics et le CORS attendu.

```text
release
  │
  ▼
Cloud Build
  ├── build/push API image
  ├── migrate PostgreSQL
  ├── deploy API
  ├── deploy analysis worker
  ├── resolve API URL
  ├── build/deploy web with API_INTERNAL_URL
  └── verify IAM / CORS
```

Le CI GitHub reste une barrière de validation. Il ne remplace pas le pipeline Cloud Build de production.

## 5. Région

La région de référence est **`europe-west9` (Paris)**. Les principaux workloads sont co-localisés dans cette région autant que possible.

## 6. Réseau et exposition

Le MVP n'introduit volontairement pas GKE, Load Balancer dédié, VPC complexe, Cloud NAT, Redis/Memorystore ou architecture multi-région. L'API et le frontend sont publics ; le worker n'est pas publiquement invokable.

La sécurité applicative reste portée par FastAPI, l'authentification, les comptes de service, Secret Manager et les règles CORS.

## 7. Observabilité

Les logs et métriques d'infrastructure utilisent Cloud Logging et Cloud Monitoring. L'application conserve également son observabilité métier afin de suivre les exécutions de workflow, les jobs, les erreurs et les opérations importantes indépendamment du fournisseur.

## 8. Sécurité

Principes : aucun secret dans le repository ; comptes de service dédiés avec privilèges minimaux ; accès Cloud SQL limité aux workloads nécessaires ; HTTPS partout ; conteneurs non-root ; migrations contrôlées et versionnées ; CI obligatoire avant release ; worker non exposé publiquement.

## 9. Coût et philosophie d'exploitation

Le compromis MVP est : Cloud Run scale-to-zero pour l'API et le frontend, worker avec une capacité minimale pour traiter les analyses, petite instance Cloud SQL, une seule région et absence de composants toujours actifs supplémentaires. La montée en gamme est déclenchée par l'usage réel.

Le coût Gemini est traité séparément car il dépend directement de la consommation des workflows et analyses.

## 10. Alternatives écartées

### Vercel + Cloud Run + Supabase

Architecture techniquement valide, mais trois plateformes augmentent le nombre de points de configuration et de diagnostic et compliquent l'authentification cross-domain.

### VPS + Docker Compose

Moins cher à très petite échelle, mais davantage de responsabilités opérationnelles et une moins bonne trajectoire de montée en charge.

### Kubernetes / GKE

Surdimensionné pour le stade actuel. La queue PostgreSQL + worker Cloud Run couvre les besoins actuels sans introduire d'orchestrateur supplémentaire.

## 11. Évolution prévue

L'évolution d'infrastructure doit rester pilotée par les contraintes réelles : augmenter les ressources Cloud SQL, renforcer sauvegardes et disponibilité, ajuster les limites Cloud Run/worker, puis ajouter des composants réseau ou de queue spécialisés uniquement si PostgreSQL ne suffit plus.

**Principe directeur : ne pas payer ni opérer une complexité dont le produit n'a pas encore besoin.**
