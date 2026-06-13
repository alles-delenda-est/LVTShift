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
- **land value** = market − improvement (residual), floored at vacant-land
  comparables, land-share clipped to [15%, 85%] with every clip flagged.
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
- **Urban Montreuil produces a credible LVT pattern:** homes −€55 median, condos
  −€292, industrial −€1,563, commercial −€298; under-used land moves from ~€0 to
  bearing ~€10M (9.8%) of the levy. The mechanism behaves as theory predicts.
- **Geography determines credibility.** Sprawling rural communes (Cahors: 57% of
  parcels are countryside) are swamped by the vacant-land valuation artifact;
  dense communes are clean. Showcase on urban communes until vacant land is fixed.
- **Arrondissement fiscal gotcha.** Paris/Lyon/Marseille arrondissements have
  INSEE codes for cadastre/DVF/buildings but **no separate taxe foncière** (the
  city + métropole levy it), so REI has no per-arrondissement produit. "Inner
  Lyon" is therefore modelled as Villeurbanne (autonomous inner-ring commune).

## Open questions / where the theory might break

- **Vacant-land valuation is now the load-bearing weakness.** Valuing building-less
  parcels at the commune's *median built-land density × area* overvalues large
  rural/agricultural parcels wildly, and the headline "vacant land pays more"
  rests entirely on it. Fix: anchor to DVF *terrain-à-bâtir* comparables (already
  fetched, not yet wired), and distinguish constructible from agricultural land.
- **Building→parcel join loses buildings.** Centroid-in-parcel misses buildings on
  parcel boundaries or spanning several parcels, wrongly flagging ~21% of built-up
  Montreuil parcels "vacant" — inflating vacant land and under-imputing
  improvements. Fix: area-weighted intersection join, not centroid.
- **Current-tax proxy remains weak** (floor-area-only VLC): ignores cadastral
  category and weighted-surface coefficients, the two largest VLC drivers. Distorts
  the *baseline* distribution; aggregates must be recouped against REI by category.
- **Non-residential market value borrows the residential €/m² surface** — flagged;
  professionnels need a separate strata (2017 VLC revision) before publication.
- **Income (Filosofi) not yet wired** — the distributional/equity charts are off
  until it lands; IRIS income exists only for communes ≥5 000 inhabitants.
- **Construction costs are coarse regional pilots** (1600–2150 €/m²); a ±15% move
  flows linearly into improvement value, so they need FFB/BT01 calibration.
