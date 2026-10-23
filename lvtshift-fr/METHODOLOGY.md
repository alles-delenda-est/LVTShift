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
| Zoning | GPU `zone_urba` (IGN) | WFS, commune bbox | current PLU/PLUi | constructibility (U/AU vs A/N) of building-less parcels; A/N test for exempt farm buildings (§3.5) |
| Agricultural prices | SAFER « Le prix des terres » | départemental table (config) | 2024 | non-constructible land €/m² |
| Building-plot fallback | EPTB (SDES) | national figure (config) | 2023 | constructible €/m² when local comparables are thin |
| Tax target | REI foncier bâti, via OFGL | Opendatasoft API by `idcom` | latest | exact revenue-neutrality target (`MONTANT RÉEL`) |
| Today's-tax split | REI (DGFiP), via OFGL `rei`: `E11` (TFPB base), `WC75` (compensation for the 2021 industrial halving), `T29`, `T29_1`, `X503` (CFE gross bases); OFGL `base-fiscale-simplifiee` 2020 TFPB rates | Opendatasoft API by `idcom` | REI 2025; rates 2020 | per-commune industrial / professional / housing shares of the TFPB base (§3.5) |
| IRIS geometry | IGN IRIS contours | WFS `STATISTICALUNITS.IRIS:contours_iris` | current | parcel → IRIS for income join |
| Income | INSEE Filosofi | CSV zip (`DISP_MED21`) | 2021 | distributional (quintile) analysis |
| Exempt public property | DGFiP « Fichiers des locaux et des parcelles des personnes morales » | yearly zips via the data.economie.gouv.fr catalog | situation 2025 | flag obviously TFPB-exempt public property (§3.5) |

All Licence Ouverte / Etalab. Exact endpoints live in `config.DATA_SOURCES`.

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
1st/99th percentile.

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
| **Built, largest building shed-type** (DRC) | terrain-à-bâtir €/m² × `activity_land_ratio` (business types) or × 1 (sports halls, annexes) × parcel area, floored at the agricultural €/m²; outside urban zoning only a yard of 3 × floor area takes that price. Market value = land + depreciated building; no residential price, no clip (`lv_flag` `built_drc`) |
| **Constructible vacant** (zone U/AUc) | DVF terrain-à-bâtir €/m² × area (cell median where ≥8 sales, else commune median, else EPTB national fallback) |
| **Constructible deferred** (AU/AUs) | as above × `au_strict_factor` (development deferred) |
| **Agricultural / natural** (zone A/N) | SAFER départemental €/m² × area |

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

**3.5 Current tax (baseline)** — the exact REI FB produit, distributed
(`estimate.current_tax`) across **built parcels only**. TFPB is a built tax;
building-less parcels bear €0 (they pay the separate TFPNB, out of scope). There
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
| Professional premises (RVLLP, art. 1498) | 0.5 × the CFE gross base of professional premises (`T29_1`, else `T29 − X503`), × **2.5**. The 0.5 is the TFPB's 50 % deduction (CGI art. 1388), which applies to every built property; the CFE takes the full rental value | The CFE is an occupier tax, so vacant premises and occupiers outside the CFE drop out: nationally the raw proxy gives 8.6 % of the base against the Cour's 22 %. The scale of 2.5 calibrates it to that national figure. The raw proxy (× 1.0) is the lower bound |
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
- **Lower bound computed alongside.** Every run also shares today's tax a
  second time with the professional target at the raw proxy (× 1.0,
  `pro_undercount_scale_low`), under the same groups, merge rule and caps. It
  is stored in the households sidecar (`current_tax_low`), checked to be
  revenue-neutral on export, and published as `baseline_sensitivity` (§3.7).
  The LVT bills do not change; only today's tax does.

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
barely moves (median residential parcel: poorest fifth −17.1 to −19.1 %, richest
+15.6 to +15.8 %). The band holds today's-tax baseline fixed. The baseline's own
uncertainty, the professional-premises scale (§3.5), moves household results
far more than the band does. It is published separately, as a lower bound shown
beside the central case (§3.7, §6 item 1).

**Income groups: totals and households, not parcel medians.** Each income
quintile (parcels ranked by their IRIS's Filosofi median income) carries three
figures, all on residential parcels: the **group total** (Σ new tax ÷ Σ current
tax − 1), the **typical household** (the parcel changes' median weighted by
dwellings, so a 200-flat block counts 200 times) and, for reference, the plain
**parcel median**. The site draws the total as the bar and the household as a
marker. The parcel median misleads where poorer areas mix many small houses
with a few large blocks: in Villeurbanne the poorest fifth's median parcel pays
+7.6 % while the group as a whole pays −6.3 % and its typical household −6.1 %
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

**Paris's land share and the 85 % cap.** Under the original rule (straight-line
to a 25 % floor) a ~95-year-old, continuously maintained Paris building fell to
≈ €575/m² against a median DVF price of ≈ €10,860/m², so 95.5 % of built parcels
sat at the 0.85 bound and the 84.9 % headline was set by the cap. The
maintained-stock rule (§3.1) values such buildings at a 30-year effective age,
which brought Paris to 83.3 % with 34.8 % of built parcels still at the bound.
With both sides of the residual on habitable area, the calibrated costs and the
per-type non-residential valuation (§3.1, §3.4, §4), Paris comes out at
**75.8 %** with 5.6 % of built parcels at the bound: its land share is
measured, not set by the cap. No commune has more than half its built parcels at
the cap; Neuilly-sur-Seine has the most (25.3 %), and the preflight
`land_share_clip` check warns nowhere. Lyon is at 60.0 %, the Paris ring 65.3 %
and the Lyon ring 55.4 %. Across the 188 modelled communes, 48 lie above 65 %
and 1 below 40 % (Cahors 38.6 %).
`headline.built_at_cap_pct` records the share of built parcels at the bound,
and the site labels the land share "plafonnée" when it is ≥ 50 %.

*The 40–65 % reference range.* It is a metro-wide benchmark (INSEE's comptes
de patrimoine put land at about 45–50 % of built real estate nationally), not a
test each commune must pass. Communes contiguous to Paris (itself 76 %)
naturally sit at 65–75 %, and land is 65–75 % of value in prime office
districts (Gemini review). Most of the 48 communes above 65 % are inner-ring
communes next to Paris (Puteaux 71.0 %, Saint-Cloud 76.8 %, Clichy 74.8 %,
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

Communes below 40 % fall from 2 to 1: Cahors, 41.2 → 38.6 %. Almost all of
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
proxy by 2.5; "low bound" uses the raw proxy (× 1.0).

| | Before (floor area) | Central (× 2.5) | Low bound (× 1.0) |
|---|---|---|---|
| Paris, income group totals Q1 … Q5, % | −20.1 −11.2 −4.2 +5.7 +14.9 | −17.4 −8.3 −1.3 +8.9 +18.9 | −27.6 −18.8 −12.1 −2.9 +3.9 |
| Lyon | −18.7 −8.5 −0.8 +3.2 +13.6 | −14.0 −3.5 +4.4 +8.5 +18.9 | −27.7 −18.2 −10.8 −7.0 +3.5 |
| Paris ring | −9.1 −5.0 −0.6 −2.7 +1.1 | −7.4 −3.0 +2.0 −1.1 +5.5 | −21.8 −16.9 −12.1 −12.6 −9.0 |
| Lyon ring | −3.7 +0.8 +5.0 −1.3 −4.7 | +0.8 +2.8 +10.7 +4.9 −1.1 | −15.8 −11.4 −7.7 −12.1 −14.2 |
| Amount shifted, % of levy: Paris / Lyon / Paris ring / Lyon ring | 19.2 / 20.4 / 28.1 / 38.3 | 19.6 / 20.9 / 30.4 / 43.0 | 30.2 / 30.9 / 36.7 / 40.6 |
| Share of parcels paying more, %: same order | 50.2 / 70.8 / 68.6 / 69.3 | 52.8 / 74.6 / 70.8 / 74.6 | 42.5 / 51.5 / 56.1 / 58.4 |

By category, central case:
- **Lyon ring.** Industry's share of today's tax rises from 10.0 to 11.9 %, and
  commerce's from 15.0 to 16.6 %. Bills under the LVT: industrial −63 %,
  commercial −24 %, houses +13 %.
- **Paris ring.** Industry's share rises from 5.3 to 5.8 %. Bills: industrial
  −36 %, commercial −15 %, houses +18 %.

Low bound: in the Lyon ring commercial bills rise 47 %, industrial fall 42 % and
houses fall 6 %; in the Paris ring commercial +77 %, industrial +1 %, houses
+1 %.

*On the site.* Each commune and territory payload carries
`baseline_sensitivity`, with a central (× 2.5) and a low (× 1.0) leg: amount
shifted, share of parcels paying more, residential median change, categories and
income-group totals (territories also rank groups within each commune). The
results page shows the two side by side in the table "Incertitude sur la taxe
actuelle des locaux professionnels", after the land-share sensitivity table. The
LVT bills are identical in both columns; only today's tax differs. In
Villepinte, for example, 68.8 % of parcels pay more in the central case and
19.3 % at the low bound. The territory figures in the table above come from a
scratch run of the same code; the published payloads should reproduce them.

**The professional scale is now the load-bearing uncertainty.** It moves the
household results by 10–15 points (Paris's poorest fifth −17.4 % central against
−27.6 % low; the Lyon ring's +0.8 % against −15.8 %). Under the central case
the progressive gradient in Paris and Lyon holds and steepens at the top, and
the rings' households gain less than on the floor-area baseline. Under the low
bound every ring income group pays less, and only the richest fifth in Paris and
Lyon pays more. The 2.5 is the better-supported
value, since the raw proxy is known to capture only about 40 % of the
professional base nationally, but one national multiplier cannot fit every
commune (§6, item 1).

**Policy finding.** In the Lyon chemical and industrial corridor, the LVT
shifts tax from industry to households under the central baseline (Saint-Fons
industrial bills −60 %, Marcy-l'Étoile −90 %).

*Plant: a design decision.* The modelled reform taxes land, and buildings at
the split rate; it does **not** tax fixed industrial plant. The project lead
took this decision, consistent with land-value-tax theory, which avoids
penalising capital investment. It needs no code change: art. 1499 values include
fixed plant, but the model's improvement value for an industrial parcel already
counts only the shed. To show how little the decision matters, a first-order
estimate (`docs/research/plant_effect.py`) adds the plant's revalued cost to the
improvement base (industrial base ÷ 0.03, gross or × 0.5 for depreciation, less
the model's building value) and re-solves the 4:1 split per commune:

| Industrial bills vs today | Shed only (published) | With plant, depreciated | With plant, gross |
|---|---|---|---|
| Lyon ring | −63 % | −62 % | −60 % |
| Paris ring | −36 % | −36 % | −33 % |
| Marcy-l'Étoile | −90 % | −84 % | −76 % |
| Saint-Fons | −60 % | −59 % | −53 % |

Taxing plant would move industrial bills by only 1–3 points in the rings
(Marcy-l'Étoile up to 14). Industry's cut is overwhelmingly the land shift:
cheap industrial land set against today's capital-heavy tax base.

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
- **Split-rate ratio**: 4:1 (land:improvement), headline scenario.
- **Agricultural €/m²** (SAFER, by département, agricultural / natural): default
  0.64 / 0.49; Lot 0.45 / 0.35; Seine-St-Denis 1.00 / 0.60; Nord 0.85 / 0.50;
  Rhône 0.70 / 0.50; Haute-Savoie 0.75 / 0.55; Isère 0.60 / 0.45; Paris,
  Hauts-de-Seine, Val-de-Marne 1.00 / 0.60 (Île-de-France anchor; immaterial).
- **EPTB building-plot fallback**: 99 €/m² (national).
- **AU discount** (`au_strict_factor`): 0.55. **Hedonic shrinkage** k = 8.
- **Today's-tax baseline** (`config.BASELINE_MODEL`, §3.5): REI 2025, 2020
  TFPB rates (Métropole de Lyon: Rhône 2014 rate, 11.03 %); professional proxy
  0.5 × CFE gross base (CGI art. 1388) × **2.5** (central; 1.0 = low bound,
  computed on every run and published beside the central case);
  per-m² weights capped at 5 × housing; industrial + professional share capped
  at 75 %.
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
  is at 38.6 % with the per-type non-residential valuation. The 40–65 % range
  is a metro-wide reference, not a per-commune test (§3.7).
- **Sign checks** — agricultural/natural land bears a negligible share of the
  levy (Cahors 0.3 %); under-used constructible land pays *more* (the LVT
  incentive); the Montreuil income gradient is progressive (group totals,
  central baseline: poorest fifth −12.2 %, richest +17.9 %).
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
     22 %). Moving from 2.5 to the raw proxy (1.0) moves household results by
     10–15 points: Paris's poorest fifth goes from −17.4 to −27.6 %, the Lyon
     ring's from +0.8 to −15.8 %, and in the Lyon ring commercial bills go from
     −24 % to +47 % (§3.7). The reform's new bills are the same in both cases;
     only the starting point moves. 2.5 is the better-supported value, but the
     undercount is surely not uniform: it should be larger where many premises
     are vacant or occupied by public bodies and associations, as in Paris.
     The site shows both side by side on every results page (table
     "Incertitude sur la taxe actuelle des locaux professionnels"); **always
     present both in any write-up too.** Per-commune professional values
     (Fichiers fonciers) are the real fix.
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
     or −60 % gross; Marcy-l'Étoile up to 14): the cut comes overwhelmingly
     from cheap industrial land.
2. **Residual amplification.** Built-parcel land = market − building, so building
   errors are amplified in the land residual where buildings are a large share of
   value. Mitigated by the [0.15, 0.85] clip, aggregation, and the sensitivity
   band. Vacant land does **not** use the residual, so the LVT headline (under-used
   land pays more) is unaffected by building-data quality.
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
8. **Income (Filosofi)**: 2021 (last vintage), communes ≥5 000 inhabitants only,
   some IRIS statistically suppressed.
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
    N zones are exempted (§3.5). Temporary exemptions (new social housing under
    CGI art. 1384 A, the QPV abatement) are not identifiable from open data, so
    the baseline still overstates today's bill on exempt HLM and understates it
    elsewhere (material in 93).

## 7. The Fichiers Fonciers access argument

Each open-data compromise maps to a specific Fichiers Fonciers (CEREMA/DGFiP)
field that would resolve it: the VLC proxy (floor area calibrated to REI group
shares with a national professional scale) → real per-parcel VLC;
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
 Flags: `--layers` (REI scope), `--baseline floor` (today's tax by plain floor
area, the pre-calibration sensitivity), `--no-dpe` (BD TOPO year
only, for the depreciation comparison), `--no-report` (CSV only), `--cache-dir`
(reuse raw downloads; makes reruns resumable). On Windows set
`PYTHONUTF8=1`. Outputs land in `output/<commune>.csv` and
`output/reports/<commune>/*.png` (both gitignored).
