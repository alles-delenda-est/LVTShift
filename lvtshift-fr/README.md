# LVTShift-FR

Adaptation française de [LVTShift](https://github.com/gregmiller00/LVTShift)
(Center for Land Economics) : simulation d'un transfert de la taxe foncière
vers une taxe sur la valeur du foncier (LVT), **à recettes constantes**,
à la parcelle, sur **données ouvertes uniquement**.

Zéro fork : le code appelle directement le solveur et l'export standard de
LVTShift (`model_split_rate_tax`, `save_standard_export`). Les améliorations
amont profitent automatiquement à la version française.

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
ingest.py        DVF, cadastre, BD TOPO, GPU, REI, contours IRIS, Filosofi
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
| Recettes TFPB | REI (DGFiP), territorialisé par **OFGL** | cible exacte de neutralité budgétaire (foncier bâti `FB`, montant réel) |
| Revenus | Filosofi IRIS (INSEE) | analyse distributive (quintiles) |
| Zonage | **GPU `zone_urba`** (Géoportail de l'Urbanisme, WFS) | constructibilité (U/AU vs A/N) des parcelles non bâties |
| Prix terrain à bâtir | ventes **terrains à bâtir** (DVF), EPTB (repli national) | valeur du foncier constructible |
| Prix terres agricoles | **SAFER** « Le prix des terres » (départemental) | valeur du foncier agricole/naturel |
| Ancrage part terrain | comptes de patrimoine INSEE (~45-50 %) | contrôle descendant |

## Méthode, en bref

1. **Valeur bâti** = emprise × niveaux × coût de construction (€/m², indices BT)
   × dépréciation linéaire plancher (25 % résiduel à 80 ans).
2. **Valeur de marché** : effets fixes cellule×type sur les €/m² DVF
   (médiane rétrécie, shrinkage k=8), volontairement simple et critiquable.
3. **Terrain : classer puis valoriser.** Parcelles bâties → résiduel
   (marché − bâti), plancher à la valeur agricole, part terrain bornée
   [15 %, 85 %] (clips flaggés `lv_flag`). Parcelles non bâties → classées par
   le zonage PLU (GPU `zone_urba` : U/AU constructible, A/N agricole/naturel) :
   le constructible est valorisé aux comparables **terrains à bâtir** DVF
   (médiane communale, repli EPTB national), le non-bâti aux prix **SAFER**
   départementaux (~0,4–1 €/m²). Bâtiments rattachés aux parcelles par
   **intersection pondérée par surface** (et non par centroïde).
4. **Taxe actuelle** : produit TFPB communal réel (REI) distribué au prorata
   d'un proxy de VLC (surface plancher). *Maillon faible assumé.*
5. **Solveur LVTShift** : split-rate 4:1, neutralité à 1 % près (vérifiée).
6. **Sensibilité** : tout résultat publié avec bande part-terrain ±10 pts.

Les résultats sont reportés aux niveaux **catégorie de bien** et **quintile
de revenu IRIS**, où les erreurs d'imputation parcellaires se moyennent.

Note comparaisons internationales : les colonnes `minority_pct`/`black_pct`
de l'export standard restent vides — la France ne produit pas de
statistiques ethniques. L'analyse d'équité se fait sur le revenu (Filosofi).

## Ce que l'accès aux Fichiers fonciers remplacerait

| Limitation de la démo | Variable FF qui la résout |
|---|---|
| VLC approximée par la surface plancher | VLC réelle par parcelle/local |
| Surfaces bâti estimées (BDNB/BD TOPO) | surfaces déclarées par local |
| Pas de typologie de propriétaires | table propriétaires (HLM, SCI, personnes physiques…) |
| Pas de vacance | indicateur de vacance 5 ans glissants |
| Exonérations ignorées | champs d'exonération par local |
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
Communes pré-configurées : `villeurbanne` (cœur lyonnais), `roubaix`,
`cahors`, `figeac` (Lot rural), `montreuil`, `grenoble`, `annemasse`.
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

- **Taxe actuelle (maillon porteur désormais).** La TFPB est un impôt sur le
  **bâti** : les parcelles non bâties portent désormais **zéro** taxe actuelle
  (elles relèvent de la TFPNB, hors cible) — elles passent de ~0 à une LVT
  positive. *Reste faible* la répartition du produit **entre parcelles bâties**
  au prorata de la seule surface plancher : elle ignore la catégorie cadastrale
  et les coefficients de pondération de surface (principaux moteurs de la VLC).
  Choix assumé : **pas** de calage sur la valeur de marché (la VLC 1970 est
  régressive vs marché, un tel calage dégraderait la fidélité au système actuel) ;
  une variante pondérée par catégorie n'est offerte qu'en **sensibilité**. Ne
  jamais publier de montants de taxe actuelle à la parcelle.
- **Nuance de zonage AU et Nh/Ah** (revue Gemini) : tout AU est traité
  constructible avec une décote forfaitaire (AU/AUs) ; les AU *fermées* mériteraient
  une décote plus forte et les pastilles `Nh/Ah` (constructibilité limitée en A/N)
  sont actuellement sous-évaluées.
- L'imputation résiduelle est contestable dans les cœurs denses (peu de
  ventes de terrains nus) ; d'où les bandes de sensibilité obligatoires.
- Le bornage de la part terrain à [15 %, 85 %] est une **contrainte de
  conception, non une mesure** : toute publication doit présenter la
  distribution **non bornée** des parts terrain à côté des résultats bornés,
  et signaler que les cœurs denses peuvent légitimement dépasser 85 %.
- Le proxy VLC (surface plancher) est le **maillon faible porteur** : il
  ignore la catégorie cadastrale et les coefficients de pondération de
  surface, deux des principaux déterminants de la VLC de 1970. Il déforme la
  distribution parcellaire de la taxe actuelle — **ne jamais publier de
  montants par parcelle**. Même agrégés (catégorie, quintile), les montants
  de la taxe *actuelle* restent indicatifs et doivent être recoupés avec les
  données REI par catégorie : la robustesse des agrégats vaut d'abord pour le
  volet LVT, pas pour la base de départ.
- DVF exclut Alsace-Moselle et Mayotte ; le DPE n'est pas représentatif du
  parc (utilisé en covariable uniquement) ; la BDNB hérite des défauts
  d'appariement BD TOPO ↔ fichiers fonciers (flag de fiabilité conservé).
- Locaux professionnels : la révision 2017 des valeurs locatives change le
  poids relatif résidentiel/professionnel ; à traiter par strate.
- Revenus (Filosofi) : millésime 2021 (le dernier produit), à l'IRIS,
  **uniquement pour les communes ≥ 5 000 habitants** ; certains IRIS sont sous
  secret statistique (revenu manquant → exclus des quintiles). L'analyse par
  quintile hérite de la faiblesse de la taxe actuelle : à lire en tendance.
