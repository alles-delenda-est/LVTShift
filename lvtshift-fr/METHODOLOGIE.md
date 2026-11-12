# LVTShift-FR — Méthodologie

Référence méthodologique complète et citable du pilote français de taxe sur la
valeur foncière (Land Value Tax, LVT) : chaque source de données, formule,
paramètre et limite réunis en un seul document. Version française parallèle de
`METHODOLOGY.md` (anglais, synchronisé avec le code). Docs associés : `README.md`
(synthèse), `THEORY.md` (théorie de fonctionnement, questions ouvertes),
`GUIDE.md` (prise en main pas-à-pas). **En cas de divergence avec le code, le
code fait foi** — maintenir ce document à jour.

## 1. Objet et périmètre

Estimer, parcelle par parcelle, la redistribution **à recettes constantes** de la
*taxe foncière sur les propriétés bâties* (TFPB) d'une commune si elle basculait
vers un impôt sur la seule valeur du sol (la TVTN, taxe sur la valeur du
terrain nu), sur **données ouvertes uniquement**. La France n'évalue pas séparément terrain et bâti : la valeur du
terrain par parcelle est donc **imputée**, avec des marges d'erreur explicites.
Les résultats sont reportés par **catégorie de bien** et **quintile de revenu**,
jamais comme des montants individuels.

Sur le plan technique, il s'agit d'un fork de l'outil américain LVTShift : le code
FR de `lvtshift-fr/` fabrique les colonnes d'entrée attendues par LVTShift à
partir des données ouvertes françaises, puis appelle ses solveurs
(`model_full_building_abatement` à 100 % pour l'impôt sur le seul sol,
`model_split_rate_tax` si un ratio est configuré) et son export
(`save_standard_export`) **sans les modifier**. Les améliorations amont profitent ainsi automatiquement à la version
française.

## 2. Sources de données

| Donnée | Source | Accès | Millésime | Rôle |
|---|---|---|---|---|
| Parcelles | Cadastre Etalab | GeoJSON par commune | dernier | géométrie, surface officielle (`contenance`) |
| Transactions | DVF géolocalisé (Etalab) | CSV par commune | 5 ans glissants | valeur de marché hédonique ; comparables terrains à bâtir |
| Bâtiments | BD TOPO V3 (IGN) | WFS `BDTOPO_V3:batiment`, emprise communale | courant | emprise, niveaux, hauteur, logements, usage, flag d'appariement FF |
| Année de construction | DPE logements existants (ADEME) | API data-fair par `code_insee_ban` | depuis 07/2021 | dépréciation (tranche → année) |
| Zonage | GPU `zone_urba` (IGN) | WFS, emprise communale | PLU/PLUi courant | constructibilité (U/AU vs A/N) des parcelles non bâties ; critère A/N des bâtiments agricoles exonérés (§3.5) |
| Prix agricoles | SAFER « Le prix des terres » | barème départemental (config) | édition 2025 (marché 2024) | €/m² du foncier non constructible |
| Repli terrain à bâtir | EPTB (SDES) | valeur nationale (config) | 2023 | €/m² constructible quand les comparables locaux manquent |
| Cible fiscale | REI foncier bâti, via OFGL | API Opendatasoft par `idcom` | dernier | cible exacte de neutralité (`MONTANT RÉEL`) |
| Impôt sur le non-bâti remplacé | REI (DGFiP), via OFGL `rei` : `B11`, `B13`, `B31`, `B33` (bases et produits de TFPNB), `B11TAFNB`, `B13TAFNB`, `B31TAFNB`, `B33TAFNB`, `B31MGPTAFNB`, `B33MGPTAFNB` (TAFNB) | API Opendatasoft par `idcom` | REI 2025 | TFPNB non agricole et TAFNB que la réforme remplace (§3.5) |
| Répartition de la taxe actuelle | REI (DGFiP), via OFGL `rei` : `E11` (base TFPB), `WC75` (compensation de la division par deux des valeurs industrielles en 2021), `T29`, `T29_1`, `X503` (bases brutes de CFE) ; taux de TFPB 2020 d'OFGL `base-fiscale-simplifiee` | API Opendatasoft par `idcom` | REI 2025 ; taux 2020 | parts industrielle / professionnelle / logement de la base TFPB, par commune (§3.5) |
| Géométrie IRIS | Contours IRIS (IGN) | WFS `STATISTICALUNITS.IRIS:contours_iris` | courant | rattachement parcelle → IRIS pour le revenu |
| Revenus | Filosofi (INSEE) | CSV zip (`DISP_MED21`) | 2021 (voir §6.8) | analyse distributive (quintiles) |
| Foncier public exonéré | DGFiP « Fichiers des locaux et des parcelles des personnes morales » | zips annuels via le catalogue data.economie.gouv.fr | situation 2025 | repérer le foncier public manifestement exonéré de TFPB ; parcelles des bailleurs sociaux (§3.5) |
| Logements sociaux | SDES RPLS, « Données détaillées au logement » | API DiDo par `DEPCOM` (décompte, puis CSV de 13 colonnes) | 1er janvier 2025 | financement, dates, convention, QPV et coordonnées de chaque logement social : exonérations et abattement actuels (§3.5) |

Le RPLS est assorti de règles de diffusion (décret 2009-1485, rappelées dans son
dictionnaire) : aucune statistique permettant d'identifier un bailleur, aucun
chiffre sur moins de 11 logements à une échelle inférieure à la commune, pas de
rediffusion des lignes. Les lignes restent dans le cache local ; seuls des
agrégats communaux sont publiés (§3.5).

Toutes sous Licence Ouverte / Etalab. Les URL exactes sont dans
`config.DATA_SOURCES`.

## 3. Chaîne de traitement et formules

Tout le calcul métrique se fait en RGF93 / Lambert-93 (EPSG:2154). `cell` = un
carreau de 400 m (effet fixe spatial transparent pour l'hédonique, et non une
géographie administrative).

**3.1 Valeur du bâti (improvement)** — coût de remplacement déprécié, agrégé à la
parcelle (`estimate.improvement_value`) :

```
surface_plancher  = emprise_m2 × niveaux       (niveaux imputés selon le type si absent)
surface_habitable = net_to_gross[type] × surface_plancher     (appartements 0,64, maisons 0,61)
coût[type]        = house_cost_eur_m2 pour les maisons s'il est fixé, sinon coût_construction_€m2
                    × ratio_coût[type de bâtiment]        (1 pour le logement ; tableau ci-dessous)
coût_hab          = coût[type] ÷ cost_net_to_gross[type]          (appartements 0,71, maisons 0,82)
âge               = année_référence − année_construction
q                 = prix hédonique médian €/m² des parcelles bâties de l'IRIS
                    ÷ coût_construction_€m2   (médiane communale si l'IRIS n'en a pas)
w                 = borne((q − 1,2) / (2,5 − 1,2), 0, 1)        (dep_q_ramp ; logement seul)
âge_effectif      = w × min(âge, 30) + (1 − w) × âge            (dep_maintained_age_cap)
dépréciation      = borne(1 − (1 − plancher[tb]) × âge_effectif / durée[tb],  min = plancher[tb])
valeur_bâti       = surface_habitable × coût_hab × dépréciation
valeur_marché     = €/m² hédonique × surface_habitable          (§3.3)
```

`année_construction` provient du DPE pour le logement (§3.2) ;
`coût_construction_€m2`, `house_cost_eur_m2`, `dep_years`, `dep_floor` sont en
config par commune (§4) ; `type` est le `type_local` dominant de la parcelle
(les types autres qu'appartement et maison prennent les ratios de surface des
appartements) ; `tb` est le type de chaque bâtiment (ci-dessous), dont la durée
et le plancher sont `dep_years` et `dep_floor` pour le logement. Les parcelles
évaluées au coût de remplacement déprécié (CRD : hangars et assimilés, §3.4) ne
rencontrent jamais de prix DVF : leur valeur bâtie reste calculée sur la
surface plancher du modèle au coût par m² brut, sans conversion en surface
habitable.

*Types de bâtiments non résidentiels* (`estimate.building_type`,
`config.BUILDING_TYPES`). Chaque bâtiment BD TOPO est typé d'après son usage et
sa nature. Le coût de chaque type est un ratio au coût du logement collectif de
la commune (`construction_cost_eur_m2`), et chaque type a sa propre durée de
vie économique et son propre plancher de dépréciation :

| Type | Règle BD TOPO | Ratio de coût | €/m², petite couronne | Durée | Plancher | Valorisation |
|---|---|---|---|---|---|---|
| Hangar (logistique, industrie) | nature « Industriel, agricole ou commercial » (IAC), sauf ligne ci-dessous | 0,250 | 600 | 40 ans | 15 % | CRD, foncier d'activité |
| Atelier | usage Industriel, autres natures | 0,354 | 850 | 40 ans | 15 % | CRD, foncier d'activité |
| Grande surface (« boîte ») | IAC × « Commercial et services » | 0,467 | 1 120 | 40 ans | 15 % | CRD, foncier d'activité |
| Bureaux | autres natures × « Commercial et services » | 0,825 | 1 980 | 60 ans | 20 % | résiduel |
| Hangar agricole | usage Agricole (s'il n'est pas exonéré, §3.5) | 0,073 | 175 | 30 ans | 10 % | CRD, foncier d'activité |
| Serre | nature Serre (si non exonérée) | 0,081 | 195 | 25 ans | 10 % | CRD, foncier d'activité |
| Salle de sport | usage Sportif | 1,033 | 2 480 | 50 ans | 20 % | CRD, terrain à bâtir |
| Annexe (garage, remise) | usage Annexe | 0,227 | 545 | 50 ans | 20 % | CRD, terrain à bâtir |
| Culte | usage Religieux | 1 | 2 400 | 80 ans | 25 % | résiduel |
| Logement | tout le reste | 1 | 2 400 | 80 ans | 25 % | résiduel |

Les ratios viennent d'un guide de coûts commercial qui couvre tous les types sur
une même base (Quostra, € de janvier 2026, recoupé sur des chiffres de
logistique, de bâtiments agricoles, de serres et de garages). Le coût de chaque
type dans le guide, passé par les coefficients géographiques, les honoraires et
l'indice BT01, est divisé par la ligne « logement social » du même guide passée
par la même chaîne. Le type garde ainsi la proportion du guide au logement mais
hérite du niveau de logement du modèle, plus bas et fondé sur des données
officielles (`docs/research/construction-costs-2025.md`) ; les chiffres bruts
du guide sont 15 à 30 % plus élevés. **Les types professionnels sont hors
TVA**, car les entreprises la récupèrent : le guide RICS sur le coût de
remplacement déprécié n'ajoute la TVA « que lorsqu'elle est irrécupérable ».
Les salles de sport sont de fait hors TVA aussi, les communes la récupérant par
le FCTVA. **Les annexes sont TTC**, comme la maison qu'elles servent. L'ancrage
reposant sur un seul guide ramené à notre niveau de logement, les ratios sont à
±25 %. Durées et planchers sont des choix raisonnés, encadrés par les durées
d'usage fiscales (20 à 50 ans), les durées par composant (gros œuvre 50 à 80
ans) et celle des vitrages de serre (20 à 30 ans). Les planchers sont inférieurs
aux 25 % du logement car les hangars subissent une obsolescence fonctionnelle
(hauteur libre, charge au sol, nombre de quais) que l'entretien ne corrige pas.
Sources : `docs/research/nonres-valuation-2025.md` §2–3 et
`docs/research/nonres_costs_calc.py`.

*Âge des bâtiments non résidentiels.* Le DPE diagnostique des logements : ses
années et la médiane communale DPE ne datent plus que le logement. Un bâtiment
non résidentiel garde son année BD TOPO s'il en a une ; sinon il est pris à
**mi-vie** (coefficient (1 + plancher) ÷ 2, soit 0,575 pour un hangar), et non à
l'âge médian des logements. La règle du bâti entretenu ci-dessous est une règle
du marché du logement et laisse le non-résidentiel à son âge.

*Base surface habitable.* Les prix DVF sont exprimés par m² de surface habitable
(`surface_reelle_bati`), alors que `surface_plancher` est l'emprise BD TOPO ×
niveaux. Mesuré sur 35 communes (surfaces habitables DPE appariées aux bâtiments
BD TOPO par leur identifiant RNB, pondération par la surface), le rapport surface
habitable ÷ `surface_plancher` vaut **0,64 pour les appartements (0,59–0,68) et
0,61 pour les maisons (0,58–0,66)** : BD TOPO compte combles, rez-de-jardin et
niveaux techniques comme des étages, si bien que `surface_plancher` surestime même
la vraie surface brute. Les deux termes du résiduel sont donc ramenés à la surface
habitable (`estimate.habitable_basis`, `market_value`). Les coûts de construction
sont exprimés par m² de vraie surface brute (§4) et deviennent un coût par m²
habitable en les divisant par `cost_net_to_gross`, le rapport habitable ÷ brut
retenu par le calage des coûts : **0,71 pour les appartements** (surface utile ÷
brut 0,74, ÷ surface utile ÷ habitable ≈ 1,04) et **0,82 pour les maisons**
(estimation documentaire). Pour une parcelle bâtie, la part foncière vaut alors
1 − coût_hab × dépréciation ÷ prix au m² : elle dépend de `cost_net_to_gross`, non
du `net_to_gross` mesuré, qui ne fixe que les niveaux en euros. Sources :
`docs/research/net-to-gross-measurement.md` et
`docs/research/construction-costs-2025.md`.

*Nombre de niveaux manquant.* Le champ `nombre_d_etages` de la BD TOPO vient des
fichiers fonciers et n'est jamais rempli pour les annexes, les constructions
légères ni les bâtiments qui n'ont pas pu y être appariés ; un nombre nul est lui
aussi traité comme manquant. Diviser la hauteur par 3 m, comme le faisait d'abord
le modèle, fait d'un entrepôt de plain-pied de 14 m un bâtiment de 5 niveaux : le
parc des expositions de Villepinte (165 000 m² d'emprise) devenait 828 000 m² de
plancher. Dans six communes test (Villepinte, Vaujours, Santeny, Périgny, Rungis,
Corbas), le nombre manque sur 42 à 56 % des hangars, 90 % de la surface des
hangars dont le nombre est connu est de plain-pied, et l'ancienne règle gonflait
leur surface plancher de 2,0 à 2,7 fois. `estimate.impute_levels` impute
désormais selon le type : **1 niveau quelle que soit la hauteur** pour les natures
de type hangar (« Industriel, agricole ou commercial », Serre, Silo), les
constructions légères (`construction_legere`) et les usages Annexe, Agricole,
Industriel, Sportif et Religieux ; **les autres bâtiments « Commercial et
services »** 1 niveau sous 7 m, sinon hauteur ÷ 3,5 m ; **le logement** hauteur
÷ 3 m comme avant (2,65 m par niveau mesurés). Les nombres connus sont conservés.
La surface plancher répartit aussi la TFPB actuelle au sein de chaque groupe de
locaux (§3.5) : la correction abaisse la valeur bâtie du non-résidentiel et
modifie la répartition de la taxe d'aujourd'hui entre bâtiments. Sources : `docs/research/nonres-valuation-2025.md` §1 et
`docs/research/nonres_probes/`.

*Bâti entretenu (âge effectif).* Là où les prix du quartier dépassent largement le
coût de reconstruction, les propriétaires rénovent en continu : l'âge réel ne
mesure plus l'usure. Un immeuble de 1880 entretenu est valorisé comme s'il avait
30 ans (coefficient 0,72) au lieu de tomber au plancher de 25 %. C'est la notion
d'âge effectif des évaluateurs (Davis, Larson, Oliner & Shui, FHFA WP 19-01),
appuyée par l'absence de dépréciation physique de long terme du bâti bien
entretenu (Francke & van de Minne 2017) ; les comptes de patrimoine de l'INSEE
capitalisent eux aussi les rénovations (durée de vie 70 ans, base 2020). Le poids
`w` croît continûment avec q, si bien que deux parcelles voisines ne basculent
jamais d'un régime à l'autre, et q est calculé à l'IRIS, non à la parcelle, pour
qu'une hausse locale du foncier ne soit pas lue comme un bâtiment plus récent. La
médiane de l'IRIS ne retient que les parcelles bâties : les terrains nus portent un
type de logement par défaut et tireraient un quartier pavillonnaire vers le prix des
appartements. Dans
les marchés faibles (q ≤ 1,2 : Roubaix, Cahors), la règle est inactive et la
dépréciation par l'âge absorbe aussi l'obsolescence économique. Un plafond uniforme
a été testé et écarté : il place la moitié des parcelles bâties de Roubaix et un
tiers de celles de Cahors à la borne basse de 15 %. q garde délibérément la base
sur laquelle sa rampe a été calée (prix habitable ÷ coût par m² brut) : le
recalculer par m² habitable recalerait la règle sans le dire. Pour la même
raison, q utilise toujours le coût communal, maisons comprises. Il baisse
légèrement avec les coûts recalés (plus élevés).

Les bâtiments sont
rattachés aux parcelles par **intersection pondérée par la surface** (un bâtiment
à cheval sur une limite crédite chaque parcelle au prorata du recouvrement), et
non par centroïde.

*Catégories de biens* (`run_commune.derive_parcel_category`). Chaque parcelle
prend la catégorie de son plus grand bâtiment en surface de plancher (étages
imputés comme ci-dessus). Les usages non résidentiels se traduisent
directement : « Commercial et services » en commerce, « Industriel » en
industriel, et Agricole, Annexe, Religieux et Sportif en « Autre bâtiment ». Un
bâtiment résidentiel ou indifférencié est classé selon son nombre de logements
BD TOPO, réparti entre parcelles au prorata de la surface : 2 à 4 logements, un
petit immeuble ; 5 ou plus, un immeuble collectif ; au plus un, une maison.
Trois garde-fous s'appliquent :
- **Un 0 enregistré** (les fichiers fonciers n'y comptent aucun logement) va en
  « Autre bâtiment ».
- **Au plus un logement sur plus de 500 m² de plancher BD TOPO**
  (`MAISON_MAX_FLOOR_M2`, environ 300 m² habitables au ratio de 0,61 des
  maisons) va aussi en « Autre bâtiment » : bureaux, usage mixte ou décompte peu
  fiable, pas une maison.
- **Sans décompte** (bâtiment non apparié aux fichiers fonciers), c'est une
  maison sous 3 étages et 500 m², et sinon des appartements à 85 m² bruts par
  logement, la règle du fichier annexe des ménages.

Jusqu'en novembre 2026, un décompte manquant s'additionnait à zéro : tout
bâtiment non apparié devenait une maison, quelle que soit sa taille. À Paris,
les parcelles « maisons » dont le bâtiment valait plus de 1,5 M€ formaient un
cinquième de la catégorie et portaient 80 % de son impôt (Lyon 67 %,
Villeurbanne 62 %, Montreuil 47 %) : les chiffres publiés des maisons les
décrivaient surtout. La catégorie fixe la surface de prix (€/m² de maison ou
d'appartement, §3.3) et le groupe publié. La taxe actuelle suit l'usage des
bâtiments, pas la catégorie (§3.5).

**3.2 Année de construction (ancrage de la dépréciation)** — le
`date_d_apparition` de BD TOPO est une date de première apparition en base, pas
une année de construction, et est souvent nulle (100 % à Cahors). On utilise donc
la tranche `periode_construction` du DPE, mappée à une année médiane de tranche
(`avant 1948`→1930, `1948-1974`→1961, … `après 2021`→2022), jointe spatialement
aux parcelles (médiane par parcelle). Les parcelles sans point DPE prennent
l'**année médiane communale pondérée par les logements** en repli, afin que l'âge
ne dégénère jamais en « inconnu ». Les deux ne valent que pour le logement ; les
bâtiments non résidentiels sans année propre sont pris à mi-vie (§3.1).

**3.3 Valeur de marché** — une hédonique log-linéaire volontairement simple sur
DVF (`estimate.fit_hedonic` / `market_value`) : médiane cellule×type du log €/m²,
rétrécie (shrinkage) vers la médiane communale par type (pseudo-effectif k = 8),
× surface habitable de la parcelle (`net_to_gross` × surface plancher, §3.1), la
base sur laquelle les prix DVF sont exprimés. DVF est nettoyé aux mutations `Vente`, agrégé à
la mutation, le €/m² écrêté aux 1er/99e centiles. Les cinq années poolées sont d'abord
ramenées en euros 2025 (paragraphe suivant).

**Déflateur de prix.** Les cinq années DVF couvrent un cycle (hausse jusqu'en 2022,
puis correction), d'ampleur très variable selon les lieux : chaque vente est donc
d'abord ramenée en euros de `reference_year` (2025) : facteur(A) = moyenne annuelle
2025 de l'indice Notaires-INSEE du territoire ÷ sa moyenne de l'année A
(`estimate.deflator_factors`, `config.PRICE_INDEX_IDBANKS`, lu en direct sur la BDM
de l'INSEE). On retient la série la plus locale publiée : appartements à Paris ;
appartements et maisons séparément pour les Hauts-de-Seine, la Seine-Saint-Denis et
le Val-de-Marne ; agglomérations de Lyon, Marseille et Lille ; régions
(Auvergne-Rhône-Alpes, PACA, Nord-Pas-de-Calais) ; Province ailleurs. Quand une
agglomération ne publie qu'un type de logement, cette série sert aux deux types :
associer une série locale d'appartements à une série régionale de maisons
déplacerait les maisons par rapport aux appartements de l'écart ville/région. Les
prix des terrains à bâtir sont déflatés par la série maisons du territoire. Une
vente parisienne de 2022 est multipliée par 0,907, une lyonnaise par 0,865, un
appartement de province par 0,996.

**3.4 Valeur du terrain — classer puis valoriser**
(`estimate.land_value_residual` → `_land_value_classified`). Les parcelles non
bâties sont classées par le zonage GPU ; chaque classe est valorisée sur le bon
référentiel :

| Parcelle | Valeur du terrain |
|---|---|
| **Bâtie** | **valeur du site** (ci-dessous) : le terrain résiduel de chaque IRIS (`marché − bâti`, plancher à la valeur agricole €/m², part foncière bornée à [0,15 ; 0,85]) est réparti à nouveau selon la surface de la parcelle et la densité habituelle de la zone ; bâti au coût déprécié, valeur = terrain + bâti, sans bornage (`lv_flag` `built_site_value`) |
| **Bâtie, plus grand bâtiment de type hangar** (CRD) | €/m² terrain à bâtir × `activity_land_ratio` (types professionnels) ou × 1 (salles de sport, annexes) × surface, plancher à la valeur agricole €/m² ; hors zone urbaine, seule une cour de 3 × la surface plancher prend ce prix. Valeur de marché = terrain + bâti déprécié ; ni prix résidentiel ni bornage (`lv_flag` `built_drc`) |
| **Constructible vacante** (zone U/AUc) | €/m² terrain à bâtir DVF × surface (médiane cellule si ≥ 8 ventes, sinon médiane communale, sinon repli national EPTB) |
| **Constructible différée** (AU/AUs) | idem × `au_strict_factor` (urbanisation différée) |
| **Agricole / naturelle** (zone A/N) | €/m² départemental SAFER × surface ; **hors de la réforme** : la parcelle garde la TFPNB actuelle, ne prend aucune part du nouvel impôt et sort des résultats publiés (comptée dans `farmland_excluded_parcels`) |

Seules les lignes DVF codées *terrains à bâtir* sont utilisées pour les prix du
constructible — le brut `valeur_fonciere/surface_terrain` est contaminé pour les
autres natures de culture car les mutations regroupent bâti et plusieurs
parcelles.

**Coût de remplacement déprécié pour les parcelles de type hangar.** Entrepôts,
ateliers, grandes surfaces, hangars agricoles, serres, salles de sport et
parcelles de garages se vendent rarement seuls, et le €/m² résidentiel du
résiduel ne dit rien d'eux. Les parcelles dont le **plus grand bâtiment** (en
surface plancher) est de l'un de ces types sont donc évaluées au coût de
remplacement déprécié (CRD, *méthode sol + construction*), la méthode de
référence pour les biens sans marché actif (RICS, *Depreciated replacement cost
method of valuation for financial reporting*, 2026, §3.1–3.2, consulté). Le
bâti vaut son coût déprécié (§3.1). Le terrain est valorisé au €/m² local des
terrains à bâtir de la parcelle (le même prix de carreau ou de commune que le
constructible vacant), multiplié par `activity_land_ratio` pour les types
professionnels : **0,45** par défaut et autour de Paris, **0,35** pour Lyon,
Villeurbanne et la couronne lyonnaise. Ces ratios viennent des ventes de
terrains nus DVF 2023–24, classées selon l'occupation du sol (MOS 2021 en
Île-de-France, périmètres des zones d'activités de la Métropole autour de
Lyon) : foncier d'activité contre foncier résidentiel, 381 contre 658 €/m² en
Seine-Saint-Denis (0,58, n = 23), 282 contre 771 dans le Val-de-Marne (0,37,
n = 20) et 0,29 à 0,40 dans la Métropole de Lyon (n = 80). Le RICS valorise lui
aussi le terrain d'un CRD à son usage dominant, non à un usage alternatif
(§7.12–7.14). Les salles de sport et les annexes gardent le plein prix du
terrain à bâtir (× 1,0) : une parcelle de garages est entourée de maisons. La
valeur de marché est terrain + bâti, sans prix résidentiel ni bornage. Le ratio
est publié dans la provenance de chaque fichier (`activity_land_ratio`).

*Cours hors zone urbaine.* Un hangar sur une parcelle de taille agricole en zone
A ou N, ou hors PLU, ferait sinon payer tout le champ comme terrain à bâtir : la
revue de sécurité a trouvé une parcelle agricole de 10 ha évaluée à 16 M€. Là,
seule une cour de **3 × la surface plancher** (`DRC_CURTILAGE_FACTOR` ; les
parcelles logistiques font environ 2 à 2,5 fois l'emprise, choix raisonné)
prend le prix du terrain à bâtir ; le reste est valorisé comme terre agricole
(€/m² SAFER).

*Les bureaux* restent au résiduel sur la surface de prix résidentielle, à leur
propre coût (0,825 × le coût du logement) : bureaux et commerces se vendent, et
une surface de prix DVF des locaux professionnels est la meilleure cible (§6,
point 7). Les lieux de culte restent au résiduel au coût du logement.

**Valeur du site des terrains bâtis** (`estimate.site_value_land`,
`config.SITE_VALUE`).
- **Le principe.** Un impôt sur la valeur foncière taxe le terrain comme s'il
  était nu, à l'usage que permet l'urbanisme. Les Bodenrichtwerte allemands
  sont définis pour le type et l'intensité d'usage habituels de la zone, et
  l'impôt foncier du Bade-Wurtemberg (2025) vaut surface × cette valeur. La
  Nouvelle-Galles du Sud évalue le terrain à son usage permis le plus
  rémunérateur, le Danemark sur la plus grande des surfaces de plancher réelle
  et permise. Dye et England (Lincoln Institute) en donnent la raison : l'impôt
  n'est neutre que si la valeur imposable ne dépend pas de l'usage actuel.
- **Ce que mesure le résiduel.** Le résiduel est une valeur d'usage actuel :
  terrain = (prix − coût) × surface de plancher. Il suit donc la surface bâtie
  sur la parcelle, et une maison basse reçoit une fraction du terrain d'un
  immeuble sur une parcelle identique. Sur 8 591 ventes DVF de maisons dans neuf
  communes, le terrain que paie le marché sous une maison croît avec la surface
  de la parcelle (élasticité d'environ 0,46 dans une maille de 400 m) et non
  avec la surface de plancher ; les élasticités du résiduel sont d'environ 0
  et 1,0 (`docs/research/site-value-2026-11/04-dvf-tests.md`).

Le résiduel ne fixe plus que le total de terrain de chaque IRIS. Dans l'IRIS
(la commune, à défaut), le terrain des parcelles bâties évaluées au résiduel
est réparti à nouveau : logements, bureaux et autres bâtiments. Les parcelles
de type hangar (déjà évaluées sur leur surface, ci-dessus), le foncier public
exonéré et les parcelles au plancher agricole restent hors de cette
répartition, qui suit la règle :

```
poids   = surface utile de la parcelle × densité ^ 0,5
densité = coefficient de référence de la zone      (usage permis)
```

- **Densité de référence.** C'est le 75ᵉ centile du coefficient d'occupation
  réalisé (plancher du modèle ÷ parcelle) des parcelles réparties dans le même
  libellé de zone du PLU (le type de zone, puis la commune, sous 20 parcelles).
  Elle tient lieu de densité permise, qui n'existe pas en données ouvertes
  structurées. Les zones d'habitat individuel vont de 0,2 à 0,9 (Lyon URi1a
  0,93, Villeurbanne URi1a 0,78, Cahors Ub 0,47), les zones mixtes et
  collectives de 1,4 à 6,6 (Paris UG 6,0, Lyon UCe2a 6,1).
- **La densité à la racine carrée.** Les coefficients allemands de conversion
  pour l'habitat font croître le terrain au m² de 0,45 à 0,54 % par 1 % de
  coefficient d'occupation (WertR 2006, annexe 11). Seule compte la densité
  de la zone, jamais celle de la parcelle (usage permis, décision du
  11 novembre 2026) : une maison et un immeuble sur des parcelles identiques
  d'une même zone reçoivent le même terrain. Jusque-là, une parcelle plus dense
  que sa zone gardait sa propre densité, au titre de l'usage existant légal (la
  surface « réelle ou possible » danoise), à la racine carrée
  (`SITE_VALUE["density_rule"] = "max_own"` la rétablit).
- **Surface utile.** C'est la surface de la parcelle, plafonnée au
  99ᵉ centile de la commune, avec deux corrections là où le terrain en plus
  n'est pas constructible :
  - *Zones agricoles et naturelles (A, N).* Seule une cour de 3 × la surface
    de plancher compte, comme pour les parcelles de type hangar. 84 % des plus
    grandes parcelles de maisons de Cahors y sont, et une surface linéaire leur
    donnait +149 %.
  - *Terrain en surplus.* Sur toute parcelle bâtie d'une zone d'habitat
    individuel (référence inférieure à 1), quoi qu'il y soit construit, la
    surface au-delà de deux
    fois la parcelle médiane de la zone compte pour un quart. Les terrains à
    bâtir pour maisons se vendent bien moins que proportionnellement plus cher
    quand ils s'agrandissent (EPTB : élasticité 0,45 à 477 m², 0,11 à
    2 000 m² ; Combes, Duranton et Gobillon), et dans DVF un m² de jardin en
    plus se vend 0,14 à 0,27 fois un m² de terrain à bâtir. La règle ne joue
    pas dans les zones plus denses, où une grande parcelle porte un grand
    bâtiment ; appliquée là, elle déplaçait du terrain des parcelles
    d'immeubles vers les maisons.
- **Bâti et valeur de marché.** Le bâti garde son coût déprécié, et la valeur
  de marché devient terrain + bâti, sans bornage de la part foncière. Le site
  peut valoir plus que la valeur de marché, fondée sur le plancher, de ce qui
  s'y dresse : 11 % des parcelles réparties à Cahors, 27 % à Villeurbanne.

La méthode figure dans la provenance de chaque fichier publié (`land_value`).
`run_commune.py --land current` reproduit le résiduel à la densité existante,
et `--site-elasticity` et `--site-ref-quantile` font varier les deux
principaux paramètres.

**Ce que cela change** (chiffres de son introduction, sous le split-rate 4:1
et l'ancienne règle de la densité propre ; voir le journal des résultats pour
l'impôt sur le seul sol). Le terrain passe, dans chaque IRIS, des bâtiments
denses aux bâtiments peu denses. À Villeurbanne, par exemple :
- les maisons passent de +21 % à +115 % au total ;
- les petits immeubles de 2 à 4 logements, de 0 à +52 % ;
- les grands immeubles, de −1 à −13 %.

Les totaux par cinquième de revenu bougent peu, puisque les totaux de terrain
par IRIS sont conservés. Les médianes des ménages baissent, la plupart des
ménages vivant en immeuble. La part de l'impôt qui change de payeur double
environ (Villeurbanne : 11,7 → 23,5 %). Les effets dans les autres communes
figurent au §3.7.

**Ce sur quoi on ne peut pas la vérifier.** La valeur du site ne s'observe pas
dans les ventes de biens bâtis, dont le prix reflète ce qui est construit, non
ce que la zone permet. Les seules preuves directes sont les rares ventes de
terrains à bâtir nus et les ventes de biens destinés à la démolition ou à la
reconstruction, que les données ouvertes ne repèrent pas. Les retrouver
supposerait de relier DVF aux permis de démolir et de construire (Sitadel,
SDES). Un seul contrôle a été fait : le terrain au m² de parcelle de la maison
type face au prix des terrains à bâtir nus de la même commune. Là où ces
terrains se vendent en nombre, l'écart est faible : Montreuil 2 183 € contre
1 791 € (résiduel publié 1 936 €), Roubaix 422 € contre 394 €. À Lyon,
Villeurbanne et Cahors, les rares ventes de terrains à bâtir sont atypiques et
bien moins chères que le terrain bâti, même au résiduel (Lyon 735 € contre
1 220 € au résiduel et 1 440 € ici) : le contrôle n'y dit rien. Le terrain au m²
de la maison type bouge peu (+1 à +28 %) : le changement porte surtout sur les
grandes parcelles et les maisons en zone dense. Les paramètres (la racine carrée, le
75ᵉ centile, les règles du surplus et de la cour) viennent de barèmes allemands
et d'études françaises sur les ventes de terrains ; aucun n'est estimé sur des
ventes françaises de biens bâtis. Sensibilité (Lyon, Villeurbanne, Cahors) :
- **Élasticité à la densité.** À 0,3 ou 0,7 au lieu de 0,5, la maison type
  passe de +85 à +53 % à Lyon (+69 % en valeur centrale) et de +72 à +39 % à
  Villeurbanne (+55 %).
- **Densité de référence.** À la médiane au lieu du 75ᵉ centile, la maison
  type est à +65 % à Lyon et +50 % à Villeurbanne.
- **Le reste.** Sur ces variantes, les grands immeubles bougent de 1 à
  8 points, les totaux par cinquième de revenu d'au plus 2, et la part de
  l'impôt qui change de payeur reste entre 20 et 25 %.

**3.5 Taxe actuelle (base de départ)** — le produit TFPB exact (REI), réparti
(`estimate.current_tax`) sur les **parcelles bâties uniquement**. La TFPB est un
impôt sur le bâti ; les parcelles non bâties n'en portent aucune part (elles
relèvent de la TFPNB, que la réforme remplace sur le non-bâti non agricole :
*Non-bâti* ci-dessous). **Aucun calage sur la valeur de marché** : la VLC 1970
est régressive par rapport au marché, et un tel calage rendrait la base de
départ moins fidèle à la taxe actuelle.

*Calage par groupe de locaux.* Au sein du bâti, le produit est calé, commune par
commune, sur sa répartition officielle REI 2025 entre trois groupes de locaux
(`config.BASELINE_MODEL` ; sources dans
`docs/research/tfpb-baseline-calibration.md` §2, §3 et §9). Aucune source
ouverte ne publie la base TFPB d'une commune par catégorie :
`ingest.fetch_rei_baseline_split` la reconstitue à partir de deux lignes du
REI :

| Groupe | Base TFPB reconstituée | Contrôle |
|---|---|---|
| Établissements industriels (art. 1499 CGI) | `WC75` ÷ (taux TFPB 2020 commune + département). `WC75` est la compensation versée par l'État pour la division par deux des valeurs industrielles en 2021 ; la loi (LFI 2021, art. 29 III A 2) la fixe à la perte de base × le taux 2020, et la base perdue égale la base restante. Les communes de la Métropole de Lyon prennent le taux 2014 du Rhône (11,03 %), comme le prévoit l'article ; Paris n'a pas de ligne départementale | Appliquée à toute la France, la méthode donne 5,7 % de la base TFPB, exactement le chiffre de la Cour des comptes (*Les taxes foncières*, 2023). La ligne industrielle de la CFE (`X503`) concorde dans un rapport de 0,6 à 1,13 |
| Locaux professionnels (RVLLP, art. 1498) | 0,5 × la base brute de CFE des locaux professionnels (`T29_1`, à défaut `T29 − X503`), × **2,5**. Le 0,5 est l'abattement de 50 % de la TFPB (art. 1388 CGI), qui vaut pour toute propriété bâtie ; la CFE retient la valeur locative entière | La CFE est un impôt d'occupant : les locaux vacants et les occupants hors CFE en sortent. Au niveau national, l'indicateur brut donne 8,6 % de la base contre 22 % pour la Cour. Le facteur 2,5 le cale sur ce chiffre national. La variante publiée est la part locale qu'implique la taxe d'habitation de 2017, 1 − 0,5 × `J11`/`E11` (REI 2017) − 2 × la part industrielle ; l'indicateur brut (× 1,0) là où cette ligne manque (`docs/research/tfpb-baseline-calibration.md` §9.5) |
| Logement et autres | le reste de la base (`E11`) | — |

Un seul taux de TFPB s'applique à toutes les catégories d'une commune : la part
de chaque groupe dans la base est donc aussi sa part du produit (au lissage RVLLP
près, moins de 0,1 %). Les deux points de droit ont été vérifiés sur Légifrance
après qu'une revue par IA (Gemini) a affirmé que l'abattement de 50 % ne vise que
le logement et que WC75 repose sur un taux 2017 : les deux affirmations étaient
fausses. Sa remarque selon laquelle l'indicateur CFE sous-compte était juste, et
le facteur 2,5 en découle.

*Application des parts* (`estimate.baseline_floor`,
`estimate.calibrated_weights`, `run_pipeline._baseline_weights`) :
- **La surface plancher est regroupée** selon l'usage BD TOPO. Industriel =
  usage Industriel. Professionnel = Commercial et services, Sportif, et le
  rez-de-chaussée des immeubles résidentiels dont l'usage secondaire
  (`usage_2`) est commercial : commerces en pied d'immeuble, présents sur 45 %
  des immeubles résidentiels des arrondissements parisiens échantillonnés, 5 % à
  Villeurbanne et moins de 1 % à Villepinte. Logement = le reste. Les parcelles
  exonérées sont écartées.
- **Le produit est partagé** entre les groupes selon les parts cibles, puis à
  la surface plancher au sein de chaque groupe. Chaque groupe reçoit ainsi une
  taxe au m² rapportée à celle du logement.
- **L'industriel rejoint le professionnel** là où il paierait moins au m² que
  les locaux professionnels : ces hangars sont imposés comme locaux
  professionnels (entrepôts), non comme établissements industriels. C'est le
  cas à Villepinte et Santeny, à environ 0,42–0,46 × le logement au m².
- **Plafonds.** Les pondérations au m² sont plafonnées à 5 × le logement. Là où
  les parts industrielle et professionnelle dépassent ensemble 75 %, elles sont
  ramenées à 75 %, le facteur national pouvant déborder dans les communes très
  tertiaires ou industrielles (Rungis 77 %, Marcy-l'Étoile 84 %, Vaujours 93 %).
- **Repli.** Si les données REI manquent ou sont malformées, la répartition
  revient à la seule surface plancher, avec une note. Les 188 communes
  modélisées sont toutes calées.
- **Publication.** La méthode, les parts cibles et les parts obtenues figurent
  dans la provenance de chaque fichier publié (`current_tax_baseline`).
  `run_commune.py --baseline floor` reproduit l'ancienne base à la surface
  plancher, en sensibilité.
- **Variante calculée en parallèle.** Chaque calcul répartit une seconde fois
  la taxe actuelle avec la cible professionnelle à la part locale qu'implique la
  taxe d'habitation de 2017, 1 − 0,5 × `J11`/`E11` (REI 2017) − 2 × la part
  industrielle (`ingest.fetch_th2017_housing_share` ; l'indicateur brut, × 1,0,
  là où la part 2017 manque ou sort de (0, 1) : Sathonay-Camp seulement, dont la
  ligne 2017 donne 1,11), selon les mêmes
  groupes, la même règle de fusion et les mêmes plafonds. Elle est conservée
  dans le fichier annexe des ménages (`current_tax_low`), vérifiée à produit
  constant à l'export et publiée sous `baseline_sensitivity` avec sa source
  (`low_source`, §3.7). Les cotisations LVT ne changent pas ; seule la taxe
  actuelle change. Jusqu'au 31 octobre 2026, la variante était l'indicateur brut
  (× 1,0) ; le contrôle par la taxe d'habitation 2017
  (`docs/research/tfpb-baseline-calibration.md` §9.5) l'a montré bien trop bas
  en ville.

Exemples de pondérations au m², rapportées au logement : Saint-Fons industriel
1,30, professionnel 0,91 ; Rungis 1,71 (industriel fondu dans le
professionnel) ; Vaujours et Marcy-l'Étoile au plafond de 5. Les parts cibles
de Paris sont de 1,4 % (industriel) et 24,9 % (professionnel) ; celles de Lyon
de 1,6 % et 27,2 %.

*Les entreprises paient plus au m² que ne le supposait la surface plancher.* On
s'attendait à ce que la base à la surface plancher surestime ce que paie
l'industrie aujourd'hui. Les parts officielles montrent l'inverse, pour deux
raisons. Les valeurs industrielles de l'art. 1499 incluent l'outillage fixe, pas
seulement le bâtiment. Les locaux professionnels ont été réévalués sur les
loyers de 2013 (révision RVLLP de 2017), alors que le logement repose toujours
sur les valeurs de 1970. La taxe actuelle des entreprises est donc plus élevée
que ne le suggérait la surface plancher, et la réforme déplace davantage de
charge des entreprises vers les ménages que ne le montrait la base à la surface
plancher (§3.7).

**Foncier public exonéré** (`exemptions.py`, spec 0003). L'art. 1382-1° du CGI
exonère les propriétés de l'État, des régions, des départements, des communes, de
leurs groupements et des établissements publics scientifiques, d'enseignement et
d'assistance affectées à un service public et improductives de revenus. Les
fichiers DGFiP « personnes morales » listent chaque droit détenu par une personne
morale sur chaque parcelle et chaque local, avec la forme juridique INSEE du
titulaire (98,4 % de leurs identifiants de parcelle se retrouvent au cadastre). Ils
ne portent ni code d'exonération ni affectation : la propriété est donc un
indicateur, et la règle pèche par défaut. Une parcelle n'est exonérée que si
**tous** les titulaires de droits sur le sol et sur chaque local sont des
personnes publiques éligibles en pleine propriété, sur leur propre territoire (le
bien d'une commune ou d'un département ailleurs n'est que partiellement exonéré,
BOFIP BOI-IF-TFB-10-50-10-10 §90/§250), sans syndic de copropriété, sans bail
(emphytéose, bail à construction, AOT…), sans démembrement et sans gérant privé ou
bailleur (les locaux de réseaux type poste ENEDIS sont ignorés). Le foncier public
**sans** local enregistré n'est exonéré que si le modèle n'y voit pas non plus de
bâtiment (parcs, bois, cimetières) ; un bâtiment y reste imposable (concession type
Stade de France) tant qu'il n'est pas corroboré. Les parcelles exonérées ne portent
aucune part du produit actuel et sortent de l'assiette LVT : le même produit pèse
sur les parcelles imposables. À Paris, 3 099 parcelles (dont 1 362 bâties) sont
signalées ; elles portaient 91,6 M€ (5,0 %) du produit que l'état initial leur
attribuait. Les dénominations ne servent qu'à reconnaître réseaux et bailleurs et
ne sont jamais stockées ni publiées.

*Les organismes sans but lucratif ne sont pas exclus.* Seules les formes
juridiques publiques ci-dessus sont retenues. Associations, fondations, écoles et
hôpitaux privés à but non lucratif paient aujourd'hui la TFPB, et le modèle taxe
leur sol comme celui de tout propriétaire. Les exceptions prévues par la loi qui
ne sont pas modélisées (édifices du culte détenus par des associations, entre
autres) restent imposables (§6 point 11).

*Ce que paierait le foncier public.* La réforme conserve l'exonération actuelle.
Si le sol public était taxé comme le sol privé, il paierait, à l'échelle
nationale (INSEE fin 2025, terrains bâtis des administrations publiques 941 Md€,
`docs/research/yields-2026.md`) : au taux actuel à rendement égal, 10,3 Md€
par an dans le scénario 1 et 12,6 Md€ dans le scénario 3 avec l'IFI. À rendement
égal avec le sol public dans l'assiette, le taux du scénario 1 passe de 1,10 % à
0,95 % : le sol public paie 9,0 Md€ et tous les autres propriétaires 13 % de moins.
Environ les trois quarts de ce sol public appartiennent aux collectivités locales
(75 % en 2019, INSEE tableau 8.200) : l'essentiel de ces montants irait d'une
commune ou d'un département à lui-même ; seule la part de l'État et de ses
opérateurs, environ un quart, serait un vrai transfert vers les budgets locaux. Le
chiffre de l'INSEE comprend aussi le sol des routes et des réseaux. Les résultats
par commune ne montrent pas la valeur des parcelles exonérées : l'export standard
la met à zéro.

**Bâtiments ruraux exonérés** (`exemptions.rural_buildings`). L'art. 1382 6° du
CGI exonère de TFPB les bâtiments affectés de manière permanente et exclusive à un
usage agricole (serres, granges, silos, étables) ; le sol qui les porte acquitte
la TFPNB, hors du produit modélisé. Le critère légal est l'usage, non la propriété
(`docs/research/nonres-valuation-2025.md` §7, consulté via doctrine.fr ;
Légifrance et le BOFiP n'ont pu être interrogés en direct). Les données ouvertes
ne voient pas l'usage : le modèle prend un indicateur BD TOPO. Un bâtiment est
rural si
- son usage est « Agricole » **et** sa nature est Serre ou Silo, ou sa parcelle
  est en zone A ou N du PLU ; ou
- c'est un hangar (« Industriel, agricole ou commercial ») sans usage renseigné
  ou « Indifférencié », en zone A ou N : la BD TOPO laisse souvent vide l'usage
  des hangars agricoles.

Un hangar « Agricole » en zone urbaine reste imposable (ce peut être un atelier
reconverti), de même que les serres de jardinerie (usage commercial). Le zonage
est désormais chargé une seule fois, avant le filtrage des bâtiments. Les
bâtiments ruraux sont retirés avant la valorisation et avant la répartition de la
TFPB actuelle. Sur une parcelle mixte (ferme et serres), la ferme reste. Une
parcelle qui ne porte que des bâtiments ruraux devient du foncier non bâti, évalué
comme toute terre agricole (€/m² SAFER agricole / naturel, ou sa classe de zone,
§3.4) : elle ne paie pas de TFPB aujourd'hui et, sous la LVT, seulement sur la
valeur de son sol, comme les autres terrains non bâtis. 156 communes modélisées
comptent au moins un bâtiment rural. En commune urbaine, la règle des zones N
saisit aussi des dépendances de parcs (Vitry-sur-Seine 1,2 % de l'emprise bâtie,
Villeurbanne 0,1 %), pour l'essentiel publiques et déjà largement exonérées.
L'indicateur ne vérifie pas l'usage agricole réel ; les codes d'exonération des
fichiers fonciers le permettraient.

`--no-exemptions` désactive à la fois l'exonération du foncier public et celle
des bâtiments ruraux, et reproduit le calcul sans signalement.

**Non-bâti : la TFPNB remplacée** (`ingest.fetch_rei_unbuilt_replaced`,
`estimate.unbuilt_tax` ; décision du 11 novembre 2026, recherches dans
`docs/research/tfpnb-2026-11/`). La réforme remplace l'impôt sur le non-bâti
autre qu'agricole : la part non agricole de la TFPNB de la commune et toute la
TAFNB (art. 1519 I du CGI). Les terres agricoles et naturelles gardent leur
TFPNB, hors de la réforme (§3.4). Jusque-là, le modèle ne maintenait constante
que la TFPB : une parcelle non bâtie payait 0 € aujourd'hui et son impôt foncier
apparaissait comme une hausse à partir de rien ; les scénarios nationaux
supposaient déjà ce remplacement (`docs/research/yields-2026.md`).

*Le montant.* Aucune source ne publie la TFPNB par nature de terrain. La TAFNB
n'est assise que sur les groupes cadastraux 7 et 10 à 13 (carrières, terrains à
bâtir, terrains d'agrément, chemins de fer, sols ; BOI-IF-AUT-80) : sa base
rapportée à celle de la TFPNB (`B11TAFNB + B31TAFNB + B31MGPTAFNB` sur `B11`, ou
`B31` pour l'EPCI) donne la part non agricole de la base, et du produit puisqu'un
seul taux s'applique à tous les groupes. Montant remplacé = part × `B13` + part
× `B33` + les produits de TAFNB (`B13TAFNB`, `B33TAFNB`, `B33MGPTAFNB`), REI
2025, sur les strates neutralisées. Il s'ajoute aux recettes maintenues
constantes. Sur les 188 communes, il représente 23,2 M€ pour 6 766 M€ de TFPB
(médiane 0,47 % de la TFPB d'une commune, de 0,02 % à 2,9 %) ; la part non
agricole a une médiane de 96 % (20 % au plus bas).

*Qui le paie aujourd'hui.* Les valeurs cadastrales de cet impôt (tarifs par
nature et classe, fixés en 1961) ne sont pas des données ouvertes : le montant
est réparti selon la surface sur les terrains qui le paient, à savoir les
parcelles non bâties comprises dans la réforme (ni terres agricoles exclues, ni
foncier public exonéré) et le terrain libre des **maisons** au-delà de cinq
ares, hors zones A et N (surface de la parcelle − emprise bâtie − 500 m²).
L'administration tient le jardin attenant à une maison pour une dépendance du
bâti jusqu'à cinq ares ; au-delà, c'est un terrain d'agrément du groupe 11,
imposé comme un terrain à bâtir (BOFiP BOI-IF-TFB-10-10-40). Les cours, jardins
et parcs des immeubles collectifs sont des dépendances de l'immeuble et ne
reçoivent aucune part. Un même poids au m² s'applique dans toute la commune, et
le modèle valorise presque partout le terrain à bâtir nu à un seul prix au m²
par commune : presque toutes les parcelles nues d'une commune ont donc la même
variation en %. C'est une moyenne communale, non le résultat d'une parcelle.

*Vérifié après une relecture par IA (Gemini).* Son affirmation selon laquelle la
majoration de l'art. 1396 sur les terrains constructibles expliquait les forts
multiples ne tient pas : la majoration relève la base communale mais ni celle
de l'EPCI ni celle de la TAFNB, et aucune des 66 communes modélisées disposant
des deux bases ne montre d'écart ; là où il n'y a pas de base intercommunale
(Paris et petite couronne), elle ajouterait au plus 0,3 M€ au total. Un
avertissement s'affiche si une commune montre un jour cet écart. Sa remarque sur
les grands jardins, qui paient aussi cet impôt, était juste et significative :
le terrain des maisons au-delà de cinq ares porte une médiane de 37 % du montant
sur les 188 communes (20 à 63 % dans les territoires publiés), d'où la part
attribuée aux jardins. Le poids double
qu'elle suggérait pour les terrains à bâtir n'avait pas de source et n'a pas été
retenu.

*Résultats* (calcul du 11 novembre 2026). Le terrain nu compris dans la réforme
a désormais une vraie variation : son impôt est multiplié par environ 3,5 à
Villeurbanne, 5 à Sète, 7 à Montreuil, 14 à Lyon, 17 à Paris, 47 à La Rochelle et
60 à Annemasse, pour une médiane de 67 € à 1 793 € par parcelle et par an. Les
autres chiffres bougent de moins d'un point, sauf le total des maisons, qui
baisse jusqu'à 25 points là où les grands jardins paient désormais aujourd'hui
(Paris +261 % → +236 %). Le site affiche les hausses d'au moins ×3 sous forme
de multiple, la barre étant coupée au bord de l'échelle.

`--no-unbuilt-tax` reproduit le calcul sans ce remplacement.

**Logement social** (`social_housing.py` ; recherches dans
`docs/research/hlm-2026-11/`). Aujourd'hui, les art. 1384 A (constructions neuves
et VEFA) et 1384 C (acquisitions) du CGI exonèrent les logements locatifs sociaux
conventionnés financés par un prêt réglementé pendant 15 ans à compter de
l'année qui suit l'achèvement ou l'acquisition, 25 ans si la décision de
financement date du 1er juillet 2004 au 31 décembre 2026 ; l'art. 1388 bis abat
de 30 % la base des logements HLM et SEM imposables situés dans un quartier
prioritaire (QPV) de 2024, pour les impositions 2025 à 2030. Le produit du REI
exclut les bases exonérées et abattues (`E11` est la base après elles, `E13` les
cotisations émises) : le modèle répartit donc l'impôt actuel sur la seule surface
imposable. La réforme met fin aux deux régimes : les bailleurs sociaux paient
l'impôt sur le sol comme tout propriétaire.

*Quelles parcelles* (`social_parcels`). D'après le fichier des personnes morales,
par département : une société est un organisme HLM si la plupart de ses lignes
portent le groupe 5 (« office HLM » ; le code est saisi ligne par ligne, et les
vrais organismes en ont environ 95 %), si elle a une forme juridique HLM (SA
5546/5646, coopérative 5547/5647, OPHLM 7371) ou si c'est un EPIC local (4140)
nommé comme un office public de l'habitat (l'OPH de la Métropole de Lyon est codé
groupe 9) ; une SEM si la plupart de ses lignes portent le groupe 6 ou si elle a
une forme de SEM. Les sociétés de logement intermédiaire (In'li) ne sont jamais
sociales. Un bailleur détient un local quand il y a un droit dont le titulaire
paie la TFPB (P, U, E, R, W), sauf la pleine propriété d'un local donné à bail à
un autre (le terrain d'une commune sous bail emphytéotique à un office est celui
de l'office). Une **résidence** est une parcelle où le bailleur détient des locaux
et le sol.

*Quels logements, quel régime* (`dwelling_status`, `fetch_rpls`). Le RPLS donne
une ligne par logement social, avec ses coordonnées mais sans parcelle ni
bailleur. Pour l'imposition 2025, un logement est exonéré s'il est conventionné
(`CONV` = 1), financé par PLAI, PLUS, PLS ou un autre prêt aidé postérieur à 1977
(`FINAN_CODE` 10, 11, 13, 14, 49), et si son délai a commencé en 2010 ou après
(15 ans), ou dès 2005 avec une convention datée de juillet 2004 à 2026 (25 ans ;
pour un départ en 2005–06, la convention doit dater de 2005, car elle peut suivre
la décision de quelques mois ; sans date de convention, à partir de 2007). Le
délai part de l'achèvement (`CONSTRUCT`) pour le neuf et la VEFA, de l'entrée dans
le patrimoine du bailleur (`PATRIMOINE`) pour les acquisitions, sauf pour les
**transferts entre bailleurs**, qui n'ouvrent pas de nouvelle exonération
(art. 1384 C ; la convention suit le logement, CCH L. 353-4) : une acquisition
dont la convention est antérieure de plus de 2 ans à l'entrée est un transfert,
et son délai part du plus tardif de l'achèvement et de la convention. L'année de
première location (`LOCAT`) ne sert qu'en repli, sans date de convention :
certains bailleurs y déclarent la première location du bâtiment, pas sa première
location sociale. À Montreuil, 1 167 transferts apparents selon `LOCAT` sont
financés par des prêts créés après leur année `LOCAT` (PLUS, depuis 1999), et
1 288 ont été conventionnés dans les 3 ans suivant leur entrée : ce sont des
acquisitions, exonérées. Le PLA ordinaire (`FINAN_CODE` 12) n'est jamais exonéré
en 2025 : le PLUS l'a remplacé en 1999, donc toute décision est antérieure à
juillet 2004 et ses 15 ans (20 avec la majoration environnementale) ont pris fin
en 2024 au plus tard. Le PLI (16) et le PCL (17) sont des loyers intermédiaires.
Un logement imposable en QPV (`PLG_QP24` « QN… ») bénéficie de l'abattement s'il
est conventionné ou financé avant 1977 par un prêt HLM (50–55, 99), qui ouvrait
l'ancienne exonération de l'art. 1384.

*Placer les logements* (`parcel_social` ; sources_report §4). Chaque point
d'adresse du RPLS va à la parcelle la plus proche où un bailleur social détient
des locaux ou le sol, dans un rayon de 30 m (96 % et 94 % des logements à
Montreuil et Villeurbanne), sinon à la parcelle qui le contient (la plus proche à
15 m). Le point d'adresse tombe souvent sur une parcelle voisine de la même
résidence : les parcelles contiguës (à 2 m) **d'un même bailleur** forment donc
une résidence, qui prend le facteur de ses logements pondéré par la surface
habitable (0 exonéré, 0,7 abattu, 1 imposable). Deux résidences voisines de
bailleurs différents restent distinctes ; une parcelle de bailleur inconnu
rejoint une résidence contiguë sans jamais en relier deux. Sur une résidence,
toute la surface de logement est sociale (celle d'une SEM seulement si sa
résidence porte des logements du RPLS : les SEM ne sont qu'en partie sociales) ;
ailleurs, la part sociale est la surface habitable du RPLS rapportée à 0,72 × la
surface brute de logement de la BD TOPO, plafonnée à 1 (0,70–0,75 mesurés par
résidence), avec le facteur des logements de la parcelle. La surface de logement
d'une parcelle pèse alors 1 − part × (1 − facteur) dans l'impôt actuel
(`estimate.current_tax`, `hlm_tax_factor`), dans le total logement de la
calibration par groupe et dans les parts atteintes : le produit que retirent les
exonérations retombe sur les autres surfaces imposables, comme dans le REI. Les
cotisations de la réforme n'en dépendent pas.

*Qui supporte la variation.* La TFPB n'est pas une charge récupérable (décret
82-955, annexe VIII) et les loyers conventionnés sont plafonnés (CCH
L. 353-9-3) : la variation sur le logement social pèse sur le bailleur, une
entreprise. Les parcelles dont la surface de logement est sociale pour moitié au
moins, et résidentielles ou annexes par l'usage, forment la catégorie **Logement
social (bailleurs)**, hors de l'ensemble résidentiel et donc de tout chiffre par
ménage ou par revenu. Ailleurs, seule la part privée des logements compte dans
les pondérations par ménage. La catégorie est attribuée après l'évaluation et ne
change aucune valeur.

*Diffusion* (`export_web`). La catégorie Logement social, et les décomptes
communaux de logements du RPLS exonérés et abattus aujourd'hui, ne sont publiés
que si au moins 3 bailleurs en détiennent les parcelles et qu'aucun n'en porte
plus de 85 % de l'impôt, aujourd'hui ou après la réforme (`MIN_SOCIAL_LANDLORDS`,
`MAX_LANDLORD_SHARE`, les deux règles du secret statistique des entreprises) ;
sinon, la catégorie rejoint « Autre ». Les sorties locales du calcul gardent une
clé de bailleur par parcelle, pour compter seulement : une empreinte du SIREN,
que la liste publique des SIREN permettrait de retrouver, et qui n'atteint donc
jamais les données publiées. Aucun SIREN, nom ou ligne du RPLS n'est publié, et
seuls des chiffres communaux le sont. Comparer les données d'une commune où la
catégorie est regroupée avec celles d'avant la modélisation du logement social
montre combien de parcelles ont quitté les lignes résidentielles pour « Autre » :
un nombre de parcelles, largement déductible du
fichier public de la DGFiP, sans aucun chiffre en € ou en % (revue de sécurité
du 4 novembre 2026).

*Résultats* (calcul du 4 novembre 2026). Sur les 188 communes, 1,11 million de
logements du RPLS, placés sur une parcelle à 98,8 % ; 22,7 % sont exonérés en
2025 et 29,7 % abattus, face à une estimation nationale de 20 à 25 % exonérés
(`legal_report.md` §6.2). Montreuil : 23,7 % des 18 755 exonérés et 41,8 %
abattus ; Villeurbanne : 25,3 % des 21 711 exonérés et 21,2 % abattus. À
Montreuil, la part de l'impôt actuel des parcelles sociales baisse de 23 % (65
d'entre elles ne paient rien aujourd'hui), les autres parcelles payant la
différence, et la catégorie paie −4,2 % au total après la réforme : les
résidences denses gagnent à un impôt foncier, même une fois leurs exonérations
supprimées. La catégorie Logement social figure dans 11 des 13 territoires
publiés ; à Cahors et Figeac, elle rejoint « Autre » par les règles de diffusion.
Retirer les résidences sociales des chiffres par ménage rend le total du
cinquième le plus modeste moins favorable là où elles logent beaucoup des plus
modestes (Villeurbanne −6,1 % → −1,5 %, Montreuil −18,8 % → −8,4 %) : le gain des
résidences revient aux bailleurs. La médiane d'une catégorie compte désormais
une parcelle qui ne paie rien aujourd'hui comme une hausse, et non comme
indéfinie (§3.7).

`--no-social-housing` reproduit le calcul sans le logement social.

**3.6 Solveur : le seul sol** — la réforme n'impose que le sol (décision du
11 novembre 2026 ; jusque-là, un split-rate 4:1, le sol imposé quatre fois plus
que le bâti, était publié). `run_pipeline.solve_reform` appelle le
`model_full_building_abatement` amont avec un abattement de 100 % : un taux
unique sur le sol, neutre en recettes, le bâti n'étant plus imposé ; les biens
exonérés et les terres agricoles exclues restent hors du champ. Le sol est la
valeur de site (§3.4), évaluée comme si le terrain était nu à la densité type
de sa zone, qui tient lieu de la densité qu'elle permet : deux parcelles
identiques d'une même zone dans un IRIS paient la même chose, quoi qu'il y
soit construit. Deux traces de l'usage actuel demeurent : le total foncier
d'un IRIS reste le résiduel de ce qui y est bâti (la seule mesure du marché
pour le sol en zone bâtie), et les hangars et entrepôts prennent le prix du
sol d'activité selon le type de bâtiment, là où l'usage permis demanderait
la destination dominante de la zone (le champ `destdomi` du standard CNIG,
pas encore récupéré). Donner un nombre à
`split_rate_ratio` rétablit le modèle split-rate, par le `model_split_rate_tax`
amont. L'export est écrit par `save_standard_export` ; les graphiques en euros
par `charts_fr` (surcouche de localisation monétaire du rapport amont).

*Décomposition* (`estimate.revalued_tax`, `export_web._steps`). Une partie de la variation de chaque groupe tient au
remplacement d'une base de 1970, non à l'imposition du sol. Un impôt
intermédiaire, au produit d'aujourd'hui, la partage en deux :

1. **Les logements aux valeurs de marché** (`revalued_tax`) : l'impôt bâti
   d'aujourd'hui, la part du groupe des logements étant répartie selon la
   surface de logement imposable × (prix hédonique du logement au m² à
   l'emplacement de la parcelle, `eur_m2`)^0,8, au lieu de la seule surface.
   (Pas la valeur de marché ÷ le plancher : après l'étape de la valeur de
   site, elle vaut terrain + bâti, et une parcelle évaluée au coût porte le
   sol de toute sa parcelle, si bien qu'un abri de jardin passerait pour le
   logement le plus cher de la ville ; revue indépendante du 12 novembre
   2026.) La chaîne vérifie que les mêmes poids, à un exposant nul, rendent
   l'impôt d'aujourd'hui. Les surfaces des groupes industriel et
   professionnel gardent leur montant d'aujourd'hui, si bien qu'un commerce
   ou une usine garde son impôt sauf s'il compte aussi des logements : les locaux professionnels ont été
   révisés en 2017, et la révision des valeurs locatives des logements
   (RVLLH, LF 2020 art. 146, désormais prévue pour les bases 2031 après la
   LF 2026 art. 106) neutralise la base des logements de chaque commune
   (art. 146 V.B). Exonérations et abattements restent ceux d'aujourd'hui ;
   l'impôt sur le non-bâti est inchangé. L'exposant est inférieur à 1 parce
   que les loyers montent moins que les prix : le rendement brut passe
   d'environ 6,3 % à 5,2 % quand le prix passe d'environ 1 600 à 3 900 €/m²
   (Chapelle et Eyméoud, PLOS ONE 2022, tableau 6), soit une élasticité des
   loyers aux prix proche de 0,8. La simulation de la révision par l'IPP
   (rapport n° 29, 2020) suppose 1 au sein d'une commune. Gemini proposait
   0,55, sans source ; nous ne l'avons pas retenu.
2. **Le passage à la TVTN** (la réforme, `new_tax`, contre l'impôt 1), qui
   comprend la fin des exonérations du logement social.

Les deux étapes sont publiées, par catégorie et par groupe de revenu, en %
de l'impôt actuel du groupe, et s'additionnent à sa variation totale (aux
arrondis près). Une première version isolait aussi la fin des exonérations,
avec un impôt qui les maintenait ; elle a été abandonnée et cet impôt n'est
plus calculé : entre lui et la réforme, l'impôt de toute parcelle non
exonérée était multiplié par un même facteur, que n'importe quelle ligne de
maisons révélait ; avec le produit publié, ce facteur donnait en euros
l'impôt sur le logement social exonéré, celui d'un seul bailleur ou d'une
seule parcelle dans certaines communes (revue de sécurité du 11 novembre
2026). Les étapes ne sont publiées que là où les groupes de locaux ont été
conservés (la base calibrée, toutes les communes publiées) ; sur la base de
la seule surface, elle déplacerait aussi l'impôt des commerces et de
l'industrie. L'exposant figure dans la provenance de chaque fichier publié
(`rent_price_elasticity`).

Les étapes sont des totaux, non des médianes, parce que seuls les totaux
s'additionnent. Les étapes d'un groupe sont retenues avec son total, ou
quand une parcelle porte plus du dixième de l'impôt du groupe, aujourd'hui,
selon l'impôt 1 ou après la réforme (groupes de revenu compris). Chaque étape
est neutre en recettes entre catégories, mais pondérée par l'impôt actuel des
catégories, qui n'est jamais publié : les lignes publiées ne permettent pas
de retrouver une ligne retenue, pourvu qu'au moins quatre soient publiées : un
groupe retenu sans logement a une étape 1 nulle et, s'il s'agit du terrain
nu, un impôt actuel proche du montant publié de l'impôt sur le non-bâti ;
avec le produit publié, deux lignes publiées fermeraient les équations
(revues de sécurité et indépendante du 12 novembre 2026) ; avec trois, les
bornes tirées d'impôts positifs restaient serrées dans quelques regroupements
d'essai, avec quatre dans aucun. Avec une ligne retenue (ni total en %, ni
total en € ; une ligne en euros, non imposée aujourd'hui, ne pèse pas) et
moins de quatre lignes publiées, aucune étape n'est publiée. Le garde-fou de l'export le vérifie. La règle des bailleurs sociaux porte aussi
sur l'impôt 1.

Ce que la première étape n'est pas : notre « aujourd'hui » est lui-même une
estimation selon la surface (§3.5), sans élément de situation ni de confort,
alors que les valeurs de 1970 portent des coefficients de catégorie et de
situation. L'étape mesure le passage d'une répartition selon la surface à une
répartition selon la valeur au sein des logements : une approximation de la
révision, non sa simulation. L'IPP trouvait que la révision baisserait de
5,6 % l'impôt des logements du décile le plus pauvre et relèverait de 9 % celui
du plus riche (20 grandes aires urbaines, hors Paris), un ordre de grandeur
auquel comparer le nôtre. Documents : `docs/research/revaluation-2026-11/`.

**3.7 Paris, Lyon et leurs couronnes** — Paris (75056) et Lyon (69123) lèvent la
TFPB en tant que commune unique, mais cadastre, DVF, DPE et IRIS sont publiés par
arrondissement (75101–75120, 69381–69389). La configuration porte les deux :
`insee_code` est le code fiscal sur lequel le REI est indexé, `sub_codes` les
codes de données. Chaque collecteur parcourt les codes de données (les requêtes
spatiales se font une emprise d'arrondissement à la fois, de sorte qu'un bâtiment
en limite n'est attribué qu'aux parcelles qu'il recouvre), les tables sont
empilées en une seule commune et **un** impôt foncier neutre en recettes est résolu
pour la ville — comme l'impôt réel, à taux unique. Les DPE rattachés au code de la
ville sont également récupérés.

Les **territoires extra-muros** — *Paris extra-muros* (les 122 communes des 92/93/94)
et *Lyon extra-muros* (les 57 autres communes de la Métropole de Lyon ; liste figée
dans `territories.py`) — ne sont **pas** un impôt métropolitain. Chaque commune
membre est résolue sur son propre produit REI et reste à recettes constantes
(`run_territory.py`, un processus par commune) ; `export_web.build_territory_payload`
agrège ensuite les résultats par parcelle. La bande de sensibilité est
recalculée commune par commune, chacune sur son propre produit, avant
agrégation ; les quintiles de revenu sont classés sur toute la
couronne. Une commune en échec figure dans le champ `coverage`, jamais imputée.
Montreuil et Villeurbanne apparaissent seules et dans leur couronne ; les totaux du
panel sur le site ne les comptent qu'une fois.

**Bande de sensibilité.** La valeur du sol étant imputée, chaque chiffre publié porte
une bande. Avec un impôt sur le seul sol, multiplier le sol de chaque parcelle
par un même facteur ne change aucun avis d'imposition : la bande du modèle
split-rate (part foncière ±10 points, sol et bâti de chaque parcelle mis à
l'échelle uniformément ; `export_web._tilted_change`, conservée pour les
résolutions split-rate) ne montrerait aucune incertitude. La bande de l'impôt
sur le sol fait varier ce qui en change la répartition : la valeur du bâti
±20 % (`config.BUILDING_COST_BAND`, qui couvre les fourchettes de la recherche
sur les coûts et le ratio habitable ÷ brut). Le coût du bâti entre dans le sol
par le résiduel des parcelles bâties, sommé par IRIS avant le partage en valeur
de site : le total foncier résiduel de chaque IRIS devient L − 0,2 B (ou
L + 0,2 B), borné à [0, L + B], et toutes les parcelles évaluées au résiduel
bougent du même facteur. Seules celles-là bougent, regroupées comme la valeur
de site les regroupe (par IRIS, à défaut la commune entière ; l'un et l'autre
notés dans le fichier annexe des ménages) : les parcelles non bâties,
évaluées sur les ventes de terrains, les parcelles évaluées au coût (hangars,
grandes surfaces) et celles au plancher agricole ne bougent pas
(`export_web._cost_shocked_land` ; revue de code du 12 novembre 2026). Chaque
hypothèse répartit de nouveau le produit de chaque commune et indique la part
foncière qu'elle implique. Le choc porte sur les valeurs du sol exportées,
sans refaire l'étape de valeur de site : les parcelles bornées à la part
foncière bougent avec le total de leur IRIS alors que, recalculées, elles
resteraient à leur borne ; là où l'essentiel d'un IRIS est à la borne basse,
l'hypothèse +20 % peut ramener son sol résiduel à zéro. Deux cas hors des
passages publiés regroupent plus que le modèle : `--land current` (sans
valeur de site, le sol de chaque parcelle est son propre résiduel, et le choc
devrait être parcelle par parcelle) et les rares parcelles au résiduel que
l'étape de valeur de site laisse hors de son regroupement (sans surface ni
coût du bâti). La bande ne
couvre pas le partage du sol entre parcelles d'un même IRIS selon la densité
permise (exposant 0,5), désormais la principale incertitude sur les valeurs
relatives du sol (revue Gemini du 11 novembre 2026 ;
`docs/research/land-only-2026-11/`). La bande est publiée pour les chiffres clés **et** pour
chaque catégorie de bien et chaque quintile de revenu (et, sur les couronnes, les
quintiles classés dans chaque commune), avec les mêmes bornes de quintile que
l'estimation centrale ; le site la trace en moustaches sur ces graphiques. La
variante centrale reproduit exactement les chiffres publiés (testé). Une conclusion
n'est tenue pour robuste que si elle vaut sur toute la bande. La bande laisse la base de la taxe
actuelle inchangée. L'incertitude propre à cette base, le facteur appliqué aux
locaux professionnels (§3.5), déplace les résultats des ménages bien plus que la
bande. Elle est publiée à part, sous forme d'une variante locale présentée à
côté du cas central (§3.7, §6 point 1).

**Groupes de revenu : totaux et ménages, pas médianes par parcelle.** Chaque
quintile de revenu (parcelles classées selon le revenu médian Filosofi de leur
IRIS) porte trois chiffres, tous sur les parcelles résidentielles : le **total du
groupe** (Σ nouvelles cotisations ÷ Σ cotisations actuelles − 1), le **ménage
type** (médiane des variations par parcelle pondérée par le nombre de logements :
un immeuble de 200 logements compte 200 fois) et, pour mémoire, la simple
**médiane par parcelle**. Le site trace le total en barre et le ménage type en
losange. La médiane par parcelle trompe là où les quartiers modestes mêlent
beaucoup de petites maisons et quelques grands immeubles : à Villeurbanne, la
parcelle médiane du quintile le plus pauvre paie +4,6 % alors que le groupe paie
−6,1 % et son ménage type −19,7 % (base centrale), car les grands immeubles, où
vivent la plupart de ses ménages, sont les plus gagnants. Les logements viennent de BD TOPO
(`nombre_de_logements`, réparti entre parcelles au prorata de l'emprise) ; les
parcelles résidentielles sans décompte sont imputées (maison = 1 ; appartements =
surface de plancher brute ÷ 85 m²), soit 5 à 11 % des parcelles résidentielles à
Paris, Lyon et Villeurbanne. Les décomptes restent dans un fichier local joint à
l'export standard (`<commune>.households.csv`, aligné ligne à ligne et contrôlé
sur `new_tax`) ; seuls les totaux par quintile sont publiés. BD TOPO sous-compte
légèrement les logements (Paris ≈ 1,14 M contre ≈ 1,4 M au recensement), ce qui
touche les pondérations, pas les totaux.

**Montants par catégorie en euros : par logement.** Les mêmes décomptes donnent,
pour chaque catégorie résidentielle, la variation en euros du ménage type : la
variation de chaque parcelle divisée par son nombre de logements, médiane
pondérée par les logements (`median_change_eur_per_dwelling`, avec les
`dwellings` de la catégorie). La médiane par parcelle en euros
(`median_change_eur`) compare un immeuble entier à une maison : dans les
fichiers d'octobre 2026, avant la valeur du site, la variation médiane d'un
immeuble lyonnais était de +800 € contre +267 € pour une maison, ce qui se lisait
comme des appartements payant trois fois plus, alors qu'en pourcentage
l'immeuble (+9,6 %) payait deux fois moins que la maison (+20,6 %). Par logement,
l'écart s'inversait : +34 € en immeuble collectif contre +287 € en maison. Depuis
la valeur du site, la parcelle médiane d'un immeuble lyonnais paie −720 € et son
logement type −103 €, une maison +769 € et +800 €. Le site affiche le chiffre par logement ; faute de décompte, il présente
celui d'une catégorie d'immeubles comme « par immeuble ». Le pourcentage du
graphique reste une médiane par parcelle : les deux chiffres peuvent donc
différer de signe, car le grand immeuble pèse davantage dans la médiane par
logement (Roubaix, immeubles collectifs : +7,2 % par parcelle, −5 € par
logement). La règle de diffusion est celle des groupes de revenu : au moins
11 parcelles portant des logements, toutes décomptées, aucune ne réunissant plus
d'un dixième des logements (`MAX_DWELLING_SHARE`). La limite était de la moitié
jusqu'en novembre 2026 : une médiane pondérée par les logements tombe sur tout
immeuble qui en porte 45 %, sauf si les autres sont très déséquilibrés, ce qui
aurait publié la variation de cet immeuble (revue de sécurité du 3 novembre 2026 ;
le changement n'a masqué aucun chiffre publié). Les mêmes décomptes donnent, pour
chaque catégorie d'immeubles, la part des logements qui paient davantage et la
variation du ménage type en % (`share_dwellings_paying_more_pct`,
`household_median_change_pct`), affichées sous le graphique des gagnants et
perdants de la page Résultats, à côté de la part des parcelles. Chaque catégorie
publie aussi sa **variation totale** (`total_change_pct`) : les médianes peuvent
toutes baisser à produit constant quand une minorité paie beaucoup plus
(La Rochelle, maisons : −5,4 % en médiane, +14,7 % au total). Le terrain nu, qui
ne paie rien aujourd'hui et n'a donc pas de %, publie son total en euros
(`total_change_eur`, au millier d'euros). Aucune catégorie ne publie les deux :
la réforme étant à produit constant, les totaux en euros des catégories d'une
commune ont une somme nulle, et un total masqué se déduirait des autres (revue
de sécurité du 4 novembre 2026). Un % seul ne permet aucune soustraction, car
l'impôt actuel d'aucune catégorie n'est publié. Un total n'est pas publié quand une seule parcelle
porte plus d'un dixième de l'impôt de la catégorie, aujourd'hui ou après la
réforme (`MAX_PARCEL_TAX_SHARE`), car il serait alors proche de sa propre
variation. La médiane en % d'une catégorie compte une parcelle qui ne paie rien
aujourd'hui comme une hausse (ou une baisse) sans borne, au lieu de l'écarter :
sinon, le logement social exonéré aujourd'hui, qui passe tout entier de 0 € à un
impôt foncier, sortirait de la médiane de sa propre catégorie. Si la médiane
tombe elle-même sur une telle parcelle (terrain nu, ou partage à égalité), aucun
% n'est publié et la médiane en euros s'affiche.

**Part foncière parisienne et borne de 85 %.** Avec la règle d'origine (linéaire
jusqu'à un plancher de 25 %), un immeuble parisien d'environ 95 ans, entretenu en
continu, tombait à ≈ 575 €/m² face à un prix DVF médian ≈ 10 860 €/m² : 95,5 % des
parcelles bâties étaient à la borne de 0,85 et le chiffre de 84,9 % était fixé par
la borne. La règle du bâti entretenu (§3.1) valorise ces immeubles à un âge
effectif de 30 ans, ce qui ramenait Paris à 83,3 % avec 34,8 % des parcelles
bâties encore à la borne. Avec les deux termes du résiduel en surface habitable et
les coûts recalés et la valorisation du non-résidentiel par type (§3.1, §3.4,
§4), Paris ressort à **75,8 %** avec 5,6 % des parcelles bâties à la borne : sa
part foncière est mesurée, non fixée par la borne. Aucune commune n'a plus de la
moitié de ses parcelles bâties au plafond ; Neuilly-sur-Seine en a le plus
(19,0 %), et le contrôle `land_share_clip` du preflight ne signale aucune
commune. Lyon est à 60,0 %, la couronne parisienne à 63,5 % et la couronne
lyonnaise à 55,2 %. Sur les 188 communes modélisées, 37 dépassent 65 % et 2 sont
sous 40 % (Cahors 36,5 %, Limeil-Brévannes 39,2 %). Chiffres du calcul en valeur
du site de novembre 2026 ; la borne n'encadre plus que le résiduel qui fixe le
total de terrain de chaque IRIS, et la part d'une parcelle peut la dépasser.
Le champ `headline.built_at_cap_pct` enregistre la part des parcelles bâties à
la borne, et le site qualifie la part foncière de « plafonnée » quand elle
atteint 50 %.

*La fourchette de référence 40–65 %.* C'est un repère à l'échelle d'une
métropole (le patrimoine national de l'INSEE place les terrains bâtis à 51 % de
la valeur terrains + logements fin 2023, 44 % pour les seuls ménages), non un test que
chaque commune devrait passer. Les communes limitrophes de Paris (elle-même à
75 %) se situent naturellement entre 65 et 75 %, et le terrain fait 65 à 75 %
de la valeur dans les quartiers de bureaux de premier rang (revue Gemini). La
plupart des 37 communes au-dessus de 65 % sont des communes de petite couronne
limitrophes de Paris (Puteaux 69,5 %, Saint-Cloud 75,3 %, Clichy 73,6 %,
Courbevoie, Nanterre, Montreuil, Pantin…) ; le WARN du registre hors de la
fourchette invite à regarder, il ne signale pas un échec.

*Coût des maisons.* Le coût propre aux maisons déplace les parts foncières dans
le sens attendu : à la hausse autour de Paris, où une maison coûte désormais
moins cher à reconstruire qu'un appartement (Paris 74,0 → 74,2 %, couronne
parisienne 60,6 → 61,7 %, Montreuil 62,5 → 63,7 %), à la baisse autour de Lyon,
où elle coûte plus cher (Lyon 58,6 → 57,8 %, couronne lyonnaise 55,4 → 52,6 %,
Villeurbanne 54,2 → 52,5 %). Plusieurs communes aisées de la petite couronne
passent juste au-dessus de 65 % (Les Lilas, Vanves, Meudon, Puteaux et Malakoff
de moins d'un point ; Sceaux 66,3 %, Marnes-la-Coquette 67,3 %), tandis que
quatre communes des Monts d'Or reviennent dans la bande (Saint-Didier, Saint-Cyr,
Collonges, Saint-Romain) et que Fleurieu-sur-Saône passe de 75,3 à 71,7 %. Il ne
relève qu'en partie les communes basses en lisière de la couronne parisienne (Santeny 33,2 →
36,2 %, Vaujours 34,3 → 35,7 %, Limeil-Brévannes 35,1 → 37,4 %, Villepinte
37,4 → 39,4 %, Périgny 38,2 → 40,3 %) : les maisons n'y font que 18 à 36 % de la
valeur bâtie, dominée par des parcelles industrielles et commerciales valorisées
au coût du logement et au prix des appartements (§6, point 7).

*Nombre de niveaux.* La règle par type (§3.1) laisse Paris (74,2 %) et Lyon
(57,8 %) inchangés et relève les couronnes (couronne parisienne 61,7 → 62,2 %,
couronne lyonnaise 52,6 → 53,0 %), surtout les communes d'entrepôts et de
commerce de la grande périphérie (Santeny 36,2 → 40,4 %, Vaujours 35,7 → 39,0 %,
Villepinte 39,4 → 42,8 %, Tremblay-en-France 44,0 → 47,6 %, Périgny 40,3 →
41,8 %, Limeil-Brévannes 37,4 → 38,0 %). Les communes sous la bande passent de 4
à 2 ; celles au-dessus de 24 à 26 (Clamart et Collonges-au-Mont-d'Or franchissent
65 % de quelques dixièmes). La taxe actuelle étant elle aussi répartie à la
surface plancher, les entrepôts en portent moins, et le montant déplacé augmente
dans les couronnes (couronne parisienne 20,6 → 21,7 % du produit, couronne
lyonnaise 23,9 → 26,4 %). Le gradient de revenu garde son sens (totaux par groupe
à Paris : cinquième le plus modeste −19,8 → −20,0 %, le plus aisé
+16,2 → +16,1 %).

*Bâtiments ruraux.* L'exonération des bâtiments agricoles (§3.5) ne compte que là
où ils sont nombreux. Périgny, la commune des serres, bouge le plus (41,8 →
47,9 %) : près de la moitié de son emprise bâtie était faite de serres et de
bâtiments agricoles. Mandres-les-Roses 60,0 → 62,1 %, Solaize 51,7 → 52,3 %,
Santeny 40,4 → 40,8 % ; toutes les autres communes bougent de moins d'un
demi-point. Les parts foncières de Paris (74,2 %), Lyon (57,8 %), de la couronne
parisienne (62,2 %) et de la couronne lyonnaise (53,0 %) sont inchangées. La part
des parcelles qui paient plus dans la couronne parisienne passe de 67,6 à
67,4 % ; dans la couronne lyonnaise, le montant déplacé passe de 26,4 à 26,6 % du
produit et la part qui paie plus de 60,7 à 60,8 %. Les effectifs hors bande ne
changent pas : 2 communes sous 40 % (Limeil-Brévannes, Vaujours), 26 au-dessus
de 65 %. Quelques parcelles publiques dont les seuls bâtiments étaient ruraux
deviennent non bâties et rejoignent le foncier public exonéré (couronne
parisienne 41 711 → 41 807 parcelles exonérées, couronne lyonnaise 21 515 →
21 585).

*Valorisation du non-résidentiel.* Coûts, durées et planchers par type (§3.1) et
évaluation au CRD des parcelles de type hangar (§3.4) relèvent les parts
foncières partout, surtout dans les communes d'entrepôts :

| Part foncière (terrain ÷ total), % | Avant | Après |
|---|---|---|
| Paris | 74,2 | 75,8 (5,6 % des parcelles bâties à la borne) |
| Lyon | 57,8 | 60,0 |
| Couronne parisienne | 62,2 | 65,3 |
| Couronne lyonnaise | 53,0 | 55,4 |
| Santeny | 40,8 | 52,1 |
| Vaujours | 39,0 | 49,8 |
| Tremblay-en-France | 47,6 | 58,3 |
| Villepinte | 42,8 | 49,5 |
| Périgny | 47,9 | 50,1 |
| Limeil-Brévannes | 38,0 | 41,7 |

Les communes sous 40 % passent de 2 à 1 : Cahors, 41,2 → 38,0 %. La baisse
tient presque entièrement au foncier commercial (197 M€ → 83 M€) : ses zones
commerciales de périphérie prennent désormais le prix local du terrain à bâtir
(médiane 38 €/m², 41 ventes) au lieu d'un résiduel sur le prix des
appartements, et une petite ville au foncier bon marché peut plausiblement se
situer sous la fourchette métropolitaine. Valoriser le foncier commercial au
plein prix du terrain à bâtir plutôt qu'au ratio d'activité ne porte Cahors
qu'à 39,0 %. Celles au-dessus de 65 % passent de 26 à 48, surtout des communes de
petite couronne limitrophes de Paris (voir la fourchette de référence
ci-dessus). Gemini (gemini-4-argon) juge ces niveaux plausibles. Dans la
couronne lyonnaise, la valeur du foncier industriel passe de 8,6 à 3,8 Md€ et
celle des bâtiments industriels de 8,5 à 2,6 Md€. Totaux par catégorie : cotes
industrielles −3,5 → −55 %, commerciales −7 → −17 %, maisons −1 → +6 % ; le
montant déplacé passe de 26,6 à 38,3 % du produit, et la variation totale du
cinquième le plus modeste de −13,5 à −3,7 %. Dans la couronne parisienne, les
cotes industrielles baissent de 31 % ; la catégorie « autre » (parcelles de
garages et de sport) monte de 67 %, mais ne porte que 1,4 % de la taxe actuelle.
Le gradient de revenu parisien bouge peu (totaux par groupe −20,1 … +14,9 % ;
Lyon −18,7 … +13,6 %). Ces chiffres reposaient encore sur la base à la surface
plancher ; la base calée ci-dessous la remplace.

*Base calée.* Caler la taxe actuelle sur la répartition REI de chaque commune
(§3.5) ne change aucune part foncière (Paris 75,8 %, Lyon 60,0 %, couronne
parisienne 65,3 %, couronne lyonnaise 55,4 %) ni aucune nouvelle cotisation :
seul le point de départ bouge. « Avant » est la base à la surface plancher ;
« centrale » applique le facteur 2,5 à l'indicateur professionnel ; « variante
locale » prend la part professionnelle qu'implique la taxe d'habitation de 2017
(§3.5). Les deux colonnes publiées sont celles des fichiers du 31 octobre 2026 ;
« avant » et l'indicateur brut (× 1,0, la variante jusque-là) sont gardés pour
mémoire.

| | Avant (surface plancher) | Centrale (× 2,5) | Variante locale (TH 2017) | Indicateur brut (× 1,0), retiré |
|---|---|---|---|---|
| Paris, totaux par groupe de revenu Q1 … Q5, % | −20,1 −11,2 −4,2 +5,7 +14,9 | −17,4 −8,3 −1,3 +8,9 +18,9 | −6,0 +3,2 +10,6 +21,8 +36,1 | −27,6 −18,8 −12,1 −2,9 +3,9 |
| Lyon | −18,7 −8,5 −0,8 +3,2 +13,6 | −14,0 −3,5 +4,4 +8,5 +18,9 | −3,0 +8,2 +16,3 +20,6 +30,6 | −27,7 −18,2 −10,8 −7,0 +3,5 |
| Couronne parisienne | −9,1 −5,0 −0,6 −2,7 +1,1 | −7,4 −3,0 +2,1 −1,2 +5,5 | +1,8 +4,8 +12,4 +11,9 +22,4 | −21,9 −16,9 −12,1 −12,6 −9,0 |
| Couronne lyonnaise | −3,7 +0,8 +5,0 −1,3 −4,7 | +0,7 +2,6 +11,0 +4,4 0,0 | +0,5 +6,3 +10,3 +4,0 +4,0 | −15,9 −11,4 −7,7 −12,1 −14,2 |
| Montant déplacé, % du produit : Paris / Lyon / couronne parisienne / couronne lyonnaise | 19,2 / 20,4 / 28,1 / 38,3 | 19,6 / 20,9 / 30,4 / 43,0 | 27,8 / 30,0 / 39,7 / 43,0 | 30,2 / 30,9 / 36,7 / 40,7 |
| Part des parcelles qui paient plus, % : même ordre | 50,2 / 70,8 / 68,6 / 69,3 | 52,8 / 74,5 / 70,5 / 70,4 | 67,1 / 78,5 / 74,5 / 67,7 | 42,5 / 51,5 / 56,2 / 58,4 |

Par catégorie, cas central :
- **Couronne lyonnaise.** La part de l'industrie dans la taxe actuelle passe de
  10,0 à 11,9 %, celle du commerce de 15,0 à 16,6 %. Cotisations sous la LVT :
  industrielles −63 %, commerciales −24 %, maisons +13 %.
- **Couronne parisienne.** La part de l'industrie passe de 5,3 à 5,8 %.
  Cotisations : industrielles −36 %, commerciales −15 %, maisons +18 %.

Variante locale, variation médiane par catégorie : Paris maisons +53,8 %,
immeubles collectifs +10,5 %, commerce −34,2 % ; Lyon maisons +39,4 %, immeubles
collectifs +19,4 %, commerce −30,2 % ; couronne parisienne maisons +27,1 %,
commerce −32,1 %, industrie −53,7 % ; couronne lyonnaise maisons +8,7 %, commerce
−24,2 %, industrie −65,8 % (cas central : maisons de Paris +29,6 %, de Lyon
+20,6 %). L'indicateur brut retiré donnait le signe inverse aux entreprises : dans
la couronne lyonnaise, commerce +47 %, industrie −42 %, maisons −6 % ; dans la
couronne parisienne, commerce +77 %, industrie +1 %, maisons +1 %.

*Sur le site.* Chaque fichier de commune et de territoire porte
`baseline_sensitivity`, avec une branche centrale (× 2,5) et une variante
(`low_source` : `th2017`, ou `mixed` pour la couronne lyonnaise, où
Sathonay-Camp garde l'indicateur brut) : montant déplacé, part des parcelles qui paient plus, variation médiane
résidentielle, catégories et totaux par groupe de revenu (les territoires
classent aussi les groupes au sein de chaque commune). La page de résultats
présente les deux côte à côte dans le tableau « Incertitude sur la taxe actuelle
des locaux professionnels », après le tableau de sensibilité à la part foncière.
Les cotisations LVT sont identiques dans les deux colonnes ; seule la taxe
actuelle diffère.

**La part professionnelle est l'incertitude porteuse.** La variante locale
déplace les résultats des ménages d'environ 10 points, dans le sens inverse de
l'indicateur brut retiré. Dans les fichiers du 31 octobre 2026 : premier
quintile parisien −17,4 % en central contre −6,0 %, lyonnais −14,0 % contre
−3,0 %, couronne parisienne −7,4 % contre +1,8 % ; la couronne lyonnaise bougeait
à peine (+0,7 % contre +0,5 %). Depuis la valeur du site : Paris −21,4 % contre
−10,6 %, Lyon −16,6 % contre −5,8 %, couronne parisienne −12,6 % contre −2,3 %,
couronne lyonnaise −8,9 % contre −8,6 % (classement dans chaque commune pour les
couronnes). Dans les deux
colonnes publiées, le gradient de Paris et de Lyon est progressif : le quintile
le plus aisé paie le plus. Dans la variante locale, tous les groupes de revenu de
Paris et de Lyon sauf le plus modeste paient plus, et les locaux professionnels
nettement moins. Le facteur 2,5 reste le cas central, car il est calé à
l'échelle nationale ; la variante locale est calée commune par commune, mais sur
des données de 2017 et un indicateur lu à ± 5 points (§6, point 1).

*Valeur du site et classement des maisons (novembre 2026).* Tous les chiffres
ci-dessus précèdent ces deux changements : la catégorie des maisons comptait
alors de grands bâtiments à un logement ou sans logement enregistré, et le
terrain bâti suivait la surface de plancher (§3.1, §3.4). Dans les fichiers
publiés depuis (cas central ; variation médiane par catégorie, totaux par groupe
de revenu, classement dans chaque commune pour les couronnes) :

| | Part déplacée, % du produit | Maisons | 2–4 | 5+ | Commerce | Totaux Q1 / Q5 |
|---|---|---|---|---|---|---|
| Grenoble | 35,7 | +48,6 | +12,2 | −30,8 | +6,9 | −46,6 / −4,1 |
| Annemasse | 25,0 | +97,3 | +22,8 | −21,1 | +8,1 | −12,3 / −4,0 |
| Villeurbanne | 23,5 | +54,7 | +24,8 | −16,8 | +45,9 | −6,1 / +3,5 |
| Roubaix | 29,1 | −15,5 | −14,7 | −27,2 | −16,0 | −26,9 / +43,9 |
| Cahors | 23,0 | +2,6 | −6,8 | −21,7 | −11,9 | — / — |
| Montreuil | 26,0 | +45,5 | +25,5 | −13,4 | +20,4 | −18,8 / +17,9 |
| Figeac | 26,2 | −0,3 | −11,1 | −30,9 | −11,4 | — / — |
| Sète | 26,0 | +30,8 | +1,2 | −28,0 | +29,0 | −16,5 / +11,1 |
| La Rochelle | 31,9 | −5,4 | −14,7 | −30,5 | −6,8 | −19,9 / +0,4 |
| Paris | 19,9 | +118,3 | +36,5 | −10,0 | +58,0 | −21,4 / +10,6 |
| Lyon | 22,4 | +69,2 | +23,2 | −8,0 | +5,0 | −16,6 / +15,4 |
| Paris extra-muros (petite couronne) | 27,3 | +31,0 | +13,5 | −21,9 | +20,2 | −12,6 / +6,8 |
| Lyon extra-muros (Métropole hors Lyon) | 31,1 | +32,3 | +2,6 | −24,9 | −27,9 | −8,9 / +6,6 |

- **Robuste sur tout le panel :** le cinquième le plus modeste paie moins dans
  chaque territoire découpé par revenu et s'en sort mieux que le plus aisé ; les
  grands immeubles paient moins partout ; l'industrie paie beaucoup moins.
- **Plus vrai partout :** le total du cinquième le plus aisé baisse à Grenoble
  (−4,1 %) et à Annemasse (−4,0 %). Maisons et petits immeubles paient plus là
  où ils côtoient des bâtiments plus denses (maisons parisiennes +118 %), et
  moins là où le bâti est homogène (Roubaix, Figeac, La Rochelle).
- **La part de l'impôt qui change de payeur** double environ (Paris 9,8 →
  19,9 %, Lyon 10,5 → 22,4 %).

*Le seul sol, à l'usage permis (passage du 11 novembre 2026).* Les chiffres
ci-dessus valent pour le split-rate 4:1 et pour un sol évalué à la densité
propre de la parcelle quand elle dépassait celle de sa zone. En n'imposant que
le sol, chaque parcelle à la densité de sa zone (§3.4, §3.6), sur les données
publiées depuis (mêmes colonnes) :

| | Transfert, % du produit | Maisons | 2–4 | 5+ | Commerces | Totaux Q1 / Q5 |
|---|---|---|---|---|---|---|
| Grenoble | 43,3 | +57,1 | +15,4 | −35,8 | +14,5 | −53,4 / −9,0 |
| Annemasse | 33,4 | +120,8 | +21,9 | −29,6 | +21,0 | −13,3 / −8,0 |
| Villeurbanne | 31,7 | +68,0 | +31,9 | −24,2 | +61,5 | +3,4 / −2,2 |
| Roubaix | 39,8 | −24,4 | −29,8 | −43,0 | −21,5 | −33,8 / +47,2 |
| Cahors | 36,6 | +14,2 | −10,7 | −35,0 | −34,2 | — / — |
| Montreuil | 33,2 | +51,5 | +23,8 | −30,6 | +34,5 | −9,5 / +12,6 |
| Figeac | 36,8 | −0,1 | −24,8 | −52,8 | −28,2 | — / — |
| Sète | 32,7 | +43,4 | +4,1 | −35,5 | +37,7 | −19,3 / +8,6 |
| La Rochelle | 37,6 | −4,8 | −18,8 | −39,1 | −4,5 | −11,9 / −3,5 |
| Paris | 23,0 | +118,8 | +36,6 | −14,2 | +68,2 | −24,9 / +7,0 |
| Lyon | 27,7 | +78,3 | +24,9 | −14,7 | +13,3 | −15,7 / +11,0 |
| Paris extra-muros (petite couronne) | 34,9 | +41,3 | +14,0 | −34,6 | +29,5 | −6,8 / +3,1 |
| Lyon extra-muros (Métropole hors Lyon) | 39,6 | +36,2 | −1,0 | −40,1 | −29,8 | −4,7 / +0,7 |

- **Plus progressif presque partout :** le cinquième le plus modeste de Paris
  −22,3 → −24,9 % par rapport au passage 4:1 sur les mêmes données, Lyon
  −12,5 → −15,7 %, Grenoble −45,2 → −53,4 % ; les grands immeubles paient
  moins partout, plus nettement qu'avant.
- **La seule exception, Villeurbanne :** le total du cinquième le plus modeste
  augmente de 3,4 % (bande de +2,0 à +4,4 %) quand celui du plus aisé baisse de
  2,2 %, porté par les maisons et petits immeubles (maisons +135 % au total) ;
  son ménage type paie tout de même 21 % de moins, la plupart vivant en grand
  immeuble. Les plus modestes paient donc moins, et s'en sortent mieux que les
  plus aisés, dans 10 des 11 territoires découpés par revenu.
- **La part de l'impôt qui change de payeur** augmente encore, de 23 % (Paris)
  à 43 % (Grenoble).

**Constat de politique publique.** Dans le couloir chimique et industriel
lyonnais, la LVT déplace l'impôt de l'industrie vers les ménages dans le cas
central (cotisations industrielles de Saint-Fons −60 %, de Marcy-l'Étoile
−90 %).

*Outillage : un choix de conception.* La réforme modélisée ne taxe que le sol,
donc ni le bâti ni l'outillage industriel fixe (ce paragraphe date du modèle
split-rate, qui taxait le bâti mais pas l'outillage). Le
responsable du projet a tranché en ce sens, conformément à la théorie de la taxe
foncière sur le sol, qui évite de pénaliser l'investissement productif. Aucun
changement de code n'est nécessaire : les valeurs de l'art. 1499 incluent
l'outillage fixe, mais la valeur bâtie du modèle pour une parcelle industrielle
ne compte déjà que le hangar. Pour montrer le faible poids de ce choix, une
estimation de premier ordre (`docs/research/plant_effect.py`) ajoute à la base
bâtie le coût réévalué de l'outillage (base industrielle ÷ 0,03, brut ou × 0,5
pour la dépréciation, moins la valeur bâtie du modèle) et résout de nouveau le
4:1 commune par commune (le modèle d'alors ; avec l'impôt sur le seul sol,
l'outillage n'a plus aucun effet) :

| Cotisations industrielles vs aujourd'hui | Hangar seul (publié) | Avec outillage, déprécié | Avec outillage, brut |
|---|---|---|---|
| Couronne lyonnaise | −63 % | −62 % | −60 % |
| Couronne parisienne | −36 % | −36 % | −33 % |
| Marcy-l'Étoile | −90 % | −84 % | −76 % |
| Saint-Fons | −60 % | −59 % | −52 % |

Taxer l'outillage ne déplacerait les cotisations industrielles que de 1 à
3 points à l'échelle de chaque couronne, davantage dans une commune industrielle
isolée (Saint-Fons 8, Tremblay-en-France 12, Marcy-l'Étoile 14 au coût brut). La baisse
industrielle tient avant tout au déplacement vers le sol : un foncier
industriel bon marché face à une base actuelle chargée en capital.

**Règle de diffusion.** Seuls des agrégats sont publiés, jamais une parcelle.
Un groupe publié de moins de 11 parcelles (`export_web.MIN_GROUP_PARCELS`) est
fusionné avec un voisin : une tranche de part du bâti avec la tranche
adjacente la plus petite, une catégorie de bien avec « Autres ». Un simple
masquage ne suffirait pas, puisque le total de la commune moins les autres
groupes le reconstituerait. Un groupe resté trop petit (quintile de revenu,
« Autres », très petite commune) garde son effectif mais aucune de ses valeurs ; un quintile où un seul immeuble porte plus
d'un dixième des logements, ou qui compte moins de 11 parcelles portant des
logements, ne publie pas ses chiffres par ménage. Les valeurs en
euros des tranches sont arrondies au millier. `assert_aggregate_only` vérifie
ces règles à l'export et sur chaque fichier publié (test CI).

## 4. Paramètres et hypothèses clés

- **Coût de construction €/m²** (`construction_cost_eur_m2`) : coût de
  remplacement clé en main d'un bâtiment moderne équivalent, € 2025, par m² de
  vraie surface brute extérieure, bâtiment seul (hors foncier, hors VRD),
  honoraires d'architectes et d'ingénieurs et TVA à 20 % inclus, marge de
  promoteur exclue. Paris, la petite couronne et les territoires lyonnais sont
  calés sur le coût « bâtiment » des logements sociaux neufs du « Bilan des
  logements aidés » DHUP/SISAL 2021–22, indexé en 2025 par l'indice BT01 de
  l'INSEE (`docs/research/construction-costs-2025.md`) : **Paris 2650**
  (fourchette plausible 2350–3100), **petite couronne 2400** (Montreuil et tout le
  92/93/94 ; 2150–2700), **Lyon et Villeurbanne 2000** (1750–2300), **couronne
  métropolitaine 1850** (1600–2100). Les autres communes du panel gardent leurs
  valeurs pilotes sur le gradient de l'enquête EPTB du SDES : Grenoble/Annemasse
  1900, Sète/La Rochelle 1850, Roubaix 1750, Cahors 1650, Figeac 1600. (Anciennes
  valeurs pilotes : Paris 2300, petite couronne 2150, Lyon et les deux
  territoires lyonnais 1950.)
- **Coût des maisons €/m²** (`house_cost_eur_m2`) : coût appliqué aux parcelles
  dont le `type_local` dominant est une maison, sur la même base que ci-dessus.
  Le coût communal étant calé sur le logement social collectif, les maisons de
  Paris, de la petite couronne et des territoires lyonnais sont valorisées sur
  l'enquête du SDES sur les maisons individuelles neuves (EPTB 2024, € par m² de
  surface de plancher : Île-de-France 1 863, Rhône 2 127), indexée en 2025 (BT01
  ×1,014), avec travaux de finition ×1,06, honoraires, assurances et études ×1,05
  (×1,03 dans la couronne lyonnaise), prime de parcelle contrainte (Paris ×1,20,
  petite couronne et Lyon ×1,10, couronne lyonnaise ×1,05), ÷ 0,90 habitable ÷
  SDP, puis × 0,82 vers la vraie surface brute
  (`docs/research/house-costs-2025.md`) : **Paris 2300**, **petite couronne
  2100** (Montreuil et tout le 92/93/94), **Lyon et Villeurbanne 2400**,
  **couronne métropolitaine 2250**, soit par m² habitable 2800, 2550, 2950 et
  2750 (fourchettes plausibles 2300–3400, 2100–3050, 2500–3450, 2400–3250). Les
  maisons coûtent moins cher que les appartements autour de Paris mais plus cher
  autour de Lyon, à rebours du gradient du logement collectif : l'échantillon
  francilien de l'EPTB est surtout fait de maisons sur catalogue des départements
  de grande couronne, alors que les maisons neuves du Rhône sont probablement plus
  sur mesure (non vérifié). Les chiffres lyonnais appellent donc plus de
  prudence ; une variante prudente pour la couronne lyonnaise serait d'environ
  2080. Les autres communes du panel gardent un coût unique (`house_cost_eur_m2`
  = None), leurs valeurs pilotes reposant déjà sur le gradient EPTB. Le
  déclencheur q du bâti entretenu garde le coût communal (§3.1).
- **Ratios de surface** (par `type_local` ; les autres types prennent le ratio
  des appartements) : `net_to_gross` = habitable ÷ surface plancher du modèle,
  mesuré : appartements 0,64 (0,59–0,68), maisons 0,61 (0,58–0,66)
  (`docs/research/net-to-gross-measurement.md`) ; `cost_net_to_gross` =
  habitable ÷ vraie surface brute sous-jacente aux coûts : appartements 0,71,
  maisons 0,82 (§3.1).
- **Dépréciation** : linéaire sur `dep_years` = 80 ans, plancher `dep_floor` = 0,25,
  appliquée à l'âge effectif ; plafond bâti entretenu 30 ans
  (`dep_maintained_age_cap`), rampe q ∈ [1,2 ; 2,5] (`dep_q_ramp`). Ce sont des
  choix raisonnés éclairés par la littérature (§3.1), non des paramètres estimés.
- **Types de bâtiments non résidentiels** (`config.BUILDING_TYPES`, §3.1) :
  ratio au coût communal, durée et plancher par type : hangar 0,25, atelier
  0,354 et grande surface 0,467 (40 ans, 15 %) ; bureaux 0,825 (60 ans, 20 %) ;
  hangar agricole 0,073 (30 ans, 10 %) ; serre 0,081 (25 ans, 10 %) ; salle de
  sport 1,033 et annexe 0,227 (50 ans, 20 %). Types professionnels hors TVA,
  annexes TTC. Ratios à ±25 % ; durées et planchers sont des choix raisonnés.
- **Ratio du foncier d'activité** (`activity_land_ratio`, §3.4) : foncier
  professionnel des parcelles au CRD en part du €/m² local des terrains à
  bâtir : 0,45 par défaut et autour de Paris, 0,35 pour Lyon, Villeurbanne et
  la couronne lyonnaise (DVF ouvert, n ≈ 20 à 80). **Facteur de cour**
  (`DRC_CURTILAGE_FACTOR`) : 3 × la surface plancher hors zone urbaine.
- **Bornes de part foncière** : [0,15 ; 0,85] — contrainte de conception, pas une
  mesure. Là où la plupart des parcelles atteignaient la borne haute (Paris, Lyon),
  les causes identifiées étaient la surdépréciation du bâti ancien entretenu et
  l'application de prix DVF par m² habitable à la surface plancher BD TOPO, plus
  grande, non un foncier réellement supérieur à 85 %. Les deux étant corrigées,
  aucune commune n'a plus de la moitié de ses parcelles bâties à l'une ou l'autre
  borne (§3.7).
- **Valeur du site** (`config.SITE_VALUE`, §3.4) :
  - élasticité à la densité 0,5 (coefficients allemands de conversion,
    0,45–0,54) ;
  - densité de référence au 75ᵉ centile du coefficient d'occupation réalisé du
    libellé de zone (au moins 20 parcelles, sinon type de zone, sinon commune) ;
  - parcelle plafonnée au 99ᵉ centile de la commune ;
  - terrain en surplus au-delà de 2 × la parcelle médiane de la zone compté
    à 0,25, sur toute parcelle bâtie d'une zone d'habitat individuel (référence
    inférieure à 1), quoi qu'il y soit construit (jusqu'au 11 novembre 2026 :
    sous la référence seulement) ;
  - en zones A et N, une cour de 3 × la surface de plancher.

  Chaque valeur est un jugement éclairé par les sources du §3.4 ; aucune n'est
  estimée sur des ventes françaises de biens bâtis.
- **Assiette** : le seul sol (`split_rate_ratio = None`), depuis le 11 novembre
  2026 ; un split-rate 4:1 (terrain:bâti) auparavant. Un choix du responsable du
  projet, conforme à la théorie de l'impôt foncier.
- **Bande sur le coût du bâti** : ±20 % (`BUILDING_COST_BAND`), la sensibilité de
  l'impôt sur le sol ; voir la bande de sensibilité au §3.7.
- **€/m² agricole** (SAFER, par département, agricole / naturel) : défaut
  0,64 / 0,49 ; Lot 0,45 / 0,35 ; Seine-St-Denis 1,00 / 0,60 ; Nord 0,85 / 0,50 ;
  Rhône 0,70 / 0,50 ; Haute-Savoie 0,75 / 0,55 ; Isère 0,60 / 0,45 ; Paris,
  Hauts-de-Seine, Val-de-Marne 1,00 / 0,60 (ancrage francilien ; sans effet
  matériel).
- **Repli terrain à bâtir EPTB** : 99 €/m² (national).
- **Décote AU** (`au_strict_factor`) : 0,55. **Shrinkage hédonique** k = 8.
- **Base de la taxe actuelle** (`config.BASELINE_MODEL`, §3.5) : REI 2025,
  taux de TFPB 2020 (Métropole de Lyon : taux 2014 du Rhône, 11,03 %) ;
  indicateur professionnel 0,5 × base brute de CFE (art. 1388 CGI) × **2,5**
  (central) ; variante = la part locale qu'implique la taxe d'habitation de 2017
  (`alt_source`, indicateur brut × 1,0 en repli), calculée à chaque passage et
  publiée à côté du cas central ; pondérations au m² plafonnées à 5 × le
  logement ; parts industrielle + professionnelle plafonnées à 75 %.
- **Logement social** (`social_housing.py`, §3.5) : imposition 2025, RPLS au
  1er janvier 2025, fichier des personnes morales 2025 ; exonéré 15 ans, ou 25
  avec une convention datée du 1er juillet 2004 au 31 décembre 2026 (dès 2005
  pour un départ en 2005–06 ; sans convention, à partir de 2007) ; facteur QPV
  0,7 ; transfert quand la convention précède de plus de 2 ans l'entrée dans le
  patrimoine ; code groupe à la majorité des lignes ; rattachement à 30 m d'une
  parcelle sociale, sinon 15 m ; résidences à 2 m, un bailleur chacune ;
  habitable ÷ brut 0,72 ; catégorie Logement social dès la moitié de la surface
  de logement ; publiée avec au moins 3 bailleurs et aucun au-delà de 85 % de
  l'impôt de la catégorie. Les durées et le taux QPV sont la loi ; le reste
  relève du jugement, vérifié sur Montreuil et Villeurbanne
  (`docs/research/hlm-2026-11/`).
- **Impôt sur le non-bâti remplacé** (§3.5) : lignes REI 2025 `B11`, `B13`,
  `B31`, `B33` et bases et produits de TAFNB ; réparti selon la surface sur les
  parcelles non bâties comprises dans la réforme et sur le terrain libre des
  maisons au-delà de 500 m² (cinq ares, BOFiP), un seul poids au m². La méthode
  de la part suit la loi ; le seuil des jardins est une pratique
  administrative et le poids égal un jugement.
- **Élasticité des loyers aux prix** (`REVALUATION["rent_price_elasticity"]`,
  §3.6) : 0,8, d'après la baisse du rendement brut avec le prix entre communes
  françaises (Chapelle et Eyméoud 2022). 1 traiterait une valeur locative
  comme une valeur vénale (l'hypothèse de l'IPP au sein d'une commune) ; une
  valeur plus faible aplatit la première étape. Un choix raisonné, sur la
  seule mesure française trouvée.
- **Strates REI** neutralisées : Commune + intercommunalité (configurable). Le
  contrôle `rei_layers` du preflight indique, par commune, les strates FB
  existantes et la part laissée de côté : dans le 92/93/94 il n'y a pas de strate
  GFP (ni les EPT ni la MGP ne lèvent de FB) ; dans la Métropole de Lyon une
  strate *Syndicat* est significative dans 45 communes (5 à 23 % du produit FB).
  Les taux syndicaux portent sur la même base VLC : les exclure réduit les montants
  en euros mais pas les variations en %.

## 5. Validation

- **Neutralité budgétaire** — exacte par construction ; vérifiée à l'euro sur
  chaque exécution réelle (Cahors 22 690 869 € ; Montreuil 101 780 897 €).
- **Part foncière descendante** — terrain total ÷ valeur immobilière bâtie totale
  doit avoisiner le patrimoine national de l'INSEE (44–51 % de terrain fin 2023). Cahors
  atteignait ~53 % après la correction d'année de construction par DPE (contre
  85 % dégénéré auparavant — voir §6) et se situe à 38,0 % avec la valorisation
  du non-résidentiel par type. La fourchette 40–65 % est un repère
  métropolitain, non un test par commune (§3.7).
- **Cohérence de signe** — le foncier agricole/naturel, hors de la réforme, ne
  porte rien du prélèvement (il en portait 1,1 % à Cahors avant son exclusion) ; le foncier constructible sous-utilisé paie
  *davantage* (l'incitation LVT) ; le gradient de revenu de Montreuil est
  progressif (totaux de groupe, base centrale : quintile le plus pauvre
  −18,8 %, le plus aisé +17,9 %).
- **Répartition de la taxe actuelle** — la reconstitution industrielle (WC75 ÷
  taux 2020), appliquée à toutes les communes de France, donne 5,7 % de la base
  TFPB, exactement le chiffre de la Cour des comptes ; la ligne industrielle de
  la CFE concorde commune par commune dans un rapport de 0,6 à 1,13 (§3.5).
- **Tests** — `test_units.py` (tests unitaires hors-ligne de la logique pure) et
  `test_synthetic.py` (bout-en-bout via le vrai solveur).

## 6. Limites (registre consolidé)

Classées par impact sur les résultats publiés (catégorie/quintile).

1. **Base de la taxe actuelle : le facteur des locaux professionnels (porteur
   pour tout chiffre distributif).**
   - **Le facteur professionnel.** Les parts industrielle et professionnelle de
     la taxe actuelle de chaque commune viennent de son REI (§3.5). La part
     industrielle est quasi exacte. La part professionnelle est un indicateur
     CFE multiplié par un facteur national unique, 2,5, car l'indicateur brut ne
     capte qu'environ 40 % de la base professionnelle nationale (8,6 % contre
     22 % pour la Cour des comptes). La variante publiée est locale : la part
     des entreprises qu'implique la taxe d'habitation de 2017 (§3.5). Elle
     dépasse le cas central dans les villes, et les ménages y paient donc plus :
     le premier quintile parisien passe de −21,4 à −10,6 %, le lyonnais de −16,6
     à −5,8 %, et les cotisations commerciales de Paris de +58,0 % à +7,2 %
     (variation médiane ; §3.7). Les nouvelles cotisations sont identiques dans
     les deux cas ; seul le point de départ bouge. Le sous-comptage n'est pas
     uniforme : il est plus fort là où beaucoup de locaux sont vacants ou
     occupés par des organismes publics et des associations, comme à Paris. Le site présente les deux côte à côte
     sur chaque page de résultats (tableau « Incertitude sur la taxe actuelle
     des locaux professionnels ») ; **les présenter aussi côte à côte dans
     toute publication.** Les valeurs professionnelles par commune (Fichiers
     fonciers) sont la vraie solution.
     **Contrôle indépendant (31 octobre 2026).** La taxe d'habitation de 2017
     donne une seconde estimation, locale : la part des logements dans la base de
     TFPB vaut environ 0,5 × la valeur locative brute de TH ÷ la base de TFPB
     (REI 2017, `J11` et `E11`). À l'échelle nationale, elle donne 32,7 % pour les
     locaux professionnels et l'industrie, contre environ 32,4 % d'après la Cour
     des comptes. Localement, elle situe cette part bien au-dessus du proxy brut
     dans toutes les villes modélisées, et au-dessus du cas à 2,5 sauf à Figeac :
     Lyon ≈ 39 % (base 2025) contre 12,5 % (brut) et 28,8 % (central), Paris
     ≈ 39 % contre 11,3 % et 26,3 %. À lire à ± 5 points par commune (vacance,
     dépendances, logements sociaux exonérés ; données 2017). Le proxy brut, cas
     où les logements de Lyon et de Paris paient moins, paraît donc invraisemblable
     en ville ; le cas central sous-estime peut-être le report sur les logements.
     Depuis le 31 octobre 2026, la colonne du proxy brut est remplacée par cette
     variante locale (§3.5, §3.7 ; `docs/research/tfpb-baseline-calibration.md`
     §9.5).
   - **Au sein de chaque groupe**, la taxe actuelle reste répartie à la surface
     plancher, qui ignore la catégorie cadastrale et les coefficients de
     pondération de surface : lire la **variation**, pas le montant de départ,
     et ne jamais publier de montants par parcelle. L'usage BD TOPO décide du
     groupe ; un commerce non enregistré en usage secondaire est imposé comme
     du logement.
   - **L'outillage est hors champ par choix, ce n'est pas une limite.** La
     réforme modélisée taxe le sol et le bâti, pas l'outillage industriel fixe
     (décision du responsable du projet, conforme à la théorie de la taxe
     foncière sur le sol ; §3.7). Les valeurs de l'art. 1499 incluent
     l'outillage et la valeur bâtie du modèle ne compte que le hangar : le
     modèle suit donc ce choix. Taxer l'outillage ne déplacerait les
     cotisations industrielles que de 1 à 3 points (couronne lyonnaise −63 % →
     −62 % déprécié ou −60 % brut ; jusqu'à 14 points dans une commune
     industrielle isolée) : la baisse
     vient avant tout du foncier industriel bon marché.
2. **Terrain bâti : une valeur du site invérifiable directement, sur un total
   résiduel.**
   - **Pas de vérification directe.** La valeur du site (§3.4) ne peut pas être
     vérifiée sur les ventes de biens bâtis ; les seules preuves directes sont
     les rares ventes de terrains à bâtir nus et les ventes de biens destinés à
     la démolition, difficiles à repérer dans les données ouvertes.
   - **Paramètres de substitution.** La densité permise est approchée par la
     densité réalisée au 75ᵉ centile de la zone, faute de règles du PLU
     (hauteurs, reculs, protections patrimoniales) lisibles par machine à
     l'échelle nationale. La racine carrée de la densité et les règles du
     surplus et de la cour sont empruntées, non estimées.
   - **Surface linéaire ailleurs.** Hors ces deux règles, le terrain est
     linéaire en surface : une grande parcelle en zone dense est évaluée comme
     un terrain à bâtir même là où sa forme ou son accès ne le permettraient
     pas. Le dixième des maisons de Villeurbanne aux plus grandes parcelles paie
     environ cinq fois l'impôt actuel (+394 %).
   - **Report de paiement.** Beaucoup de ces propriétaires auraient besoin d'un
     report de paiement, que prévoit la réforme du projet
     (`/exonerations-protections`).
   - **Ce qui dépend de ces choix.** Les résultats par catégorie pour les
     maisons et les petits immeubles bougent le plus. Les totaux par cinquième
     de revenu bougent peu : les totaux de terrain par IRIS sont conservés,
     mais ces totaux restent ceux du résiduel.
   - **Amplification du résiduel.** Les erreurs sur le bâti sont amplifiées
     dans le résiduel là où le bâti pèse lourd. C'est atténué par le bornage
     [0,15 ; 0,85], qui s'applique quand le total de l'IRIS est formé, et par
     l'agrégation. C'est rendu visible par la bande sur le coût du bâti
     (`headline_sensitivity`).
   - **Foncier non bâti.** Le foncier non bâti **n'utilise pas** le résiduel :
     le message clé (le sous-utilisé paie plus) est indépendant de la qualité
     des données bâti.
3. **Année de construction.** Issue du DPE (logements *résidentiels*
   diagnostiqués → biais de sélection) ; le repli médian communal s'applique au
   logement non diagnostiqué. Les bâtiments non résidentiels sans année BD TOPO
   sont pris à mi-vie, hypothèse neutre et non mesure (le jeu DPE tertiaire n'a
   pas été examiné). Tranche→année par
   point médian (atténué pour l'ancien d'avant 1948, qui touche le plancher de
   dépréciation). Nette amélioration sur la base dégénérée antérieure, mais
   généralisation à documenter.
4. **Coûts de construction et base de surface.** Les coûts de Paris, de la petite
   couronne et des territoires lyonnais sont calés, avec des fourchettes
   plausibles publiées (§4) ; le logement social est un indicateur du parc privé
   et sous-estimera le bâti de prestige ou protégé. Les maisons y ont leur propre
   coût fondé sur l'EPTB, dont l'étape la moins sourcée est la majoration de
   finition (chaque ±4 points la déplace de ±4 %) et dont le niveau lyonnais
   repose sur un échantillon probablement plus sur mesure que le parc. La principale incertitude
   restante est `cost_net_to_gross` (habitable ÷ vraie surface brute), le maillon
   le moins sourcé : ±0,05 déplace la valeur bâti d'environ ±7 %, qui se reporte
   sur le résiduel foncier. Le `net_to_gross` mesuré ne fixe que les niveaux en
   euros. Les autres communes du panel gardent des coûts pilotes non calés. Les
   coûts du non-résidentiel sont des ratios au coût du logement tirés d'un seul
   guide commercial (point 7). Les
   erreurs de nombre de niveaux BD TOPO sont la principale source de dispersion de
   la surface à la parcelle ; quand le nombre manque, il est imputé selon le type
   de bâtiment (§3.1), un choix raisonné testé sur six communes, et la hauteur de
   3,5 m par niveau des bâtiments commerciaux élevés n'a pas de source primaire.
5. **Bornage de part foncière** : quand la plupart des parcelles bâties sont à une
   borne, la part foncière est une hypothèse, pas un résultat, et la variation du
   bâti entre parcelles disparaît. Avant la règle du bâti entretenu, c'était le cas
   de Paris (95,5 % à la borne), de Lyon et de 53 autres communes. Aucune commune
   n'a désormais plus de la moitié de ses parcelles bâties à une borne ;
   Neuilly-sur-Seine en a le plus au plafond (25,3 %), Paris 5,6 % (§3.7). Le
   contrôle `land_share_clip` du preflight le signale. Le plafond d'âge effectif (30 ans) et
   la rampe (q 1,2–2,5) sont des choix raisonnés ; publier une sensibilité sur ces
   paramètres reste à faire (THEORY.md).
   Publier la distribution non bornée à côté (la part avant bornage est conservée
   dans la colonne `land_share_raw`). Précédence quand plancher agricole et
   bornage se contredisent : le plancher (une observation de marché) l'emporte ;
   ces parcelles sont flaggées `built_floored_ag` et leur part terrain peut
   légitimement dépasser les bornes.
6. **Nuance de zonage** : tout AU est traité constructible avec une décote
   forfaitaire ; les `AU fermées` mériteraient une décote plus forte et les
   pastilles `Nh/Ah` sont sous-évaluées.
7. **Valorisation du non-résidentiel.** Les niveaux sont imputés selon le type
   (§3.1), les bâtiments agricoles exonérés au titre de l'art. 1382 6° du CGI
   sont exclus (§3.5), chaque type de bâtiment a son coût, sa durée et son
   plancher (§3.1), et les parcelles de type hangar sont évaluées au coût de
   remplacement déprécié (§3.4). Restent :
   - **Les coûts** reposent sur un seul guide commercial ramené à notre niveau
     de logement, aucun document primaire (Moniteur, Untec, Chambre
     d'agriculture) n'ayant été accessible : ±25 %. Durées et planchers sont des
     choix raisonnés.
   - **Les bureaux** prennent toujours la surface de prix résidentielle et les
     ratios de surface des appartements, à leur propre coût. Une surface de prix
     DVF des locaux professionnels (par tranche de taille, écrêtée) est la
     meilleure cible ; les locaux professionnels (révision 2017) nécessitent une
     strate dédiée.
   - **Parcelles mixtes.** Le plus grand bâtiment de la parcelle décide de la
     méthode : une parcelle dominée par un hangar est évaluée entièrement au
     coût (y compris une maison qui s'y trouverait), une parcelle dominée par du
     logement ou des bureaux entièrement au résiduel (un hangar s'y trouvant
     gardant son propre coût).
   - **Le ratio du foncier d'activité** (0,45 / 0,35) repose sur n ≈ 20 à 80
     ventes par an et par territoire, classées par l'occupation du sol actuelle
     (MOS) ou les périmètres de zones d'activités, non par le zonage. C'est un a
     priori, pas une mesure. Le terrain d'un CRD à son usage dominant est un
     plancher pour une LVT, qui vise l'usage autorisé ; les deux coïncident dans
     les zones d'activités.
   - **Les cours** hors zone urbaine (3 × la surface plancher) sont un choix
     raisonné.
8. **Revenus (Filosofi)** : millésime 2021 ; l'INSEE a publié en mai 2026 un
   millésime « Filosofi 2 » 2023 avec indicateurs IRIS (rupture méthodologique) —
   2021 est conservé en attendant évaluation. Communes ≥ 5 000 habitants
   uniquement, certains IRIS sous secret statistique. Les quintiles exigent en
   outre ≥ 10 IRIS aux revenus distincts, deux par quintile
   (`export_web.MIN_IRIS_INCOMES`) : en dessous, un « quintile » n'est qu'un
   quartier, si bien que Cahors (9) et Figeac (4) ne publient pas de
   décomposition par revenu, et que les communes membres d'un territoire sous ce
   seuil sortent des quintiles intra-communaux.
9. **Couverture** : DVF exclut l'Alsace-Moselle et Mayotte. Paris et Lyon sont
   modélisées comme communes entières à partir de leurs arrondissements (§3.7) ;
   Marseille pourrait l'être de la même façon.
10. **Le foncier non bâti en zone U est évalué comme terrain à bâtir.** Les
    espaces publics ouverts classés urbains (PLU de Paris *UV* : parcs,
    cimetières, terrains de sport ; PLU-H de Lyon *USP* : services publics) et le
    foncier vacant en *zone d'activités* (*UEi*) reçoivent le €/m² résidentiel des
    terrains à bâtir (les hangars bâtis y prennent le ratio du foncier
    d'activité, §3.4). `audit_land.py <commune>` chiffre, par libellé de zone, la
    part de l'impôt qu'il porte.
11. **Les exonérations ne sont que partiellement modélisées.** Le foncier public
    manifestement exonéré est repéré (§3.5), mais prudemment : les locaux publics en
    copropriété ou sous bail, les lieux de culte détenus par des associations, les
    écoles et hôpitaux privés non lucratifs, l'Assemblée et le Sénat (formes
    juridiques atypiques), les exonérations partielles hors territoire et les
    bâtiments publics sans local enregistré restent imposables. Les bâtiments
    agricoles (art. 1382 6° CGI) sont repérés par l'usage BD TOPO et le zonage
    PLU, non par leur usage réel : un hangar agricole non renseigné en zone urbaine
    reste imposé, et des dépendances de parcs en zone N sont exonérées (§3.5). Les
    exonérations et l'abattement QPV du logement social sont modélisés depuis
    novembre 2026 (§3.5 et point 14) ; les autres exonérations temporaires
    (deux ans du neuf privé, délibérations locales) ne le sont pas.
12. **Mutations DVF multi-locaux.** Les locaux annexes (Dépendance) et les
    lignes hors commune gardent leur valeur dans le prix de la mutation mais
    sont exclus de la somme des surfaces, surestimant le €/m² là où les annexes
    sont fréquentes (maisons rurales) — un biais haussier spatialement structuré
    que l'écrêtage par centiles ne corrige pas (voir la docstring de
    `ingest.fetch_dvf`).
13. **Cache des données brutes optionnel.** `run_commune --cache-dir` (ou
    `LVTFR_CACHE_DIR`) met en cache les téléchargements bruts par empreinte
    d'URL, ce qui rend les lots reprenables ; sans lui, chaque exécution
    re-télécharge depuis des endpoints vivants qui bougent parfois
    (l'avertissement de config.py). Il n'y a pas encore de manifeste (source,
    URL, date, empreinte) : les exécutions sont reproductibles comme commandes,
    pas comme données.
14. **Le logement social est modélisé par appariement spatial, non à partir
    des fichiers fiscaux.** Le RPLS n'a ni parcelle ni bailleur : les logements
    sont placés par point d'adresse, et les logements d'une résidence partagent
    un même facteur d'exonération, juste au total mais flou entre les parcelles
    d'une résidence. La règle repose sur des indicateurs : la date de convention
    tient lieu de date de décision de financement (15 ou 25 ans) et indique si
    une acquisition est un transfert entre bailleurs ; le RPLS renseigne l'année
    de première location de façon inégale. Non observables : la majoration
    environnementale de 5 ans (art. 1384 A I bis), les déclarations tardives
    (art. 1406), les suppressions locales (art. 1384 C III), et la signature par
    chaque bailleur de la convention QPV (supposée partout ; les variables REI
    `G211`/`G213` permettraient de la calibrer). Le RPLS exclut les
    logements-foyers et résidences sociales : leurs parcelles comptent comme
    sociales quand un bailleur social les détient, au plein taux actuel. Les
    parcelles mixtes (VEFA en copropriété) reçoivent une part sociale tirée de la
    surface habitable du RPLS rapportée à la surface BD TOPO. Quand cette part
    est inférieure à la moitié, la parcelle reste résidentielle et toute sa
    variation compte dans les chiffres par ménage, part du bailleur comprise
    (la fin de son exonération apparaît comme une hausse pour les ménages de
    l'immeuble). Ces parcelles portent 8 à 14 % de l'impôt résidentiel actuel à
    Montreuil, Annemasse et Villeurbanne ; n'attribuer aux ménages que la part
    privée déplacerait le total d'un cinquième de revenu de 0,2 à 1,4 point, le
    plus souvent à la baisse, et le total de la catégorie des immeubles de moins
    d'un point. Non corrigé : il faudrait la part du bailleur dans l'impôt de
    chaque parcelle parmi les sorties du calcul. MAJIC a environ un
    an de retard sur le neuf : quelques logements récents tombent sur des
    parcelles sans droit d'un bailleur social. Du fait des dégrèvements d'État
    remboursés aux bailleurs après les rôles (art. 1391 E et C, environ 4 à 5 %
    de la TFPB des HLM), l'état initial fondé sur le REI surestime un peu ce que
    paient les bailleurs. Les enregistrements d'exonération des Fichiers fonciers
    remplaceraient tout cela (§7).

15. **L'impôt sur le non-bâti remplacé est un total communal réparti selon la
    surface.** Son partage entre parcelles n'est pas une donnée ouverte (tarifs
    cadastraux de 1961) : la variation en % du terrain nu est une moyenne
    communale. Trois écarts connus. Les groupes cadastraux ne sont pas les zones
    du PLU : un champ classé en zone U paie l'impôt foncier dans le modèle alors
    que sa TFPNB agricole n'est pas dans le montant remplacé, et un terrain
    d'agrément en zone N est dans le cas inverse. Les carrières et les emprises
    ferroviaires paient aussi cet impôt et ne reçoivent ici aucune part. Enfin,
    beaucoup de parcelles non bâties en ville sont des délaissés, des voies
    privées ou des cours qui ne paient peut-être rien aujourd'hui : répartir
    selon la surface sur toutes sous-estime ce que paient les vrais terrains à
    bâtir et surestime leur hausse ; le rôle compte bien moins d'articles
    imposés que le modèle n'a de parcelles non bâties (La Rochelle : 820
    articles pour tout le non-bâti, 3 822 parcelles de ce type). La règle des
    cinq ares pour les jardins est une pratique administrative appliquée au cas
    par cas, non une mesure. Le revenu cadastral par parcelle des Fichiers
    fonciers remplacerait tout cela (§7).

16. **L'étape de la révision est mesurée par rapport à une estimation
    d'aujourd'hui.** L'impôt actuel est réparti selon la surface (§3.5) : la
    première étape de la décomposition (§3.6) est donc le passage de la
    surface à la valeur, non l'effet exact de la révision des valeurs de 1970,
    dont nous ne voyons pas les coefficients de catégorie et de situation. La
    valeur au m² est le prix hédonique du logement à l'emplacement de la
    parcelle : elle ne voit ni la qualité propre d'un logement, ni sa taille,
    ni son étage, que verraient les catégories et coefficients de
    localisation de la révision. Une parcelle en copropriété compte pour une. Les valeurs locatives par
    local des Fichiers fonciers donneraient le vrai point de départ (§7).

## 7. L'argument d'accès aux Fichiers fonciers

Chaque compromis lié aux données ouvertes correspond à un champ précis des
Fichiers fonciers (CEREMA/DGFiP) qui le résoudrait : le proxy de VLC (surface
plancher calée sur les parts REI par groupe, avec un facteur professionnel
national) → la VLC réelle par parcelle ; les surfaces bâti estimées → les surfaces déclarées
par local ; l'année de construction inférée par DPE → l'année exacte ;
l'appariement spatial bâtiment↔parcelle → les liens MAJIC natifs ; l'absence de
typologie de propriétaires / vacance / exonérations → ces champs directement. Le
pilote va jusqu'ici sur données ouvertes ; l'*acte d'engagement* transforme chaque
ligne en donnée administrative exacte, à coût marginal nul pour la structure
partenaire. **La démonstration est l'argument d'accès.** Un dossier de demande
prêt à compléter, avec le tableau limitation→champ, figure dans
`docs/access/fichiers-fonciers-dossier.md` ; les étapes restantes (choix de la
structure éligible porteuse, signature) reviennent au porteur du projet.

## 8. Reproductibilité

```
pip install pandas numpy geopandas matplotlib seaborn
cd lvtshift-fr
python test_synthetic.py                 # bout-en-bout hors-ligne
python run_commune.py <commune>          # exécution réelle ; CSV + graphiques
```

Communes : `villeurbanne`, `roubaix`, `cahors`, `figeac`, `montreuil`,
`grenoble`, `annemasse`, `sete`, `larochelle`, `paris`, `lyon` (et chaque commune
des couronnes, par clé ASCII, p. ex. `boulogne-billancourt`). Options :
`--layers` (strates REI), `--baseline floor` (taxe actuelle à la seule surface
plancher, sensibilité d'avant le calage), `--no-dpe` (année BD TOPO seule, pour la comparaison de
dépréciation), `--no-report` (CSV seul), `--cache-dir` (réutilise les
téléchargements ; reprise possible). Territoires :

```
python run_territory.py lyon-extra-muros --workers 4   # lot reprenable
python export_web.py lyon-extra-muros                  # JSON agrégé
python audit_land.py paris                             # audit du foncier non bâti
```
 Sous
Windows, exporter `PYTHONUTF8=1`. Les sorties sont écrites dans
`output/<commune>.csv` et `output/reports/<commune>/*.png` (toutes deux
gitignorées).
