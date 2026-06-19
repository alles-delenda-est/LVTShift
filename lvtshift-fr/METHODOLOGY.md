# LVTShift-FR — Methodology

The complete, citeable methods reference for the French Land Value Tax (LVT)
pilot: every data source, formula, parameter, and limitation in one place.
Companion docs: **`METHODOLOGIE.md`** (parallel French version), `README.md`
(French summary), `THEORY.md` (operating theory and open questions), `GUIDE.md`
(plain-English how-to). When this file and the code disagree, the code is
canonical — keep both this file and `METHODOLOGIE.md` in sync with it.

## 1. Purpose and scope

Estimate, parcel by parcel, the revenue-neutral redistribution of a French
commune's *taxe foncière sur les propriétés bâties* (TFPB) if it shifted to a
split-rate Land Value Tax, using **open data only**. France never assesses land
and buildings separately, so per-parcel land value is **imputed**, with the error
bars made explicit. Results are reported by **property category** and **income
quintile**, never as individual bills.

Architecturally this is a fork of the US LVTShift toolkit: the FR code in
`lvtshift-fr/` manufactures LVTShift's expected input columns from French open
data and calls its *unmodified* solver (`model_split_rate_tax`) and export
(`save_standard_export`). Upstream improvements flow through automatically.

## 2. Data sources

| Datum | Source | Access | Vintage | Role |
|---|---|---|---|---|
| Parcels | Cadastre Etalab | GeoJSON per commune | latest | geometry, official area (`contenance`) |
| Transactions | DVF géolocalisé (Etalab) | CSV per commune | 5 rolling years | hedonic market value; terrain-à-bâtir comparables |
| Buildings | BD TOPO V3 (IGN) | WFS `BDTOPO_V3:batiment`, commune bbox | current | footprint, storeys, height, dwellings, usage, FF-match flag |
| Construction era | DPE logements existants (ADEME) | data-fair API by `code_insee_ban` | since 07/2021 | depreciation (period band → year) |
| Zoning | GPU `zone_urba` (IGN) | WFS, commune bbox | current PLU/PLUi | constructibility (U/AU vs A/N) of building-less parcels |
| Agricultural prices | SAFER « Le prix des terres » | départemental table (config) | 2024 | non-constructible land €/m² |
| Building-plot fallback | EPTB (SDES) | national figure (config) | 2023 | constructible €/m² when local comparables are thin |
| Tax target | REI foncier bâti, via OFGL | Opendatasoft API by `idcom` | latest | exact revenue-neutrality target (`MONTANT RÉEL`) |
| IRIS geometry | IGN IRIS contours | WFS `STATISTICALUNITS.IRIS:contours_iris` | current | parcel → IRIS for income join |
| Income | INSEE Filosofi | CSV zip (`DISP_MED21`) | 2021 | distributional (quintile) analysis |

All Licence Ouverte / Etalab. Exact endpoints live in `config.DATA_SOURCES`.

## 3. The pipeline and formulas

Spatial work is done in RGF93 / Lambert-93 (EPSG:2154). `cell` = a 400 m grid
square (a transparent hedonic fixed effect, not an admin geography).

**3.1 Building (improvement) value** — depreciated replacement cost, summed to
the parcel (`estimate.improvement_value`):

```
floor_area   = footprint_m2 × storeys          (storeys imputed from height/3 if missing)
age          = reference_year − year_built
depreciation = clip(1 − (1 − dep_floor) × age / dep_years,  min = dep_floor)
imp_value    = floor_area × construction_cost_eur_m2 × depreciation
```

`year_built` is taken from DPE (§3.2); `construction_cost_eur_m2`, `dep_years`,
`dep_floor` are per-commune config (§4). Buildings join parcels by **area-weighted
intersection** (a building straddling a boundary credits each parcel by overlap
share), not centroid.

**3.2 Construction year (depreciation anchor)** — BD TOPO's `date_d_apparition`
is a database first-appearance date, not a build year, and is often null (100 %
of Cahors). We instead use the DPE `periode_construction` era band, mapped to a
midpoint year (`avant 1948`→1930, `1948-1974`→1961, … `après 2021`→2022),
spatially joined to parcels (per-parcel median). Parcels with no DPE point take
the **commune dwelling-weighted median era** as a fallback, so age never
degenerates to "unknown".

**3.3 Market value** — a deliberately simple log-linear hedonic on DVF
(`estimate.fit_hedonic` / `market_value`): cell×type median of log €/m², shrunk
toward the commune-type median (pseudo-count k = 8), × parcel floor area. DVF is
cleaned to `Vente` mutations, aggregated to the mutation, €/m² trimmed at the
1st/99th percentile.

**3.4 Land value — classify then price** (`estimate.land_value_residual` →
`_land_value_classified`). Building-less parcels are classified by GPU zoning;
each class is priced against the right benchmark:

| Parcel | Land value |
|---|---|
| **Built** | `market − building` (residual), floored at the agricultural €/m², land share clipped to [0.15, 0.85] (every clip flagged in `lv_flag`) |
| **Constructible vacant** (zone U/AUc) | DVF terrain-à-bâtir €/m² × area (cell median where ≥8 sales, else commune median, else EPTB national fallback) |
| **Constructible deferred** (AU/AUs) | as above × `au_strict_factor` (development deferred) |
| **Agricultural / natural** (zone A/N) | SAFER départemental €/m² × area |

Only DVF rows coded *terrains à bâtir* are trusted for constructible prices —
raw `valeur_fonciere/surface_terrain` is contaminated for other cultures because
mutations bundle buildings and several parcels.

**3.5 Current tax (baseline)** — the exact REI FB produit, distributed
(`estimate.current_tax`) across **built parcels only** by a VLC proxy = floor
area. TFPB is a built tax; building-less parcels bear €0 (they pay the separate
TFPNB, out of scope). No market-value tilt (the 1970 VLC is regressive vs market,
so a tilt would worsen baseline fidelity); a category-weighted variant exists as
a labelled sensitivity only.

**3.6 Split-rate solver** — upstream `model_split_rate_tax` finds the
revenue-neutral land/improvement millages at the configured ratio (default 4:1).
Output is written by `save_standard_export`; euro charts by `charts_fr`
(currency-localised wrapper over the upstream report).

## 4. Key parameters and assumptions

- **Construction cost €/m²** (turnkey, hors foncier; pilot regional gradient,
  needs FFB/BT01 calibration): IdF 2150 (Montreuil), Lyon/Villeurbanne 1950,
  Grenoble/Annemasse 1900, Roubaix 1750, Cahors 1650, Figeac 1600.
- **Depreciation**: straight-line over `dep_years` = 80, floor `dep_floor` = 0.25.
- **Land-share bounds**: [0.15, 0.85] — a design constraint, not a measurement;
  dense cores can legitimately exceed 0.85 (publish the unclipped distribution).
- **Split-rate ratio**: 4:1 (land:improvement), headline scenario.
- **Agricultural €/m²** (SAFER, by département, agricultural / natural): default
  0.64 / 0.49; Lot 0.45 / 0.35; Seine-St-Denis 1.00 / 0.60; Nord 0.85 / 0.50;
  Rhône 0.70 / 0.50; Haute-Savoie 0.75 / 0.55; Isère 0.60 / 0.45.
- **EPTB building-plot fallback**: 99 €/m² (national).
- **AU discount** (`au_strict_factor`): 0.55. **Hedonic shrinkage** k = 8.
- **REI layers** held neutral: Commune + intercommunalité (configurable).

## 5. Validation

- **Revenue neutrality** — exact by construction; verified to the euro on every
  real run (Cahors €22,690,869; Montreuil €101,780,897).
- **Top-down land share** — total land ÷ total built real-estate value should sit
  near INSEE comptes de patrimoine (~45–50 % land). Cahors lands at ~53 % after
  the DPE construction-year fix (it was a degenerate 85 % before — see §6).
- **Sign checks** — agricultural/natural land bears a negligible share of the
  levy (Cahors 0.3 %); under-used constructible land pays *more* (the LVT
  incentive); the Montreuil income gradient is progressive (poorest quintiles
  −10 %, richer +9/+12 %).
- **Tests** — `test_units.py` (offline unit tests of the pure logic) and
  `test_synthetic.py` (end-to-end through the real solver).

## 6. Limitations (consolidated register)

Ranked by how much they move published (category/quintile) results.

1. **Current-tax baseline (load-bearing).** The VLC proxy is floor area only; it
   ignores cadastral category and weighted-surface coefficients. Distorts how
   *today's* bill is split between built properties, so read the **change**, not
   the starting bill. Resolved only by per-parcel VLC (Fichiers Fonciers).
2. **Residual amplification.** Built-parcel land = market − building, so building
   errors are amplified in the land residual where buildings are a large share of
   value. Mitigated by the [0.15, 0.85] clip, aggregation, and the sensitivity
   band. Vacant land does **not** use the residual, so the LVT headline (under-used
   land pays more) is unaffected by building-data quality.
3. **Construction year.** From DPE (diagnosed *residential* dwellings → selection
   bias); the commune-median fallback applies a residential median to
   non-residential / never-diagnosed parcels. Era→year uses band midpoints
   (mitigated for pre-1948 stock, which hits the depreciation floor regardless).
   A clear improvement over the prior degenerate baseline, but a documented
   generalisation.
4. **Construction costs** are coarse regional pilots; a ±15 % move flows linearly
   into building (hence land) value.
5. **Land-share clip** can mask genuinely >85 % land shares in dense cores
   (Montreuil); publish the unclipped distribution alongside.
6. **Zoning nuance**: all AU treated constructible with a flat discount; `AU
   fermée` deserves a steeper cut and `Nh/Ah` pastilles are undervalued.
7. **Non-residential market value** borrows the residential €/m² surface;
   professionnels (2017 VLC revision) need a separate stratum.
8. **Income (Filosofi)**: 2021 (last vintage), communes ≥5 000 inhabitants only,
   some IRIS statistically suppressed.
9. **Coverage**: DVF excludes Alsace-Moselle and Mayotte; Paris/Lyon/Marseille
   arrondissements have no separate TFPB (modelled via autonomous communes, e.g.
   Villeurbanne for inner Lyon).

## 7. The Fichiers Fonciers access argument

Each open-data compromise maps to a specific Fichiers Fonciers (CEREMA/DGFiP)
field that would resolve it: the floor-area VLC proxy → real per-parcel VLC;
estimated building surfaces → declared surfaces per local; DPE-inferred era →
exact construction year; the spatial building↔parcel join → native MAJIC links;
no owner typology / vacancy / exemptions → those fields directly. The pilot goes
this far on open data; the *acte d'engagement* turns each row into exact
administrative data at zero marginal cost to the partner. **The demo is the
argument for access.**

## 8. Reproducibility

```
pip install pandas numpy geopandas matplotlib seaborn
cd lvtshift-fr
python test_synthetic.py                 # offline end-to-end
python run_commune.py <commune>          # live open-data run; CSV + charts
```

Communes: `villeurbanne`, `roubaix`, `cahors`, `figeac`, `montreuil`,
`grenoble`, `annemasse`. Flags: `--layers` (REI scope), `--no-dpe` (BD TOPO year
only, for the depreciation comparison), `--no-report` (CSV only). On Windows set
`PYTHONUTF8=1`. Outputs land in `output/<commune>.csv` and
`output/reports/<commune>/*.png` (both gitignored).
