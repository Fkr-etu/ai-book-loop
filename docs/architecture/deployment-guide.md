# Guide de Déploiement Production : Vercel (Frontend) + GCP Cloud Run (Backend) + Supabase (PostgreSQL)

Ce guide détaille le processus complet et les bonnes pratiques DevOps pour déployer l'application **AI Book Loop / Manuscript Studio**.

---

## 1. Audit & Bonnes Pratiques Architecture DevOps

### A. Communication Cross-Domain & Cookies d'Authentification
- Le frontend étant hébergé sur Vercel (`*.vercel.app`) et le backend sur Cloud Run (`*.a.run.app`), les domaines sont distincts.
- **Cookies JWT** : Pour autoriser l'envoi du cookie de session d'un domaine à un autre, vous devez définir sur Cloud Run :
  - `AUTH_COOKIE_SECURE=true` (Requis pour HTTPS)
  - `AUTH_COOKIE_SAMESITE=none` (Requis pour l'envoi cross-origin)
  - `CORS_ORIGINS=https://votre-app.vercel.app` (Sans `/` final).

### B. Securité du Conteneur Cloud Run
- Le `Dockerfile` fourni utilise un **multi-stage build** et s'exécute sous un utilisateur non-root (`appuser`), garantissant la conformité aux exigences de sécurité Cloud Run / CIS Benchmarks.
- Uvicorn est configuré avec `--proxy-headers` et `--forwarded-allow-ips='*'` pour transmettre correctement les IP clientes réelles et les en-têtes HTTPS à FastAPI derrière le Load Balancer Google Cloud.

---

## 2. Étapes de Déploiement

### Étape 1 : Base de Données — Supabase (PostgreSQL)
1. Créez un projet sur [Supabase](https://supabase.com).
2. Dans **Project Settings** > **Database**, récupérez l'URI de connexion **Connection Pooler** (Mode Transaction - port 6543) :
   `postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`

---

### Étape 2 : Backend API — GCP Cloud Run (Python FastAPI)

1. Authentifiez-vous sur Google Cloud :
   ```bash
   gcloud auth login
   gcloud config set project [VOTRE_PROJECT_ID_GCP]
   ```
2. Activez les services requis :
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```
3. Buildez l'image Docker multi-stage avec Cloud Build :
   ```bash
   gcloud builds submit --tag gcr.io/[VOTRE_PROJECT_ID_GCP]/book-loop-api:latest .
   ```
4. Déployez le conteneur sur Cloud Run :
   ```bash
   gcloud run deploy book-loop-api \
     --image gcr.io/[VOTRE_PROJECT_ID_GCP]/book-loop-api:latest \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --set-env-vars "DATABASE_URL=postgresql://...", "GEMINI_API_KEY=...", "JWT_SECRET_KEY=cle_secrete_32_chars_min", "AUTH_COOKIE_SECURE=true", "AUTH_COOKIE_SAMESITE=none", "CORS_ORIGINS=https://votre-app.vercel.app"
   ```
5. Copiez l'URL HTTPS attribuée par Cloud Run (`https://book-loop-api-xxx-ew.a.run.app`).

---

### Étape 3 : Frontend UI — Vercel (Next.js)

1. Connectez votre projet sur [Vercel](https://vercel.com).
2. Définissez les paramètres du projet :
   - **Root Directory** : `web`
   - **Framework Preset** : Next.js
3. Ajoutez la variable d'environnement :
   - `NEXT_PUBLIC_API_URL` = `https://book-loop-api-xxx-ew.a.run.app`
4. Déployez.

---

## 3. Vérification & Tests Healthcheck

1. Testez le backend via `/docs` (Swagger OpenAPI) : `https://book-loop-api-xxx-ew.a.run.app/docs`
2. Testez le workflow d'authentification et de création de livre sur le frontend Vercel.
