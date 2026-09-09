# Audit Complet de l'Application Book Loop (SaaS)

**Date :** 9 Septembre 2026
**Auteur :** Jules, Lead Software Engineer & Architecte AI
**Cible :** Direction Produit & Équipe Tech / Investisseurs & Partenaires
**Statut :** Livrable Final (Incluant Analyse Économique & Go-To-Market)

---

## Synthèse Exécutive

Book Loop se positionne comme un **moteur de cohérence narrative et d'univers évolutifs pour créateurs** ("Keep your universe coherent, even as it grows and changes"). Son parti pris clé — **"L'IA propose, l'auteur décide"** — constitue un différenciateur fondamental face aux générateurs de texte génériques en plaçant la gouvernance du Canon au centre de la valeur produit.

L'application est construite sur une architecture moderne et propre : un backend Python FastAPI avec Clean/Hexagonal Architecture et un frontend Next.js App Router ("Manuscript Studio") riche en visualisations (React Flow pour les graphes de lore).

**Points forts majeurs :**
- Architecture hexagonale rigoureuse isolant le domaine métier des fournisseurs d'IA et de l'infrastructure.
- Moteur de cohérence hybride (LLM + règles déterministes Python spacy/LanguageTool) et graphes de connaissances factuels basés sur des assertions tridimensionnelles (Sujet, Prédicat, Objet) avec traçabilité d'extraits (Evidence).
- Grille tarifaire pragmatique (€19 / €39 par mois) alignée sur le coût des tokens LLM avec plafond d'unit economics sain (target COGS < 25%).
- Pipeline CI/CD solide avec tests unitaires, d'intégration, audit de dépendances strict et tests E2E Playwright.

**Risques et axes critiques identifiés :**
- **Dépendance bloquante à PostgreSQL dans la suite de tests :** Les tests API/Auth échouent si PostgreSQL n'est pas instancié en local (absence de fallback SQLite automatisé en environnement de développement).
- **Rupture d'onboarding sur les gros manuscrits :** Ingestion synchrone bloquante sans file d'attente (Task Queue/Celery) risquant d'atteindre le timeout HTTP Cloud Run (60s à 600s) lors de l'import de livres volumineux.
- **Risque d'inflation des coûts LLM sur les boucles de correction :** Risque de dégradation de la marge brute si les utilisateurs exécutent un grand nombre de boucles de réécriture/correction sans plafonnement strict par projet.

---

## 1. Architecture & Qualité du Code

### 1.1 Analyse de la Stack & Respect des Bonnes Pratiques
- **Backend Core (`book_loop/`) :** L'architecture respecte strictly les principes de la *Clean Architecture* / *Hexagonal Architecture*. La hiérarchie des dépendances est verrouillée : `CLI / Adaptateurs API -> Use Cases -> Domain / Ports <- Infrastructure`.
- **Injection de dépendances :** Centralisée dans `book_loop/infrastructure/container.py`. Le conteneur instancie proprement les Use Cases, les agents LLM (`WriterAgent`, `ReviewerAgent`, `OutlineAgent`) et les adaptateurs d'infrastructure (`PostgresCanonChangeRepository`, `PostgresWorkflowRunStore`).
- **Parsing et analyse textuelle :** Le découpage en chunks (`IngestDocument` dans `book_loop/application/use_cases/ingest_document.py`) s'appuie sur une fenêtre glissante déterministe respectant la ponctuation (`\n` et espaces). L'extraction d'assertions repose sur `LLMAssertionExtractor` et des règles déterministes dans `UnifiedConsistencyEngine`.
- **Frontend Studio (`web/`) :** Utilisation propre de Next.js App Router (TypeScript, Tailwind CSS v4). Modularité des composants (`StudioLayout`, `CanonImpactPanel`, `StudioBookSelector`) et intégration de React Flow (`@xyflow/react`) pour la cartographie des relations entre personnages/éléments de lore.

### 1.2 Exemples Précis Tirés du Repo
- `book_loop/infrastructure/container.py` (Lignes 69-72) : Levée d'exception stricte si `DATABASE_URL` n'est pas PostgreSQL :
  ```python
  if not self.settings.database_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg://")):
      raise ValueError("Unsupported DATABASE_URL; PostgreSQL is required (postgresql://...)")
  ```
- `book_loop/domain/models.py` : Modèles Pydantic v2 immutables et typés (`Assertion`, `CanonicalFact`, `Evidence`, `Conflict`, `Chapter`, `BookState`).
- `book_loop/application/use_cases/ingest_document.py` (Ligne 46-51) : Découpage déterministe et vérification d'offsets stricts pour éviter les décalages de surlignage dans l'interface UI :
  ```python
  if extracted.end_offset > len(chunk.content) or extracted.start_offset >= extracted.end_offset:
      raise ValueError("Extractor evidence offsets are invalid")
  ```

### 1.3 Dette Technique & Couverture de Tests
- **Problème de testabilité locale :** Bien que le repo contienne un mock repository SQLite (`SQLiteBookRepository`), le conteneur principal `Container` impose PostgreSQL. Cela empêche l'exécution simple de la suite de tests avec `pytest` sans conteneur Docker PostgreSQL actif (`connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused`).
- **Couverture de tests :** Très bonne couverture unitaire sur le domaine et les use cases, mais manque de tests d'intégration isolés avec une base en mémoire.

### 1.4 Les 3 Axes d'Amélioration Prioritaires
1. **Implémenter une abstraction SQLite/In-Memory pour les tests locaux :** Permettre au `Container` de basculer sur un dictionnaire ou SQLite en mémoire lorsque `APP_ENVIRONMENT=testing`, évitant la dépendance à une instance Postgres en local.
2. **Découpler le moteur d'extraction textuelle du LLM :** Intégrer une couche NLP déterministe hybride (ex: spaCy NER + Regex patterns) en amont du LLM pour réduire les coûts d'extraction d'assertions simples (Sujet-Prédicat-Objet).
3. **Harmoniser le contrat d'API Frontend/Backend :** Éliminer l'adaptateur double dans `web/src/services/` (`bookAdapter.ts` vs `bookApiAdapter.ts`) au profit d'un client unique autogénéré depuis le schéma OpenAPI de FastAPI.

---

## 2. Sécurité & Performance

### 2.1 Gestion de l'Authentification et Autorisation
- **Mots de passe :** Hachage sécurisé avec **Argon2id** (`Argon2PasswordHasher` dans `book_loop/infrastructure/auth.py`). Politique de mot de passe stricte (12 caractères min, majuscule, minuscule, chiffre, caractère spécial).
- **Sessions & JWT :** Authentification basée sur des tokens JWT transmis via cookies HTTP-only (`session_token`).
- **Isolation des données (Multi-tenancy) :** La dépendance FastAPI `get_owned_book` dans `book_loop/api/dependencies.py` garantit qu'un utilisateur ne peut accéder qu'aux livres dont il est propriétaire (`owner_id`).

### 2.2 Failles Potentielles & Secrets
- **Secrets dans le repo :** Aucun secret durci n'a été détecté dans le code source. Les secrets sont injectés via variables d'environnement (`AUTH_SECRET_KEY`, `GEMINI_API_KEY`, `DATABASE_URL`). `.env.example` est correctement configuré.
- **CORS & Cookies :** Le cookie `session_token` est configuré avec `httponly=True` et `samesite=lax`. Cependant, en cas de déploiement multi-domaines, la vérification CSRF repose uniquement sur la politique SameSite des cookies, sans token Anti-CSRF explicite dans les en-têtes.
- **Sécurité IP Rate Limiting :** Dans `book_loop/api/routes/auth.py`, la fonction `_client_ip` extrait l'adresse client à partir de la valeur de droite du header `X-Forwarded-For` (spécifique à la topologie GCP Cloud Run) pour éviter le spoofing d'IP.

### 2.3 Performance & Analyse de Gros Volumes de Texte
- **Calculs vectoriels et recherche hybride :** La recherche de faits canoniques réutilise `EmbeddingCanonicalRetriever` et `HybridCanonicalRetriever` (`book_loop/application/services/hybrid_retrieval.py`).
- **Goulot d'étranglement :** L'ingestion de manuscrits (`IngestDocument`) et l'analyse de cohérence (`AnalyzeConsistency`) sont exécutées de manière **synchrone** au sein des requêtes HTTP FastAPI. Pour un livre complet (50 000 à 100 000 mots), l'extraction d'assertions par LLM sur chaque chunk prendra plusieurs dizaines de secondes/minutes, provoquant un timeout de la requête HTTP du navigateur.

### 2.4 Les 3 Axes d'Amélioration Prioritaires
1. **Asynchronisme des tâches lourdes (Background Workers) :** Migrer l'ingestion de manuscrits et la vérification globale de cohérence vers un système de tâches d'arrière-plan (ex: Celery, ARQ ou GCP Cloud Tasks) avec suivi du statut par Server-Sent Events (SSE) ou WebSockets.
2. **Mise en cache vectorielle et de cohérence :** Ajouter un cache (Redis ou cache applicatif Postgres) sur les embeddings d'assertions et les résultats de diagnostics de cohérence pour éviter de réanalyser les chapitres inchangés.
3. **Renforcement CSRF & Sealing de session :** Ajouter un en-tête CSRF personnalisé (`X-CSRF-Token`) pour toutes les requêtes d'écriture (`POST`, `PUT`, `DELETE`) afin de prémunir l'application contre les attaques de type Cross-Site Request Forgery sur les navigateurs anciens.

---

## 3. DevOps, CI/CD & Infrastructure GCP

### 3.1 Inspection des Pipelines CI/CD
Le projet dispose d'une suite CI/CD sur GitHub Actions (`.github/workflows/`) :
- `ci.yml` :
  - Backend tests avec un service conteneurisé PostgreSQL 16.
  - Audit de sécurité des dépendances Python (`pip-audit --strict`) et Node.js (`npm audit --audit-level=high`).
  - Linter & Build Frontend Next.js.
  - Tests E2E Playwright en mode Mock et en mode Real API.
- `canon-e2e-validation.yml`, `postgres-integration.yml`, `real-book-run.yml` : Workflows automatisant la validation continue du moteur de cohérence.

### 3.2 Conformité du Déploiement GCP (Cloud Run & Cloud Build)
Le déploiement est orchestré par `cloudbuild.yaml` et documenté dans `infra/gcp/README.md` :
- **Région :** `europe-west9` (Paris).
- **Architecture Serverless :**
  - **API :** Cloud Run `book-loop-api` (max 3 instances, 512Mi, 1 CPU).
  - **Web :** Cloud Run `book-loop-web` (max 2 instances, 512Mi, 1 CPU).
  - **Base de données :** Cloud SQL PostgreSQL `book-loop-postgres`.
  - **Migrations Schema :** Exécutées avant le déploiement API via un **Cloud Run Job** dédié (`book-loop-migrations`) exécutant `alembic upgrade head`.

### 3.3 Points d'Attention Infra & Variables d'Environnement
- **Build-Time vs Runtime Variables Next.js :** Dans `cloudbuild.yaml`, `NEXT_PUBLIC_API_URL` est passé en `--build-arg` lors du build de l'image Docker frontend.
- **Synchronisation CORS fragile :** L'étape `sync-api-cors` de `cloudbuild.yaml` met à jour la variable d'environnement `CORS_ALLOWED_ORIGINS` de l'API après la résolution de l'URL du service Web. Si l'étape d'actualisation ou de vérification CORS échoue, l'API se retrouve temporairement redéployée avec un CORS désynchronisé.

### 3.4 Les 3 Axes d'Amélioration Prioritaires
1. **Rendre l'étape CORS de Cloud Build atomique :** Utiliser des domaines personnalisés configurés (ex: `api.bookloop.io` et `app.bookloop.io`) pour fixer la configuration CORS dans Secret Manager au lieu d'une mise à jour dynamique post-déploiement.
2. **Optimiser les limites de ressources Cloud Run :** La mémoire attribuée aux conteneurs API (512 MiB) est très juste pour exécuter spaCy et des modèles Pydantic complexes en parallèle sous forte charge. Augmenter à 1 GiB / 2 vCPU avec `min-instances=1` sur l'API pour éliminer les Cold Starts.
3. **Ajouter un monitoring d'erreurs (Sentry / GCP Error Reporting) :** Intégrer un SDK de captation d'exceptions dans FastAPI et Next.js pour suivre les erreurs de production en temps réel.

---

## 4. UX, Onboarding & Évolutivité Produit (Roadmap)

### 4.1 Fluidité du Parcours Auteur (ICP Actuel)
- **Parcours d'Onboarding :**
  1. Création de compte (`/register`) -> Configuration du projet / Creative Brief (`/setup`).
  2. Génération de la structure / Plan de livre (`/studio/outline`).
  3. Rédaction / Import de chapitre (`/import` ou `/studio/desk`).
  4. Boucle de validation de cohérence (`/studio/validation-loop`).
- **Retour des incohérences :** Très bien pensé sur le plan conceptuel. Les erreurs de continuité (chronologie, arcs personnages, faux raccords) sont affichées avec un niveau de confiance et un extrait de preuve (*Evidence*).
- **Point de friction UX :** L'importation de manuscrit existant (`/import`) est actuellement limitée à du texte brut et la remontée des propositions de faits canoniques peut être écrasante si le système propose des dizaines d'assertions à valider manuellement dès le premier chapitre sans filtre de pertinence.

### 4.2 Évolutivité Architecturale vers les Futurs Cas d'Usage
L'architecture de Book Loop a été évaluée au regard des trois étapes de la roadmap :

```
[ Court Terme : Auteurs / Écrivains ]
           │
           ▼
[ Moyen Terme : Game Designers / JDR ]
           │
           ▼
[ Long Terme : Documentation Technique Entreprise ]
```

#### Évaluation du Modèle de Données (`book_loop/domain/models.py`) :
- **Entités actuelles :** `BookState`, `Chapter`, `Character`, `CharacterRelation`, `SourceDocument`, `Assertion`, `Evidence`, `CanonicalFact`, `Conflict`.
- **Analyse d'évolutivité :**
  - **Moyen Terme (Game Design / JDR) :** Le modèle `Character` et `CharacterRelation` peut facilement être étendu. La notion de `Chapter` peut devenir un `ScenarioNode` ou `Quest`. La structure d'assertions Sujet-Prédicat-Objet (`subject`, `predicate`, `object`) est idéalement adaptée pour représenter des règles de jeu ("*Magic Spell X requires Mana Y*").
  - **Long Terme (Documentation Entreprise) :** `SourceDocument` et `DocumentChunk` gèrent déjà le suivi de version (`version`) et le hachage (`content_hash`). L'entité `CanonicalFact` avec suivi des décisions de révision (`ReviewDecision`) est exactement le modèle requis pour la gestion de vérités d'entreprise et de bases de connaissances réglementaires.

### 4.3 Les 3 Axes d'Amélioration Prioritaires
1. **Génération automatique de filtres de tri d'assertions (UX Onboarding) :** Regrouper les assertions extraites lors de l'import par entité et par degré de certitude pour permettre à l'auteur de "Tout approuver par personnage" au lieu de valider 100 assertions une par une.
2. **Généraliser l'abstraction du "Domaine de Référence" dans le modèle :** Renommer/Abstraire progressivement `BookState` vers une entité générique `UniverseContext` ou `KnowledgeSpace` afin de supporter indifféremment un livre, un livre de règles de JDR ou un espace documentaire sans refactorisation majeure du schéma de base de données.
3. **Support du format EPUB / DOCX / Markdown pour l'import :** Ajouter un parseur de fichiers multiformats dans `IngestDocument` pour éviter de forcer l'utilisateur à faire un copier-coller de texte brut.

---

## 5. Analyse Marketing, Commerciale & Économique (Unit Economics & Go-To-Market)

Une analyse produit complète nécessite d'évaluer la viabilité économique de la solution et son alignement commercial.

### 5.1 Grille Tarifaire & Positionnement Prix
La grille actuelle définie dans `docs/product/pricing-strategy.md` propose :

| Plan | Prix Mensuel | Prix Annuel | Rôle Commercial |
|---|---:|---:|---|
| **Free** | €0 | — | Découverte de la boucle produit avec quotas stricts |
| **Creator** | €19 | €190 | Écrivain indépendant actif (1 projet actif) |
| **Pro** | €39 | €390 | Écrivain intensif / multi-projets |

**Appréciation commerciale :** Le pricing à €19/mois est parfaitement aligné sur le marché SaaS B2C pour créateurs (ex: Sudowrite à ~$19-$29/mo, NovelAI à $10-$25/mo, Scrivener licence une fois). Il évite de vendre des "tokens" ou des "crédits" (ce qui génère de l'anxiété chez l'utilisateur) pour vendre plutôt une capacité de création ("Workflow Run Envelope").

### 5.2 Unit Economics & Marges Brutes (LLM vs Revenue)
D'après l'analyse des coûts documentée dans `docs/product/infrastructure-costs.md` :
- **Coût d'un Workflow Chapitre complet (Gemini 2.5 Flash) :**
  - Cas Nominal (100k tokens in / 20k out) : **~$0.08 / chapitre**
  - Cas Conservateur / Retries (250k in / 50k out) : **~$0.20 / chapitre**
  - Enveloppe de Sécurité Utilisée (Safety Margin) : **$0.50 / chapitre**
- **Marge Brute Cible (Direct COGS < 25%) :**
  - Sur le plan **Creator (€19/mois ~ $20.50)** : Le plafond COGS de 25% autorise $5.12 de coûts directs (LLM + Stripe). À $0.50 par chapitre, l'utilisateur peut consommer environ **9 à 10 chapitres générés/révisés par mois** tout en conservant **>75% de Marge Brute**.
  - Sur le plan **Pro (€39/mois ~ $42.00)** : Le plafond autorise $10.50 de coûts directs, soit environ **20 chapitres par mois**.

**Fixation des Guardrails Économiques :**
1. **L'absence d'offre "Illimitée" est une excellente décision stratégique.** Les LLMs génératifs sous-jacents ont un coût marginal non nul.
2. **Coût fixe d'infrastructure maîtrisé :** GCP Cloud Run + Cloud SQL coûtent environ **$20 à $50/mois au global** pour un démarrage MVP (soit amorti dès 3 abonnés Creator).

### 5.3 Stratégie Go-To-Market (GTM) & Acquisition
- **Canaux d'acquisition cibles :** Communautés d'auteurs d'auto-édition (KDP / Amazon Kindle Direct Publishing), sous-reddits r/writing, r/selfpublish, communautés Discord de Game Masters (JDR) et plateformes d'écriture Web (Wattpad, Inkitt).
- **Incentive d'Onboarding :** L'offre Free doit démontrer la valeur de la "détection de conflit" immédiatement. Importer un premier chapitre et se voir révéler un faux raccord (ex: "Le personnage A est droitier au chapitre 1 mais tient son épée de la main gauche au chapitre 3") est l'événement *Aha! Moment* principal qui déclenche la conversion payante.

### 5.4 Les 3 Axes d'Amélioration Prioritaires
1. **Implémenter un suivi précis du coût par utilisateur dans la base PostgreSQL :** Consigner le nombre exact de tokens consommés et le coût Gemini estimé dans la table `workflow_runs` pour ajuster dynamiquement les quotas.
2. **Créer une offre "Pass Manuscrits" (Pay-per-Manuscript / One-Shot) :** Les auteurs écrivent souvent par salves (1 livre tous les 6 mois). Un tarif à l'acte (€29 pour la vérification complète d'un manuscrit importé) capturerait les auteurs réfractaires à l'abonnement mensuel récurrent.
3. **Mettre en place un programme d'affiliation/recommandation pour auteurs :** Proposer un système de parrainage (ex: 1 mois offert pour chaque auteur parrainé) très efficace dans les micro-communautés d'écrivains.

---

## Plan d'Action Immédiat (Roadmap de Correctifs)

Afin de passer l'application au niveau supérieur de maturité technique et commerciale, voici les actions classées par priorité :

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PLAN D'ACTION IMMÉDIAT                         │
├─────────────────────────────────────────────────────────────────────────┤
│ PRIORITÉ 1 (Court terme - 1 à 2 semaines) : Robustesse & DX             │
│  - Rendre la suite de tests exécutable sans conteneur Postgres externe.  │
│  - Ajouter un parseur de fichiers (DOCX/EPUB/PDF) sur l'import.          │
│  - Fixer la configuration mémoire/CPU Cloud Run à 1Gi / 2 vCPU.          │
│                                                                         │
│ PRIORITÉ 2 (Moyen terme - 1 mois) : Scalabilité & UX Workflow           │
│  - Migrer l'ingestion et l'analyse de cohérence en tâches d'arrière-plan.│
│  - Améliorer l'UX de validation du Canon (approbation groupée).         │
│  - Consigner la consommation de tokens/coûts LLM par utilisateur.       │
│                                                                         │
│ PRIORITÉ 3 (Long terme - 3 mois) : Préparation Multi-Verticales & Business│
│  - Lancer l'offre "Pass Manuscrit" (achat ponctuel) à côté des plans.   │
│  - Abstraire le modèle `BookState` vers `UniverseSpace`.               │
│  - Exposer des API GraphQL / Webhooks pour intégration tierce (JDR/CMS).│
└─────────────────────────────────────────────────────────────────────────┘
```

---
*Fin du rapport d'audit Book Loop.*
