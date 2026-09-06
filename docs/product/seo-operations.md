# Book Loop — opérations SEO

## Vérifications techniques

Avant chaque mise en production d’une évolution SEO, vérifier :

- `NEXT_PUBLIC_SITE_URL` pointe vers l’URL publique canonique.
- `/robots.txt` est accessible et référence `/sitemap.xml`.
- `/sitemap.xml` ne contient que des pages publiques réellement accessibles.
- Les pages publiques importantes ont un titre, une description et une URL canonique propres.
- Les parcours authentifiés et privés (`/dashboard`, `/studio`, `/setup`, `/parametres`, `/login`, `/register`) portent `noindex, nofollow` côté metadata.
- Le favicon et le manifest sont présents.
- Les données structurées restent limitées à des informations publiques et stables ; aucun manuscrit, Canon, prompt ou réponse IA n’y est injecté.

## Search Console

1. Créer ou sélectionner la propriété correspondant au domaine public réel.
2. Vérifier la propriété via la méthode disponible (DNS recommandé pour un domaine contrôlé).
3. Soumettre `https://<domaine-public>/sitemap.xml`.
4. Contrôler l’indexation des pages publiques et les erreurs d’exploration.
5. Utiliser l’inspection d’URL après une nouvelle page importante ou une correction technique.

La validation de domaine et les valeurs de production restent des opérations manuelles : ne pas mettre de token de vérification ou de secret dans le dépôt.

## Bing Webmaster Tools

1. Ajouter le domaine public réel.
2. Vérifier la propriété via DNS ou une autre méthode proposée par Bing.
3. Soumettre le sitemap XML public.
4. Surveiller les erreurs d’exploration, l’indexation et les requêtes organiques.

## KPI d’acquisition

Suivre séparément de l’analytics produit :

- impressions organiques ;
- clics organiques ;
- CTR organique ;
- position moyenne par requête cible ;
- pages indexées / exclues ;
- sessions organiques vers `/guides` et les pages produit ;
- inscriptions issues du trafic organique ;
- taux `guide → inscription`.

Ne jamais transmettre de texte de manuscrit, contenu du Canon, prompt, réponse Gemini, document importé ou identifiant direct dans les métriques SEO ou produit.

## Cadence

- Hebdomadaire : anomalies d’indexation et nouvelles requêtes.
- Mensuelle : performance des guides, CTR et conversions organiques.
- À chaque nouvelle page publique : metadata, canonical, liens internes, sitemap et test automatisé.
