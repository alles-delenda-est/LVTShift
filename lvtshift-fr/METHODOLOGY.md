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
| Exempt public property | DGFiP « Fichiers des locaux et des parcelles des personnes morales » | yearly zips via the data.economie.gouv.fr catalog | situation 2025 | flag obviously TFPB-exempt public property (§3.5) |

All Licence Ouverte / Etalab. Exact endpoints live in `config.DATA_SOURCES`.

## 3. The pipeline and formulas

Spatial work is done in RGF93 / Lambert-93 (EPSG:2154). `cell` = a 400 m grid
square (a transparent hedonic fixed effect, not an admin geography).

**3.1 Building (improvement) value** — depreciated replacement cost, summed to
the parcel (`estimate.improvement_value`):

```
floor_area     = footprint_m2 × storeys          (storeys imputed from height/3 if missing)
habitable_area = net_to_gross[type] × floor_area            (flats 0.64, houses 0.61)
cost[type]     = house_cost_eur_m2 for houses where set, else construction_cost_eur_m2
cost_hab       = cost[type] ÷ cost_net_to_gross[type]             (flats 0.71, houses 0.82)
age            = reference_year − year_built
q              = median hedonic €/m² of the built parcels in the parcel's IRIS
                 ÷ construction_cost_eur_m2   (commune median if the IRIS has none)
w              = clip((q − 1.2) / (2.5 − 1.2), 0, 1)          (dep_q_ramp)
eff_age        = w × min(age, 30) + (1 − w) × age             (dep_maintained_age_cap)
depreciation   = clip(1 − (1 − dep_floor) × eff_age / dep_years,  min = dep_floor)
imp_value      = habitable_area × cost_hab × depreciation
market_value   = hedonic €/m² × habitable_area                (§3.3)
```

`year_built` is taken from DPE (§3.2); `construction_cost_eur_m2`,
`house_cost_eur_m2`, `dep_years`, `dep_floor` are per-commune config (§4); `type`
is the parcel's dominant `type_local` (types other than flat and house use the
flat ratios and the commune cost).

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

**3.2 Construction year (depreciation anchor)** — BD TOPO's `date_d_apparition`
is a database first-appearance date, not a build year, and is often null (100 %
of Cahors). We instead use the DPE `periode_construction` era band, mapped to a
midpoint year (`avant 1948`→1930, `1948-1974`→1961, … `après 2021`→2022),
spatially joined to parcels (per-parcel median). Parcels with no DPE point take
the **commune dwelling-weighted median era** as a fallback, so age never
degenerates to "unknown".

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
parcels. In Paris this flags 3,098 parcels (1,362 built) carrying €91.6 M (5.0 %) of
the produit the baseline used to spread onto them. Owner names are read only to
recognise utilities and housing managers and are never stored or published.
`--no-exemptions` reproduces the unflagged run.

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

**Sensitivity band.** Because land value is imputed, every published figure carries
a ±10 pt land-share band: the aggregate land share is tilted down and up by 10 points
(each parcel's land and building values scaled uniformly, total base and levy held
fixed) and the upstream solver is re-run (`export_web._tilted_change`). The band is
reported for the headline figures **and** for each property category and income
quintile (and, on the rings, the within-commune quintiles), using the same quintile
cut points as the central estimate; the site draws it as whiskers on those charts.
The central leg reproduces the published figures exactly (tested). A conclusion is
treated as robust only if it holds across the band; in Paris the quintile gradient
barely moves (median residential parcel: poorest fifth −18.6 to −20.3 %, richest
+12.5 to +13.6 %).

**Income groups: totals and households, not parcel medians.** Each income
quintile (parcels ranked by their IRIS's Filosofi median income) carries three
figures, all on residential parcels: the **group total** (Σ new tax ÷ Σ current
tax − 1), the **typical household** (the parcel changes' median weighted by
dwellings, so a 200-flat block counts 200 times) and, for reference, the plain
**parcel median**. The site draws the total as the bar and the household as a
marker. The parcel median misleads where poorer areas mix many small houses
with a few large blocks: in Villeurbanne the poorest fifth's median parcel pays
+4.8 % while the group as a whole pays −8.1 % and its typical household −10.1 %,
because the large blocks, where most of its households live, gain the most.
Dwellings come from BD TOPO `nombre_de_logements` (area-shared across parcels);
residential parcels without a count are imputed (a house = 1; flats = gross floor
area ÷ 85 m²), which concerns 5–11 % of residential parcels in Paris, Lyon and
Villeurbanne. The counts live in a local sidecar to the standard export
(`<commune>.households.csv`, row-aligned and checked against `new_tax`); only the
per-quintile totals are published. BD TOPO under-counts dwellings slightly
(Paris ≈ 1.14 M against ≈ 1.4 M in the census), which affects the weights, not
the totals.

**Paris's land share and the 85 % cap.** Under the original rule (straight-line
to a 25 % floor) a ~95-year-old, continuously maintained Paris building fell to
≈ €575/m² against a median DVF price of ≈ €10,860/m², so 95.5 % of built parcels
sat at the 0.85 bound and the 84.9 % headline was set by the cap. The
maintained-stock rule (§3.1) values such buildings at a 30-year effective age,
which brought Paris to 83.3 % with 34.8 % of built parcels still at the bound.
With both sides of the residual on habitable area and the calibrated costs
(§3.1, §4), Paris comes out at **74.2 %** with 3.2 % of built parcels at the
bound (0.4 % before houses got their own, lower cost): its land share is
measured, not set by the cap. No commune has more than half its built parcels at
the cap; Neuilly-sur-Seine has the most (25.0 %), and the preflight
`land_share_clip` check warns nowhere. Lyon is at 57.8 %, the Paris ring 61.7 %
and the Lyon ring 52.6 %. Across the 188 modelled communes, 24 lie above the
40–65 % plausibility band (138 before the habitable-area basis) and 4 below
(Vaujours 35.7 %, Santeny 36.2 %, Limeil-Brévannes 37.4 %, Villepinte 39.4 %).
`headline.built_at_cap_pct` records the share of built parcels at the bound,
and the site labels the land share "plafonnée" when it is ≥ 50 %.

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
- **Land-share bounds**: [0.15, 0.85] — a design constraint, not a measurement.
  Where most parcels used to hit the upper bound (Paris, Lyon), the causes found
  were over-depreciation of old maintained stock and pricing habitable-area DVF
  prices on the larger BD TOPO floor area, not land genuinely above 85 %. With
  both corrected, no commune has more than half its built parcels at either
  bound (§3.7).
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
  near INSEE comptes de patrimoine (~45–50 % land). Cahors came to ~53 % after
  the DPE construction-year fix (it was a degenerate 85 % before — see §6) and
  is at 40.7 % on the habitable-area basis.
- **Sign checks** — agricultural/natural land bears a negligible share of the
  levy (Cahors 0.3 %); under-used constructible land pays *more* (the LVT
  incentive); the Montreuil income gradient is progressive (group totals:
  poorest fifth −15.8 %, richest +14.9 %).
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
   uncalibrated pilot costs. Non-residential parcels take the flat ratios (and
   the flat €/m², item 7). BD TOPO storey miscounts are the main source of
   parcel-level scatter in floor area.
5. **Land-share clip**: when most built parcels sit at a bound, the land share is
   an assumption, not a result, and the parcel-level variation in building value is
   erased. Before the maintained-stock rule this was Paris (95.5 % at the bound),
   Lyon and 53 other communes. No commune now has more than half its built parcels
   at a bound; Neuilly-sur-Seine has the most at the cap (25.0 %), Paris 3.2 %
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
7. **Non-residential market value** borrows the residential €/m² surface and the
   flat area ratios, and its building value the housing cost; professionnels
   (2017 VLC revision) need a separate stratum. This is now the main lever on the
   communes below the plausibility band: industrial and commercial parcels
   dominate their building value (Santeny 51 % industrial, Vaujours 56 %
   industrial, Villepinte 45 % commercial — the exhibition centre — and Périgny
   50 % "other"), which is why the house cost only partly lifted them (§3.7).
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
11. **Exemptions are only partly modelled.** Obviously exempt public property is
    flagged (§3.5), but deliberately conservatively: public units inside
    condominiums or under leases, worship buildings owned by associations,
    private non-profit schools and hospitals, the Assemblée and Sénat (unusual
    legal forms), out-of-territory partial exemptions and public buildings with
    no unit recorded stay taxable. Temporary exemptions (new social housing under
    CGI art. 1384 A, the QPV abatement) are not identifiable from open data, so
    the baseline still overstates today's bill on exempt HLM and understates it
    elsewhere (material in 93).
    Farm buildings (CGI art. 1382 6°: greenhouses, barns) are not yet exempted
    either.
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
