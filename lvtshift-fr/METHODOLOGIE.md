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
| Zonage | GPU `zone_urba` (IGN) | WFS, emprise communale | PLU/PLUi courant | constructibilité (U/AU vs A/N) des parcelles non bâties |
| Prix agricoles | SAFER « Le prix des terres » | barème départemental (config) | édition 2025 (marché 2024) | €/m² du foncier non constructible |
| Repli terrain à bâtir | EPTB (SDES) | valeur nationale (config) | 2023 | €/m² constructible quand les comparables locaux manquent |
| Cible fiscale | REI foncier bâti, via OFGL | API Opendatasoft par `idcom` | dernier | cible exacte de neutralité (`MONTANT RÉEL`) |
| Géométrie IRIS | Contours IRIS (IGN) | WFS `STATISTICALUNITS.IRIS:contours_iris` | courant | rattachement parcelle → IRIS pour le revenu |
| Revenus | Filosofi (INSEE) | CSV zip (`DISP_MED21`) | 2021 (voir §6.8) | analyse distributive (quintiles) |

Toutes sous Licence Ouverte / Etalab. Les URL exactes sont dans
`config.DATA_SOURCES`.

## 3. Chaîne de traitement et formules

Tout le calcul métrique se fait en RGF93 / Lambert-93 (EPSG:2154). `cell` = un
carreau de 400 m (effet fixe spatial transparent pour l'hédonique, et non une
géographie administrative).

**3.1 Valeur du bâti (improvement)** — coût de remplacement déprécié, agrégé à la
parcelle (`estimate.improvement_value`) :

```
surface_plancher = emprise_m2 × niveaux       (niveaux imputés par hauteur/3 si absent)
âge              = année_référence − année_construction
dépréciation     = borne(1 − (1 − dep_floor) × âge / dep_years,  min = dep_floor)
valeur_bâti      = surface_plancher × coût_construction_€m2 × dépréciation
```

`année_construction` provient du DPE (§3.2) ; `coût_construction_€m2`,
`dep_years`, `dep_floor` sont en config par commune (§4). Les bâtiments sont
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
ne dégénère jamais en « inconnu ».

**3.3 Valeur de marché** — une hédonique log-linéaire volontairement simple sur
DVF (`estimate.fit_hedonic` / `market_value`) : médiane cellule×type du log €/m²,
rétrécie (shrinkage) vers la médiane communale par type (pseudo-effectif k = 8),
× surface plancher de la parcelle. DVF est nettoyé aux mutations `Vente`, agrégé à
la mutation, le €/m² écrêté aux 1er/99e centiles. Les cinq années poolées entrent
en prix **nominaux** — le crochet `fit_hedonic(deflator=…)` existe mais aucun
indice Notaires-INSEE n'est encore branché (voir §6, point 10).

**3.4 Valeur du terrain — classer puis valoriser**
(`estimate.land_value_residual` → `_land_value_classified`). Les parcelles non
bâties sont classées par le zonage GPU ; chaque classe est valorisée sur le bon
référentiel :

| Parcelle | Valeur du terrain |
|---|---|
| **Bâtie** | `marché − bâti` (résiduel), plancher à la valeur agricole €/m², part foncière bornée à [0,15 ; 0,85] (chaque écrêtement flaggé dans `lv_flag`) |
| **Constructible vacante** (zone U/AUc) | €/m² terrain à bâtir DVF × surface (médiane cellule si ≥ 8 ventes, sinon médiane communale, sinon repli national EPTB) |
| **Constructible différée** (AU/AUs) | idem × `au_strict_factor` (urbanisation différée) |
| **Agricole / naturelle** (zone A/N) | €/m² départemental SAFER × surface |

Seules les lignes DVF codées *terrains à bâtir* sont utilisées pour les prix du
constructible — le brut `valeur_fonciere/surface_terrain` est contaminé pour les
autres natures de culture car les mutations regroupent bâti et plusieurs
parcelles.

**3.5 Taxe actuelle (base de départ)** — le produit TFPB exact (REI), réparti
(`estimate.current_tax`) sur les **parcelles bâties uniquement** au prorata d'un
proxy de VLC = surface plancher. La TFPB est un impôt sur le bâti ; les parcelles
non bâties portent **0 €** (elles relèvent de la TFPNB, hors périmètre). **Aucun
calage sur la valeur de marché** (la VLC 1970 est régressive vs marché ; un calage
dégraderait la fidélité à la base actuelle) ; une variante pondérée par catégorie
n'existe qu'en sensibilité étiquetée.

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

**La part foncière de 84,9 % à Paris est fixée par la borne, pas mesurée.** 95,5 %
des parcelles bâties parisiennes (Lyon : 59,8 %) sont à la borne haute de 0,85, car
la règle de dépréciation ramène un immeuble d'environ 95 ans, entretenu en continu,
à son plancher de 25 % (≈ 575 €/m² face à un prix DVF médian ≈ 10 860 €/m²) : la
part agrégée non bornée est de 92,9 %. Valoriser le bâti entretenu comme s'il
avait ~30 ans (âge effectif, cf. littérature) donne 82–85 % (coût de reconstruction
2 760–2 300 €/m²) ; sans aucune décote, 63–79 % (borne basse). Le niveau est donc
plausible ; c'est l'uniformité du partage entre parcelles qui est un artefact. Le
champ `headline.built_at_cap_pct` enregistre la part des parcelles bâties à la
borne, et le site qualifie la part foncière de « plafonnée » quand elle atteint 50 %.

## 4. Paramètres et hypothèses clés

- **Coût de construction €/m²** (clé en main, hors foncier ; gradient régional
  pilote, à caler sur FFB/indice BT01) : Paris 2300, petite couronne 2150
  (Montreuil et tout le 92/93/94), Lyon, Villeurbanne et la couronne
  métropolitaine 1950, Grenoble/Annemasse 1900, Roubaix 1750, Cahors 1650,
  Figeac 1600.
- **Dépréciation** : linéaire sur `dep_years` = 80 ans, plancher `dep_floor` = 0,25.
- **Bornes de part foncière** : [0,15 ; 0,85] — contrainte de conception, pas une
  mesure. Là où la plupart des parcelles atteignent la borne haute (Paris, Lyon), la
  cause identifiée est la surdépréciation du bâti ancien entretenu, non un foncier
  réellement supérieur à 85 % (§3.7).
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
  atteint ~53 % après la correction d'année de construction par DPE (contre 85 %
  dégénéré auparavant — voir §6).
- **Cohérence de signe** — le foncier agricole/naturel porte une part négligeable
  du prélèvement (Cahors 0,3 %) ; le foncier constructible sous-utilisé paie
  *davantage* (l'incitation LVT) ; le gradient de revenu de Montreuil est
  progressif (quintiles les plus pauvres −10 %, plus aisés +9/+12 %).
- **Tests** — `test_units.py` (tests unitaires hors-ligne de la logique pure) et
  `test_synthetic.py` (bout-en-bout via le vrai solveur).

## 6. Limites (registre consolidé)

Classées par impact sur les résultats publiés (catégorie/quintile).

1. **Taxe actuelle (maillon porteur).** Le proxy de VLC est la seule surface
   plancher ; il ignore la catégorie cadastrale et les coefficients de
   pondération de surface. Il déforme la répartition de la taxe *actuelle* entre
   bâtis : lire la **variation**, pas le montant de départ. Résolu uniquement par
   la VLC réelle par parcelle (Fichiers fonciers).
2. **Amplification du résiduel.** Terrain bâti = marché − bâti : les erreurs sur
   le bâti sont amplifiées dans le résiduel terrain là où le bâti pèse lourd.
   Atténué par le bornage [0,15 ; 0,85] et l'agrégation, et rendu visible par la
   bande de sensibilité part-terrain ±10 pts publiée avec les chiffres clés de
   chaque commune (`headline_sensitivity`, recalculée à recettes constantes à
   chaque extrémité). Le foncier non bâti
   **n'utilise pas** le résiduel : le message clé (le sous-utilisé paie plus) est
   indépendant de la qualité des données bâti.
3. **Année de construction.** Issue du DPE (logements *résidentiels*
   diagnostiqués → biais de sélection) ; le repli médian communal applique une
   médiane résidentielle au non-résidentiel / non diagnostiqué. Tranche→année par
   point médian (atténué pour l'ancien d'avant 1948, qui touche le plancher de
   dépréciation). Nette amélioration sur la base dégénérée antérieure, mais
   généralisation à documenter.
4. **Coûts de construction** : gradient régional pilote grossier ; un écart de
   ±15 % se propage linéairement dans la valeur bâti (donc terrain).
5. **Bornage de part foncière** : quand la plupart des parcelles bâties sont à une
   borne, la part foncière est une hypothèse, pas un résultat (Paris 95,5 % à la
   borne de 0,85, Lyon 59,8 %), et la variation du bâti entre parcelles disparaît. À
   Paris, la cause est le plancher de dépréciation qui ramène le bâti ancien
   entretenu à 25 % (§3.7). Le contrôle `land_share_clip` du preflight le signale ;
   publier la distribution non bornée à côté (la part avant bornage est conservée
   dans la colonne `land_share_raw`). Précédence quand plancher agricole et
   bornage se contredisent : le plancher (une observation de marché) l'emporte ;
   ces parcelles sont flaggées `built_floored_ag` et leur part terrain peut
   légitimement dépasser les bornes.
6. **Nuance de zonage** : tout AU est traité constructible avec une décote
   forfaitaire ; les `AU fermées` mériteraient une décote plus forte et les
   pastilles `Nh/Ah` sont sous-évaluées.
7. **Valeur de marché du non-résidentiel** : emprunte la surface €/m²
   résidentielle ; les locaux professionnels (révision 2017) nécessitent une
   strate dédiée.
8. **Revenus (Filosofi)** : millésime 2021 ; l'INSEE a publié en mai 2026 un
   millésime « Filosofi 2 » 2023 avec indicateurs IRIS (rupture méthodologique) —
   2021 est conservé en attendant évaluation. Communes ≥ 5 000 habitants
   uniquement, certains IRIS sous secret statistique. Les quintiles exigent en
   outre ≥ 5 IRIS aux revenus distincts : une commune à un ou deux IRIS
   (p. ex. Figeac, pourtant ≥ 5 000 hab.) perd silencieusement ses graphiques de
   revenu (l'amont saute le graphique quand les quantiles dégénèrent).
9. **Couverture** : DVF exclut l'Alsace-Moselle et Mayotte. Paris et Lyon sont
   modélisées comme communes entières à partir de leurs arrondissements (§3.7) ;
   Marseille pourrait l'être de la même façon.
10. **Le foncier non bâti en zone U est évalué comme terrain à bâtir.** Les
    espaces publics ouverts classés urbains (PLU de Paris *UV* : parcs,
    cimetières, terrains de sport ; PLU-H de Lyon *USP* : services publics) et le
    foncier vacant en *zone d'activités* (*UEi*) reçoivent le €/m² résidentiel des
    terrains à bâtir. `audit_land.py <commune>` chiffre, par libellé de zone, la
    part de l'impôt qu'il porte.
11. **Pool de prix nominaux (2021–2025).** Les ventes DVF entrent dans
    l'hédonique et dans la base de prix terrain-à-bâtir en prix nominaux ;
    l'indice Notaires-INSEE a bougé de ~+7–8 % (2021), ~+5–6 % (2022), ~−2 %
    (2023), ~−1 % (2024) — un balancement de ~8–10 points dans la fenêtre, donc
    les cellules dont les ventes se concentrent tôt ont des niveaux de prix
    systématiquement différents de celles qui vendent tard (erreur spatialement
    structurée, signalée par la revue fondatrice du projet). Le crochet
    `deflator` de `fit_hedonic` attend l'indice cité.
12. **Discordance de concept de surface (brut vs habitable).** `surface_plancher`
    = emprise × niveaux est une surface brute murs compris (type SHOB), mais elle
    multiplie un coût de construction exprimé en €/m² SHON et un €/m² hédonique
    estimé sur la `surface_reelle_bati` DVF (habitable). Les deux niveaux de
    valeur sont surestimés (ordre de 10–25 % selon le type de bâti) et le
    résiduel hérite du biais ; le contrôle descendant du §5 l'absorbe en partie
    (numérateur et dénominateur gonflés ensemble), pas les niveaux en euros des
    graphiques. Signalé par la revue fondatrice (PR #1) ; nécessite un facteur
    brut→habitable documenté.
13. **Les exonérations ne sont pas modélisées.** Le produit REI est net
    d'exonérations (logement social neuf, art. 1384 A CGI ; abattement QPV), et
    les bâtiments publics (mairies, écoles, hôpitaux), les édifices religieux et
    les bâtiments ruraux exonérés en permanence (CGI art. 1382) sont exonérés de
    TFPB en réalité. Ici ils absorbent une part du produit actuel (via leur
    surface plancher) **et** paient la LVT simulée — surestimant la cotisation
    actuelle des HLM exonérés et du foncier public, dégonflant celle de tous les
    autres (sensible en Seine-Saint-Denis et à Paris) et déplaçant les barres par
    catégorie publiées comme chaque pourcentage. Le `exemption_flag_col` de
    l'amont est géré et inutilisé ; les attributs BD TOPO `usage_1`/`nature`
    permettraient de flagger les cas évidents.
14. **Mutations DVF multi-locaux.** Les locaux annexes (Dépendance) et les
    lignes hors commune gardent leur valeur dans le prix de la mutation mais
    sont exclus de la somme des surfaces, surestimant le €/m² là où les annexes
    sont fréquentes (maisons rurales) — un biais haussier spatialement structuré
    que l'écrêtage par centiles ne corrige pas (voir la docstring de
    `ingest.fetch_dvf`).
15. **Cache des données brutes optionnel.** `run_commune --cache-dir` (ou
    `LVTFR_CACHE_DIR`) met en cache les téléchargements bruts par empreinte
    d'URL, ce qui rend les lots reprenables ; sans lui, chaque exécution
    re-télécharge depuis des endpoints vivants qui bougent parfois
    (l'avertissement de config.py). Il n'y a pas encore de manifeste (source,
    URL, date, empreinte) : les exécutions sont reproductibles comme commandes,
    pas comme données.

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
