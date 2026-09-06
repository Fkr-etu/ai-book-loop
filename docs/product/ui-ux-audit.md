# Audit UI/UX — Book Loop

**Date :** 6 septembre 2026
**Périmètre :** parcours public, authentification, démarrage, tableau de bord et Studio. Audit statique du code et revue des captures disponibles. Les constats doivent être validés avec des tests utilisateurs avant de devenir des décisions produit.

## Résumé exécutif

L'interface a une base visuelle soignée : palette encre/parchemin, typographies éditoriales, hiérarchie claire sur les écrans isolés et effort de mise à l'échelle pour les petits écrans. Elle ne raconte toutefois pas encore avec assez de constance la promesse qui différencie Book Loop : **un espace de décision où le Canon est fiable et où l'auteur garde le contrôle**.

Le principal risque UX est la confusion entre un « atelier d'écriture IA » et le produit réellement vendu : une boucle explicable de proposition, vérification, décision et mise à jour du Canon. Le principal risque de design system est la coexistence de deux expressions : le « Parchment & Ink » défini par l'ADR et une famille de bleus Material-like plus récente. Enfin, l'interface mobile évite le débordement, mais comprime des tâches d'auteur longues en une succession de panneaux au lieu d'établir une priorité de travail.

## Méthode et limites

- Revue des routes et composants Next.js, de leurs classes responsives et des contenus affichés.
- Revue des captures de régression desktop et mobile déjà présentes dans `web/`.
- Vérification des tests Playwright et de la configuration du manifeste.
- L'audit ne comprend ni test modéré avec des auteurs, ni audit lecteur d'écran automatisé, ni mesures réelles de performance. Le build ne pouvait pas être finalisé dans cet environnement parce que `next/font` ne pouvait pas charger les quatre polices Google.

## Ce qui fonctionne déjà

1. **Une promesse lisible sur l'accueil.** Le message met à juste titre le Canon et la décision humaine au centre, avec une séquence qui explique le cycle produit.
2. **Des fondations responsives réelles.** Les colonnes deviennent verticales, les CTA prennent toute la largeur lorsque nécessaire et le Studio possède un tiroir de navigation mobile.
3. **Un système typographique expressif.** Le contraste entre Playfair pour les titres, Merriweather pour le manuscrit et Inter pour l'outil fait sens pour un produit d'auteur.
4. **Des états vides et d'erreur orientés action dans le tableau de bord.** Ils indiquent quoi faire ensuite, plutôt que de laisser l'auteur face à une page muette.

## Constats priorisés

### P0 — Faire comprendre et sécuriser la boucle de décision

| Constat | Impact auteur | Recommandation | Critère d'acceptation |
| --- | --- | --- | --- |
| Les libellés alternent entre « Canon », « lore », « bible », « reliques », « IA Canon », « Manuscript Studio » et « Book Loop ». | L'utilisateur ne sait plus ce qui est une donnée fiable, une proposition ou une zone de travail. Cela affaiblit la promesse de confiance. | Établir un vocabulaire court : **Canon**, **Proposition**, **Vérification**, **Décision**, **Historique**. Employer « lore » uniquement comme catégorie de contenu. | Sur chaque écran, un auteur peut dire quel est l'état, la preuve et la décision disponible. |
| Une version peut être affichée « APPROUVÉ (CANON) » tout en proposant « Approuver (Canon) ». | La mutation du Canon paraît réversible ou déjà exécutée ; c'est contraire au modèle d'approbation humaine explicite. | Créer une barre d'état persistante : `Brouillon` → `Proposition vérifiée` → `À votre décision` → `Canon approuvé`. Masquer ou désactiver les actions impossibles avec une explication. | Aucun écran ne propose d'approuver un élément déjà canonique. |
| La « Boucle de Validation » déclenche un linter puis une review, mais ne montre pas clairement les preuves, conflits, conséquences et décision finale. | Le produit semble être un score IA plutôt qu'un contrôle de continuité explicable. | Recomposer l'écran en file de décisions : proposition, contrôles déterministes, conflits liés aux faits sources, suggestion IA, puis `Approuver dans le Canon`, `Demander une révision`, `Rejeter`. | Chaque finding expose une source ou indique clairement qu'il s'agit d'une suggestion sans preuve. |

### P1 — Unifier le design system autour du travail d'auteur

| Constat | Impact auteur | Recommandation |
| --- | --- | --- |
| L'ADR promet « Parchment & Ink » (`#f8f5f0`, `#0b1c30`, `#ffddb8`), mais les tokens globaux privilégient une gamme bleue froide `#f8f9ff` / `#eff4ff` / `#d3e4fe`. | Les surfaces évoquent simultanément un outil administratif et un atelier littéraire ; l'identité mémorable se dilue. | Conserver le parchemin comme fond de lecture et les documents, employer le bleu encre pour navigation/commandes, réserver l'or pour le Canon et les validations. Supprimer les fonds bleus décoratifs quand ils ne codent pas un état. |
| Le même or signale décorations, icônes, Canon, alerte active et parfois succès. | Une couleur ne permet pas d'interpréter rapidement le risque ou la décision, et les utilisateurs daltoniens perdent un repère. | Définir information, proposition, succès/canon, attention, conflit et erreur comme couleurs sémantiques. Chaque état associe couleur, icône, texte et bordure ; ne jamais s'appuyer sur la couleur seule. |
| Les composants reprennent des rayons, ombres, tailles de libellés mono et couleurs directement en classes. | Les écrans se ressemblent sans être complètement cohérents, et tout changement de marque devient coûteux. | Créer des primitives documentées : `PageHeader`, `StatusBadge`, `DecisionBar`, `EvidenceCard`, `EmptyState`, `PrimaryAction`, et des tokens CSS sémantiques. |
| Les libellés mono en capitales et les intitulés très longs chargent les interfaces denses. | La navigation devient plus difficile à scanner, particulièrement sur mobile. | Utiliser la casse phrase et des noms fonctionnels : `Plan`, `Écrire`, `Canon`, `Vérifier`, `Historique`. Réserver le monospace aux données. |

### P1 — Donner une vraie priorité au mobile

| Constat | Impact auteur | Recommandation |
| --- | --- | --- |
| Le Studio conserve deux niveaux de navigation : barre globale et tiroir de huit destinations. | La zone utile est faible au moment où l'auteur doit lire, écrire ou décider. | Sur mobile, une barre compacte : nom du livre, statut courant et une action contextuelle. Déplacer toute navigation secondaire dans le tiroir. |
| Les longues tâches sont découpées en cartes qui s'empilent, avec boutons horizontaux et compteurs. | Lecture et contrôle des conflits demandent un long défilement et font perdre le contexte. | Prévoir trois modes mobiles : **Écrire**, **Vérifier**, **Décider**. Un sélecteur local bascule de mode ; la barre de décision reste accessible en bas de l'écran. |
| Le tiroir n'indique pas la destination courante au niveau de l'en-tête. | Risque de désorientation entre Plan, Canon et Validation. | Afficher un fil court (`Le titre du livre / Canon`), marquer la route active avec `aria-current="page"` et prévoir des zones tactiles d'au moins 44 × 44 px. |

### P2 — Accessibilité, qualité et langage

| Constat | Impact auteur | Recommandation |
| --- | --- | --- |
| Les styles de focus sont surtout limités à la couleur de bordure ; plusieurs boutons iconiques reposent sur un `title` ou un libellé technique en anglais. | Le parcours clavier est peu visible et l'expérience lecteur d'écran est inégale. | Ajouter un focus ring global, vérifier les contrastes AA, utiliser des libellés français descriptifs et annoncer les changements d'état avec une région `aria-live`. |
| Certaines microcopies promettent une obéissance absolue de l'IA (« respectera scrupuleusement »), ou emploient « AI Review ». | Elles surestiment l'automatisation et rompent le ton francophone, à l'opposé de la transparence voulue. | Préférer « vérifie selon vos règles et vous signale les écarts » et « analyse IA ». Toujours distinguer contrôle déterministe et suggestion du modèle. |
| Les tests existants ciblent SEO et accessibilité de base, mais pas les interactions clés du Studio, les états de décision ni les tailles mobiles. | Une régression peut préserver une page accessible tout en cassant le parcours qui fait la valeur du produit. | Ajouter des scénarios Playwright par état de contenu et des captures aux formats 375 px, 768 px et 1440 px ; compléter par axe-core dans la CI. |

## Direction recommandée pour le design system

### Intention

**Un bureau de continuité narratif, pas un générateur d'images de marque ni un tableau de bord générique.** Le geste visuel distinctif doit être la **trace de décision** : chaque proposition porte un état, des éléments de preuve et un chemin clair jusqu'au Canon. L'interface reste silencieuse pendant la lecture et devient structurée au moment de vérifier ou décider.

### Tokens proposés

| Rôle | Nom | Valeur | Usage |
| --- | --- | --- | --- |
| Toile | `--canvas` | `#F7F2E9` | Fond général, jamais pour les alertes. |
| Feuille | `--paper` | `#FFFDFC` | Manuscrit et surfaces de lecture. |
| Encre | `--ink` | `#13243A` | Navigation, titres, action primaire. |
| Ardoise | `--slate` | `#506070` | Métadonnées lisibles et texte secondaire. |
| Sceau du Canon | `--canon` | `#9A6617` | Statut approuvé et validation sur fond clair. |
| Conflit | `--conflict` | `#A33B32` | Contradictions et erreurs, avec icône et texte. |
| Proposition | `--proposal` | `#3D6F8E` | Contenu non approuvé et informations. |

La palette évite l'orange décoratif et le bleu SaaS omniprésent. Le Canon utilise un sceau ocre rare : il signifie une décision humaine durable, pas une simple puce.

### Typographie et mise en page

- **Interface :** Inter, en phrases, 14–16 px pour le texte courant.
- **Manuscrit :** Merriweather, 18–20 px, interligne généreux, largeur de mesure de 60–72 caractères.
- **Titres :** Playfair Display seulement pour le titre de livre, les grands titres de chapitre et quelques pages publiques.
- **Données :** Courier Prime pour version, horodatage, nombre de mots et références de preuve ; pas de capitales systématiques.
- **Desktop :** rail de contexte à gauche, manuscrit central, rail de décision à droite seulement lorsqu'une décision est requise.
- **Mobile :** une colonne et une action primaire ancrée. Les preuves et historiques passent dans un panneau repliable.

## Proposition de parcours cible

```text
Plan approuvé
      ↓
Écrire une proposition ──→ enregistrée comme version immuable
      ↓
Vérifier : règles + continuité + preuves consultables
      ↓
Décider : approuver / demander révision / rejeter
      ↓
Canon mis à jour avec provenance ──→ chapitre suivant
```

Sur chaque étape, une seule action primaire doit être visuellement dominante. « Générer », « vérifier » et « approuver » ne doivent jamais se concurrencer au même premier niveau visuel.

## Logo et favicon

### Problème à résoudre

L'icône actuelle de plume est générique pour l'écriture et ne représente ni la boucle ni la frontière de confiance du Canon. Elle peut accompagner la marque, mais ne peut pas, seule, différencier Book Loop dans un onglet, un favori ou une liste de produits.

### Concept recommandé : « la boucle reliée »

Un monogramme géométrique **B/L** dessiné comme un ruban fermé :

1. une boucle extérieure suggère le cycle proposition → vérification → décision ;
2. une couture intérieure verticale suggère un dos de livre et la séparation entre proposition et Canon ;
3. un petit point/sceau ocre à l'intersection signale l'approbation humaine ;
4. aucune plume, étincelle ou cerveau : ces symboles réduiraient le produit à un assistant IA générique.

La forme doit être reconnaissable sans texte à 16 px et rester monocolore dans les contextes contraints. Prévoir :

- logo horizontal : symbole encre + mot-symbole `Book Loop` en Playfair adapté ou dessin personnalisé ;
- symbole carré : encre sur papier pour les app icons ;
- favicon : symbole seul, sans sceau ocre s'il devient illisible à 16 px ;
- versions monochromes encre et blanc, et une version à contraste renforcé.

### Livrables et validation

1. Explorer trois croquis vectoriels, puis tester le symbole à 16, 32, 48 et 180 px sur fond clair et sombre.
2. Exporter `icon.svg`, `apple-touch-icon.png` (180 × 180), icônes PWA 192 et 512 px, favicon `.ico` multi-résolutions et image Open Graph.
3. Déclarer les icônes dans les métadonnées Next et le manifeste, avec `theme_color` et `background_color` cohérents.
4. Valider reconnaissance et contraste avec 5 à 7 auteurs : reconnaître l'icône parmi des onglets, pas décrire une intention graphique.

## Feuille de route de mise en œuvre

### Sprint 1 — Réduire l'ambiguïté (P0)

- Audit de tous les états et libellés Canon/proposition/décision.
- Barre d'état unique et actions conditionnelles pour chapitre, review et Canon.
- Refondre la page Validation en file de décisions avec preuves et sources.

### Sprint 2 — Systématiser et rendre mobile (P1)

- Introduire tokens sémantiques et primitives de statut/décision.
- Simplifier la navigation du Studio sur petit écran et ancrer l'action contextuelle.
- Créer les scénarios de capture responsive et de navigation clavier.

### Sprint 3 — Marque et finition (P2)

- Concevoir et tester le système de logo/favicon.
- Déployer les assets et métadonnées PWA/partage.
- Traiter contrastes, focus, annonces d'état et cohérence de microcopy.

## Mesures de succès à instrumenter

- taux d'auteurs qui atteignent l'approbation du plan avant la première génération ;
- délai et taux de complétion de la première décision sur une proposition ;
- répartition approuver / réviser / rejeter, avec motif ;
- part de conflits ouverts avant de poursuivre un chapitre ;
- abandon du Studio et retour au Canon sur mobile vs desktop ;
- résultat d'un test de compréhension : « l'IA peut-elle modifier le Canon sans vous ? » (réponse attendue : non).
