# THEORY — LVTShift-FR

## Problem thesis

France taxes property (taxe foncière, TFPB) on 1970-era cadastral rental values
(VLC), and — critically — never assesses **land** and **building** separately. A
Land Value Tax (LVT) shift cannot be modelled off the shelf because the single
indispensable input, parcel land value, does not exist in any open dataset. The
structural problem is therefore one of **imputation under transparency**: produce
a land-value estimate per parcel from open data only, honest about its error bars,
credible enough to start a policy conversation.

## Operating theory

The leverage is **reuse, not reinvention**. The US `LVTShift` toolkit already
solves the hard fiscal-mechanics problem — given per-parcel land value,
improvement value and a current-revenue target, it finds the revenue-neutral
split-rate millages and exports a standard schema. So the French problem reduces
to: *manufacture LVTShift's expected input columns from French open data, then
call its real solver unchanged.*

The pipeline is a value-decomposition chain:
- **improvement value** = depreciated replacement cost (footprint × storeys ×
  €/m² × straight-line depreciation), from BD TOPO building geometry/attributes.
- **market value** = a deliberately simple hedonic on DVF (cell × type fixed
  effects on log €/m², shrinkage toward commune-type median). `cell` is a 400 m
  grid square — a transparent spatial fixed effect, not an admin geography.
- **land value** = **classify-then-price** (see below): built parcels use the
  residual (market − improvement), building-less parcels are classified by legal
  constructibility and priced against the right benchmark. The single flaw of
  the old method was applying *one* land density to *all* land.
- **current tax** = the commune's real REI foncier-bâti produit distributed by a
  VLC proxy (floor area) — exact in aggregate, approximate per parcel.

Each weak step is **flagged in-band** (`imp_quality`, `lv_flag`) so error
propagates visibly rather than silently.

### Source decisions (verified live, June 2026)
- **Buildings: BD TOPO V3 WFS, not BDNB.** The IGN Géoplateforme exposes the same
  MAJIC-derived attributes per building (hauteur, nombre_d_etages,
  nombre_de_logements, usage_1, appariement_fichiers_fonciers) queryable by
  commune bbox — avoiding the multi-GB BDNB departmental download for equivalent
  content. Buildings join to cadastre parcels by centroid-in-polygon.
- **Tax target: OFGL's commune-level REI API.** Foncier bâti is `FB`; the target
  is the `MONTANT RÉEL` line summed over the chosen beneficiary layers (default
  Commune + intercommunalité). Which layers are held neutral is an explicit
  policy choice (one of LVTShift's five upfront questions).
- **Land classification: GPU zoning + SAFER + DVF TAB (classify-then-price).**
  Building-less parcels are classified by Géoportail-de-l'Urbanisme `zone_urba`
  `typezone` (U/AUc → constructible; AU/AUs → constructible-deferred, discounted;
  A → agricultural; N → natural). Constructible land is priced from clean DVF
  *terrain-à-bâtir* comparables (commune median, shrunk to cell where dense,
  EPTB national fallback); agricultural/natural land from SAFER départemental
  €/m². Buildings join parcels by **area-weighted intersection** (not centroid),
  so a building straddling a boundary credits each parcel — killing false
  "vacant" parcels. Verified by Gemini (France-context) and two real runs.

## Strategy

1. **Zero modification of upstream.** The FR code lives in `lvtshift-fr/` inside a
   fork and only *imports* `lvt`; upstream pulls merge cleanly and improvements
   flow through. The fork is packaging, not divergence.
2. **Aggregate, never per-parcel, for publication.** Imputation error averages out
   by property category and income quintile (Filosofi IRIS); individual bills do
   not — so they are never published.
3. **Sensitivity as a first-class output.** Every headline result carries a
   land-share ±10pt band.
4. **The access argument.** Each open-data compromise maps to a specific Fichiers
   fonciers (CEREMA/DGFiP) variable that would resolve it — making the demo itself
   the case for administrative data access.

## Key discoveries

- **Real ingest now works end-to-end on live open data.** `run_commune.py` runs
  cadastre → DVF → BD TOPO → REI → solver → euro charts for any configured
  commune, **revenue-neutral to the euro** (Montreuil €101.8M, Cahors €22.7M hit
  exactly). The pipeline is no longer synthetic-only.
- **Classify-then-price fixed the rural artifact.** After the fix, agricultural +
  natural land in Cahors (9 083 parcels, 42% of them) bears **0.3%** of the levy
  (was: it swamped the base); built stock bears 98.4%, and built categories shift
  only ±3% (was −83%). In Montreuil the built stock bears 98.5%, constructible
  vacant 1.5% — and that vacant land still pays *more* (the LVT development
  incentive, now correctly sized). Both stay revenue-neutral to the euro.
- **Arrondissement fiscal gotcha.** Paris/Lyon/Marseille arrondissements have
  INSEE codes for cadastre/DVF/buildings but **no separate taxe foncière** (the
  city + métropole levy it), so REI has no per-arrondissement produit. "Inner
  Lyon" is therefore modelled as Villeurbanne (autonomous inner-ring commune).

## Open questions / where the theory might break

- **Current-tax baseline: built-only fixed; within-built proxy remains weak.**
  The clear error is resolved — FB is a *built* tax, so building-less parcels now
  bear zero (the old `0.002 × area` term that manufactured a rural over-charge,
  and the "Cahors vacant −86%", are gone; vacant land correctly goes 0 → positive
  LVT). What remains weak is distributing the produit *within* built parcels by
  floor area alone: it ignores cadastral category and weighted-surface
  coefficients (the largest VLC drivers). Deliberately **not** tilted toward the
  hedonic market value — the 1970 VLC is regressive vs market, so a value tilt
  would *worsen* fidelity to today's system (Gemini, France-context). A
  category-weighted variant is offered only as a labelled sensitivity. The real
  resolution is per-parcel VLC from the Fichiers Fonciers (the access argument).
- **AU and Nh/Ah zoning nuance** (Gemini's main flag): all AU is treated
  constructible with a flat discount for AU/AUs; `AU fermée` deserves a steeper
  cut and `Nh/Ah` pastilles (limited building in A/N) are currently undervalued.
- **Non-residential market value borrows the residential €/m² surface** — flagged;
  professionnels need a separate strata (2017 VLC revision) before publication.
- **Income (Filosofi) wired** — parcels carry their IRIS code (IGN contours WFS),
  joined to INSEE Filosofi 2021 median disposable income; the distributional
  quintile charts now render. Montreuil shows a *progressive* gradient (poorest
  quintiles −10 %, richer +9/+12 %). Caveats: 2021 is the last vintage, IRIS
  income exists only for communes ≥5 000 inhabitants, some IRIS are suppressed
  (NaN → drop out), and the quintile split inherits the current-tax baseline
  weakness, so read it as directional.
- **Construction costs are coarse regional pilots** (1600–2150 €/m²); a ±15% move
  flows linearly into improvement value, so they need FFB/BT01 calibration.
