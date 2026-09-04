# Strategy & Options d'Hébergement — AI Book Loop / Manuscript Studio

Ce document analyse les options d'hébergement pour le projet **AI Book Loop** (Manuscript Studio), en tenant compte de sa structure fullstack (**Frontend Next.js** + **Backend Python FastAPI** + **Stockage SQLite/PostgreSQL**), d'un objectif budgétaire **très bas coût (0 € à 15 € / mois)** et de l'**absence de clients actifs** dans la phase actuelle.

---

## 1. Contexte & Contraintes Principales

1. **Architecture Applicative** :
   - **Frontend UI (`web/`)** : Application Next.js (App Router), TypeScript, Tailwind CSS v4, React Flow.
   - **Backend API (`book_loop/`)** : API REST Python (FastAPI), orchestration de workflows (LangGraph), intégration LLM (Google Gemini).
   - **Persistance** : SQLite par défaut (stockage local de fichier), évolutif vers PostgreSQL administré.

2. **Phase Projet & Trafic** :
   - Phase de validation de concept et de démo / développement.
   - Aucun client payant ni trafic continu pour le moment.
   - Besoin clé : coût fixe minimal ou nul, tout en conservant une réactivité décente pour les démos sans coupure de service intempestive.

3. **Contrainte Budgétaire** :
   - **Cible** : 0 €/mois (Gratuit) à ~5–15 €/mois grand maximum.
   - **Principe** : Ne pas payer pour du compute inutilisé, mais minimiser le *cold start* (temps de réveil) si possible.

---

## 2. Comparatif des Options d'Hébergement

### Option A : 100% Serverless / Serverless-like (Vercel + GCP Cloud Run)

| Composant | Service | Offre / Prix | Avantages | Inconvénients |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | **Vercel** (Hobby) | **0 € / mois** | • Déploiement Git instantané<br>• CDN global ultra-rapide<br>• Support Next.js natif parfait | • Limité à un usage non-commercial strict |
| **Backend** | **GCP Cloud Run** (Pay-as-you-go) | **~0 € à 2 € / mois** | • 2 millions de requêtes/mois gratuites<br>• Scaling à zéro (0 € si pas de trafic)<br>• Cold start très rapide (1-3s) | • Stockage local éphémère (nécessite une BDD externe comme Postgres ou Cloud Storage) |

- **Coût mensuel total (hors BDD)** : **0 € à ~2 € / mois**
- **Verdict** : Excellente combinaison pour démarrer avec zéro coût fixe.

---

### Option B : VPS Unique Tout-en-Un (Hetzner / Scaleway / DigitalOcean) — *Recommandé pour ~5–7 €/mois*

Dans cette option, le Frontend Next.js, le Backend FastAPI Python et la base SQLite (ou un container PostgreSQL) sont hébergés sur la même instance virtuelle VPS via **Docker Compose** ou **Dokku / CapRover** (PaaS auto-hébergé).

| Hébergeur | Offre / Specs | Prix | Avantages | Inconvénients |
| :--- | :--- | :--- | :--- | :--- |
| **Hetzner Cloud** | Cloud Server CAX11 (2 vCPU ARM, 4 GB RAM, 40 GB NVMe) | **~4,50 € / mois** | • Rapport performance/prix imbattable<br>• Pas de mise en veille (serveur 24/7)<br>• SQLite sur NVMe très performant<br>• Localisation Europe (Allemagne/Finlande) | • Nécessite un peu de configuration initiale (Docker, Traefik/Nginx, SSL Certbot) |
| **Scaleway** | Stardust ou DEV1-S (1-2 vCPU, 2 GB RAM) | **~3,00 € à 6,00 € / mois** | • Hébergeur Français souverain (RGPD)<br>• Performance constante | • Bande passante/disque limités sur Stardust |
| **DigitalOcean** | Basic Droplet (1 vCPU, 1 GB RAM) | **~6,00 $ / mois** | • Très bonne documentation et intégration GitHub Actions | • Un peu plus cher à specs égales qu'Hetzner |

- **Coût mensuel total** : **~4,50 € à 6,00 € / mois**
- **Verdict** : **La meilleure solution à très bas coût pour une expérience 100% active sans aucun cold start**, avec SQLite persistant sur disque local et déploiement simplifié via Docker.

---

### Option C : PaaS Unifié (Fly.io ou Railway)

| Service | Architecture | Offre / Prix estimé | Avantages | Inconvénients |
| :--- | :--- | :--- | :--- | :--- |
| **Fly.io** | Containers distribués (Frontend + Backend + Volume SQLite Litestream) | **~5 € à 10 € / mois** (selon RAM et volumes) | • Volumes persistant natifs pour SQLite<br>• Déploiement via `flyctl` très simple<br>• Scaling automatique proche des utilisateurs | • Facturation à la consommation avec petit crédit gratuit épuisé rapidement si 24/7 |
| **Railway** | Apps séparées + Postgres si besoin | **~5 € / mois** (Plan Hobby) | • Interface utilisateur d'une simplicité extrême<br>• CI/CD natif sur branche Git | • Coût grimpe rapidement si plusieurs containers tournent 24/7 |

- **Coût mensuel total** : **~5 € à 10 € / mois**
- **Verdict** : Très bonne alternative moderne si l'on souhaite une expérience PaaS sans gérer la configuration système d'un VPS.

---

## 3. Focus Architecture : Vercel (Front) + GCP Cloud Run (Back) + PostgreSQL

Cette architecture est particulièrement adaptée lorsque le serveur applicatif Cloud Run fonctionne en **Serverless (scaling à zéro)**. Dans Cloud Run, le système de fichiers local est **éphémère** : à chaque redémarrage ou mise en veille du conteneur, les fichiers créés localement (comme une base SQLite) sont perdus.

**Passer sur PostgreSQL est donc la démarche recommandée et nécessaire pour un déploiement Cloud Run.**

### Options de PostgreSQL Administré (Serverless / Low-Cost)

| Solution Postgres | Type d'offre | Prix estimé | Avantages | Inconvénients |
| :--- | :--- | :--- | :--- | :--- |
| **Neon.tech** | Serverless Postgres | **0 € / mois** (Free tier)<br>*(0.5 GiB stockage, branchement Git)* | • Scaling à zéro automatique (parfait avec Cloud Run)<br>• Connection pooling natif (PgBouncer intégré)<br>• Support natif de `pgvector` si besoin futur | • Légère latence au premier réveil si inactif |
| **Supabase Postgres** | Database-as-a-Service | **0 € / mois** (Free tier)<br>*(500 MB stockage)* | • Inclus Auth, Storage S3, Realtime, `pgvector`<br>• Dashboard d'administration complet | • Mise en pause automatique après 1 semaine sans requêtes |
| **GCP Cloud SQL** | Instance managée GCP (`db-f1-micro`) | **~7 € à 12 € / mois** | • Intégration GCP native parfaite (Cloud SQL Auth Proxy / IP Privée)<br>• Pas de mise en veille, performances stables | • Instance payante 24/7 même si non utilisée |

---

### Impact Architectural & Technique du Passage à PostgreSQL

1. **Changement de Connexion (Zero Code Break)** :
   - L'architecture de `book_loop` utilise un pattern Port/Adaptateur (`BookRepository`).
   - L'ORM SQLAlchemy gère déjà les modèles. Il suffit d'adapter la chaîne de connexion dans `DATABASE_URL` :
     - SQLite : `sqlite:///./book_loop.db`
     - PostgreSQL : `postgresql+psycopg://user:password@host:5432/dbname`

2. **Gestion du Pooling de Connexions en Serverless** :
   - Cloud Run crée et détruit des conteneurs à la demande.
   - **Recommandation** : Activer le connection pooling côté BDD (Pooler Neon ou PgBouncer) ou régler SQLAlchemy sur `NullPool` / taille de pool petite (`pool_size=5`, `max_overflow=10`) pour éviter la saturation du nombre de connexions ouvertes.

3. **Incrément des Coûts Globaux (Vercel + Cloud Run + Postgres)** :
   - **Combinaison 100% Free / Low-Cost** : Vercel (0€) + GCP Cloud Run (~0-1€) + Neon Postgres (0€) = **0 € à 1 € / mois**.
   - **Combinaison GCP Managed** : Vercel (0€) + GCP Cloud Run (~0-1€) + GCP Cloud SQL db-f1-micro (~9€) = **~9 € à 10 € / mois**.

---

## 4. Matrice Comparative des Solutions Globale

| Critère | Option A (Vercel + Cloud Run + Neon Postgres) | Option B (VPS Hetzner / Scaleway + Docker Compose) | Option C (Fly.io / Railway) |
| :--- | :--- | :--- | :--- |
| **Coût Mensuel** | **0 € à 1 €** | **~4,50 € à 6 €** | **~5 € à 10 €** |
| **Base de données** | PostgreSQL (Neon / Supabase) | SQLite sur NVMe ou Postgres Docker | SQLite / Postgres |
| **Cold Start / Latence** | Très faible (Cloud Run 1-2s + Neon 1-2s si inactif) | **Nul (Serveur actif 24/7)** | Faible à nul |
| **Persistance** | Managed & Backups automatiques | Disque local VPS (Backups à configurer) | Volume managé |
| **Effort de déploiement** | Très faible (CI/CD Git) | Moyen (Docker Compose une fois) | Faible (`fly deploy`) |

---

## 5. Recommandation Stratégique Finale

Si vous choisissez l'association **Vercel (Front) + GCP Cloud Run (Back)** :

1. **Infrastructures conseillées** :
   - **Frontend** : Vercel (Gratuit)
   - **Backend** : GCP Cloud Run (Pay-as-you-go, < 1 €/mois sans trafic)
   - **Base de données** : **Neon.tech (PostgreSQL Serverless Gratuit)** ou **Supabase**.
2. **Pourquoi Neon + Cloud Run ?**
   - Cloud Run a un système de fichier éphémère : SQLite en local sur Cloud Run perdrait ses données à chaque réveil.
   - Neon s'éteint et se réveille à la volée comme Cloud Run, ce qui conserve un budget **strictement égal à 0 € / mois** tant qu'il n'y a pas de client.
   - L'isolation des couches dans le code Python (`book_loop`) rend la transition de SQLite vers Postgres transparente via une simple variable d'environnement `DATABASE_URL`.
