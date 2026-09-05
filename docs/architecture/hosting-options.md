# Stratégie & options d'hébergement — AI Book Loop / Manuscript Studio

Ce document décrit les options d'hébergement compatibles avec l'architecture actuelle. **PostgreSQL est la seule base de données supportée** par l'application.

## 1. Architecture recommandée

Pour le MVP et les premières validations clients, la cible est volontairement mono-plateforme : **Google Cloud**.

| Composant | Service GCP | Rôle |
| :--- | :--- | :--- |
| Frontend | Cloud Run | Next.js |
| Backend | Cloud Run | FastAPI |
| Base de données | Cloud SQL | PostgreSQL persistant |
| Images | Artifact Registry | Images Docker |
| Secrets | Secret Manager | Secrets runtime |
| Migrations | Cloud Run Job | Alembic |
| CI/CD | Cloud Build | Déploiement depuis GitHub |

Tout est initialement déployé dans `europe-west1`.

## 2. Pourquoi GCP uniquement

Le produit n'a pas besoin de trois plateformes dès le MVP. Centraliser frontend, backend, PostgreSQL, secrets et déploiement sur GCP réduit les intégrations, les problèmes de réseau inter-fournisseurs et la charge opérationnelle.

Le frontend et le backend restent deux services Cloud Run indépendants afin de conserver une séparation claire des responsabilités.

## 3. Profil de coût MVP

L'objectif est de pouvoir fonctionner avec **zéro client** sans infrastructure disproportionnée :

- Cloud Run : `min=0` ;
- Cloud SQL : petite instance shared-core sans HA au départ ;
- Artifact Registry : images minimales ;
- Secret Manager : quelques secrets ;
- Cloud Build : déclenché sur `release` ;
- aucun GKE, Load Balancer, Memorystore ou Cloud NAT au départ.

La montée en charge se fait ensuite par augmentation des ressources, sans changement de modèle applicatif.

## 4. Configuration

La configuration applicative passe par `DATABASE_URL` pour PostgreSQL. Les formes `postgres://`, `postgresql://` et `postgresql+psycopg://` sont acceptées par la composition root et le repository PostgreSQL.

Les secrets runtime sont injectés depuis Secret Manager.

Le CI utilise PostgreSQL 16 afin de rapprocher les tests automatisés de la persistance de production. Alembic est la source de vérité du schéma en environnement déployé.

## 5. Alternatives

### VPS

Un VPS peut héberger frontend, backend et PostgreSQL avec Docker Compose et peut réduire le coût fixe. En contrepartie, il faut gérer soi-même les mises à jour, backups, sécurité, monitoring et récupération après incident.

Cette option reste possible pour un futur environnement très économique, mais elle n'est pas la cible de production actuelle.

### Autres PostgreSQL managés

Neon, Supabase ou un autre fournisseur PostgreSQL restent techniquement compatibles avec l'application grâce à `DATABASE_URL`. Ils ne sont toutefois pas retenus pour la cible actuelle : l'objectif est une infrastructure GCP unique.

## 6. Suite technique

Le passage à GCP ne modifie pas la roadmap fonctionnelle. Les prochaines priorités restent le Context Builder, la robustesse du Canon et les tests E2E/concurrence.
