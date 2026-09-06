# FE-2B.2 — Contrat UX du Studio

FE-2B.1 fixe le contrat API ↔ frontend. Ce document fixe la règle de présentation du Studio.

## Règle principale

Le Studio peut **présenter** un état reçu de l'API, mais ne doit pas **inventer** un état métier.

### Autorisé

- état du chapitre reçu dans `BookState` ;
- version courante reçue par l'API ;
- review reçue par l'API ;
- Canon/contexte reçu par l'API ;
- états de chargement locaux correspondant à une requête actuellement exécutée.

### Interdit

- déduire qu'un workflow est terminé uniquement parce qu'une requête HTTP a répondu ;
- transformer une proposition en Canon côté React ;
- conserver un état métier uniquement dans `useState` pour le restaurer après navigation ;
- afficher une action d'approbation lorsqu'une version est déjà canonique ;
- masquer une erreur API avec un `catch` silencieux.

## Vocabulaire

| État | Libellé UI | Signification |
| --- | --- | --- |
| `draft` | Brouillon | Pas encore une décision Canonique. |
| `proposed` | Proposition | Contenu proposé, non approuvé. |
| `needs_review` | À votre décision | Une décision humaine est attendue. |
| `approved` / `canonical` | Canon approuvé | La version est devenue la référence. |
| `rejected` | Rejetée | La proposition reste dans l'historique et ne modifie pas le Canon. |
| `in_progress` | En cours | Le backend signale un traitement en cours. |
| `pending` | En attente | Le backend signale une étape en attente. |

La couleur n'est jamais le seul signal : chaque état doit avoir un libellé textuel et, lorsque pertinent, une icône.

## Décision humaine

Une action `Approuver dans le Canon` n'est disponible que lorsque l'API indique qu'une décision est requise. Une version déjà approuvée ne doit jamais présenter cette action comme disponible.

`Rejeter` et `Demander une révision` doivent également rester des actions explicites : aucune transition Canonique ne doit être déclenchée implicitement par un refresh ou une génération.

## Asynchronisme

Un clic peut afficher un état local `chargement`, mais le résultat final doit être reconstruit depuis l'API. Les futurs endpoints de `ChapterWorkflowRun`, historique de versions et reviews détaillées devront donc être consommés directement par le Studio.
