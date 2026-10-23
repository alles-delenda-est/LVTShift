# DRAFT — Dossier de demande d'accès aux Fichiers Fonciers (CEREMA/DGFiP)

> **Statut : BROUILLON à compléter et envoyer par le porteur du projet.**
> Ce document donne à l'« argument d'accès » (README, METHODOLOGY §7) ce qui lui
> manquait : un dossier prêt à déposer, un porteur et un déclencheur. Les champs
> `[À COMPLÉTER]` sont volontairement laissés ouverts — identité, structure et
> signature appartiennent au porteur, pas à l'automatisation.

## 0. Porteur, voie et déclencheur

- **Porteur (owner) :** `[À COMPLÉTER — nom, qualité, structure porteuse]`.
  L'accès aux Fichiers Fonciers est délivré via l'*acte d'engagement* CEREMA à
  des **structures éligibles** (collectivités, services de l'État, chercheurs,
  et organismes exerçant une mission d'intérêt général) — le choix de la
  structure (laboratoire partenaire, collectivité pilote, association) est LA
  décision préalable.
- **Voie :** formulaire de demande Fichiers Fonciers du CEREMA (datafoncier.
  cerema.fr) + acte d'engagement ; à défaut d'éligibilité directe, partenariat
  avec une collectivité pilote (une des communes simulées) qui, elle, est
  éligible de droit.
- **Déclencheur (trigger) :** dépôt du dossier **à la publication des résultats
  du pilote** (les communes exportées + bandes de sensibilité) — le pilote
  publié EST la pièce maîtresse de la demande.

## 1. Objet de la demande

Accès aux **Fichiers Fonciers (millésime le plus récent)**, périmètre :
départements des territoires modélisés — **75 (Paris), 92, 93, 94 (petite
couronne), 69 (Rhône / Métropole de Lyon)** et ceux des communes du panel
— **38 (Isère), 74 (Haute-Savoie), 59 (Nord), 46 (Lot), 34 (Hérault),
17 (Charente-Maritime)** — tables parcelles, locaux et propriétaires
(variables listées §3), à des fins de recherche
méthodologique **non commerciale** : évaluation de la faisabilité d'une
assiette foncière (land value tax) à recettes constantes.

## 2. Le projet en deux paragraphes

`lvtshift-fr` simule, parcelle par parcelle et **sur données ouvertes
uniquement** (DVF, cadastre Etalab, BD TOPO, GPU, REI/OFGL, Filosofi), le
remplacement de la TFPB par une taxe assise sur la valeur du terrain, à
recettes constantes, pour Paris, Lyon, leurs petites couronnes (188 communes
au total) et un panel de villes pilotes. Chaque approximation imposée
par l'absence d'accès administratif est documentée dans un registre de limites
public (METHODOLOGY §6) et, quand c'est possible, bornée par une bande de
sensibilité publiée.

La demande d'accès n'est pas un préalable au projet : le pilote **existe et
publie déjà** ses résultats. Elle en est la conclusion logique : chaque ligne
du tableau §3 remplace une imputation documentée par la donnée administrative
exacte, à coût marginal nul pour l'administration.

## 3. Ce que l'accès remplacerait, limitation par limitation

| Limitation actuelle (registre METHODOLOGY §6) | Champ Fichiers Fonciers qui la résout |
|---|---|
| **Taxe actuelle par parcelle** : le produit TFPB de chaque commune est réparti entre établissements industriels, locaux professionnels et logements selon la ventilation officielle reconstituée du REI, puis à la surface plancher. La part des locaux professionnels n'est connue qu'à un facteur près (la base CFE omet les locaux vacants et les occupants non assujettis : ×1 à ×2,5), et ce seul paramètre déplace les résultats par quintile de revenu de 10 à 15 points — c'est aujourd'hui l'incertitude principale | **VLC réelle par local** (catégorie de local, tarif RVLLP, méthode comptable) |
| Surfaces bâti estimées (emprise × niveaux BD TOPO, ramenées en surface habitable par un ratio mesuré sur les DPE ; niveaux manquants imputés par type de bâtiment) | **Surfaces déclarées par local** (habitables, pondérées) et **nombre de niveaux** |
| Année de construction inférée des DPE pour les logements ; bâtiments non résidentiels pris à mi-vie | **Année de construction exacte par local** |
| Type de bâtiment déduit des usages BD TOPO (hangar, bureaux, commerce…) ; parcelles mixtes classées par leur plus grand bâtiment | **Nature et catégorie de chaque local** (habitation, professionnel, industriel) |
| Appariement bâtiment↔parcelle spatial (intersection pondérée) | **Liens MAJIC natifs** local↔parcelle |
| Exonérations : foncier public repéré par la propriété (règle prudente) et bâtiments agricoles par l'usage BD TOPO et le zonage ; exonérations temporaires (HLM neufs art. 1384 A, abattement QPV) invisibles | **Champs d'exonération par local** (nature, durée) |
| Pas de typologie fine des propriétaires ni de vacance | **Table propriétaires** (personnes morales/physiques, HLM) ; **indicateur de vacance** |

## 4. Engagements

- Usage strictement méthodologique/statistique ; **aucune publication de
  montants individuels** (règle déjà en vigueur : résultats agrégés par
  catégorie et quintile uniquement — METHODOLOGY §1).
- Respect de l'acte d'engagement CEREMA : hébergement sécurisé, non-rediffusion
  des données brutes, publication des seuls agrégats, suppression au terme.
- Réplicabilité : le code de traitement est public ; seuls les jeux de données
  sous licence restent hors dépôt (le pipeline sépare déjà ingest/estimate).
- Point de contact données personnelles : `[À COMPLÉTER]`.

## 5. Pièces jointes au dossier

1. Résultats publiés du pilote (agrégats par commune et par territoire, avec
   la bande de sensibilité ±10 points sur la part foncière et la fourchette
   sur la taxe actuelle des locaux professionnels).
2. METHODOLOGY.md / MÉTHODOLOGIE.md (registre de limites intégral).
3. Ce tableau de correspondance limitation→champ (§3).
4. `[À COMPLÉTER]` statuts/mandat de la structure porteuse.

---

*Suivi : ouvrir une issue « Accès Fichiers Fonciers » sur le dépôt avec ce
dossier en corps, assignée au porteur, dès que la structure porteuse est
choisie — c'est l'étape qui transforme l'argument en démarche.*
