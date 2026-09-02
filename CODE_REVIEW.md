# Revue de Code & Analyse d'Architecture : API, Clean Architecture & Couverture de Tests

**Projet :** AI Book Loop (`book_loop`)
**Auteur de la revue :** Jules, Expert Software Engineer & Clean Architect
**Date :** Septembre 2026
**Périmètre :** Backend Python (`book_loop/`), API REST FastAPI (`book_loop/api/`), Infrastructure, Domaine, Application, Workflows, Agents & Couverture des Tests. (Frontend exclu).

---

## 1. Résumé Exécutif

Le projet **AI Book Loop** repose sur une intention architecturale très claire : implémenter une **Clean Architecture** (Ports & Adapters / Hexagonale) pour un système de génération et de révision de livres par agents IA.

### Constats majeurs :
1. **Conception du Domaine & Cas d'Usage (Application) :** La séparation des responsabilités au niveau des couches `domain/` et `application/use_cases/` est bien pensée. Les entités Pydantic (`BookState`, `Chapter`, `SceneReview`) et les protocoles (`BookRepository`, `LLMProvider`, etc.) sont propres et indépendants des détails techniques.
2. **Dérive du niveau API (`book_loop/api/app.py`) :** C'est le point d'attention principal. **L'API bypass fréquemment la couche Application**. Elle contient de la logique métier directe (Bypass de `GenerateChapter`, mock/stubbing inline de drafts de chapitres, révision arbitraire codée en dur, gestion manuelle d'état et seeding automatique non désactivable).
3. **Dualité d'Orchestration Workflow :** Il existe deux fichiers de workflow (`book_loop/workflow/chapter.py` et `book_loop/workflow/chapter_graph.py`). `chapter_graph.py` utilise LangGraph tandis que `chapter.py` est une boucle Python sans framework. L'API n'utilise ni l'un ni l'autre sur l'endpoint `/api/books/{id}/chapters/{num}/generate`, provoquant un décalage entre le comportement réel de l'API et les cas d'utilisation métier.
4. **Analyse de la Couverture de Tests (84% Global, mais disparités critiques) :** La suite de tests compte 21 tests qui réussissent tous à 100%. Cependant, le use case central `GenerateChapter` n'est couvert qu'à **38%**, le module `prompts.py` à **0%**, et la couche API à **74%** avec plusieurs routes clés partiellement testées.

---

## 2. Respect de la Clean Architecture & Matrice des Dépendances

La Clean Architecture impose que la règle de dépendance aille toujours **vers l'intérieur** (de l'Infrastructure/UI vers le Domaine, jamais l'inverse).

```
   +---------------------------------------------------+
   |  API (FastAPI) / CLI                             |
   +-------------------------+-------------------------+
                             |
                             v
   +---------------------------------------------------+
   |  Infrastructure (SQLite, LLM, Container)         |
   +-------------------------+-------------------------+
                             |
                             v
   +---------------------------------------------------+
   |  Application (Use Cases, Services, Policies)     |
   +-------------------------+-------------------------+
                             |
                             v
   +---------------------------------------------------+
   |  Domain (Models: BookState, Protocols)           |
   +---------------------------------------------------+
```

### Évaluation du respect des couches :

| Couche | Statut | Remarques / Violations |
| :--- | :---: | :--- |
| **Domain** (`book_loop/domain/`) | **Conforme (10/10)** | Aucune dépendance externe vers les frameworks HTTP/DB. Modèles Pydantic purs et définitions de protocoles/interfaces (`Protocols`). |
| **Application** (`book_loop/application/`) | **Conforme (9/10)** | Orchestre la logique métier à travers les Use Cases (`CreateBook`, `GenerateOutline`, `ApproveOutline`, `AddChapter`, `GenerateChapter`). Services d'aide (`ContextBuilder`, `ChapterLinter`) bien isolés. |
| **Agents / Workflow** (`book_loop/agents/`, `book_loop/workflow/`) | **Moyennement Conforme (7/10)** | Implémente l'orchestration décisionnelle avec LangGraph. Cependant, présence de deux implémentations concurrentes (`workflow/chapter.py` et `workflow/chapter_graph.py`). |
| **Infrastructure** (`book_loop/infrastructure/`) | **Conforme (8/10)** | `SQLiteBookRepository` et `Container` (Root Composition) gèrent l'injection de dépendance. |
| **API** (`book_loop/api/app.py`) | **Non-Conforme (4/10)** | **Violation majeure de la Clean Architecture.** L'API FastAPI ne délègue pas ses opérations aux Use Cases sur plusieurs endpoints clés (`generate_chapter`, `review_chapter`, `approve_chapter`, `reject_chapter`, `update_book`). |

---

## 3. Analyse Détaillée du Composant API (`book_loop/api/app.py`)

La couche API présente plusieurs incohérences majeures par rapport au reste du projet :

### 1. Bypass du Use Case `GenerateChapter` et du Workflow LangGraph
- **Problème :** Sur l'endpoint `POST /api/books/{book_id}/chapters/{chapter_number}/generate`, l'API génère un texte de chapitre fictif en dur :
  ```python
  draft_content = f"Chapitre {chapter.number}: {chapter.title}. Objectif: {chapter.objective}.\n\nDans la pénombre du scriptorium..."
  ```
  Au lieu de faire appel à `container.generate_chapter().execute(book, chapter_number)` (qui exécute le workflow multi-agents avec écriture, linting, révision et résumé), l'API met à jour la version manuellement.
- **Impact :** Les capacités de génération IA réelles (Gemini/Fake LLM) et l'orchestration LangGraph sont inutilisées lors de l'appel HTTP.

### 2. Logique de Révision codée en dur dans le Handler API
- **Problème :** L'endpoint `POST /api/books/{book_id}/chapters/{chapter_number}/review` exécute un contrôle de mots interdits en ligne (`"ordinateur"`, `"robot"`, etc.) directement dans le handler HTTP FastAPI.
- **Impact :** Duplication / Incohérence avec `ReviewerAgent`, `ChapterLinter` et `application/policies/review.py`. L'API réinvente la règle de révision au lieu de solliciter la couche applicative.

### 3. Effet de Bord : Fonction `_get_or_seed_book`
- **Problème :** L'API intercepte tout livre inconnu en injectant un livre par défaut ("L'Écho du Codex").
- **Impact :** Empêche le retour d'une vraie erreur HTTP 404 lors de requêtes sur un `book_id` inexistant et fausse la persistance SQLite en créant des données fantômes.

### 4. Violation du Statut `ChapterStatus`
- **Problème :** Dans `review_chapter`, le statut du chapitre passe à `NEEDS_REVIEW` lorsque la révision est *approuvée* :
  ```python
  chapter.status = ChapterStatus.NEEDS_REVIEW if approved else ChapterStatus.REJECTED
  ```
  Or, selon le domaine, un chapitre révisé et approuvé devrait être en statut `PROPOSED` ou `APPROVED`.

### 5. Incohérence DTO / Modèles de Domaine
- **Problème :** `update_book` accepte un dictionnaire brut `dict[str, Any]` et fait un `model_validate` direct, contournant les cas d'utilisation applicatifs.

---

## 4. Analyse de la Couverture & Qualité des Tests (`pytest --cov`)

La commande de couverture sur `book_loop` indique une couverture globale de **84%** (504 lignes exécutées sur 601), mais dissimule des zones aveugles critiques :

### Tableau synthétique de couverture par module :

| Module | Taux de couverture | Statut | Code manquant / Remarques |
| :--- | :---: | :---: | :--- |
| `domain/models.py` & `protocols.py` | **100%** | Excellent | Modèles Pydantic et protocoles testés. |
| `application/policies/review.py` | **100%** | Excellent | Règle de décision entièrement couverte. |
| `application/services/context.py` & `linter.py` | **100%** | Excellent | Construction du contexte et linting validés. |
| `application/services/prompts.py` | **0%** | **Critique** | **Aucun test** sur les gabarits de prompts générés pour le LLM. |
| `application/use_cases/generate_chapter.py` | **38%** | **Critique** | **62% du Use Case non exécuté par les tests** (exceptions d'ordre de chapitre non testées). |
| `api/app.py` | **74%** | **Moyen** | 40 lignes non couvertes (notamment les cas d'erreur HTTP 400/404, `get_canonical_context` complexe, etc.). |
| `infrastructure/llm/fake.py` | **55%** | **Faible** | Fallbacks du Fake LLM non testés. |
| `cli/main.py` | **62%** | **Faible** | Les commandes CLI secondaires ne sont pas validées. |
| `workflow/chapter_graph.py` | **94%** | Bon | Bonne couverture de l'orchestrateur LangGraph via `test_workflow.py`. |

### Lacunes qualitatives des tests actuels :
1. **Tests unitaires des Use Cases incomplets (`test_use_cases.py`) :** `test_use_cases.py` ne testait pas du tout `GenerateChapter`. Seul `test_workflow.py` appelait le workflow sous-jacent.
2. **Absence de tests d'erreurs d'API (`test_api.py`) :** Aucun test ne vérifie le retour des codes d'erreur HTTP (`400 Bad Request`, `404 Not Found`) dans l'API FastAPI. Les cas limites (tenter de générer un chapitre avant d'approuver l'outline, ajouter un chapitre invalide) ne sont pas testés au niveau API.
3. **Mocks/Stubs isolés :** Comme l'API bypass le workflow réel, la suite de tests `test_api.py` valide un comportement mocké qui n'est pas celui de l'application réelle.

---

## 5. Matrice de Criticité des Anomalies

| ID | Catégorie | Description | Criticité |
| :---: | :--- | :--- | :---: |
| **ANO-01** | Architecture / API | Bypass des Use Cases et des Workflows IA dans les handlers de génération et révision (`app.py`). | **CRITIQUE** |
| **ANO-02** | Qualité / Tests | Couverture de 38% sur `GenerateChapter` et 0% sur `prompts.py`. Absence de tests d'erreur HTTP 400/404. | **MAJEUR** |
| **ANO-03** | Logique Métier / API | Logique de révision et contrôle d'anachronismes codée en dur dans le handler HTTP au lieu de la couche Policy/Agent. | **MAJEUR** |
| **ANO-04** | Domaine / Statut | Inversion de logique du statut `ChapterStatus` (`NEEDS_REVIEW` assigné en cas de succès de révision dans l'API). | **MAJEUR** |
| **ANO-05** | Architecture / API | Seeding automatique systématique (`_get_or_seed_book`) masquant les erreurs HTTP 404 sur les ressources. | **MOYEN** |
| **ANO-06** | Redondance Code | Coexistence de deux orchestrateurs de workflow (`workflow/chapter.py` vs `workflow/chapter_graph.py`). | **MINEUR** |
| **ANO-07** | Pattern / DI | Incomplétude du `Container` auquel il manque des fabriques pour les use cases de révision et d'approbation. | **MINEUR** |

---

## 6. Plan d'Action & Recommandations de Refactorisation

Pour amener le projet à un niveau de qualité expert conforme aux principes de la Clean Architecture, voici le plan de refactorisation recommandé :

### Phase 1 : Encapsulation des Cas d'Usage de Chapitre
1. Créer des Use Cases dédiés dans `book_loop/application/use_cases/` :
   - `ReviewChapter` : fait appel à `ReviewerAgent` ou `ChapterLinter` + `ReviewPolicy`.
   - `ApproveChapter` / `RejectChapter` : gère la transition canonique et le statut du chapitre.
2. Ajouter ces cas d'usage dans le `Container` (`book_loop/infrastructure/container.py`).

### Phase 2 : Alignement du Handler FastAPI (`book_loop/api/app.py`)
1. Modifier `generate_chapter` pour appeler le cas d'usage `GenerateChapter` exécutant le workflow réel.
2. Déplacer la logique de validation de `review_chapter` dans le cas d'usage `ReviewChapter`.
3. Corriger le seeding automatique `_get_or_seed_book` pour lever un `HTTPException(404)` standard lorsque la ressource n'existe pas (le seeding ne doit servir que de mode démo optionnel ou de fixture).
4. Corriger la mise à jour des statuts `ChapterStatus`.

### Phase 3 : Renforcement de la Suite de Tests (`tests/`)
1. Compléter `test_use_cases.py` pour tester toutes les branches de garde du use case `GenerateChapter` (outline non approuvé, chapitre précédent non validé).
2. Compléter `test_api.py` pour tester le comportement d'erreur HTTP (400, 404) et la chaîne d'appel complète de l'API vers les cas d'utilisation.
3. Ajouter un test unitaire pour `application/services/prompts.py`.

### Phase 4 : Nettoyage et Harmonisation
1. Supprimer l'implémentation obsolète `book_loop/workflow/chapter.py` au profit de `chapter_graph.py`.

---

## 7. Conclusion

Le projet **AI Book Loop** dispose de fondations solides en termes de modélisation du domaine et de séparation des agents IA. L'effort principal de refactorisation doit porter sur le **réalignement de l'API FastAPI avec la couche Application** et le **renforcement de la suite de tests unitaires/API** pour couvrir les cas d'erreur et supprimer les réponses simulées en dur.

---

## 8. Statut de la Refactorisation (Post-Analyse)

À la suite de l'analyse et de la revue de code expert, les corrections majeures recommandées ont été implémentées avec succès :

1. **Cas d'Utilisation Applicatifs (`application/use_cases`) :**
   - Création des use cases `ReviewChapter`, `ApproveChapter`, `RejectChapter`.
   - Enregistrement des nouveaux cas d'utilisation dans le `Container` de l'infrastructure.
2. **Alignement de l'API FastAPI (`book_loop/api/app.py`) :**
   - Les endpoints `generate`, `review`, `approve` et `reject` passent désormais intégralement par les Use Cases applicatifs et le workflow multi-agents LangGraph.
   - Suppression du mock en dur dans `generate_chapter` et déportation de la logique de révision vers `ReviewChapter`.
   - Correction de la gestion des exceptions HTTP 404/400.
3. **Consolidation des Workflows :**
   - Suppression du fichier obsolète `book_loop/workflow/chapter.py` pour unifier l'orchestration sur LangGraph (`chapter_graph.py`).
4. **Renforcement des Tests & Couverture (`tests/`) :**
   - Ajout de tests pour `prompts.py`, augmentation de la couverture globale à **89%** (avec 100% sur la quasi-totalité des use cases et du container).
   - Validation complète des 24 tests unitaires et d'intégration via `pytest`.
