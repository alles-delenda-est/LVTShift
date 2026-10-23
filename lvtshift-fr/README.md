# LVTShift-FR

Adaptation française de [LVTShift](https://github.com/gregmiller00/LVTShift)
(Center for Land Economics) : simulation d'un transfert de la taxe foncière
vers une taxe sur la valeur du foncier (LVT), **à recettes constantes**,
à la parcelle, sur **données ouvertes uniquement**.

Zéro modification de l'amont : le code (dans `lvtshift-fr/`, au sein de ce
fork) appelle directement le solveur et l'export standard de LVTShift
(`model_split_rate_tax`, `save_standard_export`) sans toucher aux fichiers
amont. Les améliorations amont profitent automatiquement à la version
française.

## Pourquoi ce dépôt existe

La France n'évalue pas séparément terrain et bâti (la taxe foncière repose
sur la valeur locative cadastrale de 1970). Ce pipeline **impute** la valeur
du terrain par méthode résiduelle, avec des bornes de sensibilité publiées.
L'objectif est double :

1. produire une première simulation LVT crédible pour une commune pilote ;
2. **démontrer l'utilité d'un accès aux Fichiers fonciers** (CEREMA/DGFiP),
   en rendant explicite, limitation par limitation, ce que cet accès
   débloquerait (voir tableau ci-dessous).

## Architecture

```
config.py        communes, coûts de construction, benchmarks fonciers, URLs
ingest.py        DVF, cadastre, BD TOPO, GPU, DPE, REI, contours IRIS, Filosofi
estimate.py      valeur bâti (coût de remplacement déprécié)
                 -> hédonique DVF -> terrain « classer puis valoriser » -> taxe
run_pipeline.py  orchestration + appel du solveur LVTShift réel
run_commune.py   pilote données réelles (ingest -> solveur) pour une commune
test_synthetic.py  test bout-en-bout sur données synthétiques (passe ✅)
```

## Sources de données (toutes ouvertes)

| Donnée | Source | Rôle |
|---|---|---|
| Transactions | DVF géolocalisé (Etalab) | modèle hédonique de valeur de marché |
| Parcelles | Cadastre Etalab | géométries, surfaces |
| Bâtiments | **BD TOPO V3** (IGN, WFS Géoplateforme) | emprise, niveaux, hauteur, logements, usage, flag d'appariement Fichiers fonciers |
| Année de construction | **DPE logements existants** (ADEME) | période de construction → dépréciation (BD TOPO `date_d_apparition` peu fiable/souvent nulle) |
| Recettes TFPB | REI (DGFiP), territorialisé par **OFGL** | cible exacte de neutralité budgétaire (foncier bâti `FB`, montant réel) |
| Revenus | Filosofi IRIS (INSEE) | analyse distributive (quintiles) |
| Foncier public exonéré | fichiers DGFiP des **personnes morales** (locaux et parcelles) | repérer le foncier public manifestement exonéré de TFPB (règle prudente) |
| Zonage | **GPU `zone_urba`** (Géoportail de l'Urbanisme, WFS) | constructibilité (U/AU vs A/N) des parcelles non bâties ; repérage des bâtiments agricoles exonérés (zones A/N) |
| Prix terrain à bâtir | ventes **terrains à bâtir** (DVF), EPTB (repli national) | valeur du foncier constructible |
| Prix terres agricoles | **SAFER** « Le prix des terres » (départemental) | valeur du foncier agricole/naturel |
| Ancrage part terrain | comptes de patrimoine INSEE (~45-50 %) | contrôle descendant |

## Méthode, en bref

1. **Valeur bâti** = surface habitable × coût de construction par m² habitable
   × dépréciation linéaire plancher (25 % résiduel à 80 ans), appliquée à
   l'**âge effectif** : là où les prix de l'IRIS dépassent nettement le coût de
   reconstruction, le bâti entretenu compte au plus 30 ans. Surface habitable =
   emprise × niveaux (BD TOPO) × 0,64 (appartements) ou 0,61 (maisons), ratios
   mesurés sur 35 communes (DPE × BD TOPO). Coûts 2025 par m² brut, honoraires et
   TVA inclus, calés pour Paris (2 650), la petite couronne (2 400), Lyon et
   Villeurbanne (2 000) et la couronne lyonnaise (1 850) sur les coûts du
   logement social neuf (DHUP/SISAL, indice BT01) ; les maisons y ont leur
   propre coût, tiré de l'enquête EPTB du SDES sur les maisons neuves (Paris
   2 300, petite couronne 2 100, Lyon et Villeurbanne 2 400, couronne lyonnaise
   2 250). Ces coûts sont divisés par 0,71 (appartements) ou 0,82 (maisons)
   pour passer au m² habitable. Les bâtiments non résidentiels sont typés
   d'après l'usage et la nature BD TOPO (hangar, atelier, grande surface,
   bureaux, hangar agricole, serre, salle de sport, annexe, culte) ; chaque
   type a un coût en ratio du coût du logement collectif (hangar 0,25,
   bureaux 0,825, salle de sport 1,033…, hors TVA pour les types
   professionnels), une durée de vie et un plancher propres, et, sans année
   connue, il est pris à mi-vie (le DPE ne date que le logement).
2. **Valeur de marché** : effets fixes cellule×type sur les €/m² DVF
   (médiane rétrécie, shrinkage k=8) × surface habitable, volontairement simple
   et critiquable ;
   chaque vente est d'abord ramenée en euros 2025 par l'indice Notaires-INSEE
   le plus local (Paris, départements de petite couronne, agglomérations de
   Lyon, Marseille, Lille, régions, Province).
3. **Terrain : classer puis valoriser.** Parcelles bâties → résiduel
   (marché − bâti), plancher à la valeur agricole, part terrain bornée
   [15 %, 85 %] (clips flaggés `lv_flag`). Parcelles non bâties → classées par
   le zonage PLU (GPU `zone_urba` : U/AU constructible, A/N agricole/naturel) :
   le constructible est valorisé aux comparables **terrains à bâtir** DVF
   (médiane communale, repli EPTB national), le non-bâti aux prix **SAFER**
   départementaux (~0,4–1 €/m²). Bâtiments rattachés aux parcelles par
   **intersection pondérée par surface** (et non par centroïde). Les parcelles
   dont le plus grand bâtiment est un hangar, un atelier, une grande surface,
   un hangar agricole, une serre, une salle de sport ou une annexe sont
   évaluées au **coût de remplacement déprécié** (« sol + construction ») :
   bâti au coût déprécié, terrain au prix local des terrains à bâtir × 0,45
   (Paris et ailleurs) ou × 0,35 (territoires lyonnais) pour le foncier
   d'activité (ventes DVF de terrains d'activité), × 1 pour le sport et les
   annexes ; hors zone urbaine, seule une cour de 3 × la surface plancher prend
   ce prix. Les bureaux restent au résiduel, à leur propre coût.
4. **Taxe actuelle** : produit TFPB communal réel (REI), calé commune par
   commune sur sa répartition REI 2025 entre établissements industriels
   (compensation WC75 ÷ taux 2020), locaux professionnels (base brute de CFE
   × 0,5 × 2,5) et logement, puis réparti à la surface plancher au sein de
   chaque groupe (usage BD TOPO). `--baseline floor` garde l'ancienne
   répartition à la seule surface plancher. *Maillon faible assumé.* Le foncier
   public manifestement exonéré (art. 1382-1° CGI) et les bâtiments agricoles
   (art. 1382 6° : serres, granges, silos, repérés par l'usage BD TOPO et le
   zonage A/N) sont exclus, aujourd'hui comme sous la LVT ; une parcelle qui ne
   porte que des bâtiments agricoles est traitée comme une terre agricole non
   bâtie. `--no-exemptions` désactive les deux.
5. **Solveur LVTShift** : split-rate 4:1, neutralité à 1 % près (vérifiée).
6. **Sensibilité** : tout résultat publié avec bande part-terrain ±10 pts —
   chiffres clés, catégories de bien et quintiles de revenu (moustaches sur le site).

Les résultats sont reportés aux niveaux **catégorie de bien** et **quintile
de revenu IRIS**, où les erreurs d'imputation parcellaires se moyennent.

Référence méthodologique complète (sources, formules, paramètres, validation,
limites) : **`METHODOLOGIE.md`** (français) / `METHODOLOGY.md` (anglais).

Note comparaisons internationales : les colonnes `minority_pct`/`black_pct`
de l'export standard restent vides — la France ne produit pas de
statistiques ethniques. L'analyse d'équité se fait sur le revenu (Filosofi).

## Ce que l'accès aux Fichiers fonciers remplacerait

| Limitation de la démo | Variable FF qui la résout |
|---|---|
| VLC approximée par la surface plancher, calée sur les parts REI par groupe (facteur professionnel national) | VLC réelle par parcelle/local |
| Surfaces bâti estimées (BD TOPO) | surfaces déclarées par local |
| Année de construction inférée (DPE) | année de construction exacte par local |
| Pas de typologie de propriétaires | table propriétaires (HLM, SCI, personnes physiques…) |
| Pas de vacance | indicateur de vacance 5 ans glissants |
| Exonérations approchées par la propriété publique (règle prudente) et, pour les bâtiments agricoles, par l'usage BD TOPO et le zonage ; exonérations temporaires ignorées | champs d'exonération par local |
| Appariement bâtiment-parcelle approximatif | liens MAJIC natifs |

**C'est l'argument d'accès** : la démo va jusqu'ici sur données ouvertes ;
l'acte d'engagement transforme chaque ligne du tableau en donnée
administrative exacte, à coût marginal nul pour la structure partenaire.

## Lancer

Le code vit *dans* ce dépôt (fork de LVTShift) ; le paquet `lvt` est à la
racine et `lvtshift-fr/` à côté. On clone donc le fork, pas l'amont.

```bash
git clone https://github.com/alles-delenda-est/LVTShift.git
cd LVTShift
pip install pandas numpy geopandas matplotlib seaborn
cd lvtshift-fr
python test_synthetic.py            # bout-en-bout synthétique (sans réseau)
python run_commune.py montreuil     # commune réelle, données ouvertes en direct
```

`run_commune.py` enchaîne l'ingest réel (cadastre Etalab, DVF, bâtiments
BD TOPO via WFS IGN, cible REI via OFGL) puis appelle le solveur LVTShift.
Communes pré-configurées : `villeurbanne`, `roubaix`, `cahors`, `figeac`
(Lot rural), `montreuil`, `grenoble`, `annemasse`, `sete`, `larochelle`,
`paris` et `lyon` (assemblées depuis leurs arrondissements, taux unique), plus
les 179 communes des couronnes (`run_territory.py paris-extra-muros` /
`lyon-extra-muros`, chacune à recettes constantes sur son propre produit).
`--layers Commune` pour ne neutraliser que la part communale ;
`--no-report` pour un export CSV seul.

> Sous Windows, exporter `PYTHONUTF8=1` avant de lancer (les libellés de
> l'export amont contiennent des caractères Unicode que la console cp1252
> refuse). Python 3.15+ le fera par défaut.

Guide pas-à-pas pour non-codeur (Windows/PowerShell) : voir **`GUIDE.md`**.

`run()` écrit l'export standard `output/<commune>.csv` **et**, si matplotlib
est installé, les graphiques PNG sous `output/reports/<commune>/` : impact par
catégorie de bien, part de parcelles à ±10 %, quintile de revenu (Filosofi) et
distribution des variations. Les graphiques d'origine ethnique de l'export
américain sont automatiquement ignorés (colonnes nulles par principe). Pour un
export CSV seul : `run(..., make_report=False)`.

## Limites connues (à reproduire dans toute publication)

- **Toujours publier côte à côte le cas central et la borne basse.** La part
  des locaux professionnels dans la taxe actuelle est un indicateur CFE
  multiplié par un facteur national (2,5, cas central) ; l'indicateur brut
  (× 1,0) est la borne basse. Ce facteur déplace les résultats des ménages de
  10 à 15 points : premier quintile de revenu à Paris −17,4 % (central) contre
  −27,6 % (borne basse), couronne lyonnaise +0,8 % contre −15,8 %. Les
  nouvelles cotisations sont identiques ; seul le point de départ bouge. Un
  facteur national unique ne peut convenir à toutes les communes ; les
  Fichiers fonciers le remplaceraient par les vraies valeurs.
- **Constat inverse de l'attendu.** Les entreprises paient aujourd'hui plus au
  m² que ne le supposait la surface plancher (valeurs industrielles incluant
  l'outillage, locaux professionnels réévalués sur les loyers de 2013 quand le
  logement reste sur 1970) : la réforme déplace donc davantage de charge des
  entreprises vers les ménages. Dans le couloir chimique et industriel
  lyonnais, la LVT déplace l'impôt de l'industrie vers les ménages dans le cas
  central. La LVT modélisée exonère implicitement l'outillage industriel (seul
  le hangar compte dans la valeur bâtie) ; c'est un choix politique, de poids
  mineur dans la baisse industrielle.
- **Taxe actuelle (maillon porteur).** La TFPB est un impôt sur le
  **bâti** : les parcelles non bâties portent **zéro** taxe actuelle
  (elles relèvent de la TFPNB, hors cible) — elles passent de ~0 à une LVT
  positive. Au sein de chaque groupe de locaux (industriel, professionnel,
  logement), le produit reste réparti à la seule surface plancher, qui ignore
  la catégorie cadastrale et les coefficients de pondération de surface.
  Choix assumé : **pas** de calage sur la valeur de marché (la VLC 1970 est
  régressive vs marché, un tel calage dégraderait la fidélité au système
  actuel). Ne jamais publier de montants de taxe actuelle à la parcelle.
- **Nuance de zonage AU et Nh/Ah** (revue Gemini) : tout AU est traité
  constructible avec une décote forfaitaire (AU/AUs) ; les AU *fermées* mériteraient
  une décote plus forte et les pastilles `Nh/Ah` (constructibilité limitée en A/N)
  sont actuellement sous-évaluées.
- L'imputation résiduelle est contestable dans les cœurs denses (peu de
  ventes de terrains nus) ; d'où la bande de sensibilité ±10 pts publiée avec
  chaque commune (voir METHODOLOGY §6).
- Le bornage de la part terrain à [15 %, 85 %] est une **contrainte de
  conception, non une mesure** : toute publication doit présenter la
  distribution **non bornée** des parts terrain à côté des résultats bornés.
  La dépréciation du bâti ancien entretenu se fait à l'**âge effectif** (au
  plus 30 ans là où les prix de l'IRIS dépassent nettement le coût de
  reconstruction) : sans cela, 95,5 % des parcelles bâties parisiennes étaient
  à la borne de 85 %. Avec cette règle, les deux termes du résiduel en surface
  habitable, les coûts recalés et la valorisation du non-résidentiel, Paris
  ressort à 75,8 % (5,6 % des parcelles bâties à la borne) ; aucune commune
  n'a plus de la moitié de ses parcelles bâties au plafond (Neuilly-sur-Seine
  en a le plus, 25,3 %). La fourchette 40–65 % est un repère métropolitain,
  pas un test par commune : les communes limitrophes de Paris se situent
  naturellement entre 65 et 75 %.
  La part avant bornage est conservée (colonne `land_share_raw`) pour publier
  la distribution non bornée.
- **Exonérations TFPB partiellement modélisées** : le foncier public
  manifestement exonéré est repéré (règle prudente, voir plus haut), comme les
  bâtiments agricoles (CGI art. 1382 6°, approchés par l'usage BD TOPO et le
  zonage) ; les édifices religieux associatifs et les exonérations temporaires
  (HLM neufs, abattement QPV) absorbent encore une part du produit actuel **et**
  paient la LVT simulée.
- **Coûts de construction et ratio habitable ÷ brut.** Hors Paris, petite
  couronne et territoires lyonnais, les coûts restent des valeurs pilotes non
  calées. Le maillon le moins sourcé est le rapport surface habitable ÷ vraie
  surface brute sous-jacent aux coûts (0,71 / 0,82) : ±0,05 déplace la valeur
  bâti d'environ ±7 %. Le coût des maisons est plus incertain autour de Lyon,
  où les maisons neuves de l'échantillon EPTB sont probablement plus sur
  mesure que le parc. Quand la BD TOPO ne donne pas le nombre d'étages, il
  est imputé selon le type de bâtiment (1 niveau pour les hangars, annexes et
  constructions légères ; hauteur ÷ 3,5 m pour les autres bâtiments
  commerciaux de 7 m et plus ; hauteur ÷ 3 m pour le logement) : l'ancienne
  règle unique hauteur ÷ 3 m gonflait 2 à 2,7 fois la surface des entrepôts.
  Les coûts du non-résidentiel reposent sur un seul guide commercial ramené
  à notre niveau de logement (±25 %), le ratio du foncier d'activité sur
  n ≈ 20 à 80 ventes, et les bureaux restent valorisés au prix résidentiel.
  Sur une parcelle mixte, le plus grand bâtiment décide de la méthode.
- Même agrégés (catégorie, quintile), les montants de la taxe *actuelle*
  restent indicatifs : seules les parts industrielle et professionnelle de
  chaque commune sont calées sur le REI. La robustesse des agrégats vaut
  d'abord pour le volet LVT, pas pour la base de départ.
- DVF exclut Alsace-Moselle et Mayotte ; les bâtiments viennent de BD TOPO V3
  (emprise + attributs dérivés MAJIC, flag d'appariement fichiers fonciers
  conservé), l'appariement bâtiment ↔ parcelle se fait par intersection pondérée.
- Locaux professionnels : la révision 2017 des valeurs locatives change le
  poids relatif résidentiel/professionnel ; la base calée en tient compte au
  niveau de la commune, pas au sein de chaque groupe.
- Année de construction (DPE) : la période est issue des DPE (logements
  **diagnostiqués** uniquement — biais de sélection), mappée à l'année médiane de
  la tranche ; pour les logements sans DPE on retombe sur l'**année médiane
  communale** (issue des DPE résidentiels) ; le non-résidentiel sans année
  propre est pris à mi-vie.
  Nette amélioration sur la base dégénérée précédente (bâti ≈ 0 quand l'année BD
  TOPO est nulle), mais généralisation à documenter.
- Revenus (Filosofi) : millésime 2021 (le dernier produit), à l'IRIS,
  **uniquement pour les communes ≥ 5 000 habitants** ; certains IRIS sont sous
  secret statistique (revenu manquant → exclus des quintiles). L'analyse par
  quintile hérite de la faiblesse de la taxe actuelle : à lire en tendance.
