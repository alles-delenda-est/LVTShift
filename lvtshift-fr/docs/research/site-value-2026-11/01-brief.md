# Research brief: land value of built parcels by plot area, not floor area

## Project
LVTShift-FR models a revenue-neutral shift of the French taxe foncière (TFPB) per commune onto land value. It is a 4:1 split: land is taxed at four times the building rate. It uses French open data only and publishes aggregates only (by property category, by income fifth, per commune), never per-parcel figures. The French fork is in `lvtshift-fr/` (read `lvtshift-fr/THEORY.md` and `lvtshift-fr/METHODOLOGY.md` §3).

## How land value is imputed today (`lvtshift-fr/estimate.py`, `_land_value_classified`)
- **Market value** = hedonic €/m² × habitable floor area. The €/m² is the median log €/m² of DVF sales per 400 m grid cell × type (house or flat), shrunk towards the commune median. **There is no plot-size term.**
- **Building value** = construction cost per m² × habitable floor area × depreciation (by age and type).
- **Built parcels: land = market − building**, floored at the agricultural value of the plot, and with the land *share* clipped to 15–85 %. Because both sides scale with floor area, land = (P − C·d) × floor area: land value is proportional to the *existing* floor area, and the plot area hardly matters.
- **Exceptions where the plot area is used:**
  - vacant buildable land (terrain-à-bâtir €/m² from DVF × plot area);
  - sheds, retail boxes and similar buildings, valued at depreciated replacement cost (DRC), whose land = building-plot €/m² × plot area;
  - farmland at SAFER €/m².

## The problem (confirmed by an independent check)
- Within each IRIS, over built residential parcels, the elasticity of imputed land value is +0.03 to +0.17 with respect to plot area, against +0.75 to +0.91 with respect to building value.
- So a 10-storey block on the same plot as a 1-storey house gets about 10× the house's land value. And within a 400 m cell, a house on 1,000 m² and one on 200 m² with the same floor area get the same land value.
- The model therefore measures land in its *current use*, at the existing density, not the *site value* that an LVT is meant to tax. It **mutes the LVT's defining shift onto under-used land** (low buildings on valuable plots).
- Commune totals are unaffected, but category and income results are. In a crude bracketing test, land of built residential parcels was reassigned in proportion to plot area within each IRIS, keeping each IRIS's total. Effects on the land tax step:
  - large blocks ±2 points;
  - income fifths ±2–4 points;
  - **houses −7 to −15 points, with an unstable sign** (56 % of Paris houses hit a 95 % share cap);
  - small 2–4-dwelling buildings up to +25 points.
- That test is in `probe2.py`; the per-parcel loader is `decomp2.py` in the same folder. The earlier report is `reval_opus_report.md` there.

## Open data that could help (to check)
- **DVF:** sale price, `surface_reelle_bati`, `surface_terrain` (plot area of a house sale), terrain-à-bâtir sales, nature de culture. The pipeline already fetches DVF.
- **SDES EPTB** (enquête sur le prix des terrains à bâtir): €/m² of plot for individual house plots, by department and region, by plot size.
- **Cerema DV3F / "prix des terrains"**, and the Notaires' **charge foncière** (land price per m² of permitted floor area, the developer's residual "compte à rebours").
- **GPU** (Géoportail de l'urbanisme): PLU zone types (U/AU/A/N). Are prescriptions such as height, emprise au sol or CES available in structured form anywhere?
- **BD TOPO:** building footprint and height. **Cadastre:** plot area. **IRIS** boundaries.

## The questions
1. **Concept.** What land value should a split-rate or land value tax use: land in its current use, or site value assuming the land is vacant at its highest-and-best or permitted use?
   - What do the literature and practice say? Examples: Dye & England (Lincoln Institute); IAAO standards on mass appraisal and land valuation; Pennsylvania split-rate cities; NSW and other Australian states (site value); New Zealand; Denmark (grundværdi, 2024 reform); Germany (Bodenrichtwerte; Baden-Württemberg's Bodenwertmodell under the 2025 Grundsteuer reform: standard land value × plot area); Estonia; UK and Scottish LVT studies.
2. **Methods.** How do mass appraisal and research impute land value for built parcels?
   - Land residual/abstraction, allocation, sales comparison of vacant land with lot-size adjustment curves, and hedonic models with plot size and interactions ("land leverage": Bourassa et al.; Davis & Heathcote; Davis, Larson, Oliner & Shui 2021; Albouy, Ehrlich & Shin 2018; Haughwout et al. for NYC).
   - What are their known biases, especially at high density?
   - How do they treat flats in copropriété (land shared among units)?
3. **French specifics.**
   - How do French practice and statistics value land under buildings? Examples: Insee/Banque de France national accounts for land under dwellings; the Notaires' charge foncière (€ per m² of permitted floor area); EPTB; Cerema; French LVT proposals (CAE notes, Trannoy & Wasmer, the Sénat).
   - Is permitted density (PLU) available as open data in structured form?
4. **Candidate designs for this model**, all from open data, revenue-neutral, aggregate publication:
   - (a) Keep the residual for each IRIS's total land, but allocate it within the IRIS by plot area (a "standard land value per m² of plot" zone, like the Bodenrichtwert), with zoning and lot-size adjustments.
   - (b) Land = local land €/m² of plot (from terrain-à-bâtir and DVF house sales with `surface_terrain`) × plot area, reconciled with the residual at IRIS level.
   - (c) A hedonic on DVF house sales with a log plot-area term, to estimate the marginal value of plot area, applied to houses. Flats get a share of the plot.
   - (d) Permitted-density site value (charge foncière × permitted floor area), if data allow.
   - (e) Hybrids, or bounding with a published sensitivity band.

   For each: data feasibility, known biases, how to validate against observed prices, and what would change in the published results.
5. **Validation.** What observable tests could tell us which method is closer to the truth?
   - Examples: the price gradient on plot size in DVF house sales within a cell; terrain-à-bâtir prices per IRIS against implied land €/m² of plot; EPTB department averages; land shares in the national accounts.
