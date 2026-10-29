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
  Costs are calibrated per m² of true gross area and divided by the habitable ÷
  true-gross ratio they assume (0.71 flats, 0.82 houses); the land share then
  depends on that ratio, not on the measured one, which only sets euro levels.
  Each building type takes the cost of its own evidence: flats and other
  buildings the DHUP/SISAL collective social-housing cost (Paris 2 650, inner
  ring 2 400, Lyon 2 000, Lyon ring 1 850), houses the SDES EPTB new-house survey
  brought to a turnkey basis (Paris 2 300, inner ring 2 100, Lyon 2 400, Lyon
  ring 2 250), non-residential buildings a type-specific ratio to the collective
  cost, VAT excluded for businesses (warehouse 0.25, retail box 0.47, office
  0.83). Housing depreciation is market-conditional: where IRIS prices far exceed
  rebuild cost, effective age is capped at 30 years (maintained stock);
  construction eras come from DPE, which dates dwellings only. Other buildings
  have their own lives (sheds 40 years) and, undated, sit at mid-life.
- **land value** = classify-then-price. Built parcels take the residual, except
  those dominated by sheds, retail boxes, farm, sports or garage buildings: they
  rarely sell and match no residential price, so they take depreciated
  replacement cost (land at the local building-plot price, × 0.45/0.35 for
  business land, building at depreciated cost). Building-less parcels are
  classified by legal constructibility (GPU zoning) and priced against
  terrain-à-bâtir comparables or SAFER farmland. Unbuilt A/N land is then
  left out of the reform: it keeps today's TFPNB (decision D6, 2026-10-29).
  That was nearly free in revenue terms (1 % of the levy in Cahors) but it
  changes the published picture in rural communes, where farmland parcels
  outnumbered the built stock and dominated "who pays more".
- **current tax** = the commune's real REI foncier-bâti produit, split between
  industrial establishments, professional premises and housing in the
  commune's official proportions (rebuilt from REI aggregates: the State's
  compensation for the 2021 industrial halving, and the CFE professional base
  scaled to the national total), then by floor area within each group; shops
  below flats count as professional. Public property obviously exempt under
  CGI 1382-1° (DGFiP *personnes morales* files, conservative ownership rule) and
  farm buildings under CGI 1382 6° (BD TOPO agricultural use, greenhouses, sheds
  in farmland zones) bear nothing today and nothing under the LVT.

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
  calibrating costs brought Paris to 74 % with only 3 % of built parcels at the
  clip: the land share is now measured, not set by the bound. With the
  non-residential fixes Paris is 76 %, Lyon 60 %, rings 65 % / 55 %; Gemini judges
  these consistent with French evidence.
- **A wrong-looking commune is not always the parameter it looks like.** House-
  heavy outer-ring communes sat at 33–38 % land share, which pointed at the house
  cost. A separate house cost was right (around Paris ~13 % cheaper per m² than a
  flat; around Lyon, surprisingly, ~20 % dearer) but moved them 2–4 points:
  houses were a third or less of their building value. Decomposing by category
  found three non-residential errors stacked on each other: tall single-storey
  sheds imputed as five storeys from their height (the Villepinte exhibition hall
  counted 828 000 m² of floor on a 165 000 m² footprint), farm greenhouses taxed
  and valued as housing, and every shed priced at the flat price and the housing
  cost. Fixed in turn, they lift Santeny 36 → 52 % and Vaujours 36 → 50 %.
- **The baseline error ran the other way from the one we expected.** Once
  industrial land was valued at business-land prices (Lyon ring €8.6bn → €3.8bn),
  industry's LVT share fell, and we and Gemini read the −55 % industrial cut as
  a floor-area baseline overstating what factories pay today. Calibrating the
  baseline to official REI shares showed the opposite: business pays *more* per
  m² than housing (fixed plant in art. 1499 values; professional premises on
  2013 rents vs housing on 1970 values), so the cut deepens (−63 %) and the
  Lyon ring's poorest fifth goes from −3.7 % to +0.6 %. Taxing plant moves this
  only 1–3 points across a ring (up to 14 in a single industrial commune): in an industrial corridor the LVT genuinely shifts tax from
  capital-heavy industry on cheap land to households. Expectations, including
  a reviewer's, are hypotheses to test against data.
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
- **The professional-premises share of today's tax is now the load-bearing
  uncertainty.** The open proxy (CFE base) misses vacant premises and non-CFE
  occupiers and captures ~40 % nationally; it is scaled ×2.5 to the Cour des
  comptes total. At the raw proxy (×1.0) every household quintile gains 10–15
  points more (Paris −27.6/+3.9 vs −17.4/+18.9). New bills are the same either
  way; only the starting point moves. One national multiplier cannot fit every
  commune; the per-parcel VLC in the Fichiers fonciers is the real fix. HLM
  (art. 1384 A) and QPV abatements are not yet modelled either.
- **Whether a reform should tax industrial plant is a policy choice.** Today's
  industrial base includes fixed installations; the modelled LVT taxes only the
  shed. Estimated from REI, adding plant moves industrial bills by 1–3 points
  across a ring, more in single industrial communes (Saint-Fons 8,
  Tremblay-en-France 12, Marcy-l'Étoile 14 at gross cost). The project lead
  has decided the reform taxes land and buildings, not plant.
- **Non-residential costs rest on one commercial guide** scaled to our housing
  level (±25 %), the business-land ratio on 20–80 sales per area, and offices
  still read the residential price surface, which overstates distressed suburban
  office markets (La Défense). Mixed parcels follow their largest building.
- **The house cost rests on a survey of new catalogue houses.** The finishing-work
  uplift is a judgement, and Lyon coming out dearer than the Paris ring is
  probably a sample effect (bespoke Rhône houses vs outer-IdF catalogue houses).
  Panel communes outside the Paris and Lyon areas keep their single pilot costs.
- **The 40–65 % band is a metro-wide reference, not a per-commune test.** 48
  communes now sit above it, nearly all contiguous to Paris (itself 76 %), where
  Gemini judges 65–75 % normal; only Cahors is below. Neuilly (78 %) and
  Fleurieu-sur-Saône (72 %) remain the ones to check.
- **Maintained-stock parameters are judgement calls** (30-year cap, 1.2–2.5 ramp),
  informed by the literature but not estimated; a DPE condition signal would ground
  effective age in the building rather than the neighbourhood price.
- **Building-less public and industrial land** is still priced as residential
  building land where the exemption rule does not reach it (Paris UV parks partly,
  Port Édouard Herriot); built industrial land now takes the business-land price.
- **Income data limits.** Filosofi 2021 is the last vintage, IRIS income exists only
  for communes of 5 000+ inhabitants, and small communes cannot form five quintiles,
  so no income chart is published for them.
- **DPE selection bias.** DPE covers diagnosed residential dwellings, for both the
  construction-era anchor and the habitable-area measurement.
