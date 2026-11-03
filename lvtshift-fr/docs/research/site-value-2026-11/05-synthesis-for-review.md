# Proposed fix for land value of built parcels (LVTShift-FR): please critique

## Context
LVTShift-FR models a revenue-neutral 4:1 split-rate shift (land taxed at 4× the building rate) of the French TFPB, per commune, from open data. It publishes aggregates only.

Today, built parcels get:
- **market value** = hedonic €/m² (400 m cell × house/flat, no plot term) × habitable floor area;
- **land** = market value − depreciated construction cost, with the land share clipped to 15–85 %.

So land scales with existing floor area, not plot area.

## Evidence gathered (two independent research agents, one of them on the model's own data)
1. **Concept.** Working LVTs value site value: land as if vacant, at its permitted or zone-typical use. Examples: Germany (BauGB §196, ImmoWertV §40), Baden-Württemberg's 2025 tax (plot area × Bodenrichtwert), NSW, Denmark, Wales; also Dye & England (Lincoln Institute).
   - Denmark prices apartment land per m² of floor on the higher of actual and permitted floor area, so a density link is accepted practice.
2. **Literature elasticities.** Plot price rises about 0.3 % per 1 % more area at the median French house plot (Combes, Duranton & Gobillon, EPTB). Land per m² of plot rises about 0.5 % per 1 % more FAR (German GFZ conversion tables). Davis et al. (FHFA) find the residual method understates land under old structures.
3. **DVF house sales**, 8,591 of them in Paris, Lyon, Villeurbanne, Montreuil, Roubaix, Aulnay-sous-Bois, Ormesson-sur-Marne, Cahors and Figeac; the plot area matches the cadastre for 93–99 % of sales.
   - Within a 400 m cell, the price elasticity with respect to plot area is 0.12–0.34 (pooled 0.23), holding floor area and age fixed.
   - Taking (price − model building value) as market land, its elasticity with respect to plot area is about 0.46, and with respect to floor area about −0.13. The model's is about 0 for plot area and about 1.0 for floor area.
   - The level matches: market land share on sales 0.62, model 0.62.
4. **DVF flat sales** (about 190,000). Within a cell, price per m² does not vary with the building's plot per m² of floor (elasticity −0.005 ± 0.003). So floor-area-proportional land for flats matches what buyers pay.
5. **Classification problem.** In the house category ("Single Family Residential", ≤ 1 dwelling), a fifth of Paris parcels have a building value above €1.5 m and carry 80 % of the category's current tax (Lyon 67 %, Villeurbanne 62 %, Montreuil 47 %). These are large buildings recorded with one dwelling or none, so the published "house" figures mostly describe them.
6. **Designs tested** (re-solved at 4:1; error = median absolute log error of modelled value against sale price within a cell, on sales not used to calibrate):

| Design | House error | Flat error |
|---|---|---|
| Published | 0.246 | 0.124 |
| (a) IRIS land total reallocated by plot area across all residential | 0.22 | 0.18–0.20 |
| (c) House hedonic with a plot term | 0.262 | 0.124 |
| **Recommended:** IRIS house land total reallocated among houses ≤ 300 m² by plot^γ, γ = 0.3–0.5 | 0.180–0.185 | 0.124 |

   - Building-plot comparables × area are 4–9× too low in dense cities.
   - Plot-based land exceeds today's modelled market value for 8–40 % of city houses even within the house-only pool. That suggests the published market value undervalues small houses on decent plots.
7. **Robustness.** These survive every design:
   - the poorest fifth pays less (group total and household median);
   - the richest fifth's group total rises;
   - business and industry pay less.

   These do not survive:
   - the sign for houses in several communes;
   - small 2–4-dwelling buildings (+20 to +90 points under site-value variants);
   - large blocks flat in Paris and Lyon (−3 to −15 under site value);
   - the richest fifth's household median rising (turns negative in Villeurbanne and Montreuil under site value).

## Proposed plan (separate PRs)
1. **Fix the house classification**: large single- or no-dwelling buildings move out of "houses", by floor-area threshold and building use.
2. **Houses ≤ 300 m²**: keep each IRIS's house land total, reallocate it by plot^0.35 (band 0.3–0.5), and set market value = land + building cost, with no land-share cap. Report how many exceed the old market value.
3. **Flats, blocks and other buildings**: keep the residential residual.
4. **Publish a "site value" upper band**: zone-typical density, separate house and block pools, no cap. Label it a concept variant that can't be checked against sale prices.
5. **Validation**:
   - Main test: teardown sales (DVF sales followed by a demolition or building permit on the same parcel, from the SDES Sitadel permits).
   - Also: house price errors by plot-size decile; EPTB benchmarks.

## Questions
1. Is the central case defensible, given that it is the current-use land value the data can check, with site value as an upper band? Or should the central case be site value, as LVT practice implies?
2. Is γ = 0.35, estimated from French house sales, sound? Note that a sale-price plot coefficient measures marginal garden value (Glaeser & Gyourko), not site value.
3. Holding IRIS totals fixed while reallocating within them: is it sound? What are the risks, for example IRISes dominated by large blocks with only a few houses?
4. Removing the land-share cap for houses: what are the risks, and what guardrails are needed?
5. Is the 300 m² threshold, plus building use, a reasonable way to separate real houses from large single-owner buildings? Better open-data signals: BD TOPO usage and nombre de logements, the RNB, the BDNB?
6. Anything missing or wrong? Please rank the issues.
