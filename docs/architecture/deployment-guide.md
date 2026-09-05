# Guide de Déploiement Production : Vercel (Frontend) + GCP Cloud Run (Backend) + Supabase (PostgreSQL)

Ce guide détaille le processus complet et les bonnes pratiques DevOps pour déployer l'application **AI Book Loop / Manuscript Studio**.

---

## 1. Audit & Bonnes Pratiques Architecture DevOps

### A. Communication Cross-Domain & Cookies d'Authentification
- Le frontend étant hébergé sur Vercel (`*.vercel.app`) et le backend sur Cloud Run (`*.a.run.app`), les domaines sont distincts.
- **Cookies JWT** : pour autoriser l'envoi du cookie de session d'un domaine à un autre, définissez sur Cloud Run :
  - `AUTH_COOKIE_SECURE=true` (requis pour HTTPS)
  - `AUTH_COOKIE_SAMESITE=none` (requis pour l'envoi cross-origin)
  - `CORS_ALLOWED_ORIGINS=["https://votre-app.vercel.app"]`.

### B. Sécurité du Conteneur Cloud Run
- Le `Dockerfile` fourni utilise un **multi-stage build** et s'exécute sous un utilisateur non-root (`appuser`).
- Uvicorn est configuré avec `--proxy-headers` et `--forwarded-allow-ips='*'` pour transmettre correctement les en-têtes HTTPS à FastAPI derrière Cloud Run.
- L'application expose `GET /health` comme endpoint de liveness léger, sans dépendance à Gemini ou à une session utilisateur.

---

## 2. Étapes de Déploiement

### Étape 1 : Base de Données — Supabase (PostgreSQL)
1. Créez un projet sur Supabase.
2. Dans **Project Settings** > **Database**, récupérez l'URI de connexion **Connection Pooler** (Mode Transaction - port 6543) :
   `postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`

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
4. Déployez le conteneur sur Cloud Run avec les noms de variables réellement consommés par `Settings` :
   ```bash
   gcloud run deploy book-loop-api \
     --image gcr.io/[VOTRE_PROJECT_ID_GCP]/book-loop-api:latest \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --set-env-vars '^||^DATABASE_URL=postgresql://...||GEMINI_API_KEY=...||AUTH_SECRET_KEY=...||AUTH_COOKIE_SECURE=true||AUTH_COOKIE_SAMESITE=none||CORS_ALLOWED_ORIGINS=["https://votre-app.vercel.app"]'
   ```

   Le séparateur `||` évite les collisions avec les virgules présentes dans les valeurs JSON et permet de conserver l'URL PostgreSQL telle quelle.

5. Vérifiez le backend avant de configurer Vercel :
   ```bash
   curl https://book-loop-api-xxx-ew.a.run.app/health
   ```
   Résultat attendu :
   ```json
   {"status":"ok"}
   ```
6. Copiez l'URL HTTPS attribuée par Cloud Run.

### Étape 3 : Frontend UI — Vercel (Next.js)

1. Connectez le projet sur Vercel.
2. Définissez :
   - **Root Directory** : `web`
   - **Framework Preset** : Next.js
3. Ajoutez :
   - `NEXT_PUBLIC_API_URL` = URL HTTPS du backend Cloud Run
4. Déployez.

---

## 3. Vérification & Tests

1. **Liveness Cloud Run** : `GET /health` doit retourner HTTP 200 et `{"status":"ok"}`.
2. **OpenAPI** : ouvrez `/docs` sur l'URL Cloud Run.
3. **Authentification** : testez register → login → `/api/auth/me` depuis le frontend Vercel.
4. **Persistance** : vérifiez la création d'un livre dans Supabase PostgreSQL.
5. **Cross-origin** : vérifiez que le cookie de session est bien conservé entre Vercel et Cloud Run.
