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
| Agricultural prices | SAFER « Le prix des terres » | départemental table (config) | 2025 edition (2024 sales) | non-constructible land €/m² |
| Building-plot fallback | EPTB (SDES) | national figure (config) | 2023 | constructible €/m² when local comparables are thin |
| Tax target | REI foncier bâti, via OFGL | Opendatasoft API by `idcom` | latest | exact revenue-neutrality target (`MONTANT RÉEL`) |
| IRIS geometry | IGN IRIS contours | WFS `STATISTICALUNITS.IRIS:contours_iris` | current | parcel → IRIS for income join |
| Income | INSEE Filosofi | CSV zip (`DISP_MED21`) | 2021 (see §6.8) | distributional (quintile) analysis |

All Licence Ouverte / Etalab. Exact endpoints live in `config.DATA_SOURCES`.

## 3. The pipeline and formulas

Spatial work is done in RGF93 / Lambert-93 (EPSG:2154). `cell` = a 400 m grid
square (a transparent hedonic fixed effect, not an admin geography).

**3.1 Building (improvement) value** — depreciated replacement cost, summed to
the parcel (`estimate.improvement_value`):

```
floor_area   = footprint_m2 × storeys          (storeys imputed from height/3 if missing)
age          = reference_year − year_built
q            = median hedonic €/m² of the built parcels in the parcel's IRIS
               ÷ construction_cost_eur_m2   (commune median if the IRIS has none)
w            = clip((q − 1.2) / (2.5 − 1.2), 0, 1)          (dep_q_ramp)
eff_age      = w × min(age, 30) + (1 − w) × age             (dep_maintained_age_cap)
depreciation = clip(1 − (1 − dep_floor) × eff_age / dep_years,  min = dep_floor)
imp_value    = floor_area × construction_cost_eur_m2 × depreciation
```

`year_built` is taken from DPE (§3.2); `construction_cost_eur_m2`, `dep_years`,
`dep_floor` are per-commune config (§4).

*Maintained stock (effective age).* Where neighbourhood prices are far above
rebuild cost, owners keep renovating, so years since construction stop measuring
wear: a maintained 1880 building is valued as if 30 years old (factor 0.72)
instead of hitting the 25 % floor. This follows the appraisal concept of
effective age (Davis, Larson, Oliner & Shui, FHFA WP 19-01) and the evidence that
well-maintained dwellings show little long-run physical deterioration (Francke &
van de Minne 2017); INSEE's own stock accounts capitalise renovation the same way
(70-year life, base 2020). The weight `w` ramps continuously with q, so
neighbouring parcels never jump between regimes, and q is taken at IRIS level, not
per parcel, so a local land-price rise is not read as a newer building. The IRIS
median uses built parcels only: vacant plots carry a placeholder dwelling type and
would pull a house-dominated area towards the flat price. In weak
markets (q ≤ 1.2: Roubaix, Cahors) the rule is inactive and age-based depreciation
also absorbs economic obsolescence. A uniform cap was tested and rejected: it puts
half of Roubaix's and a third of Cahors's built parcels on the 15 % lower bound.

Buildings join parcels by **area-weighted
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
1st/99th percentile. The five pooled years enter at **nominal** prices — the
`fit_hedonic(deflator=…)` hook exists but no Notaires-INSEE index is wired in
yet (see §6, item 10).

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

**3.7 Paris, Lyon and the inner rings** — Paris (75056) and Lyon (69123) levy
the TFPB as one commune, but cadastre, DVF, DPE and IRIS are published per
arrondissement (75101–75120, 69381–69389). A config carries both: `insee_code` is
the fiscal code REI is keyed on, `sub_codes` the data codes. Every fetcher loops
the data codes (spatial fetches one arrondissement bbox at a time, so a boundary
building is credited only to the parcels it overlaps), the frames are stacked into
one commune, and **one** revenue-neutral split-rate is solved for the city — as the
real levy has one rate. DPE records filed under the city code are also pulled.

The **extra-muros territories** — *Paris extra-muros* (all 122 communes of 92/93/94)
and *Lyon extra-muros* (the 57 other communes of the Métropole de Lyon; membership
frozen in `territories.py`) — are **not** a metropolitan tax. Each member is run on
its own REI produit and held revenue-neutral on its own (`run_territory.py`, one
process per commune); `export_web.build_territory_payload` then pools the
per-parcel results into aggregates. The ±10 pt sensitivity is re-solved commune by
commune (each tilted around its own land share) before pooling; income quintiles
are ranked across the whole ring. A member that fails is listed in the payload's
`coverage`, never imputed. Montreuil and Villeurbanne appear both alone and in
their ring; the site's panel totals count them once.

**Paris's land share and the 85 % cap.** Under the original rule (straight-line
to a 25 % floor) a ~95-year-old, continuously maintained Paris building fell to
≈ €575/m² against a median DVF price of ≈ €10,860/m², so 95.5 % of built parcels
sat at the 0.85 bound (Lyon 59.8 %; 55 communes flagged) and the 84.9 % headline
was set by the cap. The maintained-stock rule (§3.1) values such buildings at a
30-year effective age: Paris now comes out at **83.9 %**, with 47.6 % of built
parcels still at the bound. That residue is genuine, not an artefact: at Paris
prices even a building valued at 72 % of rebuild cost leaves land above 85 % on
expensive streets (Neuilly-sur-Seine is the one commune still above half at the
bound). Lyon falls to 72.0 % with no parcel at the bound; across the panel the
`land_share_clip` warnings fall from 55 to 1. No write-down at all would give
63–79 % for Paris, a lower bound. `headline.built_at_cap_pct` records the share of
built parcels at the bound, and the site labels the land share "plafonnée" when it
is ≥ 50 %.

## 4. Key parameters and assumptions

- **Construction cost €/m²** (turnkey, hors foncier; pilot regional gradient,
  needs FFB/BT01 calibration): Paris 2300, IdF inner ring 2150 (Montreuil and
  all of 92/93/94), Lyon, Villeurbanne and the Métropole ring 1950,
  Grenoble/Annemasse 1900, Roubaix 1750, Cahors 1650, Figeac 1600.
- **Depreciation**: straight-line over `dep_years` = 80, floor `dep_floor` = 0.25,
  on the effective age; maintained-stock cap 30 years (`dep_maintained_age_cap`),
  ramp q ∈ [1.2, 2.5] (`dep_q_ramp`). Both are judgement calls informed by the
  literature (§3.1); the cap and ramp end-points are not directly estimated.
- **Land-share bounds**: [0.15, 0.85] — a design constraint, not a measurement.
  Where most parcels hit the upper bound (Paris, Lyon), the cause found so far is
  over-depreciation of old maintained stock, not land genuinely above 85 % (§3.7).
- **Split-rate ratio**: 4:1 (land:improvement), headline scenario.
- **Agricultural €/m²** (SAFER, by département, agricultural / natural): default
  0.64 / 0.49; Lot 0.45 / 0.35; Seine-St-Denis 1.00 / 0.60; Nord 0.85 / 0.50;
  Rhône 0.70 / 0.50; Haute-Savoie 0.75 / 0.55; Isère 0.60 / 0.45; Paris,
  Hauts-de-Seine, Val-de-Marne 1.00 / 0.60 (Île-de-France anchor; immaterial).
- **EPTB building-plot fallback**: 99 €/m² (national).
- **AU discount** (`au_strict_factor`): 0.55. **Hedonic shrinkage** k = 8.
- **REI layers** held neutral: Commune + intercommunalité (configurable). The
  preflight `rei_layers` check reports, per commune, which FB layers exist and the
  share left out: in 92/93/94 there is no GFP layer (EPTs and the MGP levy no
  FB); in the Métropole de Lyon a *Syndicat* layer is material in 45 communes
  (5–23 % of the FB bill). Syndicat rates sit on the same VLC base, so leaving
  them out scales the euro amounts but not the % changes.

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
   value. Mitigated by the [0.15, 0.85] clip and aggregation, and made visible
   by the land-share ±10 pt sensitivity band published with every commune's
   headline figures (`headline_sensitivity`, re-solved revenue-neutral at each
   end). Vacant land does **not** use the residual, so the LVT headline
   (under-used land pays more) is unaffected by building-data quality.
3. **Construction year.** From DPE (diagnosed *residential* dwellings → selection
   bias); the commune-median fallback applies a residential median to
   non-residential / never-diagnosed parcels. Era→year uses band midpoints
   (mitigated for pre-1948 stock, which hits the depreciation floor regardless).
   A clear improvement over the prior degenerate baseline, but a documented
   generalisation.
4. **Construction costs** are coarse regional pilots; a ±15 % move flows linearly
   into building (hence land) value.
5. **Land-share clip**: when most built parcels sit at a bound, the land share is
   an assumption, not a result, and the parcel-level variation in building value is
   erased. Before the maintained-stock rule this was Paris (95.5 % at the bound),
   Lyon and 53 other communes; it is now Neuilly-sur-Seine only, with Paris at
   47.6 % (§3.7). The preflight `land_share_clip` check flags it. The effective-age
   cap (30 years) and ramp (q 1.2–2.5) are judgement calls; publishing a
   sensitivity on them is open (THEORY.md).
   Publish the unclipped distribution alongside (the pre-clip share is kept as
   `land_share_raw` in the parcel frame). Precedence when the agricultural floor
   and the clip conflict: the floor (a market observation) wins; such parcels are
   flagged `built_floored_ag` and their land share may legitimately exceed the
   bounds.
6. **Zoning nuance**: all AU treated constructible with a flat discount; `AU
   fermée` deserves a steeper cut and `Nh/Ah` pastilles are undervalued.
7. **Non-residential market value** borrows the residential €/m² surface;
   professionnels (2017 VLC revision) need a separate stratum.
8. **Income (Filosofi)**: 2021 vintage; INSEE published a « Filosofi 2 » 2023
   vintage with IRIS indicators in May 2026 (methodological break) — 2021 is
   retained pending evaluation. Communes ≥5 000 inhabitants only, some IRIS
   statistically suppressed. Quintiles additionally need ≥5 income-distinct
   IRIS: a commune with one or two IRIS (e.g. Figeac, though ≥5 000) silently
   loses its income charts (upstream skips the chart when quantile bins
   collapse).
9. **Coverage**: DVF excludes Alsace-Moselle and Mayotte. Paris and Lyon are
   modelled as whole communes from their arrondissements (§3.7); Marseille could
   be added the same way.
10. **Building-less land in U zones is priced as building land.** Public open
    space zoned urban (Paris PLU *UV*: parks, cemeteries, sports grounds; Lyon
    PLU-H *USP* public-service land) and vacant *industrial-zone* land (*UEi*)
    take the residential terrain-à-bâtir €/m². `audit_land.py <commune>`
    quantifies the levy this land carries per zoning label.
11. **Nominal price pooling (2021–2025).** DVF sales enter the hedonic and the
    terrain-à-bâtir price base at nominal prices; the Notaires-INSEE index
    moved ~+7–8 % (2021), ~+5–6 % (2022), ~−2 % (2023), ~−1 % (2024) — an
    ~8–10-point swing inside the pooled window, so cells whose sales cluster
    early get systematically different price levels than cells clustering
    late (spatially structured error, flagged by the project's founding
    review). The `deflator` hook in `fit_hedonic` awaits the cited index.
12. **Surface concept mismatch (gross vs habitable).** `floor_area` =
    footprint × storeys is a gross, walls-included (SHOB-like) surface, but it
    multiplies both a construction cost stated in €/m² SHON and a hedonic €/m²
    estimated on DVF `surface_reelle_bati` (habitable). Both value levels are
    overstated (order 10–25 % depending on building type) and the residual
    inherits the bias; the top-down §5 check partially absorbs it (numerator
    and denominator inflated together), euro levels on charts do not. Flagged
    by the founding review (PR #1); needs a documented gross→habitable factor.
13. **Exemptions are not modelled.** The REI produit is net of exemptions (new
    social housing under CGI art. 1384 A, the QPV abatement), and public
    buildings (mairies, schools, hospitals), religious buildings and permanently
    exempt farm buildings (CGI art. 1382) are TFPB-exempt in reality. Here they
    both absorb a share of today's produit (via their floor area) and pay the
    modelled LVT — overstating today's bill on exempt HLM and public property,
    deflating everyone else's (material in 93 and Paris), and moving the
    published category bars and every percentage change. Upstream's
    `exemption_flag_col` is supported and unused; BD TOPO `usage_1`/`nature`
    attributes could flag the obvious cases.
14. **DVF multi-local mutations.** Annex locals (Dépendance) and rows outside
    the commune keep their value in the mutation price but are excluded from
    the floor-area sum, overstating €/m² where annexes are common (rural
    houses) — a spatially structured upward bias the percentile trim does not
    remove (see `ingest.fetch_dvf` docstring).
15. **Raw-data caching is opt-in.** `run_commune --cache-dir` (or
    `LVTFR_CACHE_DIR`) caches raw downloads by URL hash, so batch runs are
    resumable; without it every run re-downloads from live endpoints that
    occasionally move (config.py's warning). There is no manifest (source, URL,
    fetch date, hash) yet, so runs are reproducible as commands rather than as
    data.

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
`grenoble`, `annemasse`, `sete`, `larochelle`, `paris`, `lyon` (plus every ring
member, by ASCII key, e.g. `boulogne-billancourt`). Territories:

```
python run_territory.py lyon-extra-muros --workers 4   # resumable batch
python export_web.py lyon-extra-muros                  # aggregate JSON
python audit_land.py paris                             # building-less land audit
```
 Flags: `--layers` (REI scope), `--no-dpe` (BD TOPO year
only, for the depreciation comparison), `--no-report` (CSV only), `--cache-dir`
(reuse raw downloads; makes reruns resumable). On Windows set
`PYTHONUTF8=1`. Outputs land in `output/<commune>.csv` and
`output/reports/<commune>/*.png` (both gitignored).
