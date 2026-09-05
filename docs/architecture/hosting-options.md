# Stratégie & options d'hébergement — AI Book Loop / Manuscript Studio

Ce document décrit les options d'hébergement compatibles avec l'architecture actuelle. **PostgreSQL est désormais la seule base de données supportée** par l'application ; SQLite n'est plus un backend de persistance.

## 1. Architecture actuelle

- **Frontend** : Next.js / TypeScript (`web/`).
- **Backend** : FastAPI / Python (`book_loop/`).
- **Workflow** : génération de chapitre durable et reprenable, avec état persistant.
- **Persistance** : PostgreSQL via `DATABASE_URL`.
- **LLM** : Google Gemini.

Le choix PostgreSQL est volontaire : il permet d'utiliser les mêmes sémantiques SQL en développement, CI, staging et production, notamment pour les transactions, contraintes et opérations concurrentes du workflow et du Canon.

## 2. Option recommandée : Vercel + Cloud Run + PostgreSQL managé

| Composant | Service possible | Rôle |
| :--- | :--- | :--- |
| Frontend | Vercel | Déploiement Next.js et CDN |
| Backend | GCP Cloud Run | API FastAPI et workers HTTP |
| Base de données | Neon / Supabase / Cloud SQL | PostgreSQL persistant |

Cloud Run possède un système de fichiers éphémère : une base locale n'est donc pas adaptée au stockage durable de l'application. PostgreSQL élimine cette dépendance au disque local et permet de conserver les checkpoints de workflow et les données du Canon entre les redémarrages.

Pour un faible trafic, un PostgreSQL managé avec une offre gratuite ou peu coûteuse peut convenir. Pour une charge plus importante, Cloud SQL ou une offre PostgreSQL managée équivalente fournit une capacité et une supervision supérieures.

## 3. Alternative : VPS

Un VPS peut héberger le frontend, le backend et PostgreSQL avec Docker Compose. Cette option reste pertinente pour minimiser le coût fixe et garder un serveur actif en permanence.

**PostgreSQL doit néanmoins rester la base utilisée par l'application** : on ne propose plus de variante SQLite sur VPS.

## 4. Configuration

La configuration applicative passe par une seule variable :

```text
DATABASE_URL=postgresql://user:password@host:5432/database
```

Les formes `postgres://`, `postgresql://` et `postgresql+psycopg://` sont acceptées par la composition root et le repository PostgreSQL.

Le CI utilise PostgreSQL 16 afin de rapprocher au maximum les tests automatisés de la persistance de production.

## 5. Suite technique

Avant C3 (Context Builder), la priorité est :

1. terminer la suppression des derniers usages SQLite ;
2. stabiliser les tests PostgreSQL et la concurrence ;
3. introduire **Alembic** pour les migrations de schéma ;
4. documenter le bootstrap PostgreSQL local et les variables d'environnement ;
5. puis poursuivre le Context Builder et l'enrichissement du pipeline Canon.

Le passage à PostgreSQL ne modifie pas la roadmap fonctionnelle : il simplifie uniquement la couche d'infrastructure en supprimant un backend divergent.
