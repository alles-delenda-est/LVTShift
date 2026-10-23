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
  €/m² × straight-line depreciation), from BD TOPO building geometry. The
  construction era driving depreciation comes from **ADEME DPE** per parcel (BD
  TOPO's date_d_apparition is a database first-appearance date, often null), with
  a commune-median-era fallback so age never degenerates to "unknown".
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
  content. Buildings join to cadastre parcels by area-weighted intersection
  (see the land-classification bullet below).
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
   land-share ±10pt band, published with each commune's figures
   (`headline_sensitivity`).
4. **The access argument.** Each open-data compromise maps to a specific Fichiers
   fonciers (CEREMA/DGFiP) variable that would resolve it — making the demo itself
   the case for administrative data access.
5. **Coverage is a finding, not a silent failure.** `preflight.py` probes every
   source per commune and runs the post-run validations, classifying each
   OK/WARN/FAIL with an analysed cause and adaptation, and writes a register
   (`docs/INGESTION_REGISTER.md` + `site/public/data/ingestion_register.json`).
   A commune that cannot be modelled is *documented with its reason*, never
   dropped quietly — the register is itself part of the transparency argument.
   The advocacy-site data layer (`export_web.py`) emits aggregate-only JSON per
   commune (+ `validate_external.py` independent checks) for the public site.

## Key discoveries

- **Real ingest works end-to-end on live open data**, revenue-neutral to the
  euro on every run. Classify-then-price fixed the rural artifact: farm/natural
  land now bears a negligible share (Cahors 0.3 %), and vacant constructible land
  still pays *more* — the LVT incentive, correctly sized.
- **Construction year was a hidden degeneracy.** BD TOPO's date_d_apparition is
  null for whole communes (100 % of Cahors), so every building's age was
  "unknown" → building value ≈ 0 → every built parcel pinned at the 85 %
  land-share clip. Anchoring depreciation on DPE eras (parcel-specific where
  diagnosed, commune-median otherwise) un-pins it: Cahors built parcels move from
  100 % clipped / 0.85 median land share to 0 % clipped / 0.54 — a land/building
  split (~53/47) that matches INSEE comptes de patrimoine (~45-50 % land). The
  effect is large where buildings are a real share of value (cheap-land communes)
  and negligible where land dominates and the clip legitimately binds (Montreuil
  stays ~0.85) — the residual's sensitivity to building value, made visible.
- **Paris and Lyon were never a data gap, only a key mismatch.** Their
  arrondissements carry the data codes (cadastre/DVF/DPE/IRIS) while the city's
  INSEE code carries the levy (REI). Splitting a config into a fiscal code and
  data codes, fetching spatially one arrondissement at a time, and solving one
  city-wide rate (as the PLM-law city actually votes) models both whole cities
  revenue-neutral to the euro (Paris €1,840.9M on 78k parcels, Lyon €362.9M).
- **Inner rings are aggregates of jurisdictions, not a metro tax.** The 179
  extra-muros communes (122 in 92/93/94, 57 in the Métropole de Lyon) are each
  solved on their own levy and pooled afterwards; the sensitivity band is
  re-solved per commune. Live REI settles the layer question with data: no
  GFP/EPT foncier-bâti exists in the petite couronne (two Gemini reviews
  asserted otherwise, once each way — both checked against REI), and the
  Métropole de Lyon has no départemental FB layer (its ex-départemental share
  sits inside the commune rate since 2021). Syndicat layers are material in 45
  Lyon-ring communes but scale euros, not percentages.
- **Pooling incomes across jurisdictions manufactures a false gradient.** Ranked
  ring-wide, the Lyon ring looks regressive (poorest quintile +9 %, richest
  −1 %); ranked within each commune it is progressive (+5 % → +12 %). The
  ring-wide view mixes the reform with rich-vs-poor commune differences that
  the reform does not touch. Territories therefore publish both views.
- **Age is not wear where markets pay for maintenance; the 85 % cap was mostly a
  depreciation artefact.** Straight-line-to-25 % depreciation treated maintained
  Haussmann stock as worn out (≈ €575/m² against ≈ €10,860/m² prices), so 95.5 %
  of Paris's built parcels, and 55 communes in all, sat on the 85 % clip. A
  uniform effective-age cap fixed strong markets but pushed Roubaix and Cahors
  onto the 15 % *lower* clip: in weak markets age-based depreciation is also
  absorbing economic obsolescence (price ≈ rebuild cost). The adopted rule is
  market-conditional: effective age capped at 30 years, phased in continuously
  as the IRIS price/rebuild-cost ratio goes from 1.2 to 2.5 (q at IRIS level so
  land uplift is not read as a newer building). Clip warnings fall from 55 to 1
  (Neuilly); Paris 83.9 % with 47.6 % still at the cap, which is genuine at
  Paris prices. Every distributional direction survived the change, so the
  quintile story is robust to the building-value assumption. Paris still reads
  largely as a revaluation from a floor-area bill to a value bill, and rests on
  the weakest input, the current-tax proxy.
- **Building-less land is mispriced locally, not in aggregate.** U-zoned public
  open space (Paris UV parks, Lyon USP, Saint-Cloud's UL domain) and vacant
  industrial/port land (UEi, Port Édouard Herriot UEp) take the residential
  terrain-à-bâtir price. Aggregate effect is small (Paris 0.9 % of levy, rings
  3.6 % / 6.2 %), but it concentrates: Saint-Cloud 24 %, Feyzin 19 %. Since the
  site shows per-commune rows, this matters there first.
- **Alsace-Moselle is a hard coverage boundary.** Depts 57/67/68 record sales in
  the **Livre Foncier** (German-law registry), not the DGFiP DVF — so the open
  DVF dataset has *no* file for them (Mulhouse/Colmar/Strasbourg/Metz all 404;
  verified). With no sales there is no hedonic and no terrain-à-bâtir floor, so
  these communes are **not modellable by this method** — not a transient miss,
  not fixable by retry or fallback. Mulhouse is therefore documented in the
  register as a coverage gap and excluded from the modelled panel (now 9: it was
  the "Est/Rhin" slot). A Livre-Foncier ingest would be the only fix.
- **The full 9-commune panel runs on live data.** One background pass ran all
  ten; nine succeeded revenue-neutral, Mulhouse failed structurally. Re-running
  also replaced a stale Grenoble sample (5 000-row/3-IRIS) with the real
  12 853-parcel run — a reminder that cached CSVs can silently predate the
  pipeline, which the register's post-run checks now catch.
- **Imputed land share runs systematically high in hot markets.** The register
  shows 6 of 9 communes above a 40–65 % land-share band (Montreuil 84 %, La
  Rochelle 83.5 %, Villeurbanne 72 %). Partly the genuine LVT thesis (land
  dominates value in high-demand cores), but the magnitude points at the
  construction-cost calibration (too-low €/m² → inflated land residual) — the
  first-order sensitivity below, now visible per commune rather than asserted.
- **The "owner-occupier pays less" message is only half true — and the model
  says which half.** The campaign's instinct (shifting off buildings spares the
  resident household) holds for **apartments**, whose land is split across the
  copropriété, so they are building-heavy and mostly pay *less*. It fails for the
  **individual house on a valuable plot**, which is land-heavy: in dense/high-land
  communes the large majority of *maisons individuelles* pay **more** — Villeurbanne
  90.8 %, Annemasse 90.2 %, Grenoble 88.9 %, Sète 89.5 % (median change +15 to
  +29 %) — while in cheap-land communes (Roubaix 25.8 %, La Rochelle 27.2 %) most
  pay less. The determinant is the property's land share, not tenure. This is the
  honest core of the distributional story and a genuine tension for advocacy: the
  reform is *not* a free lunch for all owner-occupiers. The site states this
  plainly (the sceptiques pager + a data-grounded callout reading live figures)
  rather than repeating the comfortable slogan — but the framing of the campaign
  message itself is a decision for the domain expert, not the model.
- **The advocacy site** (Next.js, `site/`) reads aggregate JSON only: the
  `/resultats` explorer (communes + the two ring aggregates with a per-member
  table), argument pagers, and a méthodologie page carrying the register.

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
  weakness, so read it as directional. **Small communes can't form 5 quintiles**
  at all — Cahors and Figeac have too few distinct IRIS incomes, so the exporter
  emits `null` and no quintile chart is published (the register flags this per
  commune via the real `build_by_income_quintile`, not a proxy).
- **The maintained-stock parameters are judgement calls.** The 30-year cap and
  the 1.2–2.5 ramp are informed by the literature but not estimated; no sensitivity
  on them is published yet. A condition signal (DPE energy class) would ground
  effective age in the building rather than the neighbourhood price.
- **Construction costs are coarse regional pilots** (1600–2300 €/m²); a ±15% move
  flows linearly into improvement value, so they need FFB/BT01 calibration — and
  a stated floor-area basis (BD TOPO footprint × storeys is gross, published
  costs are mostly per m² surface utile). In old dense stock depreciation, not
  cost, decides the split.
- **Exemptions are absent from the baseline** (HLM art. 1384 A, QPV abatement,
  public land): the produit is net of them but spread over every built parcel.
  Open proxies exist (RPLS social-housing register, QPV perimeters, BD TOPO
  zones d'activité) but none is wired in yet.
- **DPE construction year carries selection bias.** DPE covers diagnosed (sold/
  rented/renovated) *residential* dwellings, so the commune-median-era fallback
  applies a residential-diagnosed median to non-residential and never-diagnosed
  parcels (Gemini: a clear improvement over the degenerate baseline, but the
  generalisation must be flagged). Era→year uses band midpoints (mitigated for
  pre-1948 stock, which hits the depreciation floor regardless).
