# FE-2B — Contrat API ↔ frontend

**Date:** 6 septembre 2026
**Statut:** contrat de référence pour le développement du Studio

Ce document décrit le contrat réellement exposé par l'API au moment du démarrage de FE-2B. Le frontend ne doit pas inventer de champs, d'états ou de transitions absents du backend.

## 1. Principes

- Le backend est l'autorité pour `BookState`, Outline, chapitres, Canon et workflow.
- Le frontend adapte les réponses API pour son modèle d'affichage ; il ne reproduit pas les règles métier.
- Une réponse `404` sur un livre signifie aussi « livre inaccessible » lorsqu'il appartient à un autre utilisateur.
- Une proposition IA n'est jamais canonique par défaut.
- Les états affichés après un retour sur le site doivent provenir d'une lecture API, pas de l'état React précédent.

## 2. Authentification et session

### Endpoints

| Méthode | Endpoint | Réponse | Erreurs principales |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | `UserPublic` ou enveloppe utilisateur | `400` générique / `422` validation / `429` throttling |
| POST | `/api/auth/login` | `UserPublic` ou enveloppe utilisateur | `401` générique / `429` throttling |
| POST | `/api/auth/logout` | message | `4xx` |
| GET | `/api/auth/me` | `UserPublic` | `401` si session absente/expirée |

La session utilise un cookie HTTP-only et l'API accepte également `Authorization: Bearer ...`. Le client réel envoie `credentials: include`.

### Protection anti-brute-force

Le login est protégé par deux limites indépendantes, évaluées côté backend :

- **par compte** : 5 tentatives sur une fenêtre glissante de 15 minutes ;
- **par IP** : 5 tentatives sur une fenêtre glissante de 15 minutes.

La persistance est assurée par PostgreSQL afin que la protection reste cohérente entre plusieurs instances Cloud Run. Une réussite de connexion réinitialise le compteur associé au compte. Le backend renvoie `429` avec un message générique ; le frontend ne doit pas afficher quel compteur a été dépassé.

L'inscription est également limitée par IP (10 créations sur 15 minutes) pour réduire l'abus automatisé.

### Anti-enumeration

Les échecs de connexion utilisent toujours le même message, que l'adresse existe ou non : `Adresse e-mail ou mot de passe incorrect.` Le backend effectue également une vérification de hash factice lorsqu'aucun compte n'existe afin de réduire les différences de temps de réponse.

Une tentative d'inscription avec une adresse déjà utilisée ne confirme pas l'existence du compte et retourne un message générique.

## 3. Livres

### `GET /api/books`

Retourne uniquement les livres du compte courant : `BackendBook[]`.

### `GET /api/books/{bookId}`

Retourne un `BackendBook`.

- `404` si le livre n'existe pas ou appartient à un autre utilisateur.
- `401` si la session est absente ou invalide.

### `POST /api/books`

Payload :

```json
{
  "title": "string",
  "theme": "string",
  "author_idea": "string",
  "lore": "string",
  "constraints": ["string"]
}
```

Le `owner_id` est déterminé côté backend à partir de la session. Le frontend ne doit jamais l'envoyer comme autorité.

### `PUT /api/books/{bookId}`

Payload partiel libre actuellement. Le backend applique les champs modifiables. Le frontend doit rester explicite sur les champs envoyés.

## 4. Modèle `BookState`

```text
id
owner_id
title
theme
author_idea
creative_brief | null
lore
constraints[]
outline | null
outline_approved
chapters[]
```

Le frontend ne doit pas transformer `outline_approved` en une règle locale indépendante : c'est l'état persistant retourné par l'API.

## 5. Outline

### `POST /api/books/{bookId}/outline/generate`

Génère une proposition d'Outline et retourne le `BookState` mis à jour.

### `PUT /api/books/{bookId}/outline`

Payload :

```json
{
  "outline": {
    "chapters": [
      {
        "number": 1,
        "title": "string",
        "objective": "string",
        "synopsis": "string"
      }
    ]
  }
}
```

Le backend valide notamment que les numéros sont consécutifs à partir de 1.

### `POST /api/books/{bookId}/outline/approve`

Valide explicitement l'Outline et retourne le `BookState`.

**Règle UI :** générer/modifier ne signifie pas approuver. Le bouton d'approbation doit rester une décision humaine distincte.

## 6. Canon

### `GET /api/books/{bookId}/assertions`

Retourne `{ "assertions": BackendAssertion[] }`.

Une assertion possède notamment :

```text
id
statement
subject
predicate
object
confidence
status: proposed | accepted | rejected | deferred
evidence_id
```

### `POST /api/books/{bookId}/assertions/{assertionId}/review`

Payload :

```json
{
  "decision": "accept | reject | defer",
  "rationale": "string"
}
```

La décision est persistée par le backend. Le frontend ne doit pas déduire qu'une assertion est canonique à partir de `confidence` ou d'un score IA.

### `GET /api/books/{bookId}/canonical-facts`

Retourne `{ "facts": BackendCanonicalFact[] }` avec les faits canoniques actifs.

### `GET /api/books/{bookId}/conflicts`

Retourne `{ "conflicts": BackendConflict[] }`.

## 7. Chapitres

### `POST /api/books/{bookId}/chapters`

Payload : `{ "chapter_number": number }`.

Le numéro doit correspondre au workflow métier du backend. Le frontend ne doit pas envoyer un titre/objective comme source de vérité : ces informations proviennent de l'Outline.

### `POST /api/books/{bookId}/chapters/{chapterNumber}/generate`

Retour actuel :

```json
{
  "book": "BackendBook",
  "versionNumber": 1,
  "content": "string"
}
```

Le backend exécute actuellement le workflow avant de répondre. Le frontend peut afficher le résultat retourné, mais **ne doit pas présenter ce endpoint comme un suivi durable de progression** tant qu'un endpoint de lecture du `ChapterWorkflowRun` n'est pas exposé.

### `POST /api/books/{bookId}/chapters/{chapterNumber}/review`

Payload :

```json
{
  "versionNumber": 1,
  "draftText": "string"
}
```

Retour : `{ "book": BackendBook, "review": BackendSceneReview }`.

### `POST /api/books/{bookId}/chapters/{chapterNumber}/approve`

Retourne le `BookState` avec un bloc `canonSync` supplémentaire contenant la synchronisation du Canon déclenchée par l'approbation.

### `POST /api/books/{bookId}/chapters/{chapterNumber}/reject`

Retourne le `BookState`.

### `GET /api/books/{bookId}/chapters/{chapterNumber}/context`

Retourne le contexte de génération : idée auteur, thème, lore, Outline, contraintes, résumés précédents, objectif courant et contexte formaté.

## 8. Documents / ingestion

### `POST /api/books/{bookId}/documents/ingest`

Payload : nom, contenu et type de source. Retourne la source ingérée et les assertions produites.

Cette opération peut servir à alimenter le Canon, mais l'ingestion ne constitue pas une approbation humaine.

## 9. Erreurs et comportement du client

Le client réel doit conserver le statut HTTP via `RealApiError.status`.

- `401` sur login : message générique `Adresse e-mail ou mot de passe incorrect.`
- `400` sur inscription pour conflit : message générique ; ne pas confirmer qu'un compte existe.
- `422` : erreur de validation exploitable par l'UI (notamment la politique de mot de passe).
- `429` : opération temporairement limitée → afficher une explication utilisateur simple et ne pas indiquer quel compteur a déclenché la limite.
- `404` : livre/ressource introuvable ou livre d'un autre compte → écran/not-found approprié, sans fuite d'existence.
- `408/429/500/502/503/504` sur GET : retry limité déjà implémenté par `RealApiClient`.
- timeout réseau : message explicite ; ne pas masquer l'erreur sous un faux état métier.

## 10. Gaps bloquants identifiés pour FE-2B

Ces éléments existent dans le domaine/backend mais ne sont pas encore lisibles de façon suffisante par le frontend après un reload :

1. **Workflow durable** — `ChapterWorkflowRun` est persisté côté backend, mais aucun endpoint frontend public de lecture d'un run n'est exposé. Le Studio ne peut donc pas reconstruire fidèlement `running / needs_review / completed`, `step`, `attempt`, `review`, `summary` et `run id` après navigation.
2. **Historique des versions** — le modèle de domaine persiste des versions immuables, mais l'API publique ne propose pas de liste/lecture des versions d'un chapitre. Le Studio ne peut pas afficher un historique fiable après reload.
3. **Evidence Canon** — les assertions exposent `evidence_id`, mais l'API publique ne propose pas encore de lecture des `Evidence` liées. Le frontend peut afficher le statut d'une assertion, pas sa preuve complète de manière fiable après reload.
4. **Review détaillée persistée** — le chapitre expose `reviewed_version`, mais le `BookState` ne contient pas la review détaillée. Une API de lecture de review/version est nécessaire pour reconstruire la file de décision.
5. **Statut métier vs exécution** — `ChapterStatus` et `WorkflowRunStatus` sont deux concepts différents. Le frontend doit les modéliser séparément dès que le contrat de workflow sera exposé.

**Conséquence :** FE-2B.2 peut construire la coque du Studio avec les données disponibles, mais FE-2B.5/6 ne doit pas simuler ces données. Les gaps ci-dessus doivent être traités dans l'API/backend avant de promettre un Studio pleinement reconstructible.

## 11. Frontend adapter

`RealApiClient` reste la frontière HTTP. `bookApiAdapter` transforme les objets backend en modèles historiques du frontend.

Pendant FE-2B, cette couche doit progressivement évoluer vers les modèles backend plutôt que d'ajouter de nouveaux champs fictifs au modèle legacy. Toute incompatibilité doit être traitée dans l'adapter ou, si elle correspond à une information métier manquante, dans l'API.
