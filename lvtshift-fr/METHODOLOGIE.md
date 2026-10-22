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
vers une LVT à taux différenciés (split-rate), sur **données ouvertes
uniquement**. La France n'évalue pas séparément terrain et bâti : la valeur du
terrain par parcelle est donc **imputée**, avec des marges d'erreur explicites.
Les résultats sont reportés par **catégorie de bien** et **quintile de revenu**,
jamais comme des montants individuels.

Sur le plan technique, il s'agit d'un fork de l'outil américain LVTShift : le code
FR de `lvtshift-fr/` fabrique les colonnes d'entrée attendues par LVTShift à
partir des données ouvertes françaises, puis appelle son solveur
(`model_split_rate_tax`) et son export (`save_standard_export`) **sans les
modifier**. Les améliorations amont profitent ainsi automatiquement à la version
française.

## 2. Sources de données

| Donnée | Source | Accès | Millésime | Rôle |
|---|---|---|---|---|
| Parcelles | Cadastre Etalab | GeoJSON par commune | dernier | géométrie, surface officielle (`contenance`) |
| Transactions | DVF géolocalisé (Etalab) | CSV par commune | 5 ans glissants | valeur de marché hédonique ; comparables terrains à bâtir |
| Bâtiments | BD TOPO V3 (IGN) | WFS `BDTOPO_V3:batiment`, emprise communale | courant | emprise, niveaux, hauteur, logements, usage, flag d'appariement FF |
| Année de construction | DPE logements existants (ADEME) | API data-fair par `code_insee_ban` | depuis 07/2021 | dépréciation (tranche → année) |
| Zonage | GPU `zone_urba` (IGN) | WFS, emprise communale | PLU/PLUi courant | constructibilité (U/AU vs A/N) des parcelles non bâties ; critère A/N des bâtiments agricoles exonérés (§3.5) |
| Prix agricoles | SAFER « Le prix des terres » | barème départemental (config) | 2024 | €/m² du foncier non constructible |
| Repli terrain à bâtir | EPTB (SDES) | valeur nationale (config) | 2023 | €/m² constructible quand les comparables locaux manquent |
| Cible fiscale | REI foncier bâti, via OFGL | API Opendatasoft par `idcom` | dernier | cible exacte de neutralité (`MONTANT RÉEL`) |
| Géométrie IRIS | Contours IRIS (IGN) | WFS `STATISTICALUNITS.IRIS:contours_iris` | courant | rattachement parcelle → IRIS pour le revenu |
| Revenus | Filosofi (INSEE) | CSV zip (`DISP_MED21`) | 2021 | analyse distributive (quintiles) |
| Foncier public exonéré | DGFiP « Fichiers des locaux et des parcelles des personnes morales » | zips annuels via le catalogue data.economie.gouv.fr | situation 2025 | repérer le foncier public manifestement exonéré de TFPB (§3.5) |

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
La surface plancher répartit aussi la TFPB actuelle (§3.5) : la correction abaisse
la valeur bâtie du non-résidentiel et retire aux entrepôts une partie de la taxe
d'aujourd'hui. Sources : `docs/research/nonres-valuation-2025.md` §1 et
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
la mutation, le €/m² écrêté aux 1er/99e centiles.

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
| **Bâtie** | `marché − bâti` (résiduel), plancher à la valeur agricole €/m², part foncière bornée à [0,15 ; 0,85] (chaque écrêtement flaggé dans `lv_flag`) |
| **Bâtie, plus grand bâtiment de type hangar** (CRD) | €/m² terrain à bâtir × `activity_land_ratio` (types professionnels) ou × 1 (salles de sport, annexes) × surface, plancher à la valeur agricole €/m² ; hors zone urbaine, seule une cour de 3 × la surface plancher prend ce prix. Valeur de marché = terrain + bâti déprécié ; ni prix résidentiel ni bornage (`lv_flag` `built_drc`) |
| **Constructible vacante** (zone U/AUc) | €/m² terrain à bâtir DVF × surface (médiane cellule si ≥ 8 ventes, sinon médiane communale, sinon repli national EPTB) |
| **Constructible différée** (AU/AUs) | idem × `au_strict_factor` (urbanisation différée) |
| **Agricole / naturelle** (zone A/N) | €/m² départemental SAFER × surface |

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

**3.5 Taxe actuelle (base de départ)** — le produit TFPB exact (REI), réparti
(`estimate.current_tax`) sur les **parcelles bâties uniquement** au prorata d'un
proxy de VLC = surface plancher. La TFPB est un impôt sur le bâti ; les parcelles
non bâties portent **0 €** (elles relèvent de la TFPNB, hors périmètre). **Aucun
calage sur la valeur de marché** (la VLC 1970 est régressive vs marché ; un calage
dégraderait la fidélité à la base actuelle) ; une variante pondérée par catégorie
n'existe qu'en sensibilité étiquetée.

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

**3.6 Solveur split-rate** — le `model_split_rate_tax` amont trouve les taux
fonciers/bâti neutres en recettes au ratio configuré (4:1 par défaut). L'export
est écrit par `save_standard_export` ; les graphiques en euros par `charts_fr`
(surcouche de localisation monétaire du rapport amont).

**3.7 Paris, Lyon et leurs couronnes** — Paris (75056) et Lyon (69123) lèvent la
TFPB en tant que commune unique, mais cadastre, DVF, DPE et IRIS sont publiés par
arrondissement (75101–75120, 69381–69389). La configuration porte les deux :
`insee_code` est le code fiscal sur lequel le REI est indexé, `sub_codes` les
codes de données. Chaque collecteur parcourt les codes de données (les requêtes
spatiales se font une emprise d'arrondissement à la fois, de sorte qu'un bâtiment
en limite n'est attribué qu'aux parcelles qu'il recouvre), les tables sont
empilées en une seule commune et **un** split-rate neutre en recettes est résolu
pour la ville — comme l'impôt réel, à taux unique. Les DPE rattachés au code de la
ville sont également récupérés.

Les **territoires extra-muros** — *Paris extra-muros* (les 122 communes des 92/93/94)
et *Lyon extra-muros* (les 57 autres communes de la Métropole de Lyon ; liste figée
dans `territories.py`) — ne sont **pas** un impôt métropolitain. Chaque commune
membre est résolue sur son propre produit REI et reste à recettes constantes
(`run_territory.py`, un processus par commune) ; `export_web.build_territory_payload`
agrège ensuite les résultats par parcelle. La bande de sensibilité ±10 pt est
recalculée commune par commune (chacune inclinée autour de sa propre part
foncière) avant agrégation ; les quintiles de revenu sont classés sur toute la
couronne. Une commune en échec figure dans le champ `coverage`, jamais imputée.
Montreuil et Villeurbanne apparaissent seules et dans leur couronne ; les totaux du
panel sur le site ne les comptent qu'une fois.

**Bande de sensibilité.** La valeur du sol étant imputée, chaque chiffre publié porte
une bande de ±10 pt de part foncière : la part foncière agrégée est abaissée puis
relevée de 10 points (valeurs terrain et bâti de chaque parcelle mises à l'échelle
uniformément, base totale et produit constants) et le solveur amont est relancé
(`export_web._tilted_change`). La bande est publiée pour les chiffres clés **et** pour
chaque catégorie de bien et chaque quintile de revenu (et, sur les couronnes, les
quintiles classés dans chaque commune), avec les mêmes bornes de quintile que
l'estimation centrale ; le site la trace en moustaches sur ces graphiques. La
variante centrale reproduit exactement les chiffres publiés (testé). Une conclusion
n'est tenue pour robuste que si elle vaut sur toute la bande ; à Paris, le gradient
par quintile bouge à peine (parcelle résidentielle médiane : premier quintile
−19,3 à −21,5 %, dernier +11,6 à +11,9 %).

**Groupes de revenu : totaux et ménages, pas médianes par parcelle.** Chaque
quintile de revenu (parcelles classées selon le revenu médian Filosofi de leur
IRIS) porte trois chiffres, tous sur les parcelles résidentielles : le **total du
groupe** (Σ nouvelles cotisations ÷ Σ cotisations actuelles − 1), le **ménage
type** (médiane des variations par parcelle pondérée par le nombre de logements :
un immeuble de 200 logements compte 200 fois) et, pour mémoire, la simple
**médiane par parcelle**. Le site trace le total en barre et le ménage type en
losange. La médiane par parcelle trompe là où les quartiers modestes mêlent
beaucoup de petites maisons et quelques grands immeubles : à Villeurbanne, la
parcelle médiane du quintile le plus pauvre paie +4,8 % alors que le groupe paie
−8,1 % et son ménage type −10,1 %, car les grands immeubles, où vivent la plupart
de ses ménages, sont les plus gagnants. Les logements viennent de BD TOPO
(`nombre_de_logements`, réparti entre parcelles au prorata de l'emprise) ; les
parcelles résidentielles sans décompte sont imputées (maison = 1 ; appartements =
surface de plancher brute ÷ 85 m²), soit 5 à 11 % des parcelles résidentielles à
Paris, Lyon et Villeurbanne. Les décomptes restent dans un fichier local joint à
l'export standard (`<commune>.households.csv`, aligné ligne à ligne et contrôlé
sur `new_tax`) ; seuls les totaux par quintile sont publiés. BD TOPO sous-compte
légèrement les logements (Paris ≈ 1,14 M contre ≈ 1,4 M au recensement), ce qui
touche les pondérations, pas les totaux.

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
(25,3 %), et le contrôle `land_share_clip` du preflight ne signale aucune
commune. Lyon est à 60,0 %, la couronne parisienne à 65,3 % et la couronne
lyonnaise à 55,4 %. Sur les 188 communes modélisées, 48 dépassent 65 % et 1 est
sous 40 % (Cahors 38,6 %).
Le champ `headline.built_at_cap_pct` enregistre la part des parcelles bâties à
la borne, et le site qualifie la part foncière de « plafonnée » quand elle
atteint 50 %.

*La fourchette de référence 40–65 %.* C'est un repère à l'échelle d'une
métropole (les comptes de patrimoine de l'INSEE placent le terrain à environ 45
à 50 % de la valeur de l'immobilier bâti au niveau national), non un test que
chaque commune devrait passer. Les communes limitrophes de Paris (elle-même à
76 %) se situent naturellement entre 65 et 75 %, et le terrain fait 65 à 75 %
de la valeur dans les quartiers de bureaux de premier rang (revue Gemini). La
plupart des 48 communes au-dessus de 65 % sont des communes de petite couronne
limitrophes de Paris (Puteaux 71,0 %, Saint-Cloud 76,8 %, Clichy 74,8 %,
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

Les communes sous 40 % passent de 2 à 1 (Cahors, 41,2 → 38,6 %, cause non
encore examinée) ; celles au-dessus de 65 % de 26 à 48, surtout des communes de
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
Lyon −18,7 … +13,6 %). **La baisse industrielle, et les gains plus faibles des
ménages autour de Lyon, sont exagérés par la base de la taxe actuelle** (§6,
point 1) : elle répartit toujours le produit TFPB à la surface plancher, sans
pondération par catégorie, ce qui surestime ce que paient aujourd'hui entrepôts
et usines. Ces chiffres distributifs ne devraient pas être publiés tant que la
base ne porte pas de pondérations par catégorie, prochaine étape proposée.

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
- **Ratio split-rate** : 4:1 (terrain:bâti), scénario de référence.
- **€/m² agricole** (SAFER, par département, agricole / naturel) : défaut
  0,64 / 0,49 ; Lot 0,45 / 0,35 ; Seine-St-Denis 1,00 / 0,60 ; Nord 0,85 / 0,50 ;
  Rhône 0,70 / 0,50 ; Haute-Savoie 0,75 / 0,55 ; Isère 0,60 / 0,45 ; Paris,
  Hauts-de-Seine, Val-de-Marne 1,00 / 0,60 (ancrage francilien ; sans effet
  matériel).
- **Repli terrain à bâtir EPTB** : 99 €/m² (national).
- **Décote AU** (`au_strict_factor`) : 0,55. **Shrinkage hédonique** k = 8.
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
  doit avoisiner les comptes de patrimoine INSEE (~45–50 % de terrain). Cahors
  atteignait ~53 % après la correction d'année de construction par DPE (contre
  85 % dégénéré auparavant — voir §6) et se situe à 38,6 % avec la valorisation
  du non-résidentiel par type. La fourchette 40–65 % est un repère
  métropolitain, non un test par commune (§3.7).
- **Cohérence de signe** — le foncier agricole/naturel porte une part négligeable
  du prélèvement (Cahors 0,3 %) ; le foncier constructible sous-utilisé paie
  *davantage* (l'incitation LVT) ; le gradient de revenu de Montreuil est
  progressif (totaux de groupe : quintile le plus pauvre −15,4 %, le plus aisé
  +13,6 %).
- **Tests** — `test_units.py` (tests unitaires hors-ligne de la logique pure) et
  `test_synthetic.py` (bout-en-bout via le vrai solveur).

## 6. Limites (registre consolidé)

Classées par impact sur les résultats publiés (catégorie/quintile).

1. **Taxe actuelle (maillon porteur ; bloque la publication des résultats du
   non-résidentiel).** Le proxy de VLC est la seule surface plancher ; il ignore
   la catégorie cadastrale et les coefficients de pondération de surface. Il
   déforme la répartition de la taxe *actuelle* entre bâtis : lire la
   **variation**, pas le montant de départ. Le non-résidentiel étant désormais
   évalué à son propre coût et à son propre prix du terrain, bien plus bas
   (§3.1, §3.4), l'erreur ne se compense plus : répartir le produit à la surface
   plancher sans pondération par catégorie **surestime ce que paient
   aujourd'hui entrepôts et usines**. Les valeurs locatives industrielles
   (méthode comptable, art. 1499 CGI) ont été divisées par deux en 2021, et les
   tarifs RVLLP de 2017 pour les entrepôts et les grandes surfaces sont bas au
   m². La baisse industrielle (couronne lyonnaise −55 %, couronne parisienne
   −31 %) et les gains plus faibles des ménages autour de Lyon sont donc
   exagérés. La recommandation, que partage la revue Gemini, est de ne pas
   publier les chiffres distributifs de cette étape tant que la base ne porte
   pas de pondérations par catégorie (prochaine étape proposée ; produits REI
   de la DGFiP par catégorie s'ils existent). Seule la VLC réelle par parcelle
   (Fichiers fonciers) le résoudrait entièrement.
2. **Amplification du résiduel.** Terrain bâti = marché − bâti : les erreurs sur
   le bâti sont amplifiées dans le résiduel terrain là où le bâti pèse lourd.
   Atténué par le bornage [0,15 ; 0,85], l'agrégation et la bande de sensibilité.
   Le foncier non bâti **n'utilise pas** le résiduel : le message clé (le
   sous-utilisé paie plus) est indépendant de la qualité des données bâti.
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
8. **Revenus (Filosofi)** : 2021 (dernier millésime), communes ≥ 5 000 habitants
   uniquement, certains IRIS sous secret statistique.
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
    exonérations temporaires (logement social neuf, art. 1384 A CGI ; abattement QPV) ne sont
    pas identifiables en données ouvertes : l'état initial surestime encore la
    cotisation actuelle des HLM exonérés et la sous-estime ailleurs (sensible en
    Seine-Saint-Denis).

## 7. L'argument d'accès aux Fichiers fonciers

Chaque compromis lié aux données ouvertes correspond à un champ précis des
Fichiers fonciers (CEREMA/DGFiP) qui le résoudrait : le proxy de VLC par surface
→ la VLC réelle par parcelle ; les surfaces bâti estimées → les surfaces déclarées
par local ; l'année de construction inférée par DPE → l'année exacte ;
l'appariement spatial bâtiment↔parcelle → les liens MAJIC natifs ; l'absence de
typologie de propriétaires / vacance / exonérations → ces champs directement. Le
pilote va jusqu'ici sur données ouvertes ; l'*acte d'engagement* transforme chaque
ligne en donnée administrative exacte, à coût marginal nul pour la structure
partenaire. **La démonstration est l'argument d'accès.**

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
`--layers` (strates REI), `--no-dpe` (année BD TOPO seule, pour la comparaison de
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
