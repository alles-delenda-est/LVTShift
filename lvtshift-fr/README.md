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
config.py        commune, coûts de construction, bornes de sensibilité, URLs
ingest.py        téléchargements : DVF, cadastre, BDNB, REI, Filosofi
estimate.py      valeur bâti (coût de remplacement déprécié)
                 -> hédonique DVF -> terrain résiduel ancré -> taxe actuelle
run_pipeline.py  orchestration + appel du solveur LVTShift réel
test_synthetic.py  test bout-en-bout sur données synthétiques (passe ✅)
```

## Sources de données (toutes ouvertes)

| Donnée | Source | Rôle |
|---|---|---|
| Transactions | DVF géolocalisé (Etalab) | modèle hédonique de valeur de marché |
| Parcelles | Cadastre Etalab | géométries, surfaces |
| Bâtiments | **BDNB** (CSTB) : BD TOPO + DPE + attributs appariés Fichiers fonciers | emprise, niveaux, hauteur, année, usage |
| Recettes TFPB | REI (DGFiP) | cible exacte de neutralité budgétaire |
| Revenus | Filosofi IRIS (INSEE) | analyse distributive (quintiles) |
| Ancrages terrain | ventes de terrains à bâtir (DVF), EPTB (agrégats), comptes de patrimoine INSEE (part terrain ~45-50 %) | calibration / bornes |

## Méthode, en bref

1. **Valeur bâti** = emprise × niveaux × coût de construction (€/m², indices BT)
   × dépréciation linéaire plancher (25 % résiduel à 80 ans).
2. **Valeur de marché** : effets fixes cellule×type sur les €/m² DVF
   (médiane rétrécie, shrinkage k=8), volontairement simple et critiquable.
3. **Terrain = marché − bâti**, avec : plancher aux comparables terrains nus,
   parcelles vacantes valorisées directement aux comparables, part terrain
   bornée [15 %, 85 %] (chaque clip est flaggé `lv_flag`).
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

```bash
git clone https://github.com/gregmiller00/LVTShift.git   # à côté de ce dossier
pip install pandas numpy geopandas matplotlib
python test_synthetic.py        # bout-en-bout synthétique (sans réseau)
# puis : compléter ingest.py (BDNB, REI, Filosofi) et appeler run_pipeline.run()
```

`run()` écrit l'export standard `output/<commune>.csv` **et**, si matplotlib
est installé, les graphiques PNG sous `output/reports/<commune>/` : impact par
catégorie de bien, part de parcelles à ±10 %, quintile de revenu (Filosofi) et
distribution des variations. Les graphiques d'origine ethnique de l'export
américain sont automatiquement ignorés (colonnes nulles par principe). Pour un
export CSV seul : `run(..., make_report=False)`.

## Limites connues (à reproduire dans toute publication)

- L'imputation résiduelle est contestable dans les cœurs denses (peu de
  ventes de terrains nus) ; d'où les bandes de sensibilité obligatoires.
- Le proxy VLC déforme la distribution parcellaire de la taxe actuelle ;
  les agrégats (catégorie, quintile) sont robustes, les factures
  individuelles ne le sont pas — ne jamais publier de montants par parcelle.
- DVF exclut Alsace-Moselle et Mayotte ; le DPE n'est pas représentatif du
  parc (utilisé en covariable uniquement) ; la BDNB hérite des défauts
  d'appariement BD TOPO ↔ fichiers fonciers (flag de fiabilité conservé).
- Locaux professionnels : la révision 2017 des valeurs locatives change le
  poids relatif résidentiel/professionnel ; à traiter par strate.
