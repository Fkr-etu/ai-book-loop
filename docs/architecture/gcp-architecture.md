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
        │
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

Le choix est principalement pragmatique :

- réduire le nombre de plateformes à administrer ;
- conserver backend, frontend, base de données, secrets, images et déploiement dans un même environnement ;
- éviter les problèmes opérationnels liés aux domaines et cookies cross-origin entre Vercel et Cloud Run ;
- simplifier le diagnostic, les logs et la gestion des permissions ;
- disposer d'une trajectoire de montée en charge sans devoir réarchitecturer l'application ;
- garder une configuration reproductible via Cloud Build et Alembic.

Le choix n'est **pas** motivé par un besoin de services GCP avancés. L'objectif initial est au contraire de rester minimal.

## 3. Composants retenus

### 3.1 Cloud Run — Backend

FastAPI est déployé comme un service Cloud Run stateless.

Principes :

- scale-to-zero (`min instances = 0`) pour éviter un coût fixe lorsque le produit n'est pas utilisé ;
- nombre maximal d'instances limité au démarrage ;
- aucune donnée durable dans le filesystem du conteneur ;
- endpoint `/health` indépendant de Gemini et d'une session utilisateur ;
- secrets injectés depuis Secret Manager ;
- PostgreSQL comme seule persistance applicative.

Cloud Run est adapté au workflow durable car l'état métier et les checkpoints sont stockés dans PostgreSQL, et non dans la mémoire du conteneur.

### 3.2 Cloud Run — Frontend

Le frontend Next.js est également conteneurisé et déployé sur Cloud Run.

Ce choix évite de maintenir une plateforme frontend distincte et permet de faire évoluer ultérieurement la stratégie de rendu sans changer de fournisseur.

Le frontend reçoit l'URL publique de l'API via `NEXT_PUBLIC_API_URL` au build/déploiement selon la configuration retenue.

### 3.3 Cloud SQL — PostgreSQL

Cloud SQL PostgreSQL est la base de production.

Configuration initiale volontairement frugale :

- instance partagée de petite taille (`db-f1-micro`) ;
- une seule zone ;
- pas de haute disponibilité au démarrage ;
- stockage SSD minimal ;
- sauvegardes/configuration adaptées au stade MVP.

Le coût fixe de PostgreSQL est accepté car la base doit rester persistante alors que Cloud Run peut être arrêté lorsqu'il n'y a aucune requête.

Cette configuration est un **point de départ**, pas une cible de charge. Si l'usage augmente, la capacité, les sauvegardes et la disponibilité pourront être renforcées sans modifier le modèle applicatif.

### 3.4 Artifact Registry

Deux images sont conservées dans Artifact Registry :

- `book-loop-api` ;
- `book-loop-web`.

Le registre est placé dans la même région que les workloads afin de limiter les transferts inutiles.

### 3.5 Secret Manager

Les secrets applicatifs ne sont pas stockés dans Git ni dans les manifests en clair.

Les valeurs sensibles typiques sont :

- `DATABASE_URL` ;
- `GEMINI_API_KEY` ;
- `AUTH_SECRET_KEY`.

Cloud Run et le job de migration reçoivent ces secrets via les mécanismes natifs GCP.

### 3.6 Alembic / migrations

Les changements de schéma PostgreSQL sont gérés par Alembic.

Les migrations sont exécutées comme une étape explicite du déploiement, idéalement via un **Cloud Run Job**, avant de rendre la nouvelle version applicative active.

Elles ne doivent pas être exécutées automatiquement à chaque démarrage d'un conteneur Cloud Run : plusieurs instances pourraient sinon tenter de migrer simultanément et le démarrage deviendrait dépendant de l'état de la base.

## 4. Stratégie de déploiement

La production est déclenchée par une release explicite.

```text
feature branch ──► CI
       │
       └──► Pull Request ──► CI
                              │
main ─────────────────────────┤
                              ▼
                         release tag/event
                              │
                              ▼
                         Cloud Build
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
          build API/web              migrations
                 │                         │
                 ▼                         ▼
        Artifact Registry             Cloud SQL
                 │
                 ▼
            Cloud Run
```

Le CI GitHub reste une barrière de sécurité et de validation. Il ne devient pas le système de déploiement de production.

## 5. Région

La région de référence est **`europe-west1`**.

Tous les composants principaux sont regroupés dans cette région autant que possible :

- Cloud Run API ;
- Cloud Run frontend ;
- Cloud SQL ;
- Artifact Registry ;
- jobs de migration.

Cette co-localisation réduit la complexité réseau et les coûts de transfert.

## 6. Réseau et exposition

Le MVP n'introduit volontairement pas :

- Google Kubernetes Engine ;
- Load Balancer dédié ;
- VPC complexe ;
- Cloud NAT ;
- Redis / Memorystore ;
- architecture multi-région.

Cloud Run fournit les endpoints HTTPS publics nécessaires. La sécurité applicative reste portée par FastAPI, l'authentification, les secrets et les règles CORS.

Une architecture réseau plus complexe pourra être ajoutée lorsque les contraintes réelles du produit la justifieront.

## 7. Observabilité

Les logs applicatifs et événements d'observabilité utilisent les services GCP adaptés, notamment Cloud Logging et Cloud Monitoring.

L'application conserve également son modèle d'observabilité métier afin de pouvoir suivre les exécutions de workflow, les erreurs et les opérations importantes indépendamment du fournisseur.

## 8. Sécurité

Principes :

1. aucun secret dans le repository ;
2. comptes de service dédiés avec privilèges minimaux ;
3. accès Cloud SQL limité aux workloads nécessaires ;
4. HTTPS partout ;
5. conteneurs non-root ;
6. migrations contrôlées et versionnées ;
7. CI obligatoire avant release.

## 9. Coût et philosophie d'exploitation

Le projet étant encore au stade MVP, l'infrastructure doit rester proportionnée à son usage réel.

Le compromis retenu est donc :

- **Cloud Run** : scale-to-zero ;
- **Cloud SQL** : petite instance persistante ;
- pas de HA initiale ;
- pas de composants toujours actifs supplémentaires ;
- montée en gamme uniquement lorsque l'usage le justifie.

Le coût de Gemini est traité séparément car il dépend directement de la consommation du workflow d'écriture et ne constitue pas un coût d'infrastructure fixe.

## 10. Alternatives écartées

### Vercel + Cloud Run + Supabase

Architecture techniquement valide, mais trois plateformes augmentent le nombre de points de configuration et de diagnostic. Elle imposait également une gestion cross-domain plus délicate pour l'authentification.

### VPS + Docker Compose

Moins cher à très petite échelle et simple conceptuellement, mais apporte davantage de responsabilités opérationnelles : mises à jour système, disponibilité, sauvegardes, supervision et montée en charge.

### Kubernetes / GKE

Surdimensionné pour le stade actuel. Il serait justifié par une complexité opérationnelle ou une charge que le produit n'a pas encore.

## 11. Évolution prévue

Cette décision ne modifie pas la roadmap fonctionnelle.

La prochaine évolution d'infrastructure sera déclenchée par les besoins réels :

1. augmenter les ressources Cloud SQL ;
2. renforcer sauvegardes et disponibilité ;
3. augmenter les limites Cloud Run ;
4. ajouter des composants réseau uniquement si nécessaire ;
5. envisager une architecture plus distribuée uniquement lorsque les contraintes de charge ou de fiabilité l'imposent.

**Principe directeur : ne pas payer ni opérer une complexité dont le produit n'a pas encore besoin.**
