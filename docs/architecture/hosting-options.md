# Stratégie d'hébergement — AI Book Loop / Manuscript Studio

## 1. Architecture de référence

**Google Cloud est désormais la plateforme de production de référence et la seule plateforme nécessaire au déploiement applicatif.**

| Composant | Service | Rôle |
| :--- | :--- | :--- |
| Frontend | Cloud Run | Application Next.js |
| Backend | Cloud Run | API FastAPI |
| Base de données | Cloud SQL PostgreSQL | Persistance durable |
| Images | Artifact Registry | Images Docker |
| Secrets | Secret Manager | Secrets applicatifs |
| Migrations | Cloud Run Job + Alembic | Évolution du schéma |
| CI/CD | GitHub Actions + Cloud Build | Validation puis déploiement |
| Observabilité | Cloud Logging / Monitoring | Logs et supervision |

La région de référence est `europe-west1`.

La description détaillée et les décisions associées sont documentées dans [`gcp-architecture.md`](./gcp-architecture.md).

## 2. Pourquoi une plateforme unique

Le produit est encore au stade MVP. Une architecture multi-plateforme comme Vercel + Cloud Run + Supabase est techniquement viable mais ajoute des interfaces opérationnelles sans bénéfice nécessaire à ce stade.

Le regroupement sur GCP permet de :

- réduire le nombre de plateformes à administrer ;
- centraliser IAM, secrets, logs et déploiements ;
- simplifier les problèmes de domaines et d'authentification ;
- conserver une architecture capable d'évoluer avec le produit.

Cette décision est pragmatique et pourra être réévaluée si un fournisseur spécialisé apporte un avantage réel et mesurable.

## 3. Philosophie de coût

Le trafic initial pouvant être très faible, l'infrastructure est volontairement minimale :

- Cloud Run scale-to-zero ;
- petite instance Cloud SQL sans HA ;
- pas de GKE ;
- pas de Load Balancer dédié ;
- pas de Redis/Memorystore ;
- pas de réseau VPC complexe ;
- une seule région.

Le coût fixe accepté est principalement celui de PostgreSQL persistant. Les services serverless doivent rester arrêtables lorsqu'ils ne sont pas utilisés.

## 4. Alternatives

### Vercel + Cloud Run + PostgreSQL managé

Écartée comme architecture de référence pour limiter le nombre de plateformes et la complexité cross-domain. Elle reste techniquement compatible avec le produit si une contrainte future le justifie.

### VPS + Docker Compose

Pertinent pour minimiser certains coûts fixes, mais implique davantage de responsabilités opérationnelles et de maintenance.

### GKE / Kubernetes

Écarté car surdimensionné pour le trafic et les besoins actuels.

## 5. Persistance

**PostgreSQL est la seule base supportée par l'application.**

Cloud SQL est utilisé en production afin de conserver les checkpoints du workflow durable, les versions immuables de chapitres et le Canon entre les redémarrages des conteneurs.

Alembic est la source de vérité des migrations de schéma.

## 6. Déploiement

Les branches et Pull Requests passent par le CI. La production est déclenchée explicitement par `release` : Cloud Build construit les images, publie dans Artifact Registry, exécute les migrations puis déploie les services Cloud Run.

Aucun déploiement de production ne doit être déclenché simplement par l'ouverture ou la mise à jour d'une Pull Request.

## 7. Évolution

Le choix GCP ne modifie pas la roadmap fonctionnelle. L'infrastructure sera renforcée uniquement lorsque les besoins réels le justifieront : capacité PostgreSQL, haute disponibilité, réseau, limites Cloud Run ou architecture distribuée.
