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
  €/m² × straight-line depreciation), from BDNB/BD TOPO geometry.
- **market value** = a deliberately simple hedonic on DVF (cell × type fixed
  effects on log €/m², shrinkage toward commune-type median).
- **land value** = market − improvement (residual), floored at vacant-land
  comparables, land-share clipped to [15%, 85%] with every clip flagged.
- **current tax** = the commune's real REI TFPB produit distributed by a VLC
  proxy (floor area) — exact in aggregate, approximate per parcel.

Each weak step is **flagged in-band** (`imp_quality`, `lv_flag`) so error
propagates visibly rather than silently.

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

- **The upstream API matches the FR code's assumptions exactly** (verified
  against `lvt/lvt_utils.py`): `model_split_rate_tax` signature/returns, every
  `CATEGORY_MAP` value is a valid `STANDARD_PROPERTY_CATEGORIES` member, and
  `save_standard_export` defaults line up. The integration is real, not aspirational.
- **The synthetic end-to-end test passes through the real solver** on a clean
  environment (pandas 3.x) — revenue-neutral within 1%, vacant land correctly
  pays more. No hidden version landmine.
- **Fork layout needs one change only:** the `lvt` package sits at the repo root
  (not a sibling `../LVTShift`), so `run_pipeline.py`'s path line drops the
  `/ "LVTShift"` suffix. Nothing else.

## Open questions / where the theory might break

- **The current-tax proxy is the load-bearing weakness.** Independent review
  (Gemini, France-context) judges a floor-area-only VLC proxy potentially
  indefensible even at category/quintile level: it ignores cadastral category and
  weighted-surface coefficients, the two largest VLC drivers. Candidate fixes:
  model VLC from DVF+BDNB, or anchor to TFPB aggregates by cadastral category ×
  IRIS. Until then, the *baseline* — not the LVT side — is what could discredit
  the exercise.
- **Land-share clipping distorts the tails.** Dense central parcels can genuinely
  exceed an 85% land share; clipping must be presented as a design constraint with
  the unclipped distribution shown alongside, not as a measurement.
- **Building value unit mismatch** (SHON cost × SHOB-like surface) and a generic
  €1,900/m² with a possibly-high 25% depreciation floor need regional calibration.
- **DVF hygiene** (multi-lot mutations, non-market sales, Notaires-INSEE vs CPI
  deflation) is assumed handled upstream of the hedonic; robustness untested on
  real data.
- Real ingest (BDNB, REI, Filosofi) is still `NotImplementedError` — the pipeline
  is proven on synthetic data only.
