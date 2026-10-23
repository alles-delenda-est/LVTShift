# THEORY — LVTShift-FR

## Problem thesis

France taxes property (taxe foncière, TFPB) on 1970-era cadastral rental values
(VLC), and never assesses **land** and **building** separately. A Land Value Tax
(LVT) shift cannot be modelled off the shelf because its one indispensable input,
parcel land value, exists in no open dataset. The problem is **imputation under
transparency**: produce a land-value estimate per parcel from open data only,
honest about its error bars, credible enough to start a policy conversation.

## Operating theory

The leverage is **reuse, not reinvention**. The US `LVTShift` toolkit already
solves the fiscal mechanics: given per-parcel land value, improvement value and a
revenue target, it finds the revenue-neutral split-rate millages. So the French
problem reduces to *manufacturing LVTShift's input columns from French open data,
then calling its real solver unchanged*.

The pipeline is a value-decomposition chain, and the decisive discipline is that
**both sides of the land residual are measured in the same unit**:
- **habitable area** = measured habitable ÷ BD TOPO (footprint × storeys) ratio,
  0.64 for flats and 0.61 for houses (DPE habitable surfaces matched to BD TOPO
  buildings by RNB id, 35 communes). BD TOPO counts attics, raised basements and
  technical levels as storeys, so its area overstates even true gross area.
- **market value** = DVF hedonic €/m² (habitable) × habitable area. Sales are
  first brought to 2025 euros with the most local Notaires-INSEE index, one series
  per agglomeration (mixing a local flats series with a regional houses series
  created artefacts).
- **improvement value** = cost per habitable m² × habitable area × depreciation.
  Costs are calibrated per m² of true gross area (DHUP/SISAL building-only social
  housing cost, BT01-indexed, fees and VAT: Paris 2 650, inner ring 2 400, Lyon
  2 000, Lyon ring 1 850) and divided by the habitable ÷ true-gross ratio they
  assume (0.71 flats, 0.82 houses). The land share then depends on that ratio,
  not on the measured one, which only sets euro levels. Depreciation is
  market-conditional: where IRIS prices far exceed rebuild cost, effective age is
  capped at 30 years (maintained stock); construction eras come from DPE.
- **land value** = classify-then-price: built parcels take the residual;
  building-less parcels are classified by legal constructibility (GPU zoning) and
  priced against terrain-à-bâtir comparables or SAFER farmland.
- **current tax** = the commune's real REI foncier-bâti produit spread by a floor-
  area proxy over taxable built parcels. Public property obviously exempt under
  CGI 1382-1° (DGFiP *personnes morales* files, conservative ownership rule) bears
  nothing today and nothing under the LVT.

Each weak step is flagged in-band and every published figure carries a ±10-point
land-share band, so error propagates visibly rather than silently.

## Strategy

1. **Zero modification of upstream.** The French code lives in `lvtshift-fr/`
   and only imports `lvt`; upstream merges stay clean.
2. **Aggregate, never per-parcel, for publication.** Imputation error averages out
   by category and income group; individual bills do not. An aggregate-only guard
   and disclosure control (minimum group size, no dominant parcel) enforce it.
3. **Sensitivity as a first-class output.** The ±10-point band is published for
   headlines, every category and every income quintile.
4. **The access argument.** Each open-data compromise maps to a Fichiers fonciers
   variable that would resolve it, so the demo is itself the case for access.
5. **Coverage is a finding.** `preflight.py` probes every source per commune and
   writes a register; a commune that cannot be modelled is documented, never
   dropped quietly.
6. **One change per PR, results regenerated on the combined stack.** Features
   that each move the published numbers are chained, not fanned out, so no
   branch's data silently contradicts another's.

## Key discoveries

- **The Paris "cap problem" was two artefacts, not a market fact.** First,
  straight-line depreciation treated maintained Haussmann stock as worn out (95.5 %
  of Paris's built parcels on the 85 % clip); the market-conditional effective age
  fixed that (34.8 % left). Second, market value multiplied a *habitable* price by
  an inflated BD TOPO area while building value used the same area, so both sides
  were overstated by different amounts. Putting both on habitable area and
  calibrating costs brings Paris to **74.0 %** with **0.4 %** of built parcels at
  the clip: the land share is now measured, not set by the bound. Lyon 58.6 %,
  rings 60.6 % / 55.4 %; communes above the 40–65 % plausibility band fall from
  138 to 21. Gemini judges these consistent with French evidence.
- **Changing a variable's units silently retunes every rule calibrated on it.**
  Restating the depreciation trigger per habitable m² halved Lyon's maintained
  weight before it was caught; the trigger keeps its calibrated basis. Check
  downstream thresholds whenever a unit changes.
- **Parcels are not households.** A 200-flat block is one parcel, like a house.
  Parcel medians showed every Villeurbanne income quintile paying more while the
  poorest fifth as a group pays −7.9 % and its typical household −11.8 %, because
  the large blocks where most poorer households live gain the most. The site now
  shows group totals and a dwelling-weighted household median.
- **Pooling incomes across jurisdictions manufactures a false gradient.** Ranked
  ring-wide, the Lyon ring looks regressive; ranked within each commune it is
  progressive. Each commune keeps its own levy, so territories publish both views.
- **Ownership rules need the *right* holder, not every holder.** A domaine national
  is State property managed under droit Z by a public agency; reading the agency
  as a blocking owner kept Saint-Cloud's park taxable (23 % of its LVT levy).
- **Paris and Lyon were a key mismatch, not a data gap**: arrondissements carry the
  data codes, the city carries the levy; one city-wide rate is solved. The inner
  rings are aggregates of per-commune solves, never a metropolitan tax.
- **The "owner-occupier pays less" message is half true.** Flats, whose land is
  shared in the copropriété, mostly pay less; the house on a valuable plot pays
  more. The determinant is the property's land share, not tenure — a framing
  decision for the domain expert, which the site states plainly.
- **Coverage boundaries are structural.** Alsace-Moselle sales are in the Livre
  Foncier, not DVF, so Mulhouse is documented as unmodellable.
- **External reviews must be checked against data.** Gemini reviews caught real
  errors (the surface-utile step, the stack fan-out) but also asserted things the
  data disproved (Saint-Cloud already exempt, Marnes-la-Coquette failing, wrong
  exemption counts); every claim is verified before it changes code or docs.

## Open questions / where the theory might break

- **The habitable ÷ true-gross ratio behind the costs is now the main
  uncertainty** (0.71 flats, 0.82 houses): ±0.05 moves building value about ±7 %.
  The flats figure traces to the cost research's surface-utile conversion; the
  houses figure is a desk estimate.
- **One cost per commune fits house-dominated suburbs poorly.** Outer-ring house
  communes (Santeny 33 %, Vaujours 34 %) take the inner-ring collectif cost; a
  per-type cost (EPTB for houses) is the likely fix. Panel communes outside the
  Paris and Lyon areas still use uncalibrated pilot costs.
- **Small-commune outliers** (Fleurieu-sur-Saône 75 %) may reflect thin DVF samples
  or BD TOPO annexes; worth checking before they are quoted.
- **Non-residential parcels borrow the flat price and ratios.** No open cost series
  exists for sheds or shops; the ±10-point band bounds it, but per-commune rows
  with large industrial land (Feyzin) are fragile.
- **Current-tax baseline within built parcels** still spreads the produit by floor
  area, ignoring cadastral category and weighting coefficients — the per-parcel VLC
  in the Fichiers fonciers is the real resolution. Exemptions beyond obvious public
  property (HLM art. 1384 A, QPV abatement) are not yet modelled.
- **Maintained-stock parameters are judgement calls** (30-year cap, 1.2–2.5 ramp),
  informed by the literature but not estimated; a DPE condition signal would ground
  effective age in the building rather than the neighbourhood price.
- **Building-less public and industrial land** is still priced as residential
  building land where the exemption rule does not reach it (Paris UV parks partly,
  Port Édouard Herriot, Feyzin's chemical valley).
- **Income data limits.** Filosofi 2021 is the last vintage, IRIS income exists only
  for communes of 5 000+ inhabitants, and small communes cannot form five quintiles,
  so no income chart is published for them.
- **DPE selection bias.** DPE covers diagnosed residential dwellings, for both the
  construction-era anchor and the habitable-area measurement.
