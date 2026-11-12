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
tax on land value alone (the TVTN, taxe sur la valeur du terrain nu), using
**open data only**. France never assesses land
and buildings separately, so per-parcel land value is **imputed**, with the error
bars made explicit. Results are reported by **property category** and **income
quintile**, never as individual bills.

Architecturally this is a fork of the US LVTShift toolkit: the FR code in
`lvtshift-fr/` manufactures LVTShift's expected input columns from French open
data and calls its *unmodified* solvers (`model_full_building_abatement` at
100 % for the land-only tax, `model_split_rate_tax` when a ratio is configured)
and export (`save_standard_export`). Upstream improvements flow through automatically.

## 2. Data sources

| Datum | Source | Access | Vintage | Role |
|---|---|---|---|---|
| Parcels | Cadastre Etalab | GeoJSON per commune | latest | geometry, official area (`contenance`) |
| Transactions | DVF géolocalisé (Etalab) | CSV per commune | 5 rolling years | hedonic market value; terrain-à-bâtir comparables |
| Buildings | BD TOPO V3 (IGN) | WFS `BDTOPO_V3:batiment`, commune bbox | current | footprint, storeys, height, dwellings, usage, FF-match flag |
| Construction era | DPE logements existants (ADEME) | data-fair API by `code_insee_ban` | since 07/2021 | depreciation (period band → year) |
| Zoning | GPU `zone_urba` (IGN) | WFS, commune bbox | current PLU/PLUi | constructibility (U/AU vs A/N) of building-less parcels; A/N test for exempt farm buildings (§3.5) |
| Agricultural prices | SAFER « Le prix des terres » | départemental table (config) | 2025 edition (2024 sales) | non-constructible land €/m² |
| Building-plot fallback | EPTB (SDES) | national figure (config) | 2023 | constructible €/m² when local comparables are thin |
| Tax target | REI foncier bâti, via OFGL | Opendatasoft API by `idcom` | latest | exact revenue-neutrality target (`MONTANT RÉEL`) |
| Unbuilt-land tax replaced | REI (DGFiP), via OFGL `rei`: `B11`, `B13`, `B31`, `B33` (TFPNB bases and amounts), `B11TAFNB`, `B13TAFNB`, `B31TAFNB`, `B33TAFNB`, `B31MGPTAFNB`, `B33MGPTAFNB` (TAFNB) | Opendatasoft API by `idcom` | REI 2025 | non-agricultural TFPNB and TAFNB that the reform replaces (§3.5) |
| Today's-tax split | REI (DGFiP), via OFGL `rei`: `E11` (TFPB base), `WC75` (compensation for the 2021 industrial halving), `T29`, `T29_1`, `X503` (CFE gross bases); OFGL `base-fiscale-simplifiee` 2020 TFPB rates | Opendatasoft API by `idcom` | REI 2025; rates 2020 | per-commune industrial / professional / housing shares of the TFPB base (§3.5) |
| IRIS geometry | IGN IRIS contours | WFS `STATISTICALUNITS.IRIS:contours_iris` | current | parcel → IRIS for income join |
| Income | INSEE Filosofi | CSV zip (`DISP_MED21`) | 2021 (see §6.8) | distributional (quintile) analysis |
| Exempt public property | DGFiP « Fichiers des locaux et des parcelles des personnes morales » | yearly zips via the data.economie.gouv.fr catalog | situation 2025 | flag obviously TFPB-exempt public property; parcels held by social landlords (§3.5) |
| Social dwellings | SDES RPLS, « Données détaillées au logement » | DiDo API by `DEPCOM` (row count, then CSV of 13 columns) | 1 January 2025 | social dwellings' financing, dates, convention, QPV and coordinates: today's exemptions and abatement (§3.5) |

All Licence Ouverte / Etalab. Exact endpoints live in `config.DATA_SOURCES`. The
RPLS also carries diffusion rules (décret 2009-1485, restated in its dictionary):
no statistic identifying a landlord, no figure on fewer than 11 dwellings below
commune level, no redistribution of the rows. The rows stay in the local download
cache; only commune-level aggregates are published (§3.5).

## 3. The pipeline and formulas

Spatial work is done in RGF93 / Lambert-93 (EPSG:2154). `cell` = a 400 m grid
square (a transparent hedonic fixed effect, not an admin geography).

**3.1 Building (improvement) value** — depreciated replacement cost, summed to
the parcel (`estimate.improvement_value`):

```
floor_area     = footprint_m2 × storeys          (storeys imputed by building type if missing)
habitable_area = net_to_gross[type] × floor_area            (flats 0.64, houses 0.61)
cost[type]     = house_cost_eur_m2 for houses where set, else construction_cost_eur_m2
                 × cost_ratio[building type]             (1 for housing; table below)
cost_hab       = cost[type] ÷ cost_net_to_gross[type]             (flats 0.71, houses 0.82)
age            = reference_year − year_built
q              = median hedonic €/m² of the built parcels in the parcel's IRIS
                 ÷ construction_cost_eur_m2   (commune median if the IRIS has none)
w              = clip((q − 1.2) / (2.5 − 1.2), 0, 1)          (dep_q_ramp; housing only)
eff_age        = w × min(age, 30) + (1 − w) × age             (dep_maintained_age_cap)
depreciation   = clip(1 − (1 − floor[bt]) × eff_age / life[bt],  min = floor[bt])
imp_value      = habitable_area × cost_hab × depreciation
market_value   = hedonic €/m² × habitable_area                (§3.3)
```

`year_built` is taken from DPE for housing (§3.2); `construction_cost_eur_m2`,
`house_cost_eur_m2`, `dep_years`, `dep_floor` are per-commune config (§4); `type`
is the parcel's dominant `type_local` (types other than flat and house use the
flat area ratios); `bt` is each building's type (below), whose life and floor
are `dep_years` and `dep_floor` for housing. Parcels valued by depreciated
replacement cost (DRC: sheds and the like, §3.4) never meet a DVF price, so their
building value stays on the model's floor area at the cost per gross m²: there
is no habitable-area conversion for them.

*Non-residential building types* (`estimate.building_type`,
`config.BUILDING_TYPES`). Each BD TOPO building is typed from its usage and
nature. Each type's cost is a ratio to the commune's collective-housing cost
(`construction_cost_eur_m2`), and each type has its own economic life and
depreciation floor:

| Type | BD TOPO rule | Cost ratio | €/m², Paris inner ring | Life | Floor | Valuation |
|---|---|---|---|---|---|---|
| Shed (logistics, industrial) | nature « Industriel, agricole ou commercial » (IAC), unless a row below applies | 0.250 | 600 | 40 y | 15 % | DRC, business land |
| Workshop | usage Industriel, other natures | 0.354 | 850 | 40 y | 15 % | DRC, business land |
| Retail box | IAC × « Commercial et services » | 0.467 | 1 120 | 40 y | 15 % | DRC, business land |
| Office | other natures × « Commercial et services » | 0.825 | 1 980 | 60 y | 20 % | residual |
| Farm shed | usage Agricole (when not exempt, §3.5) | 0.073 | 175 | 30 y | 10 % | DRC, business land |
| Greenhouse | nature Serre (when not exempt) | 0.081 | 195 | 25 y | 10 % | DRC, business land |
| Sports hall | usage Sportif | 1.033 | 2 480 | 50 y | 20 % | DRC, building land |
| Annex (garage, store) | usage Annexe | 0.227 | 545 | 50 y | 20 % | DRC, building land |
| Religious | usage Religieux | 1 | 2 400 | 80 y | 25 % | residual |
| Housing | everything else | 1 | 2 400 | 80 y | 25 % | residual |

The ratios come from one commercial cost guide that covers every type on a
single basis (Quostra, January 2026 €, cross-checked against logistics,
farm-building, greenhouse and garage figures). Each type's guide cost, run
through geographic coefficients, fees and the BT01 index, is divided by the same
guide's social-housing line run through the same chain. The type thus keeps the
guide's proportion to housing but inherits the model's lower, official-data
housing level (`docs/research/construction-costs-2025.md`); the unanchored guide
figures are 15–30 % higher. **Business types exclude VAT**, because firms recover
it: RICS's DRC guidance allows for VAT "only where this is an irrecoverable
cost". Sports halls are effectively VAT-free too, since communes recover it
through the FCTVA. **Annexes include VAT**, like the house they serve. Because
the anchor is one guide scaled to our housing level, treat the ratios as ±25 %.
Lives and floors are judgement, bracketed by fiscal *durées d'usage* (20–50
years), component lives (structure 50–80 years) and greenhouse glazing (20–30
years). The floors sit below housing's 25 % because sheds suffer functional
obsolescence (clear height, floor loading, dock ratio) that maintenance cannot
cure. Evidence: `docs/research/nonres-valuation-2025.md` §2–3 and
`docs/research/nonres_costs_calc.py`.

*Ages of non-residential buildings.* DPE diagnoses dwellings, so DPE years and
the DPE commune median now date housing only. A non-residential building keeps
its own BD TOPO year if it has one; otherwise it is taken at **mid-life**
(depreciation factor (1 + floor) ÷ 2, e.g. 0.575 for a shed), not at the
dwellings' median age. The maintained-stock rule below is a housing-market rule
and leaves non-residential buildings on their age.

*Habitable-area basis.* DVF prices are per m² of habitable area
(`surface_reelle_bati`), while `floor_area` is BD TOPO footprint × storeys.
Measured on 35 communes (DPE habitable surfaces matched to BD TOPO buildings by
their RNB id, area-weighted), habitable ÷ `floor_area` is **0.64 for flats
(0.59–0.68) and 0.61 for houses (0.58–0.66)**: BD TOPO counts attics, raised
basements and technical levels as storeys, so `floor_area` overstates even the
true gross area. Both sides of the residual are therefore put on habitable area
(`estimate.habitable_basis`, `market_value`). Construction costs are quoted per
m² of true gross area (§4) and become a cost per habitable m² by dividing by
`cost_net_to_gross`, the habitable ÷ true gross ratio the cost calibration
assumed: **0.71 for flats** (surface utile ÷ gross 0.74, ÷ surface utile ÷
habitable ≈ 1.04) and **0.82 for houses** (desk estimate). For a built parcel the
land share is then 1 − cost_hab × depreciation ÷ price per m²: it depends on
`cost_net_to_gross`, not on the measured `net_to_gross`, which only sets the euro
levels. Evidence: `docs/research/net-to-gross-measurement.md` and
`docs/research/construction-costs-2025.md`.

*Missing storey counts.* BD TOPO's `nombre_d_etages` comes from the fichiers
fonciers and is never filled for annexes, light structures or buildings that
could not be matched to them; a zero count is treated as missing too. Dividing
the height by 3 m, as the model first did, turns a 14 m single-storey warehouse
into 5 storeys: the Villepinte exhibition hall (165 000 m² of footprint) became
828 000 m² of floor. In six sample communes (Villepinte, Vaujours, Santeny,
Périgny, Rungis, Corbas) the count is missing on 42–56 % of sheds, 90 % of the
area of sheds with a known count is single-storey, and the old rule inflated
shed floor area 2.0–2.7×. `estimate.impute_levels` now imputes by type: **1
level whatever the height** for shed-type natures (« Industriel, agricole ou
commercial », Serre, Silo), light structures (`construction_legere`) and the
usages Annexe, Agricole, Industriel, Sportif and Religieux; **other « Commercial
et services » buildings** 1 level below 7 m, else height ÷ 3.5 m; **housing**
height ÷ 3 m as before (measured 2.65 m per storey). Known counts are kept. Floor
area also allocates today's TFPB within each tax group (§3.5), so the fix lowers
non-residential building values and changes how today's tax is spread between
buildings. Evidence:
`docs/research/nonres-valuation-2025.md` §1 and `docs/research/nonres_probes/`.

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
q deliberately keeps the basis its ramp was calibrated on (habitable price ÷ cost
per gross m²): restating it per habitable m² would silently retune the rule. For
the same reason q always uses the commune cost, houses included. It falls
slightly with the recalibrated (higher) costs.

Buildings join parcels by **area-weighted
intersection** (a building straddling a boundary credits each parcel by overlap
share), not centroid.

*Property categories* (`run_commune.derive_parcel_category`). Each parcel takes
the category of its largest building by floor area (storeys imputed as above).
Non-residential usages map directly: « Commercial et services » to commerce,
« Industriel » to industrial, and Agricole, Annexe, Religieux and Sportif to
« Autre bâtiment ». A residential or undifferentiated building is classed by
its BD TOPO dwelling count, area-shared across parcels: 2–4 dwellings is a small
building, 5 or more a large one, at most one a house. Three guards apply:
- **A recorded 0** (the fichiers fonciers hold no dwelling in it) goes to
  « Autre bâtiment ».
- **At most one dwelling on more than 500 m² of BD TOPO floor area**
  (`MAISON_MAX_FLOOR_M2`, about 300 m² habitable at the houses' 0.61 ratio) also
  goes to « Autre bâtiment »: offices, mixed use or an unreliable count, not a
  house.
- **No count** (a building unmatched to the fichiers fonciers) is a house below
  3 storeys and 500 m², and otherwise flats at 85 m² gross per dwelling, the
  households sidecar's rule.

Until November 2026 a missing count summed to zero, so every unmatched building
became a house whatever its size. In Paris, "house" parcels with buildings worth
over €1.5 M were a fifth of the category and carried 80 % of its tax (Lyon 67 %,
Villeurbanne 62 %, Montreuil 47 %), so the published house figures mostly
described them. The category sets the price surface (house or flat €/m², §3.3)
and the published group. Today's tax follows building use, not category (§3.5).

**3.2 Construction year (depreciation anchor)** — BD TOPO's `date_d_apparition`
is a database first-appearance date, not a build year, and is often null (100 %
of Cahors). We instead use the DPE `periode_construction` era band, mapped to a
midpoint year (`avant 1948`→1930, `1948-1974`→1961, … `après 2021`→2022),
spatially joined to parcels (per-parcel median). Parcels with no DPE point take
the **commune dwelling-weighted median era** as a fallback, so age never
degenerates to "unknown". Both apply to housing only; non-residential buildings
without a year of their own are taken at mid-life (§3.1).

**3.3 Market value** — a deliberately simple log-linear hedonic on DVF
(`estimate.fit_hedonic` / `market_value`): cell×type median of log €/m², shrunk
toward the commune-type median (pseudo-count k = 8), × the parcel's habitable
area (`net_to_gross` × floor area, §3.1), the basis DVF prices are quoted on. DVF is
cleaned to `Vente` mutations, aggregated to the mutation, €/m² trimmed at the
1st/99th percentile. The five pooled years are first brought to 2025 euros
(next paragraph).

**Price deflator.** The five DVF years span a cycle (prices up to 2022, then a
correction), and by very different amounts by place, so each sale is first brought
to `reference_year` (2025) euros: factor(Y) = annual mean of the area's
Notaires-INSEE index in 2025 ÷ its mean in Y (`estimate.deflator_factors`,
`config.PRICE_INDEX_IDBANKS`, fetched live from the INSEE BDM). The most local
series INSEE publishes is used: Paris flats; flats and houses separately for
Hauts-de-Seine, Seine-Saint-Denis and Val-de-Marne; the Lyon, Marseille and Lille
agglomerations; regions (Auvergne-Rhône-Alpes, PACA, Nord-Pas-de-Calais); Province
elsewhere. Where an agglomeration publishes one dwelling type only, that series is
used for both types: pairing a local flats series with a regional houses series
would move houses against flats by the city-vs-region gap. Terrain-à-bâtir prices
are deflated with the area's house series. A 2022 Paris sale is scaled by 0.907,
a Lyon one by 0.865, a provincial flat by 0.996.

**3.4 Land value — classify then price** (`estimate.land_value_residual` →
`_land_value_classified`). Building-less parcels are classified by GPU zoning;
each class is priced against the right benchmark:

| Parcel | Land value |
|---|---|
| **Built** | **site value** (below): each IRIS's residual land (`market − building`, floored at the agricultural €/m², land share clipped to [0.15, 0.85]) is shared again by plot area and the zone's typical density; building at depreciated cost, value = land + building, no clip (`lv_flag` `built_site_value`) |
| **Built, largest building shed-type** (DRC) | terrain-à-bâtir €/m² × `activity_land_ratio` (business types) or × 1 (sports halls, annexes) × parcel area, floored at the agricultural €/m²; outside urban zoning only a yard of 3 × floor area takes that price. Market value = land + depreciated building; no residential price, no clip (`lv_flag` `built_drc`) |
| **Constructible vacant** (zone U/AUc) | DVF terrain-à-bâtir €/m² × area (cell median where ≥8 sales, else commune median, else EPTB national fallback) |
| **Constructible deferred** (AU/AUs) | as above × `au_strict_factor` (development deferred) |
| **Agricultural / natural** (zone A/N) | SAFER départemental €/m² × area; **outside the reform**: the parcel keeps today's TFPNB, takes no share of the new tax and leaves the published results (counted in `farmland_excluded_parcels`) |

Only DVF rows coded *terrains à bâtir* are trusted for constructible prices —
raw `valeur_fonciere/surface_terrain` is contaminated for other cultures because
mutations bundle buildings and several parcels.

**Depreciated replacement cost for shed-type parcels.** Warehouses, workshops,
retail boxes, farm sheds, greenhouses, sports halls and garage plots rarely sell
on their own, and the residential €/m² that the residual uses says nothing
about them. Parcels whose **largest building** (by floor area) is of one of
these types are therefore valued by depreciated replacement cost (DRC, the
French *méthode sol + construction*), the standard method for property with no
active market (RICS, *Depreciated replacement cost method of valuation for
financial reporting*, 2026, §3.1–3.2, fetched). The building is its
depreciated cost (§3.1). The land is priced at the parcel's local
terrain-à-bâtir €/m² (the same cell or commune price as constructible vacant
land) times `activity_land_ratio` for business types: **0.45** by default and
around Paris, **0.35** for Lyon, Villeurbanne and the Lyon ring. The ratios come
from open DVF land-only sales in 2023–24, classified by land use (MOS 2021 in
Île-de-France, the Métropole's business-zone polygons around Lyon): activity
land against residential land is 381 vs 658 €/m² in Seine-Saint-Denis (0.58,
n = 23), 282 vs 771 in Val-de-Marne (0.37, n = 20) and 0.29–0.40 in the
Métropole de Lyon (n = 80). RICS likewise prices DRC land at its prevailing,
not alternative, use (§7.12–7.14). Sports halls and annexes keep the full
building-land price (× 1.0): a garage plot sits among houses. Market value is
land + building, with no residential price and no land-share clip. The ratio
is published in each payload's provenance (`activity_land_ratio`).

*Yards outside urban zoning.* A shed on a farm-sized parcel in an A or N zone,
or on unzoned land, would otherwise price the whole field as building land: the
security review found a 10 ha farmland parcel valued at €16 M. There, only a
yard of **3 × floor area** (`DRC_CURTILAGE_FACTOR`; logistics plots run about
2–2.5 × the footprint, judgement) takes the building-land price, and the rest
is priced as farmland (SAFER €/m²).

*Offices* stay on the residual against the residential price surface, at their
own cost (0.825 × the housing cost): offices and shops do sell, and a
business-premises price surface from DVF is the better target (§6, item 7).
Religious buildings stay on the residual at the housing cost.

**Site value of built land** (`estimate.site_value_land`, `config.SITE_VALUE`).
- **The concept.** A land value tax taxes land as if vacant, at the use planning
  allows. Germany's Bodenrichtwerte are defined for the zone's typical type and
  intensity of use, and Baden-Württemberg's 2025 land tax is plot area × that
  value. NSW values land at its most valuable permitted use, and Denmark on the
  higher of actual and permitted floor area. Dye & England (Lincoln Institute)
  give the reason: the tax is neutral only if the taxable value does not depend
  on current use.
- **What the residual measures instead.** The residual is a current-use value:
  land = (price − cost) × floor area, so it follows the floor area that stands
  on the plot, and a low house gets a fraction of the land of a block on an
  identical plot. Tested on 8,591 DVF house sales in nine communes, the market's
  land under a house rises with plot area (elasticity about 0.46 within a
  400 m cell) and not with floor area; the residual's elasticities are about 0
  and 1.0 (`docs/research/site-value-2026-11/04-dvf-tests.md`).

The residual now only sets each IRIS's land total. Within the IRIS (the
commune, where there is none) the land of the built parcels valued by the
residual is shared again. Those are housing, offices and other buildings; the
shared pool excludes shed-type parcels (already priced on their plot, above),
exempt public property and parcels floored at the farmland value. The rule is:

```
weight  = effective plot × density ^ 0.5
density = reference floor-area ratio of the zone      (permitted use)
```

- **Reference density.** It is the 75th percentile of the realised floor-area
  ratio (model floor area ÷ plot) of the pooled parcels in the same PLU zone
  label (the zone type, then the commune, below 20 parcels). It stands in for
  permitted density, which is not open data in structured form. Individual-housing
  zones run 0.2–0.9 (Lyon URi1a 0.93, Villeurbanne URi1a 0.78, Cahors Ub 0.47),
  mixed and collective zones 1.4–6.6 (Paris UG 6.0, Lyon UCe2a 6.1).
- **Density at the square root.** German residential conversion coefficients
  have land per m² of plot rising 0.45–0.54 % per 1 % of floor-area ratio
  (WertR 2006, Anlage 11). Only the zone's density counts, never the
  plot's own (permitted use, decision of 2026-11-11): a house and a block on
  identical plots of one zone get the same land. Until then a parcel denser
  than its zone kept its own density, as lawful existing use (Denmark's
  "actual or possible" floor area), at the square root
  (`SITE_VALUE["density_rule"] = "max_own"` restores it).
- **Effective plot.** This is the plot area, capped at the commune's 99th
  percentile, with two corrections where the extra land is not building land:
  - *Natural and agricultural zones (A, N).* Only a yard of 3 × floor area
    counts, as for shed-type parcels. 84 % of Cahors's largest house plots lie
    there, and linear plot area gave them +149 %.
  - *Surplus land.* On any built parcel of a house-scale zone (reference
    below 1), whatever stands on it, area beyond twice the zone's median
    plot counts at a quarter. Vacant house plots sell for far less than
    proportionally more as they grow (EPTB: elasticity 0.45 at 477 m², 0.11 at
    2,000 m²; Combes, Duranton & Gobillon), and in DVF an extra m² of garden
    sells for 0.14–0.27 of a building-plot m². The rule does not apply in denser
    zones, where a large plot carries a large building; applied there, it moved
    land from blocks' plots to houses.
- **Building and market value.** The building keeps its depreciated cost, and
  market value becomes land + building, with no land-share clip. The site can be
  worth more than the floor-based market value of what stands on it: 11 % of the
  re-shared parcels in Cahors and 27 % in Villeurbanne.

The method is recorded in each payload's provenance (`land_value`).
`run_commune.py --land current` reproduces the residual at the existing density,
and `--site-elasticity` and `--site-ref-quantile` vary the two main parameters.

**What it changes** (figures from its introduction, under the 4:1 split rate
and the earlier own-density rule; see the results log for the land-only
tax). Land moves within each IRIS from dense buildings to low-density ones.
In Villeurbanne, for example:
- houses go from +21 % to +115 % in total;
- small 2–4-dwelling buildings go from 0 to +52 %;
- large blocks go from −1 to −13 %.

Income-fifth totals barely move, because IRIS land totals are kept. Household
medians fall, since most households live in blocks. The share of the levy that
changes payer about doubles (Villeurbanne 11.7 → 23.5 %). Effects in the other
communes are in §3.7.

**What it cannot be checked against.** Site value is not observed in sales of
built property, which price what stands on the plot, not what the zone allows.
The only direct evidence is the rare sale of a vacant building plot, and
teardown sales (a built parcel bought to demolish or rebuild), which open data
do not flag. Finding them would mean linking DVF to demolition and building
permits (SDES Sitadel). One check was run: the typical house's land per m² of
plot against the vacant building-plot price in the same commune. Where such
plots sell in numbers it is close: Montreuil €2,183 against €1,791 (published
residual €1,936), Roubaix €422 against €394. In Lyon, Villeurbanne and Cahors
the few building-plot sales are atypical and priced far below built land even
under the residual (Lyon €735 against €1,220 under the residual and €1,440 here),
so the check says nothing there. The typical house's land per m² moves little
(+1 to +28 %): the change falls mostly on large plots and on houses in dense
zones. The parameters (the square root, the 75th
percentile, the surplus and yard rules) come from German tables and French
plot-sale studies; none is estimated on French sales of built property.
Sensitivity (Lyon, Villeurbanne, Cahors):
- **Density elasticity.** At 0.3 or 0.7 instead of 0.5, the typical house goes
  from +85 to +53 % in Lyon (+69 % central) and from +72 to +39 % in
  Villeurbanne (+55 %).
- **Reference density.** At the median instead of the 75th percentile, the
  typical house is +65 % in Lyon and +50 % in Villeurbanne.
- **Everything else.** Across these variants, large blocks move by 1–8
  points, income-fifth totals by at most 2, and the share of the levy that
  changes payer stays between 20 and 25 %.

**3.5 Current tax (baseline)** — the exact REI FB produit, distributed
(`estimate.current_tax`) across **built parcels only**. TFPB is a built tax;
building-less parcels bear none of it (they pay the separate TFPNB, which the
reform replaces on non-agricultural land: *Unbuilt land* below). There
is no market-value tilt: the 1970 VLC is regressive against market value, so a
tilt would make the baseline less faithful to today's tax.

*Calibrated by tax group.* Within the built stock, the produit is calibrated per
commune to its official 2025 REI split between three groups of premises
(`config.BASELINE_MODEL`; evidence in `docs/research/tfpb-baseline-calibration.md`
§2, §3 and §9). No open source publishes a commune's TFPB base by category, so
`ingest.fetch_rei_baseline_split` rebuilds it from two REI lines:

| Group | TFPB base rebuilt as | Check |
|---|---|---|
| Industrial establishments (CGI art. 1499) | `WC75` ÷ (2020 commune + département TFPB rate). `WC75` is the State's compensation for the 2021 halving of industrial values; by law (LFI 2021 art. 29 III A 2) it equals the base lost × the 2020 rate, and the base lost equals the base that remains. Métropole de Lyon communes use the Rhône 2014 rate (11.03 %), as the article requires; Paris has no département line | A national run gives 5.7 % of the TFPB base, exactly the Cour des comptes figure (*Les taxes foncières*, 2023). The CFE industrial line (`X503`) agrees within a ratio of 0.6–1.13 |
| Professional premises (RVLLP, art. 1498) | 0.5 × the CFE gross base of professional premises (`T29_1`, else `T29 − X503`), × **2.5**. The 0.5 is the TFPB's 50 % deduction (CGI art. 1388), which applies to every built property; the CFE takes the full rental value | The CFE is an occupier tax, so vacant premises and occupiers outside the CFE drop out: nationally the raw proxy gives 8.6 % of the base against the Cour's 22 %. The scale of 2.5 calibrates it to that national figure. The published alternative is the local share implied by the 2017 taxe d'habitation, 1 − 0.5 × `J11`/`E11` (REI 2017) − 2 × the industrial share; the raw proxy (× 1.0) where that line is missing (`docs/research/tfpb-baseline-calibration.md` §9.5) |
| Housing and other | the rest of the base (`E11`) | — |

One TFPB rate applies to every category in a commune, so each group's share of
the base is also its share of the produit (up to the RVLLP lissage, under 0.1 %).
Both legal points were checked on Légifrance after an AI review (Gemini) claimed
the 50 % deduction covers housing only and that WC75 uses a 2017 rate; both
claims were wrong. Its point that the CFE proxy undercounts was right, and the
2.5 scale follows from it.

*Applying the shares* (`estimate.baseline_floor`, `estimate.calibrated_weights`,
`run_pipeline._baseline_weights`):
- **Floor area is grouped** from BD TOPO usage. Industrial = usage Industriel.
  Professional = Commercial et services, Sportif, and the ground floor of
  residential buildings whose secondary usage (`usage_2`) is commercial: shops
  below flats, found on 45 % of residential buildings in sampled Paris
  arrondissements, 5 % in Villeurbanne and under 1 % in Villepinte. Housing = the
  rest. Exempt parcels are left out.
- **The produit is shared** between the groups in the target proportions, and
  by floor area within each group. Each group thus gets a tax per m² relative to
  housing.
- **Industrial merges into professional** where it would pay less per m² than
  professional premises: such sheds are taxed as professional premises
  (warehouses), not as plants. Villepinte and Santeny are examples, at about
  0.42–0.46 × housing per m².
- **Caps.** Per-m² weights are capped at 5 × housing. Where the industrial and
  professional shares together exceed 75 %, both are scaled down to 75 %, because
  the national scale can overshoot in business-heavy communes (Rungis 77 %,
  Marcy-l'Étoile 84 %, Vaujours 93 %).
- **Fallback.** Missing or malformed REI data fall back to plain floor area,
  with a note. All 188 modelled communes are calibrated.
- **Published.** The method, the targets and the achieved shares are in each
  payload's provenance (`current_tax_baseline`). `run_commune.py --baseline
  floor` reproduces the old floor-area baseline as a sensitivity.
- **Alternative computed alongside.** Every run also shares today's tax a
  second time with the professional target at the local share implied by the
  2017 taxe d'habitation, 1 − 0.5 × `J11`/`E11` (REI 2017) − 2 × the industrial
  share (`ingest.fetch_th2017_housing_share`; the raw proxy, × 1.0, where the
  2017 share is missing or outside (0, 1): Sathonay-Camp only, whose 2017 line
  gives 1.11), under the same groups, merge rule
  and caps. It is stored in the households sidecar (`current_tax_low`), checked
  to be revenue-neutral on export, and published as `baseline_sensitivity`
  with its `low_source` (§3.7). The LVT bills do not change; only today's tax
  does. Until 31 October 2026 the alternative was the raw proxy (× 1.0); the
  2017 check (`docs/research/tfpb-baseline-calibration.md` §9.5) showed it far
  too low in cities.

Example weights per m², relative to housing: Saint-Fons industrial 1.30,
professional 0.91; Rungis 1.71 (industrial merged into professional); Vaujours
and Marcy-l'Étoile at the cap of 5. Paris's targets are 1.4 % industrial and
24.9 % professional; Lyon's 1.6 % and 27.2 %.

*Business pays more per m² than floor area implied.* We expected the floor-area
baseline to overstate what industry pays today. The official shares show the
opposite, for two reasons. Industrial values under art. 1499 include fixed plant,
not just the building. Professional premises were revalued to 2013 rents (the
2017 RVLLP reform), while housing is still valued on 1970 rents. So today's tax
on business is higher than floor area suggested, and the reform shifts more from
businesses to households than the floor-area baseline showed (§3.7).

**Exempt public property** (`exemptions.py`, spec 0003). CGI art. 1382-1° exempts
the property of the State, regions, départements, communes, their groupings and
public scientific / teaching / assistance bodies when it serves a public purpose
and yields no income. The DGFiP « personnes morales » files list every right a
legal person holds on each parcel and building unit, with the holder's INSEE legal
form (98.4 % of their parcel ids match the cadastre). They carry no exemption code
and no use, so ownership is a proxy and the rule errs towards under-flagging: a
parcel is exempt only when **every** holder of a right on its land and on every
building unit is a qualifying public body with full ownership, on its own territory
(a commune's or département's property elsewhere is only partly exempt, BOFIP
BOI-IF-TFB-10-50-10-10 §90/§250), with no condominium syndic, no lease (emphytéose,
bail à construction, AOT…), no dismemberment and no private or housing manager
(units of network operators such as ENEDIS substations, held in full ownership,
are ignored). Public land with **no**
building unit recorded is exempt only where the model also sees no building
(parks, woods, cemeteries); a building there (a concession such as the Stade de
France) stays taxable until corroborated. Exempt parcels bear no share of today's
produit and are left out of the LVT base, so the same levy falls on the taxable
parcels. In Paris this flags 3,099 parcels (1,362 built) carrying €91.6 M (5.0 %) of
the produit the baseline used to spread onto them. Owner names are read only to
recognise utilities and housing managers and are never stored or published.

*Non-profits are not excluded.* Only the public legal forms above qualify.
Associations, foundations, private non-profit schools and hospitals pay the TFPB
today, and the model taxes their land like any other owner's. The exceptions
that exist in law and are not modelled (worship buildings owned by associations,
among others) stay taxable (§6 item 11).

*What public property would pay.* The reform keeps today's exemption. If public
land were taxed like private land instead, it would pay, at the national scale
(INSEE end-2025, built land of general government 941 Md€,
`docs/research/yields-2026.md`): at today's equal-yield rate, 10.3 Md€ a year in
scenario 1 and 12.6 Md€ in scenario 3 with the IFI. Held at equal yield with
public land in the base, the S1 rate falls from 1.10 % to 0.95 %: public land
pays 9.0 Md€ and every other owner 13 % less. About three quarters of that public
land belongs to local authorities (75 % in 2019, INSEE table 8.200), so most of
that money would go from a commune or département to itself; only the State's
and its agencies' share, about a quarter, would be a real transfer to local
budgets. The INSEE figure also includes land under roads and networks. The
commune results do not show the value of exempt parcels: the standard export
sets it to zero.

**Exempt rural buildings** (`exemptions.rural_buildings`). CGI art. 1382 6°
exempts from the TFPB buildings permanently and exclusively used for agriculture
(greenhouses, barns, silos, stables); the land under them pays the TFPNB, outside
the modelled levy. The legal test is use, not ownership
(`docs/research/nonres-valuation-2025.md` §7, read via doctrine.fr; Légifrance and
BOFiP could not be fetched live). Open data cannot see use, so the model takes a
BD TOPO proxy. A building counts as rural when either
- its usage is « Agricole » **and** its nature is Serre or Silo, or its parcel
  lies in a PLU A or N zone; or
- it is a shed (« Industriel, agricole ou commercial ») with no usage recorded or
  « Indifférencié », in an A or N zone: BD TOPO often leaves farm sheds unlabelled.

An « Agricole » shed in an urban zone stays taxable (it may be a converted
workshop), and so do garden-centre greenhouses (commercial usage). Zoning is now
fetched once, before the buildings are filtered. Rural buildings are dropped
before valuation and before today's TFPB is shared out. On a mixed parcel
(farmhouse plus greenhouses) the farmhouse stays. A parcel holding only rural
buildings becomes unbuilt land and is priced like any other farmland (SAFER
agricultural / natural €/m², or its zone class, §3.4): it bears no TFPB today and
only its land value under the LVT, as other unbuilt land does. 156 modelled
communes have at least one rural building. In urban communes the N-zone rule
also catches outbuildings in parks (Vitry-sur-Seine 1.2 % of building footprint,
Villeurbanne 0.1 %); these are mostly public and largely exempt anyway. The
proxy cannot check actual agricultural use; the fichiers fonciers' exemption
codes would.

`--no-exemptions` turns off both the public-property and the rural-building
exemption and reproduces the unflagged run.

**Unbuilt land: the TFPNB replaced** (`ingest.fetch_rei_unbuilt_replaced`,
`estimate.unbuilt_tax`; decision of 11 November 2026, research in
`docs/research/tfpnb-2026-11/`). The reform replaces the tax on unbuilt land
other than farmland: the non-agricultural share of the commune's TFPNB and the
whole TAFNB (CGI art. 1519 I). Agricultural and natural land keeps its TFPNB,
outside the reform (§3.4). Until then the model held the TFPB alone constant,
so a building-less parcel paid 0 today and its land tax showed as a rise from
nothing; the national scenarios already assumed the replacement
(`docs/research/yields-2026.md`).

*The amount.* No source publishes the TFPNB by kind of land. The TAFNB is
assessed on cadastral groups 7 and 10–13 only (quarries, building plots,
amenity land, railways, sols; BOI-IF-AUT-80), so its base ÷ the TFPNB base
(`B11TAFNB + B31TAFNB + B31MGPTAFNB` over `B11`, or `B31` for the EPCI) is the
non-agricultural share of the base, and of the amount since one rate applies to
every group. Replaced = share × `B13` + share × `B33` + the TAFNB amounts
(`B13TAFNB`, `B33TAFNB`, `B33MGPTAFNB`), REI 2025, over the layers held neutral.
It joins the revenue held constant. Across the 188 communes it is €23.2 M
against €6,766 M of TFPB (median 0.47 % of a commune's TFPB, from 0.02 % to
2.9 %); the non-agricultural share has a median of 96 % (20 % at the lowest).

*Who pays it today.* The cadastral values behind this tax (tariffs per nature
and class, set in 1961) are not open data, so the amount is shared by area over
the ground that pays it: building-less parcels inside the reform (not excluded
farmland, not exempt public property), and the open ground of **houses** beyond
five ares outside zones A and N (parcel area − building footprint − 500 m²).
The administration treats a garden attached to a house as part of the built
property up to five ares; beyond, it is amenity land in group 11, taxed like a
building plot (BOFiP BOI-IF-TFB-10-10-40). The courtyards, gardens and parks of
collective buildings are dependences of the building and take no share. One
weight per m² applies across the commune, and the model prices vacant building
land at one €/m² per commune in most places, so nearly every vacant parcel in a
commune gets the same percentage change: it is a commune average, not a
parcel's result.

*Checked after an AI review (Gemini).* Its claim that the art. 1396 surcharge
on building land explained the large multiples did not hold: the surcharge
raises the commune's base but neither the EPCI's nor the TAFNB's, and none of
the 66 modelled communes with both bases shows a gap; where there is no EPCI
base (Paris and the inner ring) the most it could add is €0.3 M in all. A
warning is printed if a commune ever shows the gap. Its point that large
gardens also pay this tax was right, and material: houses' ground beyond five
ares carries a median of 37 % of the amount across the 188 communes (20–63 % in
the published territories), hence the garden share.
Its suggested double weight for building plots had no source and was not used.

*Results* (run of 11 November 2026). Vacant land inside the reform now has a
real change: its tax is multiplied by about 3.5 in Villeurbanne, 5 in Sète, 7 in
Montreuil, 14 in Lyon, 17 in Paris, 47 in La Rochelle and 60 in Annemasse, for a
median of €67 to €1,793 a parcel a year. Every other figure moves by under a
point, except houses' totals, which fall by up to 25 points where large
gardens now pay today (Paris +261 % → +236 %). The site shows rises of ×3 or
more as a multiple, with the bar cut at the edge of the scale.

`--no-unbuilt-tax` reproduces the run without it.

**Social housing** (`social_housing.py`; research in
`docs/research/hlm-2026-11/`). Today, CGI art. 1384 A (new builds and VEFA) and
1384 C (acquisitions) exempt conventioned social rental dwellings financed by a
prêt réglementé for 15 years from the year after completion or acquisition, 25
years when the financing decision falls between 1 July 2004 and 31 December 2026;
art. 1388 bis abates by 30 % the base of taxable HLM and SEM dwellings in a 2024
priority neighbourhood (QPV), for the tax years 2025 to 2030. The REI produit
excludes exempt and abated bases (`E11` is the base after them, `E13` the
cotisations issued), so the model shares today's produit over taxable floor only.
The reform ends both regimes: social landlords pay the land tax like every owner.

*Which parcels* (`social_parcels`). From the DGFiP « personnes morales » file, per
département: a company is an HLM body if most of its rows carry groupe 5
(« office HLM »; the code is recorded per row, and real HLM bodies have about
95 %), or it has an HLM legal form (5546/5646 SA, 5547/5647 coopérative, 7371
OPHLM), or it is a local EPIC (4140) named like a public housing office (the
Métropole de Lyon's OPH is coded groupe 9); an SEM if most rows carry groupe 6
or it has an SEM form. Intermediate-rent companies (In'li) are never social. A
landlord holds a building unit when it has a right whose holder pays the TFPB
(P, U, E, R, W), except full ownership of a unit someone else leases (a commune's
land under an emphyteutic lease to an office is the office's). An **estate** is a
parcel where the landlord holds units and the land.

*Which dwellings, which regime* (`dwelling_status`, `fetch_rpls`). The RPLS gives
one row per social dwelling, with coordinates but no parcel and no landlord. For
the 2025 tax year, a dwelling is exempt when it is conventioned (`CONV` = 1),
financed by PLAI, PLUS, PLS or other post-1977 aided loans (`FINAN_CODE` 10, 11,
13, 14, 49), and its clock started in 2010 or later (15 years), or from 2005 with
a convention dated between July 2004 and 2026 (25 years; for 2005–06 starts the
convention must date from 2005, since a convention can follow the decision by
months; without a convention date, from 2007). The clock is the completion year
(`CONSTRUCT`) for new builds and VEFA, and the year of entry into the landlord's
stock (`PATRIMOINE`) for acquisitions, except for **transfers between landlords**,
which carry no new exemption (art. 1384 C; the convention follows the dwelling,
CCH L. 353-4): an acquisition whose convention is more than 2 years older than its
entry is a transfer, and its clock is the later of completion and convention.
The first-letting year (`LOCAT`) is only the fallback without a convention date:
some landlords report the building's first letting ever, not its first social
letting. In Montreuil 1,167 apparent transfers by `LOCAT` were financed by loans
created after their `LOCAT` year (PLUS, since 1999), and 1,288 were conventioned
within 3 years of their entry: they are purchases, and exempt. PLA ordinaire
(`FINAN_CODE` 12) is never exempt in 2025: PLUS replaced it in 1999, so every
such decision predates July 2004 and its 15 years (20 with the environmental
bonus) ended by 2024. PLI (16) and PCL (17) are intermediate rents. A taxable
dwelling in a QPV (`PLG_QP24` « QN… ») is abated if it is conventioned or has
pre-1977 HLM financing (50–55, 99), which had the old art. 1384 exemption.

*Placing the dwellings* (`parcel_social`; sources_report §4). Each RPLS address
point goes to the nearest parcel where a social landlord holds units or land
within 30 m (96 % and 94 % of dwellings in Montreuil and Villeurbanne), otherwise
to the parcel holding it (nearest within 15 m). Address points often fall on a
neighbouring parcel of the same estate, so contiguous parcels of **one landlord**
(within 2 m) form an estate, and each estate takes the habitable-area-weighted
factor of its dwellings (0 exempt, 0.7 abated, 1 taxable). Neighbouring estates of
different landlords stay apart; a parcel of unknown landlord joins a touching
estate but never bridges two. On an estate the whole housing floor is social (an
SEM's only if its estate holds RPLS dwellings: SEMs are partly non-social); on
other parcels the social share is the RPLS habitable area over 0.72 × the BD TOPO
gross housing floor, capped at 1 (0.70–0.75 measured per estate), with the
parcel's own dwellings' factor. A parcel's housing floor then carries the weight
1 − share × (1 − factor) in today's tax (`estimate.current_tax`,
`hlm_tax_factor`), in the group calibration's housing total and in the achieved
shares; the produit lost to exemptions falls on the other taxable floor, as in
the REI. The reform's bills do not depend on it.

*Who bears the change.* The TFPB is not a recoverable charge (décret 82-955,
annex VIII) and conventioned rents are capped (CCH L. 353-9-3), so the change on
social housing falls on the landlord, a business. Parcels whose housing floor is
at least half social, and residential or annex by use, form the category
**Social Housing** (« Logement social (bailleurs) »), outside the residential set
and so outside every household and income figure. On other parcels, only the
private share of dwellings counts in the household weights. Category assignment
comes after valuation and does not change any value.

*Disclosure* (`export_web`). The Social Housing category, and the commune's counts
of RPLS dwellings exempt and abated today, are published only where at least 3
landlords hold its parcels and none carries more than 85 % of its tax, today or
under the reform (`MIN_SOCIAL_LANDLORDS`, `MAX_LANDLORD_SHARE`, the two rules of
French business statistics' secrecy); otherwise the category joins "Other". The
local run outputs keep a landlord key per parcel, for counting only: a hash of
the SIREN, which anyone with the public SIREN list could reverse, so it never
reaches a payload. No SIREN, name or RPLS row is published, and only
commune-level figures are. Comparing a folded commune's payload with the release
before social housing was modelled shows how many parcels left the residential
rows for "Other": a count of parcels, largely derivable
from the public DGFiP file, with no € or % figure attached (security review,
2026-11-04).

*Results* (run of 4 November 2026). Across the 188 communes, 1.11 M RPLS
dwellings, 98.8 % placed on a parcel; 22.7 % are exempt in 2025 and 29.7 %
abated, against a national estimate of 20–25 % exempt (`legal_report.md` §6.2).
Montreuil: 23.7 % of 18,755 exempt and 41.8 % abated; Villeurbanne: 25.3 % of
21,711 exempt and 21.2 % abated. In Montreuil the social parcels' share of
today's tax falls by 23 % (65 of them pay nothing today), the other parcels
making up the difference, and the category pays −4.2 % in total under the
reform: dense
estates gain from a land tax even once their exemptions end. The Social Housing
category is shown in 11 of the 13 published territories; in Cahors and Figeac it
joins "Other" under the disclosure rules. Taking social estates out of the
household figures makes the poorest fifth's total less favourable where they
house many of the poorest (Villeurbanne −6.1 % → −1.5 %, Montreuil −18.8 % →
−8.4 %): the estates' gain goes to their landlords. A category median now
counts a parcel paying nothing today as a rise, not as undefined (§3.7).

`--no-social-housing` reproduces the run without it.

**3.6 Solver: land only** — the reform taxes land alone (decision of
2026-11-11; until then a 4:1 split rate, land taxed four times the building
rate, was published). `run_pipeline.solve_reform` calls upstream
`model_full_building_abatement` with a 100 % abatement: one revenue-neutral
rate on land, buildings untaxed, exempt property and excluded farmland
outside. Land is the site value (§3.4), valued as if vacant at its zone's
typical density standing in for the density it permits, so two identical
plots of one zone in an IRIS pay alike whatever stands on them. Two traces
of current use remain: an IRIS's land total is still the residual of what
stands there (the market's only evidence of land value in built areas), and
sheds and warehouses take the business-land price by building type, where
permitted use would need the zone's dominant use (the CNIG `destdomi` field,
not yet fetched).
Setting `split_rate_ratio` to a number restores the split-rate model through
upstream `model_split_rate_tax`. Output is written by `save_standard_export`;
euro charts by `charts_fr` (currency-localised wrapper over the upstream
report).

*Decomposition* (`estimate.revalued_tax`, `export_web._steps`). Part of each
group's change comes from replacing a 1970 base, not from taxing land. An
intermediate bill, holding the same revenue as today, splits the change in
two:

1. **Housing at market values** (`revalued_tax`): today's built tax with the
   housing group's amount re-shared by taxable housing floor ×
   (hedonic housing price per m² of the parcel's location, `eur_m2`)^0.8,
   instead of taxable housing floor alone. (Not market value ÷ floor area:
   after the site-value step that is land + building, and a parcel valued at
   replacement cost carries its whole plot's land, so a shed would look like
   the dearest housing in town; independent review, 2026-11-12.) The
   pipeline checks that the same weights at an exponent of 0 give today's
   bills back. The floor of the industrial and professional groups keeps
   today's amounts, so a shop or plant keeps its bill unless it also holds
   housing floor:
   professional premises were revised in 2017, and the pending housing
   revision (RVLLH, LF 2020 art. 146, now due in the 2031 bases after LF 2026
   art. 106) neutralises each commune's housing base (art. 146 V.B).
   Exemptions and abatements stay as today; the unbuilt-land bill is
   unchanged. The exponent is below 1 because rents rise less than prices:
   gross yields fall from about 6.3 % to 5.2 % as prices rise from about
   €1,600 to €3,900/m² (Chapelle & Eyméoud, PLOS ONE 2022, table 6), a
   rent-to-price elasticity near 0.8. The IPP's simulation of the revision
   (rapport n° 29, 2020) assumes 1 within a commune. Gemini suggested 0.55
   without a source; we did not use it.
2. **The move to the TVTN** (the reform, `new_tax`, against bill 1), which
   includes the end of the social housing exemptions.

Both steps are published, per category and per income group, as a % of the
group's tax today, adding up to its total change (to rounding). A first
version also split off the end of the exemptions, with a bill that kept
them; it was dropped and is no longer computed: between that bill and the
reform every unexempt parcel's bill scales by one factor, which any row of
houses gave away, and with the published levy that factor yielded the euro
tax on exempt social housing, one landlord's or one parcel's in some
communes (security review, 2026-11-11). The steps are published only where the
run kept the tax groups (the calibrated baseline, every published commune);
on the plain floor-area baseline it would re-weight shops and industry too.
The exponent is in each payload's provenance (`rent_price_elasticity`).

The steps are totals, not medians, because only totals add up. A group's
steps are withheld with its total, or when one parcel carries more than a
tenth of the group's tax today, under bill 1 or under the reform (income
groups included). Each step is revenue-neutral across categories, but
weighted by the categories' taxes today, which are never published, so the
published rows cannot recover a withheld one, provided at least four
publish: a withheld group with no housing has a step 1 of exactly 0, and if it
is vacant land its tax today is about the published unbuilt-tax amount, so
with the published levy two published rows would close the equations
(security and independent reviews, 2026-11-12); with three, bounds from
non-negative taxes were still tight in a few test groupings, with four in
none. With a withheld row (one with neither a % nor a € total; a row in euros
is untaxed today and has no weight) and fewer than four publishing, no
category's steps are published.
The payload guard checks it. The social landlord rule is
tested on bill 1 as well.

What the first step is not: our "today" is itself a floor-area estimate
(§3.5), with no location or comfort element, whereas the 1970 values carry
category and situation coefficients. The step measures the move from shares
by size to shares by value within housing, a stand-in for the revision, not
a simulation of it. The IPP found the revision would lower the poorest
decile's dwellings by 5.6 % and raise the richest decile's by 9 %
(20 large urban areas, outside Paris), an order of magnitude to check ours
against. Docs: `docs/research/revaluation-2026-11/`.

**3.7 Paris, Lyon and the inner rings** — Paris (75056) and Lyon (69123) levy
the TFPB as one commune, but cadastre, DVF, DPE and IRIS are published per
arrondissement (75101–75120, 69381–69389). A config carries both: `insee_code` is
the fiscal code REI is keyed on, `sub_codes` the data codes. Every fetcher loops
the data codes (spatial fetches one arrondissement bbox at a time, so a boundary
building is credited only to the parcels it overlaps), the frames are stacked into
one commune, and **one** revenue-neutral land tax is solved for the city — as the
real levy has one rate. DPE records filed under the city code are also pulled.

The **extra-muros territories** — *Paris extra-muros* (all 122 communes of 92/93/94)
and *Lyon extra-muros* (the 57 other communes of the Métropole de Lyon; membership
frozen in `territories.py`) — are **not** a metropolitan tax. Each member is run on
its own REI produit and held revenue-neutral on its own (`run_territory.py`, one
process per commune); `export_web.build_territory_payload` then pools the
per-parcel results into aggregates. The sensitivity band is re-solved commune by
commune, each on its own levy, before pooling; income quintiles
are ranked across the whole ring. A member that fails is listed in the payload's
`coverage`, never imputed. Montreuil and Villeurbanne appear both alone and in
their ring; the site's panel totals count them once.

**Sensitivity band.** Because land value is imputed, every published figure carries
a band. Under a land-only tax, scaling every parcel's land by one factor changes
no bill, so the split-rate model's band (land share ±10 points, each parcel's
land and building scaled uniformly; `export_web._tilted_change`, kept for
split-rate runs) would show no uncertainty. The land-only band shocks what
moves the shares: building values ±20 % (`config.BUILDING_COST_BAND`, spanning
the cost research's ranges and the habitable ÷ gross ratio). Building cost
enters land through the residual of built parcels, summed by IRIS before the
site-value sharing, so each IRIS's residual land total becomes L − 0.2 B (or
L + 0.2 B), clipped to [0, L + B], and every parcel the residual priced moves
by the same factor. Only those parcels move, pooled as the site value pools
them (by IRIS, else the whole commune; both recorded in the households
sidecar): building-less parcels, priced from plot sales, parcels valued at
replacement cost (sheds, retail boxes) and parcels floored at the farmland
value do not (`export_web._cost_shocked_land`; code review, 2026-11-12). Each
leg re-shares each commune's levy and reports the land share it implies. The
shock is applied to the exported land values, not by re-running the
site-value step: parcels clipped to the land-share bounds move with their
IRIS total though, re-run, they would stay at their bound; where most of an
IRIS sits at the lower bound, the +20 % leg can take its residual land to
zero. Two cases outside the published runs pool more than the model does:
`--land current` (no site value: each parcel's land is its own residual, so
the right shock would be per parcel) and the few residual parcels the
site-value step leaves out of its pool (no plot area or building cost). The
band does not cover the within-IRIS sharing of land by permitted density
(exponent 0.5), now the main uncertainty on relative land values (Gemini
review, 2026-11-11; `docs/research/land-only-2026-11/`). The band is
reported for the headline figures **and** for each property category and income
quintile (and, on the rings, the within-commune quintiles), using the same quintile
cut points as the central estimate; the site draws it as whiskers on those charts.
The central leg reproduces the published figures exactly (tested). A conclusion is
treated as robust only if it holds across the band. The band holds today's-tax baseline fixed. The baseline's own
uncertainty, the professional-premises scale (§3.5), moves household results
far more than the band does. It is published separately, as a local
alternative shown beside the central case (§3.7, §6 item 1).

**Income groups: totals and households, not parcel medians.** Each income
quintile (parcels ranked by their IRIS's Filosofi median income) carries three
figures, all on residential parcels: the **group total** (Σ new tax ÷ Σ current
tax − 1), the **typical household** (the parcel changes' median weighted by
dwellings, so a 200-flat block counts 200 times) and, for reference, the plain
**parcel median**. The site draws the total as the bar and the household as a
marker. The parcel median misleads where poorer areas mix many small houses
with a few large blocks: in Villeurbanne the poorest fifth's median parcel pays
+4.6 % while the group as a whole pays −6.1 % and its typical household −19.7 %
(central baseline), because the large blocks, where most of its households live,
gain the most.
Dwellings come from BD TOPO `nombre_de_logements` (area-shared across parcels);
residential parcels without a count are imputed (a house = 1; flats = gross floor
area ÷ 85 m²), which concerns 5–11 % of residential parcels in Paris, Lyon and
Villeurbanne. The counts live in a local sidecar to the standard export
(`<commune>.households.csv`, row-aligned and checked against `new_tax`); only the
per-quintile totals are published. BD TOPO under-counts dwellings slightly
(Paris ≈ 1.14 M against ≈ 1.4 M in the census), which affects the weights, not
the totals.

**Category amounts in euros: per dwelling.** The same counts give, for each
residential category, the typical household's change in euros: each parcel's
change divided by its dwellings, median weighted by dwellings
(`median_change_eur_per_dwelling`, with the category's `dwellings`). The
parcel median in euros (`median_change_eur`) compares a whole block with one
house: in the October 2026 payloads, before site value, a Lyon block's median
change was +800 € against +267 € for a house, which read as flats paying three
times more when in percentage the block (+9.6 %) paid half what the house did
(+20.6 %). Per dwelling the gap reversed: +34 € in a block against +287 € in a
house. Since site value, a Lyon block's median parcel pays −720 € and its typical
dwelling −103 €, a house +769 € and +800 €. The site shows the
per-dwelling figure; without counts, it labels a building category's figure
"par immeuble". The chart's percentage remains a parcel median, so the two
figures can differ in sign, because large blocks weigh more in the
per-dwelling median (Roubaix, blocks: +7.2 % per parcel, −5 € per dwelling).
The disclosure rule is the income groups' rule: at least 11 parcels with
dwellings, every parcel counted, no parcel holding more than a tenth of the
dwellings (`MAX_DWELLING_SHARE`). It was half until November 2026: a
dwelling-weighted median lands on any building with 45 % of the dwellings unless
the rest are lopsided, which would have published that building's own change
(security review, 2026-11-03; nothing published was blanked by the change). The
same counts give each building category's share of dwellings paying more and the
typical household's change in % (`share_dwellings_paying_more_pct`,
`household_median_change_pct`), shown under the Résultats win/lose chart beside
the share of parcels. Each category also publishes its **total change**
(`total_change_pct`): medians can all fall while the levy is unchanged when a
minority pays much more (La Rochelle, houses: −5.4 % at the median, +14.7 % in
total). Vacant land, which pays no tax today and so has no %, publishes its total
in euros instead (`total_change_eur`, to the thousand). No category publishes
both: the reform is revenue-neutral, so the euro totals of a commune's
categories sum to zero, and a withheld euro total would be the others' sum
negated (security review, 2026-11-04). A % alone gives nothing to subtract,
since no category's tax today is published. A total is withheld when one parcel
carries more than a tenth of the category's tax, today or under the reform
(`MAX_PARCEL_TAX_SHARE`), since it would then be close to that parcel's own
change. A category's median % counts a parcel that pays nothing today as a rise
(or a fall) of unbounded size, rather than leaving it out: otherwise the
social housing exempt today, which all goes from 0 € to a land tax, would drop
out of its own category's median. Where the median itself falls on such a
parcel (vacant land, or an even split), no % is published and the euro median
shows instead.

**Paris's land share and the 85 % cap.** Under the original rule (straight-line
to a 25 % floor) a ~95-year-old, continuously maintained Paris building fell to
≈ €575/m² against a median DVF price of ≈ €10,860/m², so 95.5 % of built parcels
sat at the 0.85 bound and the 84.9 % headline was set by the cap. The
maintained-stock rule (§3.1) values such buildings at a 30-year effective age,
which brought Paris to 83.3 % with 34.8 % of built parcels still at the bound.
With both sides of the residual on habitable area, the calibrated costs and the
per-type non-residential valuation (§3.1, §3.4, §4), Paris comes out at
**75.3 %** with 3.6 % of built parcels whose residual sits at the bound: its
land share is measured, not set by the cap. No commune has more than half its
built parcels at the cap; Neuilly-sur-Seine has the most (19.0 %), and the
preflight `land_share_clip` check warns nowhere. Lyon is at 60.0 %, the Paris
ring 63.5 % and the Lyon ring 55.2 %. Across the 188 modelled communes, 37 lie
above 65 % and 2 below 40 % (Cahors 36.5 %, Limeil-Brévannes 39.2 %). Figures
are from the November 2026 site-value run; under site value the clip bounds
only the residual that sets each IRIS's land total, so a parcel's own share can
pass it. `headline.built_at_cap_pct` records the share of built parcels whose
residual is at the bound, and the site labels the land share "plafonnée" when it
is ≥ 50 %.

*The 40–65 % reference range.* It is a metro-wide benchmark (INSEE's national
balance sheet puts built land at 51 % of land + dwellings at end-2023, 44 % for
households alone), not a
test each commune must pass. Communes contiguous to Paris (itself 75 %)
naturally sit at 65–75 %, and land is 65–75 % of value in prime office
districts (Gemini review). Most of the 37 communes above 65 % are inner-ring
communes next to Paris (Puteaux 69.5 %, Saint-Cloud 75.3 %, Clichy 73.6 %,
Courbevoie, Nanterre, Montreuil, Pantin…); the register's WARN outside the
range is a prompt to look, not a failure.

*House costs.* The house cost moves land shares the way its sign predicts:
up around Paris, where houses are now cheaper to rebuild than flats (Paris
74.0 → 74.2 %, the Paris ring 60.6 → 61.7 %, Montreuil 62.5 → 63.7 %), down
around Lyon, where they are dearer (Lyon 58.6 → 57.8 %, the Lyon ring
55.4 → 52.6 %, Villeurbanne 54.2 → 52.5 %). Several affluent inner-ring
communes moved just over 65 % (Les Lilas, Vanves, Meudon, Puteaux and Malakoff
by under a point; Sceaux 66.3 %, Marnes-la-Coquette 67.3 %), while four
Monts-d'Or communes fell back inside the band (Saint-Didier, Saint-Cyr,
Collonges, Saint-Romain) and Fleurieu-sur-Saône fell from 75.3 to 71.7 %. It
only partly lifts the low outer-ring communes (Santeny 33.2 →
36.2 %, Vaujours 34.3 → 35.7 %, Limeil-Brévannes 35.1 → 37.4 %, Villepinte
37.4 → 39.4 %, Périgny 38.2 → 40.3 %): houses are only 18–36 % of their building
value, which is dominated by industrial and commercial parcels valued at the
housing cost and the flat price (§6, item 7).

*Storey counts.* The type-based storey rule (§3.1) leaves Paris (74.2 %) and Lyon
(57.8 %) unchanged and lifts the rings (Paris ring 61.7 → 62.2 %, Lyon ring
52.6 → 53.0 %), most of all the warehouse and retail communes of the outer ring
(Santeny 36.2 → 40.4 %, Vaujours 35.7 → 39.0 %, Villepinte 39.4 → 42.8 %,
Tremblay-en-France 44.0 → 47.6 %, Périgny 40.3 → 41.8 %, Limeil-Brévannes
37.4 → 38.0 %). Communes below the band fall from 4 to 2; those above it rise
from 24 to 26 (Clamart and Collonges-au-Mont-d'Or cross 65 % by a fraction of a
point). Because today's tax is also shared out by floor area, warehouses now
carry less of it, and the amount shifted rises in the rings (Paris ring 20.6 →
21.7 % of the levy, Lyon ring 23.9 → 26.4 %). The income gradient is unchanged
in direction (Paris group totals: poorest fifth −19.8 → −20.0 %, richest
+16.2 → +16.1 %).

*Rural buildings.* Exempting farm buildings (§3.5) matters only where there are
many of them. Périgny, the greenhouse commune, moves most (41.8 → 47.9 %): about
half its building footprint was greenhouses and farm buildings. Mandres-les-Roses
60.0 → 62.1 %, Solaize 51.7 → 52.3 %, Santeny 40.4 → 40.8 %; every other commune
moves by less than half a point. The land shares of Paris (74.2 %), Lyon (57.8 %),
the Paris ring (62.2 %) and the Lyon ring (53.0 %) are unchanged. The share of
parcels paying more in the Paris ring falls from 67.6 to 67.4 %; in the Lyon ring
the amount shifted rises from 26.4 to 26.6 % of the levy and the share paying
more from 60.7 to 60.8 %. The band counts are unchanged: 2 communes below 40 %
(Limeil-Brévannes, Vaujours), 26 above 65 %. A few public parcels whose only
buildings were rural now count as unbuilt and join the exempt public land (Paris
ring 41,711 → 41,807 exempt parcels, Lyon ring 21,515 → 21,585).

*Non-residential valuation.* Per-type costs, lives and floors (§3.1) and DRC
valuation of shed-type parcels (§3.4) raise land shares everywhere, most of all
in the warehouse communes:

| Land share (land ÷ total), % | Before | After |
|---|---|---|
| Paris | 74.2 | 75.8 (5.6 % of built parcels at the cap) |
| Lyon | 57.8 | 60.0 |
| Paris ring | 62.2 | 65.3 |
| Lyon ring | 53.0 | 55.4 |
| Santeny | 40.8 | 52.1 |
| Vaujours | 39.0 | 49.8 |
| Tremblay-en-France | 47.6 | 58.3 |
| Villepinte | 42.8 | 49.5 |
| Périgny | 47.9 | 50.1 |
| Limeil-Brévannes | 38.0 | 41.7 |

Communes below 40 % fall from 2 to 1: Cahors, 41.2 → 38.0 %. Almost all of
the fall is commercial land (€197M → €83M): its edge-of-town retail sites now
take the town's building-plot price (median €38/m², 41 sales) instead of a
residual off flat prices, and a cheap-land small town is plausibly below the
metro-wide range. Pricing retail land at the full plot price rather than the
business-land ratio only moves Cahors to 39.0 %. Those above 65 % rise from 26 to 48, mostly inner-ring communes
next to Paris (see the reference range above). Gemini (gemini-4-argon) judges
these levels plausible. In the Lyon ring industrial land value falls from €8.6bn
to €3.8bn and industrial buildings from €8.5bn to €2.6bn. Category totals
there: industrial bills −3.5 → −55 %, commercial −7 → −17 %, houses −1 → +6 %;
the amount shifted rises from 26.6 to 38.3 % of the levy, and the poorest
fifth's total change from −13.5 to −3.7 %. In the Paris ring industrial bills
fall 31 %; "other" (garage and sports plots) rises 67 %, but that category is
only 1.4 % of today's tax. The Paris income gradient is little changed (group
totals −20.1 … +14.9 %; Lyon −18.7 … +13.6 %). These figures were still on the
floor-area baseline; the calibrated baseline below replaces it.

*Calibrated baseline.* Calibrating today's tax to each commune's REI split
(§3.5) leaves every land share unchanged (Paris 75.8 %, Lyon 60.0 %, Paris ring
65.3 %, Lyon ring 55.4 %) and every new bill unchanged: only the starting point
moves. "Before" is the floor-area baseline; "central" scales the professional
proxy by 2.5; "local variant" takes the professional share implied by the 2017
taxe d'habitation (§3.5). The two published columns are the 31 October 2026
payloads; "before" and the raw proxy (× 1.0, the alternative until then) are
kept for the record.

| | Before (floor area) | Central (× 2.5) | Local variant (TH 2017) | Raw proxy (× 1.0), retired |
|---|---|---|---|---|
| Paris, income group totals Q1 … Q5, % | −20.1 −11.2 −4.2 +5.7 +14.9 | −17.4 −8.3 −1.3 +8.9 +18.9 | −6.0 +3.2 +10.6 +21.8 +36.1 | −27.6 −18.8 −12.1 −2.9 +3.9 |
| Lyon | −18.7 −8.5 −0.8 +3.2 +13.6 | −14.0 −3.5 +4.4 +8.5 +18.9 | −3.0 +8.2 +16.3 +20.6 +30.6 | −27.7 −18.2 −10.8 −7.0 +3.5 |
| Paris ring | −9.1 −5.0 −0.6 −2.7 +1.1 | −7.4 −3.0 +2.1 −1.2 +5.5 | +1.8 +4.8 +12.4 +11.9 +22.4 | −21.9 −16.9 −12.1 −12.6 −9.0 |
| Lyon ring | −3.7 +0.8 +5.0 −1.3 −4.7 | +0.7 +2.6 +11.0 +4.4 0.0 | +0.5 +6.3 +10.3 +4.0 +4.0 | −15.9 −11.4 −7.7 −12.1 −14.2 |
| Amount shifted, % of levy: Paris / Lyon / Paris ring / Lyon ring | 19.2 / 20.4 / 28.1 / 38.3 | 19.6 / 20.9 / 30.4 / 43.0 | 27.8 / 30.0 / 39.7 / 43.0 | 30.2 / 30.9 / 36.7 / 40.7 |
| Share of parcels paying more, %: same order | 50.2 / 70.8 / 68.6 / 69.3 | 52.8 / 74.5 / 70.5 / 70.4 | 67.1 / 78.5 / 74.5 / 67.7 | 42.5 / 51.5 / 56.2 / 58.4 |

By category, central case:
- **Lyon ring.** Industry's share of today's tax rises from 10.0 to 11.9 %, and
  commerce's from 15.0 to 16.6 %. Bills under the LVT: industrial −63 %,
  commercial −24 %, houses +13 %.
- **Paris ring.** Industry's share rises from 5.3 to 5.8 %. Bills: industrial
  −36 %, commercial −15 %, houses +18 %.

Local variant, median change by category: Paris houses +53.8 %, blocks
+10.5 %, commercial −34.2 %; Lyon houses +39.4 %, blocks +19.4 %, commercial
−30.2 %; Paris ring houses +27.1 %, commercial −32.1 %, industrial −53.7 %; Lyon
ring houses +8.7 %, commercial −24.2 %, industrial −65.8 % (central: Paris
houses +29.6 %, Lyon +20.6 %). The retired raw proxy had the opposite sign for
business: in the Lyon ring commercial bills +47 %, industrial −42 %, houses −6 %;
in the Paris ring commercial +77 %, industrial +1 %, houses +1 %.

*On the site.* Each commune and territory payload carries
`baseline_sensitivity`, with a central (× 2.5) and an alternative leg
(`low_source`: `th2017`, or `mixed` for the Lyon ring, where Sathonay-Camp
keeps the raw proxy): amount
shifted, share of parcels paying more, residential median change, categories and
income-group totals (territories also rank groups within each commune). The
results page shows the two side by side in the table "Incertitude sur la taxe
actuelle des locaux professionnels", after the land-share sensitivity table. The
LVT bills are identical in both columns; only today's tax differs.

**The professional share is the load-bearing uncertainty.** The local variant
moves household results by about 10 points the other way from the retired raw
proxy. On the 31 October 2026 payloads: Paris's poorest fifth −17.4 % central
against −6.0 %, Lyon's −14.0 % against −3.0 %, the Paris ring's −7.4 % against
+1.8 %; the Lyon ring barely moved (+0.7 % against +0.5 %). Since site value:
Paris −21.4 % against −10.6 %, Lyon −16.6 % against −5.8 %, the Paris ring
−12.6 % against −2.3 %, the Lyon ring −8.9 % against −8.6 % (within-commune
ranking for the rings). Under both published columns the gradient in
Paris and Lyon is progressive: the richest fifth pays most. Under the local
variant every income group in Paris and Lyon except the poorest pays more, and
business premises pay markedly less. The 2.5 stays the central case because it
is calibrated nationally; the local variant is calibrated commune by commune
but on 2017 data and a proxy read at ± 5 points (§6, item 1).

*Site value and the house classification (November 2026).* Every figure
above predates both: the house category then held large buildings with one
recorded dwelling or none, and built land followed the floor area on the plot
(§3.1, §3.4). On the payloads published since (central case; median change by
category, income-group totals, within-commune ranking for the rings):

| | Shift, % of levy | Houses | 2–4 | 5+ | Commercial | Q1 / Q5 totals |
|---|---|---|---|---|---|---|
| Grenoble | 35.7 | +48.6 | +12.2 | −30.8 | +6.9 | −46.6 / −4.1 |
| Annemasse | 25.0 | +97.3 | +22.8 | −21.1 | +8.1 | −12.3 / −4.0 |
| Villeurbanne | 23.5 | +54.7 | +24.8 | −16.8 | +45.9 | −6.1 / +3.5 |
| Roubaix | 29.1 | −15.5 | −14.7 | −27.2 | −16.0 | −26.9 / +43.9 |
| Cahors | 23.0 | +2.6 | −6.8 | −21.7 | −11.9 | — / — |
| Montreuil | 26.0 | +45.5 | +25.5 | −13.4 | +20.4 | −18.8 / +17.9 |
| Figeac | 26.2 | −0.3 | −11.1 | −30.9 | −11.4 | — / — |
| Sète | 26.0 | +30.8 | +1.2 | −28.0 | +29.0 | −16.5 / +11.1 |
| La Rochelle | 31.9 | −5.4 | −14.7 | −30.5 | −6.8 | −19.9 / +0.4 |
| Paris | 19.9 | +118.3 | +36.5 | −10.0 | +58.0 | −21.4 / +10.6 |
| Lyon | 22.4 | +69.2 | +23.2 | −8.0 | +5.0 | −16.6 / +15.4 |
| Paris extra-muros (petite couronne) | 27.3 | +31.0 | +13.5 | −21.9 | +20.2 | −12.6 / +6.8 |
| Lyon extra-muros (Métropole hors Lyon) | 31.1 | +32.3 | +2.6 | −24.9 | −27.9 | −8.9 / +6.6 |

- **Robust across the panel:** the poorest fifth pays less in every territory
  with income groups and fares better than the richest; large blocks pay less
  everywhere; industry pays much less.
- **No longer panel-wide:** the richest fifth's total falls in Grenoble
  (−4.1 %) and Annemasse (−4.0 %). Houses and small buildings pay more where
  they sit among denser buildings (Paris houses +118 %) and less where the
  housing stock is homogeneous (Roubaix, Figeac, La Rochelle).
- **The levy that changes payer** roughly doubles (Paris 9.8 → 19.9 %, Lyon
  10.5 → 22.4 %).

*Land only, at permitted use (run of 11 November 2026).* The figures above
are for the 4:1 split rate and for land valued with a plot's own density
where it exceeded its zone's. Taxing land alone, each plot at its zone's
density (§3.4, §3.6), on the payloads published since (same columns):

| | Shift, % of levy | Houses | 2–4 | 5+ | Commercial | Q1 / Q5 totals |
|---|---|---|---|---|---|---|
| Grenoble | 43.3 | +57.1 | +15.4 | −35.8 | +14.5 | −53.4 / −9.0 |
| Annemasse | 33.4 | +120.8 | +21.9 | −29.6 | +21.0 | −13.3 / −8.0 |
| Villeurbanne | 31.7 | +68.0 | +31.9 | −24.2 | +61.5 | +3.4 / −2.2 |
| Roubaix | 39.8 | −24.4 | −29.8 | −43.0 | −21.5 | −33.8 / +47.2 |
| Cahors | 36.6 | +14.2 | −10.7 | −35.0 | −34.2 | — / — |
| Montreuil | 33.2 | +51.5 | +23.8 | −30.6 | +34.5 | −9.5 / +12.6 |
| Figeac | 36.8 | −0.1 | −24.8 | −52.8 | −28.2 | — / — |
| Sète | 32.7 | +43.4 | +4.1 | −35.5 | +37.7 | −19.3 / +8.6 |
| La Rochelle | 37.6 | −4.8 | −18.8 | −39.1 | −4.5 | −11.9 / −3.5 |
| Paris | 23.0 | +118.8 | +36.6 | −14.2 | +68.2 | −24.9 / +7.0 |
| Lyon | 27.7 | +78.3 | +24.9 | −14.7 | +13.3 | −15.7 / +11.0 |
| Paris extra-muros (petite couronne) | 34.9 | +41.3 | +14.0 | −34.6 | +29.5 | −6.8 / +3.1 |
| Lyon extra-muros (Métropole hors Lyon) | 39.6 | +36.2 | −1.0 | −40.1 | −29.8 | −4.7 / +0.7 |

- **More progressive almost everywhere:** Paris's poorest fifth −22.3 → −24.9 %
  against the 4:1 run on the same data, Lyon −12.5 → −15.7 %, Grenoble
  −45.2 → −53.4 %; large blocks pay less everywhere, by more than before.
- **The one exception, Villeurbanne:** the poorest fifth's total rises 3.4 %
  (band +2.0 to +4.4 %) while the richest fifth's falls 2.2 %, carried by
  houses and small buildings (houses +135 % in total); its typical household
  still pays 21 % less, as most live in large blocks. So the poorest pay less,
  and fare better than the richest, in 10 of the 11 territories with income
  groups.
- **The levy that changes payer** rises again, to 23 % (Paris) – 43 % (Grenoble).

**Policy finding.** In the Lyon chemical and industrial corridor, the LVT
shifts tax from industry to households under the central baseline (Saint-Fons
industrial bills −60 %, Marcy-l'Étoile −90 %).

*Plant: a design decision.* The modelled reform taxes land only, so neither
buildings nor fixed industrial plant (this paragraph dates from the split-rate
model, under which buildings were taxed and plant was not). The project lead
took this decision, consistent with land-value-tax theory, which avoids
penalising capital investment. It needs no code change: art. 1499 values include
fixed plant, but the model's improvement value for an industrial parcel already
counts only the shed. To show how little the decision matters, a first-order
estimate (`docs/research/plant_effect.py`) adds the plant's revalued cost to the
improvement base (industrial base ÷ 0.03, gross or × 0.5 for depreciation, less
the model's building value) and re-solves the 4:1 split per commune (the
model then; under the land-only tax plant has no effect at all):

| Industrial bills vs today | Shed only (published) | With plant, depreciated | With plant, gross |
|---|---|---|---|
| Lyon ring | −63 % | −62 % | −60 % |
| Paris ring | −36 % | −36 % | −33 % |
| Marcy-l'Étoile | −90 % | −84 % | −76 % |
| Saint-Fons | −60 % | −59 % | −52 % |

Taxing plant would move industrial bills by only 1–3 points across each
ring, more in single industrial communes (Saint-Fons 8, Tremblay-en-France 12, Marcy-l'Étoile 14 at gross cost). Industry's cut is overwhelmingly the land shift:
cheap industrial land set against today's capital-heavy tax base.

**Disclosure rule.** Only aggregates are published, never a parcel. A published
group of fewer than 11 parcels (`export_web.MIN_GROUP_PARCELS`) is merged with a
neighbour: a building-share band with its smaller adjacent band, a property
category with "Other". Blanking alone would not do, since the commune total
minus the other groups would rebuild it. A group still too small (an income
fifth, "Other", a very small commune) keeps its count but none of its figures; a fifth in which one building holds more than a tenth of the dwellings,
or with fewer than 11 parcels holding dwellings, publishes no household figures. Bucket values in euros are rounded to the
thousand. `assert_aggregate_only` enforces these rules on export and on every
published file (CI test).

## 4. Key parameters and assumptions

- **Construction cost €/m²** (`construction_cost_eur_m2`): turnkey replacement
  cost of a modern equivalent building, 2025 €, per m² of true gross external
  area, building only (hors foncier, hors VRD), architects'/engineers' fees and
  20 % VAT included, developer margin excluded. Paris, the inner ring and the
  Lyon areas are calibrated on the DHUP/SISAL « Bilan des logements aidés »
  2021–22 building-only cost of new social housing, indexed to 2025 with INSEE
  BT01 (`docs/research/construction-costs-2025.md`): **Paris 2650** (plausible
  range 2350–3100), **inner ring 2400** (Montreuil and all of 92/93/94;
  2150–2700), **Lyon and Villeurbanne 2000** (1750–2300), **Métropole ring 1850**
  (1600–2100). The other panel communes keep pilot values on the SDES house-cost
  (EPTB) gradient: Grenoble/Annemasse 1900, Sète/La Rochelle 1850, Roubaix 1750,
  Cahors 1650, Figeac 1600. (Earlier pilots: Paris 2300, inner ring 2150, Lyon
  and both Lyon areas 1950.)
- **House cost €/m²** (`house_cost_eur_m2`): the cost applied to parcels whose
  dominant `type_local` is a house, on the same basis as above. The commune cost
  is calibrated on collective social housing, so in Paris, the inner ring and the
  Lyon areas houses are priced instead on the SDES survey of new individual
  houses (EPTB 2024, € per m² of surface de plancher: Île-de-France 1 863, Rhône
  2 127), indexed to 2025 (BT01 ×1.014), with finishing works ×1.06, fees,
  insurance and studies ×1.05 (×1.03 in the Lyon ring), a tight-plot premium
  (Paris ×1.20, inner ring and Lyon ×1.10, Lyon ring ×1.05), ÷ 0.90 habitable ÷
  SDP, then × 0.82 to true gross (`docs/research/house-costs-2025.md`): **Paris
  2300**, **inner ring 2100** (Montreuil and all of 92/93/94), **Lyon and
  Villeurbanne 2400**, **Lyon ring 2250**, i.e. per habitable m² 2800, 2550,
  2950 and 2750 (plausible ranges 2300–3400, 2100–3050, 2500–3450,
  2400–3250). Houses are cheaper than flats around Paris but dearer around
  Lyon, the opposite of the collective-housing gradient: EPTB's Île-de-France
  sample is mostly outer-département catalogue houses, while Rhône new builds
  are probably more bespoke (unverified). The Lyon figures deserve more caution;
  a cautious alternative for the Lyon ring is about 2080. The other panel
  communes keep their one cost (`house_cost_eur_m2` = None), as their pilots are
  already on the EPTB gradient. The maintained-stock trigger q keeps the commune
  cost (§3.1).
- **Area ratios** (by `type_local`; other types use the flat ratio):
  `net_to_gross` = habitable ÷ the model's floor area, measured: flats 0.64
  (0.59–0.68), houses 0.61 (0.58–0.66)
  (`docs/research/net-to-gross-measurement.md`); `cost_net_to_gross` = habitable
  ÷ true gross area behind the costs: flats 0.71, houses 0.82 (§3.1).
- **Depreciation**: straight-line over `dep_years` = 80, floor `dep_floor` = 0.25,
  on the effective age; maintained-stock cap 30 years (`dep_maintained_age_cap`),
  ramp q ∈ [1.2, 2.5] (`dep_q_ramp`). Both are judgement calls informed by the
  literature (§3.1); the cap and ramp end-points are not directly estimated.
- **Non-residential building types** (`config.BUILDING_TYPES`, §3.1): cost ratio
  to the commune cost, life and floor per type: shed 0.25, workshop 0.354 and
  retail box 0.467 (40 years, 15 %); office 0.825 (60 years, 20 %); farm shed
  0.073 (30 years, 10 %); greenhouse 0.081 (25 years, 10 %); sports hall 1.033
  and annex 0.227 (50 years, 20 %). Business types exclude VAT, annexes include
  it. Ratios ±25 %; lives and floors are judgement.
- **Business-land ratio** (`activity_land_ratio`, §3.4): business land for DRC
  parcels as a share of the local terrain-à-bâtir €/m²: 0.45 by default and
  around Paris, 0.35 for Lyon, Villeurbanne and the Lyon ring (open DVF, n ≈
  20–80). **Yard factor** (`DRC_CURTILAGE_FACTOR`): 3 × floor area outside
  urban zoning.
- **Land-share bounds**: [0.15, 0.85] — a design constraint, not a measurement.
  Where most parcels used to hit the upper bound (Paris, Lyon), the causes found
  were over-depreciation of old maintained stock and pricing habitable-area DVF
  prices on the larger BD TOPO floor area, not land genuinely above 85 %. With
  both corrected, no commune has more than half its built parcels at either
  bound (§3.7).
- **Site value** (`config.SITE_VALUE`, §3.4):
  - density elasticity 0.5 (German conversion coefficients, 0.45–0.54);
  - reference density at the 75th percentile of the zone label's realised
    floor-area ratio (at least 20 parcels, else zone type, else commune);
  - plot capped at the commune's 99th percentile;
  - surplus land beyond 2 × the zone's median plot at 0.25, on every built
    parcel of a house-scale zone (reference below 1), whatever stands on it
    (until 2026-11-11: on parcels below the reference only);
  - in A and N zones, a yard of 3 × floor area.

  Every value is a judgement informed by the sources cited in §3.4; none is
  estimated on French sales of built property.
- **Tax base**: land only (`split_rate_ratio = None`), since 2026-11-11; a 4:1
  split rate (land:improvement) before. A judgement call by the project lead,
  consistent with land-value-tax theory.
- **Building-cost band**: ±20 % (`BUILDING_COST_BAND`), the land-only tax's
  sensitivity; see the sensitivity band in §3.7.
- **Agricultural €/m²** (SAFER, by département, agricultural / natural): default
  0.64 / 0.49; Lot 0.45 / 0.35; Seine-St-Denis 1.00 / 0.60; Nord 0.85 / 0.50;
  Rhône 0.70 / 0.50; Haute-Savoie 0.75 / 0.55; Isère 0.60 / 0.45; Paris,
  Hauts-de-Seine, Val-de-Marne 1.00 / 0.60 (Île-de-France anchor; immaterial).
- **EPTB building-plot fallback**: 99 €/m² (national).
- **AU discount** (`au_strict_factor`): 0.55. **Hedonic shrinkage** k = 8.
- **Today's-tax baseline** (`config.BASELINE_MODEL`, §3.5): REI 2025, 2020
  TFPB rates (Métropole de Lyon: Rhône 2014 rate, 11.03 %); professional proxy
  0.5 × CFE gross base (CGI art. 1388) × **2.5** (central); alternative = the
  local share implied by the 2017 taxe d'habitation (`alt_source`, raw proxy
  × 1.0 as fallback), computed on every run and published beside the central
  case;
  per-m² weights capped at 5 × housing; industrial + professional share capped
  at 75 %.
- **Social housing** (`social_housing.py`, §3.5): tax year 2025, RPLS at
  1 January 2025, PM file 2025; exempt for 15 years, or 25 with a convention
  dated 1 July 2004 – 31 December 2026 (from 2005 for 2005–06 starts; without
  one, from 2007); QPV factor 0.7; a transfer when the convention is more than
  2 years older than the entry into the stock; groupe code by majority of rows;
  join within 30 m of a social parcel, else 15 m; estates within 2 m, one
  landlord each; habitable ÷ gross 0.72; Social Housing category from half the
  housing floor; published with at least 3 landlords and none above 85 % of the
  category's tax. The durations and the QPV rate are law; the rest are
  judgement calls checked on Montreuil and Villeurbanne (`docs/research/hlm-2026-11/`).
- **Unbuilt-land tax replaced** (§3.5): REI 2025 lines `B11`, `B13`, `B31`,
  `B33` and the TAFNB bases and amounts; shared by area over building-less
  parcels inside the reform and houses' open ground beyond 500 m² (five ares,
  BOFiP), one weight per m². The share method follows the law; the garden
  allowance is an administrative practice and the equal weight a judgement.
- **Rent-to-price elasticity** (`REVALUATION["rent_price_elasticity"]`, §3.6):
  0.8, from the fall of gross yields with price across French communes
  (Chapelle & Eyméoud 2022). 1 would treat a rental value as a capital value
  (the IPP's within-commune assumption); lower values flatten the first step.
  A judgement call on the only quantitative French evidence found.
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
  near INSEE's national balance sheet (44–51 % land at end-2023). Cahors came to ~53 % after
  the DPE construction-year fix (it was a degenerate 85 % before — see §6) and
  is at 38.0 % with the per-type non-residential valuation. The 40–65 % range
  is a metro-wide reference, not a per-commune test (§3.7).
- **Sign checks** — agricultural/natural land, outside the reform, bears none of
  the levy (1.1 % in Cahors before it was excluded); under-used constructible land pays *more* (the LVT
  incentive); the Montreuil income gradient is progressive (group totals,
  central baseline: poorest fifth −18.8 %, richest +17.9 %).
- **Today's-tax split** — the industrial reconstruction (WC75 ÷ 2020 rate),
  run on every commune in France, gives 5.7 % of the TFPB base, exactly the
  Cour des comptes figure; the CFE industrial line agrees commune by commune
  within a ratio of 0.6–1.13 (§3.5).
- **Tests** — `test_units.py` (offline unit tests of the pure logic) and
  `test_synthetic.py` (end-to-end through the real solver).

## 6. Limitations (consolidated register)

Ranked by how much they move published (category/quintile) results.

1. **Today's-tax baseline: the professional-premises scale (load-bearing for
   every distributional figure).**
   - **The professional scale.** Each commune's industrial and professional
     shares of today's tax come from its REI (§3.5). The industrial share is
     close to exact. The professional share is a CFE proxy scaled by one
     national multiplier, 2.5, because the raw proxy captures only about 40 %
     of the professional base nationally (8.6 % against the Cour des comptes'
     22 %). The published alternative is local: the business share implied by
     the 2017 taxe d'habitation (§3.5). It is higher than the central case in
     the cities, so households pay more: Paris's poorest fifth goes from −21.4
     to −10.6 %, Lyon's from −16.6 to −5.8 %, and Paris commercial bills from
     +58.0 % to +7.2 % (median change; §3.7). The reform's new bills are the
     same in both cases; only the starting point moves. The undercount is
     not uniform: it is larger where many premises are vacant or occupied by
     public bodies and associations, as in Paris.
     The site shows both side by side on every results page (table
     "Incertitude sur la taxe actuelle des locaux professionnels"); **always
     present both in any write-up too.** Per-commune professional values
     (Fichiers fonciers) are the real fix.
     **Independent check (2026-10-31).** The 2017 taxe d'habitation gives a
     second, local estimate: the housing share of the TFPB base is about
     0.5 × the TH gross rental value ÷ the TFPB base (REI 2017 `J11`, `E11`).
     Nationally it gives 32.7 % for business premises and industry, against
     about 32.4 % implied by the Cour des comptes. Locally it puts that share
     far above the raw proxy in every modelled city, and above the 2.5 case
     except in Figeac: Lyon ≈ 39 % (2025 basis) against 12.5 % (raw) and 28.8 %
     (central), Paris ≈ 39 % against 11.3 % and 26.3 %. Read ± 5 points per
     commune (vacancy, outbuildings, exempt social housing; 2017 data). The raw
     proxy, the case where homes in Lyon and Paris pay less, therefore looks
     implausible in cities; the central case may understate the shift onto
     homes. Since 31 October 2026 the raw-proxy column has been replaced by
     this local variant (§3.5, §3.7; `docs/research/tfpb-baseline-calibration.md`
     §9.5).
   - **Within each group** today's tax is still shared by floor area, which
     ignores cadastral category and weighted-surface coefficients, so read the
     **change**, not the starting bill, and never publish per-parcel amounts.
     BD TOPO usage decides the group; a shop not recorded as a secondary usage
     is taxed as housing.
   - **Plant is out of scope by design, not a limitation.** The modelled
     reform taxes land and buildings, not fixed industrial plant (the project
     lead's decision, in line with land-value-tax theory; §3.7). Art. 1499
     values include plant and the model's improvement value counts only the
     shed, so the model matches the decision. Taxing plant would move
     industrial bills by only 1–3 points (Lyon ring −63 % → −62 % depreciated
     or −60 % gross; up to 14 points in single industrial communes): the cut
     comes overwhelmingly
     from cheap industrial land.
2. **Built land: a site value that cannot be checked directly, on a residual
   total.**
   - **No direct check.** Site value (§3.4) cannot be checked against sales of
     built property; the only direct evidence is rare vacant building-plot sales
     and teardown sales, which are hard to identify in open data.
   - **Proxy parameters.** Permitted density is proxied by the zone's
     75th-percentile realised density, because PLU rules (heights, setbacks,
     heritage protections) are not machine-readable nationally. The square-root
     density term and the surplus and yard rules are borrowed, not estimated.
   - **Linear plot area elsewhere.** Outside the yard and surplus rules, land is
     linear in plot area: a large plot in a dense zone is valued as a building
     site even where its shape or access would not allow it. The largest-plot
     tenth of Villeurbanne's houses pays about five times today's tax
     (+394 %).
   - **Deferral.** Many such owners would need a payment deferral, which the
     project's reform includes (`/exonerations-protections`).
   - **What moves with these choices.** Category results for houses and small
     buildings move most. Income-fifth totals barely move: IRIS land totals
     are kept, but those totals are still the residual's.
   - **Residual amplification.** Building errors are amplified in the residual
     wherever buildings are a large share of value. This is mitigated by the
     [0.15, 0.85] clip, which applies when the IRIS total is formed, and by
     aggregation. It is made visible by the building-cost band
     (`headline_sensitivity`).
   - **Vacant land.** Vacant land does **not** use the residual, so the
     headline that under-used land pays more does not depend on building-data
     quality.
3. **Construction year.** From DPE (diagnosed *residential* dwellings → selection
   bias); the commune-median fallback applies to never-diagnosed housing.
   Non-residential buildings without a BD TOPO year are taken at mid-life, a
   neutral assumption rather than a measurement (the DPE tertiaire dataset is
   unchecked). Era→year uses band midpoints
   (mitigated for pre-1948 stock, which hits the depreciation floor regardless).
   A clear improvement over the prior degenerate baseline, but a documented
   generalisation.
4. **Construction costs and the area basis.** Costs for Paris, the inner ring and
   the Lyon areas are calibrated, with published plausible ranges (§4); social
   housing is a proxy for the private stock and will understate prime or
   listed buildings. Houses there have their own EPTB-based cost, whose
   least-sourced step is the finishing uplift (each ±4 points moves it ±4 %) and
   whose Lyon level rests on a sample that is probably more bespoke than the
   stock. The main remaining uncertainty is `cost_net_to_gross`
   (habitable ÷ true gross area), the least-sourced link: ±0.05 moves building
   value by about ±7 %, and that flows into the land residual. The measured
   `net_to_gross` sets euro levels only. The other panel communes keep
   uncalibrated pilot costs. Non-residential costs are ratios to the housing
   cost from one commercial guide (item 7). BD TOPO storey miscounts are the main source of
   parcel-level scatter in floor area; where the count is missing it is imputed
   by building type (§3.1), a judgement tested on six communes, and the 3.5 m
   storey height for tall commercial buildings has no primary source.
5. **Land-share clip**: when most built parcels sit at a bound, the land share is
   an assumption, not a result, and the parcel-level variation in building value is
   erased. Before the maintained-stock rule this was Paris (95.5 % at the bound),
   Lyon and 53 other communes. No commune now has more than half its built parcels
   at a bound; Neuilly-sur-Seine has the most at the cap (25.3 %), Paris 5.6 %
   (§3.7). The preflight `land_share_clip` check flags it. The effective-age cap
   (30 years) and ramp (q 1.2–2.5) are judgement calls; publishing a sensitivity
   on them is open (THEORY.md).
   Publish the unclipped distribution alongside (the pre-clip share is kept as
   `land_share_raw` in the parcel frame). Precedence when the agricultural floor
   and the clip conflict: the floor (a market observation) wins; such parcels are
   flagged `built_floored_ag` and their land share may legitimately exceed the
   bounds.
6. **Zoning nuance**: all AU treated constructible with a flat discount; `AU
   fermée` deserves a steeper cut and `Nh/Ah` pastilles are undervalued.
7. **Non-residential valuation.** Storeys are imputed by type (§3.1), farm
   buildings exempt under CGI art. 1382 6° are left out (§3.5), each building
   type has its own cost, life and floor (§3.1), and shed-type parcels are
   valued by depreciated replacement cost (§3.4). What remains:
   - **Costs** rest on one commercial guide scaled to our housing level, with
     no Moniteur, Untec or Chambre d'agriculture primary document reachable:
     ±25 %. Lives and floors are judgement.
   - **Offices** still take the residential price surface and the flat area
     ratios, at the office cost. A business-premises price surface from DVF
     (by size band, trimmed) is the better target; professionnels (2017 VLC
     revision) need a separate stratum.
   - **Mixed parcels.** The parcel's largest building decides its route: a
     parcel led by a shed is valued wholly at cost (any house on it included),
     and one led by housing or an office wholly by the residual (any shed on it
     at its own cost).
   - **The business-land ratio** (0.45 / 0.35) rests on n ≈ 20–80 sales a
     year per area, classified by current land use (MOS) or business-zone
     polygons, not by zoning. It is a prior, not a measurement. DRC land at
     prevailing use is a floor for an LVT, which wants the permitted use; the
     two coincide inside business zones.
   - **Yards** outside urban zoning (3 × floor area) are judgement.
8. **Income (Filosofi)**: 2021 vintage; INSEE published a « Filosofi 2 » 2023
   vintage with IRIS indicators in May 2026 (methodological break) — 2021 is
   retained pending evaluation. Communes ≥5 000 inhabitants only, some IRIS
   statistically suppressed. Quintiles additionally need ≥10 income-distinct
   IRIS, two per fifth (`export_web.MIN_IRIS_INCOMES`): below that a "fifth" is
   one neighbourhood, so Cahors (9) and Figeac (4) publish no income breakdown,
   and territory members below it are left out of the within-commune fifths.
9. **Coverage**: DVF excludes Alsace-Moselle and Mayotte. Paris and Lyon are
   modelled as whole communes from their arrondissements (§3.7); Marseille could
   be added the same way.
10. **Building-less land in U zones is priced as building land.** Public open
    space zoned urban (Paris PLU *UV*: parks, cemeteries, sports grounds; Lyon
    PLU-H *USP* public-service land) and vacant *industrial-zone* land (*UEi*)
    take the residential terrain-à-bâtir €/m² (built sheds there take the
    business-land ratio, §3.4). `audit_land.py <commune>`
    quantifies the levy this land carries per zoning label.
11. **Exemptions are only partly modelled.** Obviously exempt public property is
    flagged (§3.5), but deliberately conservatively: public units inside
    condominiums or under leases, worship buildings owned by associations,
    private non-profit schools and hospitals, the Assemblée and Sénat (unusual
    legal forms), out-of-territory partial exemptions and public buildings with
    no unit recorded stay taxable. Farm buildings (CGI art. 1382 6°) are
    identified from BD TOPO usage and PLU zoning, not from actual use: an
    unlabelled farm shed in an urban zone stays taxed, and park outbuildings in
    N zones are exempted (§3.5). Social housing's exemptions and QPV abatement
    are modelled since November 2026 (§3.5, and item 14); other temporary
    exemptions (new private builds' two years, local deliberations) are not.
12. **DVF multi-local mutations.** Annex locals (Dépendance) and rows outside
    the commune keep their value in the mutation price but are excluded from
    the floor-area sum, overstating €/m² where annexes are common (rural
    houses) — a spatially structured upward bias the percentile trim does not
    remove (see `ingest.fetch_dvf` docstring).
13. **Raw-data caching is opt-in.** `run_commune --cache-dir` (or
    `LVTFR_CACHE_DIR`) caches raw downloads by URL hash, so batch runs are
    resumable; without it every run re-downloads from live endpoints that
    occasionally move (config.py's warning). There is no manifest (source, URL,
    fetch date, hash) yet, so runs are reproducible as commands rather than as
    data.
14. **Social housing is modelled from a spatial join, not from the tax files.**
    The RPLS has no parcel and no landlord, so dwellings are placed by address
    point, and an estate's dwellings share one exemption factor: right in total,
    blurred between the parcels of an estate. The rule rests on proxies: the
    convention date stands in for the financing decision date (15 or 25 years),
    and for whether an acquisition was a transfer between landlords; RPLS
    reports the first-letting year inconsistently. Not observable: the 5-year
    environmental extension (art. 1384 A I bis), late declarations (art. 1406),
    local opt-outs (art. 1384 C III), and whether each landlord signed the QPV
    convention (all are assumed to have; REI `G211`/`G213` would calibrate it).
    The RPLS leaves out logements-foyers and résidences sociales: their parcels
    count as social when a social landlord holds them, at today's full rate.
    Mixed parcels (VEFA in a condominium) take a social share from the RPLS
    habitable area against the BD TOPO floor. Where that share is under half,
    the parcel stays residential and its whole change counts in the household
    figures, the landlord's part included (its lost exemption shows as a rise
    for the building's households). Such parcels carry 8–14 % of residential
    tax today in Montreuil, Annemasse and Villeurbanne; attributing only the
    private share to households would move an income fifth's total by 0.2 to
    1.4 points, mostly downwards, and flats' category total by under 1 point.
    Not corrected: it needs the landlord's part of each parcel's tax in the
    run outputs. MAJIC lags new builds by about a
    year, so some recent dwellings land on parcels with no social right. On
    State dégrèvements refunded to landlords after the rolls (art. 1391 E and
    C, about 4–5 % of HLM TFPB), the REI-based baseline slightly overstates what
    landlords pay. The Fichiers fonciers' exemption records would replace all of
    this (§7).

15. **The unbuilt-land tax replaced is a commune total shared by area.** Its
    split between parcels is not open data (1961 cadastral tariffs), so vacant
    land's percentage change is a commune average. Three known gaps. Cadastral
    groups are not PLU zones: a field zoned U pays the land tax in the model
    while its agricultural TFPNB is not in the amount replaced, and amenity
    land in an N zone is the reverse. Quarries and railway land also pay this
    tax and receive no share here. And many building-less parcels in towns are
    slivers, private roads or yards that may pay nothing today, so sharing by
    area over all of them understates what true building plots pay today and
    overstates their rise; the roll counts far fewer taxed accounts than the
    model has building-less parcels (La Rochelle: 820 accounts for all unbuilt
    land, 3,822 such parcels). The five-are rule for gardens is an
    administrative practice applied case by case, not a measurement. The
    Fichiers fonciers' per-parcel cadastral income would replace all of this
    (§7).

16. **The revaluation step is measured against an estimate of today.** Today's
    tax is shared by floor area (§3.5), so the first step of the
    decomposition (§3.6) is the move from size to value, not the true effect
    of revising the 1970 values, whose category and situation coefficients we
    cannot see. The price per m² is the hedonic housing price of the
    parcel's location: it does not see a dwelling's own quality, size class
    or floor, which the revision's categories and localisation coefficients
    would. A parcel holding a co-ownership counts as one. The Fichiers fonciers' per-local rental
    values would give the true starting point (§7).

## 7. The Fichiers Fonciers access argument

Each open-data compromise maps to a specific Fichiers Fonciers (CEREMA/DGFiP)
field that would resolve it: the VLC proxy (floor area calibrated to REI group
shares with a national professional scale) → real per-parcel VLC;
estimated building surfaces → declared surfaces per local; DPE-inferred era →
exact construction year; the spatial building↔parcel join → native MAJIC links;
no owner typology / vacancy / exemptions → those fields directly. The pilot goes
this far on open data; the *acte d'engagement* turns each row into exact
administrative data at zero marginal cost to the partner. **The demo is the
argument for access.** A ready-to-complete request dossier, with the
limitation→field table, is in `docs/access/fichiers-fonciers-dossier.md`; the
open steps (choosing the eligible host structure, signing) are the project
lead's.

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
 Flags: `--layers` (REI scope), `--baseline floor` (today's tax by plain floor
area, the pre-calibration sensitivity), `--no-dpe` (BD TOPO year
only, for the depreciation comparison), `--no-report` (CSV only), `--cache-dir`
(reuse raw downloads; makes reruns resumable). On Windows set
`PYTHONUTF8=1`. Outputs land in `output/<commune>.csv` and
`output/reports/<commune>/*.png` (both gitignored).
