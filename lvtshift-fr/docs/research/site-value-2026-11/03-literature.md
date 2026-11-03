# Land value of built parcels: literature and practice review for LVTShift-FR

*Questions 1, 2, 3 and 5 of `landvalue_brief.md`, plus the literature side of question 4. Prepared 2 November 2026. No repo files were changed.*

---

## 0. Bottom line (for Patrick)

1. **Concept.** Every working land value tax I could check values land **as if it were vacant**, at the use that planning rules allow and the market would pay for. That is *site value*, not land in its current use. This holds for Germany (BauGB §196, ImmoWertV §40), Baden-Württemberg's 2025 Grundsteuer, NSW, Denmark and Wales, and it is IAAO practice. Dye & England (Lincoln Institute) state the reason plainly: a land tax is neutral only if the taxable value is "independent of its current use". The current model measures land at its existing density, so by construction it **mutes the shift onto under-used land**. That is a conceptual gap, not a tuning issue.
2. **But "site value" is not "plot area × one price".** Practice and evidence agree on two refinements:
   - **Land value rises with plot size much less than proportionally.** In French building-plot sales (EPTB), the elasticity of total plot price to plot area is about **+0.3 at the median plot**: +0.45 at 477 m² and +0.1 at 2,000 m². This is derived from Combes, Duranton & Gobillon.
   - **Land value per m² of plot rises with permitted density, at roughly the square root.** The official German conversion table gives an elasticity of about **0.5** with respect to floor-area ratio (GFZ).

   So the current model (elasticity about 1 to existing floor area, about 0 to plot area) and the brief's crude test (1 to plot area, 0 to density) are **two extremes**. The evidence points between them.
3. **Recommendation, in ranked order:**
   - **(i) First, a plot-area term in the house price model (design c).** This is a fix to an observable error, and high confidence.
   - **(ii) Then, within each IRIS, reallocate the residual land total by a weight of (plot area)^β × (reference density)^θ**, with β ≈ 0.3–0.6 and θ ≈ 0.5. Reference density means the higher of actual and zone-typical density, as in Danish practice ("actual or possible"). This is a hybrid of (a) and (e), at moderate confidence.
   - **(iii) Publish the current method and the pure plot-area allocation as the bounds of a sensitivity band.**
   - **(iv) Permitted-density site value (design d) is feasible only for Paris and Lyon** (they publish structured height and CES layers). Elsewhere it is not feasible, because France has no structured national data on permitted density.
4. **The best open-data test is "teardown" sales.** These are DVF sales of built parcels followed by a demolition or building permit on the same parcel; SDES permit lists carry cadastral parcel references back to 2013. Their price is close to pure site value. That is the test Davis et al., Haughwout et al. and the Danish land-value curve all lean on.

---

## 1. Concept: current-use land value or site value?

### 1.1 What mainstream practice does

| Jurisdiction / source | What the land is valued as | Treatment of what stands on it | Source status |
|---|---|---|---|
| **IAAO Standard on Mass Appraisal** (2017, reprinted Feb 2022) | Highest and best use (HBU): "legally permissible, physically possible, appropriately supported, and financially feasible". Zoning "normally dictate[s]" the HBU of vacant land. The standard warns of "properties in transition, interim or nonconforming uses … and excess land". | §4.5: sales comparison is "the primary approach to land valuation and is always preferred". In the absence of adequate sales, the alternatives are allocation, abstraction, anticipated use, ground-rent capitalisation and land-residual capitalisation. §4.6.5: subtracting RCNLD (replacement cost new less depreciation) from improved sales "tends to work best for relatively new improvements". | **Opened** (PDF) |
| **Germany: BauGB §196(1)** (Bodenrichtwerte, the standard land values) | "In bebauten Gebieten sind Bodenrichtwerte mit dem Wert zu ermitteln, der sich ergeben würde, wenn der Boden unbebaut wäre." (In built-up areas, standard land values are set at the value the land would have if it were unbuilt.) Zones are drawn over areas that "nach Art und Maß der Nutzung weitgehend übereinstimmen" (largely alike in type and intensity of use). The reference plot's characteristics, density included, are published. | As if unbuilt. | **Opened** (gesetze-im-internet) |
| **Germany: ImmoWertV 2021 §40** | §40(1): the land value is set "ohne Berücksichtigung der vorhandenen baulichen Anlagen" (without regard to existing buildings), primarily by comparison, or by an adjusted Bodenrichtwert (§40(2)). §40(3): deductive methods are allowed if comparables are lacking. §40(5) Nr. 1: for built plots, "ein erhebliches Abweichen der tatsächlichen von der … maßgeblichen Nutzung" (a substantial gap between actual and relevant use) is taken into account where the market does so. Nr. 3: demolition-ripe property follows §43. | As if unbuilt, but lawful excess or deficient use can be recognised if the market recognises it. | **Opened** |
| **ImmoWertV §19, §41** | §19: conversion coefficients ("Umrechnungskoeffizienten") adjust for "Maß der baulichen Nutzung oder der Grundstücksgröße und -tiefe" (intensity of use, plot size and plot depth). §41: where a plot "erheblich" exceeds the usual size, the surplus area may be valued separately. | Plot-size and density adjustments are formal parts of the method. | **Opened** |
| **Baden-Württemberg Landesgrundsteuergesetz §38** (2025 Grundsteuer) | Grundsteuerwert = plot area × Bodenrichtwert. The City of Stuttgart says: "Auf die Bebauung kommt es dabei nicht an" (buildings play no part), and differences between the reference plot and the actual plot "werden nicht berücksichtigt" (are not taken into account). §38(4) lets an owner prove, with a qualified appraisal, that value deviates by more than 30 %. | Pure site value with no density or size adjustment. It is crude by design, with a 30 % appeal valve. Search results report that the BFH upheld the law on 20 May 2026 (II R 26/24, II R 27/24). | Stuttgart page **opened**; statute text, 30 % clause and BFH ruling from **snippets** |
| **NSW Valuer General** | Valuers consider the "most valuable use of the land" with "zoning, heritage restrictions, and other use constraints". Sales are adjusted to "remove the added value of improvements (such as buildings)". | As if vacant. For strata (condominium) sites: one land value for the whole site; "each unit's land value is a portion of the whole strata scheme's land value … based on the unit entitlement". | NSW gov pages **opened**; Valuation of Land Act s6A **not opened** (403) |
| **Denmark, houses** (Den Juridiske Vejledning 2026-2, H.A.5.2.2) | The land-value curve ("grundværdikurve") is built from sales of undeveloped plots *and properties bought for demolition*. A standard 1970 house is placed on the **actual plot** ("Standardhuset tillægges den faktiske grundstørrelse"). The result is then adjusted for the use the plan permits and for unused development potential. Only the first 5,000 m² takes the house curve; the rest is valued as recreational land. | Site value at the plan-permitted use. The plot-size effect comes from the curve. | **Opened** (tax.dk) |
| **Denmark, apartment buildings** (EVL §19 a; H.A.5.2.3.1.1 and H.A.5.5.3.1) | Applies "uanset EVL §15" (notwithstanding §15). Land = "grundværdien pr. kvadratmeter boligareal" (land value per m² of residential area) × "det faktiske eller mulige boligareal" (actual *or possible* residential area). The per-flat land value is a standardised flat value minus a standardised building value. Unused permitted floor area is added from Plandata.dk. | **A hybrid.** Land is priced per m² of floor (a charge-foncière logic) on the higher of built and permitted area. The guidance says this method "begrænser metodefriheden" (limits the agency's freedom of method). | **Opened** |
| **Wales** (Bangor 2020; Welsh Government 2026) | 2020: "Site value should form the conceptual basis", meaning the value at which "a comparable but empty site would transact". 2026 feasibility work: land = (model price of a representative property ÷ representative plot size) × 0.3 × parcel area, explicitly a "notional value". | Site value, implemented as zone €/m² × plot area with a flat 30 % land share. The VOA found individual open-market land values "not feasible" at scale. | **Opened** (both PDFs) |
| **Dye & England** (Lincoln Institute, 2010) | "for a tax to be neutral with regard to the timing of development, it is also necessary that the taxable value of land be independent of its current use and instead be based on its 'highest and best use'". | Allocation "cannot provide the assessment data that a two-rate system … needs". Abstraction (extraction) is "the most common approach" and needs subjective depreciation judgements. CAMA (computer-assisted mass appraisal) contribution models break value into "location, lot size and shape, building square footage…". | **Opened** (PDF) |
| Estonia | Land-only tax. Land is mass-valued with statistical models, every 4 years from 2022. | Land only. | **Snippets only** (Land Board page returned 403) |
| New Zealand | Rating Valuations Act 1998 s2 defines land value as the sum the owner's interest "might be expected to realise". | Unimproved. | **Snippet only** (403) |
| Mirrlees Review, ch. 16 | Recommends an LVT on business and agricultural land. | Not verified. | **Snippet only** (PDF not retrievable) |

### 1.2 Verdict

**Mainstream practice values site value**: land as if vacant, at the use that planning rules allow and the market would pay for. The economics are clear on why (Dye & England). Value land at its current use and the tax rises when an owner builds more, so it becomes a disguised tax on buildings and loses its neutrality and its incentive effect.

Two qualifications matter for France:

- **"Highest and best use" in practice means "permitted use, at typical intensity for the zone".** It is not speculative maximum use. German standard land values are defined for the typical "Art und Maß der Nutzung" (type and intensity of use) of their zone. Denmark reads permitted floor area from its planning register. NSW uses zoning. France's PLU (local zoning plan) is a binding regulation, so it is closer to the German and Danish settings than to Wales's discretionary planning system. The concept is therefore legally workable in France. The data are the obstacle (§3.4).
- **Lawful existing density above or below the norm is not ignored.** Germany admits it where the market does (§40(5)). Denmark uses the higher of actual and possible floor area for apartment buildings. A 10-storey block in a zone where 4 storeys is now typical can therefore carry more land value than its neighbour, **but much less than 10×** (§2.4).

**Implication for the model.** The current imputation is a *current-use* land value: land is roughly proportional to existing floor area. That suits the national accounts (which want current-use wealth). It does not suit an LVT incidence study, whose central question is how much tax moves onto under-used land. The fix should make land value, within a location, depend on (a) plot area with diminishing returns and (b) a reference density, meaning the higher of actual and zone-typical density, with an elasticity well below 1.

---

## 2. Methods for imputing land under buildings, and their biases

### 2.1 Sales comparison of vacant land (the preferred method)

- **Practice.** IAAO §4.5 and §4.6.5: sales are posted on maps, standard unit values are derived (per m², per front foot, per parcel) and turned into land value maps or tables. The German Bodenrichtwert and the NSW component method are this method at scale.
- **Plot-size curve ("plattage").** Price per m² falls as plots get larger.
  - *Combes, Duranton & Gobillon (IZA DP 7027, 2012; published in REStud 2019).* They use 27,850 EPTB building-plot purchases completed in 2008 in mainland urban areas. Their preferred first-step regression of log price per m² has "log parcel area" = **0.93** and "squared log-area" = **−0.12**, with 345 urban-area fixed effects and log distance (Table 3, column 5). Log area and its square "matter most": without them the R² falls from 48 % to 10 %. The authors note that price per m² is "bell-shaped" with a small peak, so prices per m² "generally decline with parcel area". Median plot: 838 m².
  - *My derivation from those coefficients.* The elasticity of total plot price to area is 1 + 0.93 − 0.24·ln(A): **+0.45 at 477 m²** (1st decile), **+0.31 at 838 m²** (median), **+0.11 at 2,000 m²** (9th decile). Please check this arithmetic before using it.
  - *Other evidence.* Davis, Larson, Oliner & Shui (FHFA WP 19-01; JME 2021) standardise land prices to a quarter acre because "the price of land per acre tends to fall as acreage increases, the so-called 'plattage effect'". Germany's §19 coefficients and §41 surplus-area rule, and Denmark's 5,000 m² cap, embody the same idea.
- **Biases.**
  - *Selection.* Vacant lots in dense cores are few and atypical: leftovers, odd shapes, lots awaiting a permit. EPTB covers only individual-house plots in the diffuse sector, so it says nothing about collective-housing land.
  - *Composition.* Within a city, larger plots are farther out. Combes et al. note that parcel area "is likely to reflect local zoning and development patterns".
  - *Unbuildable area.* Combes et al. warn that "the area of a parcel does not reflect the area that is actually constructible" (slopes, partly unzoned parcels).

### 2.2 Abstraction (extraction, residual): what the model does now

- **Practice.** Land = total value − depreciated building cost. Dye & England call it "the most common approach". IAAO says it works best for new buildings.
- **Bias 1: underestimates land under old or under-used buildings.** Davis et al. built a teardown-option model. In it, the true land share rises from 30 % (new house) to **100 % at teardown**, while the residually measured share reaches **only about 60 %**: at teardown it is 30 − 10.8 = 19.2 instead of 30. The two agree only for buildings younger than about 20 years (41.6 % against 39.2 % at 20 years). They therefore keep only appraisals with effective age ≤ 15 years. The bias falls on **exactly the properties an LVT is meant to reach**: low, old buildings on valuable land.
- **Bias 2: sensitive to inputs.** Wales 2026: the residual "is highly sensitive to a number of input assumptions, such that a small change in the cost of materials and labour can change the land values from positive to negative". The THEORY.md finding that a ±0.05 net-to-gross ratio moves building value by about ±7 % is the same issue.
- **Bias 3 (specific to this model): the market value cannot see the plot.** Market value = €/m² of floor × floor area. Two identical houses on 200 m² and 1,000 m² therefore get the same market value, and so the same residual land. This error sits in the **observable** step: DVF prices can test it and correct it. Design (c) addresses it.
- **Bias 4: at high density the residual becomes current-use land.** Land = (P − C·d) × floor area, so land is proportional to existing floor area. Denmark does this *deliberately* for apartment buildings (land per m² of residential area), but on the **higher of actual and possible** floor area. The model takes only the actual area.

### 2.3 Allocation (a fixed ratio)

Dye & England: allocation "makes the arbitrary assumption that land values are the same fixed percentage of total value for each and every property" and "cannot provide the assessment data that a two-rate system … needs". Even so, the Welsh 2026 VOA (Valuation Office Agency) feasibility study fell back on a heuristic 30/70 split, because "neither approach (nor a combination of them) can be sensibly applied at scale to produce individual land valuations defensible … as representing open-market values". The lesson is that **administrations end up with notional, rule-based land values**, which strengthens the case for a transparent rule in this model.

### 2.4 Hedonic models with plot size, and "land leverage"

- **Intensive and extensive margins.** Glaeser & Gyourko (FRBNY EPR 2003) compare two measures. The hedonic value of extra lot area is the *intensive* margin: what a homeowner pays at the margin for more garden. Price minus construction cost, per acre, is the *extensive* margin: the value of a plot with a house on it. In regulated markets, "the hedonic estimates produce land values that often are about 10 percent of the values calculated with the extensive methodology".
  - **Implication for design (c):** a DVF hedonic coefficient on plot area measures the *marginal* garden value. It must not be read as the average land price per m². Its legitimate use is as an *allocator* (the shape of land value against plot size), with the level anchored elsewhere.
- **Hybrid decomposable models.** IAAO: models "decomposable into land and building values" can be calibrated from improved sales, but separation "is more reliable when both vacant and improved sales are available". The Danish curve is the working example: vacant and teardown sales fix the level, and a standard house on the actual plot gives the shape.
- **Land leverage.** Bourassa, Hoesli, Scognamiglio & Zhang (RSUE 2011, Swiss single-family homes, *abstract only*): the land share (land leverage) varies across locations and drives price dynamics. Davis et al. confirm that land prices per acre are "negatively correlated with lot size and … positively correlated with the size of the housing structure". The second point is a reminder that a hedonic must not attribute a location effect to the building.
- **Density.** The WertR 2006 Anlage 11 conversion coefficients for residential land (valid to 31 Dec 2021, now superseded by the regional coefficients of the Vergleichswertrichtlinie) are: GFZ 0.4 = 0.66, 1.0 = 1.00, 2.0 = 1.45, 2.4 = 1.61 (table opened on haufe.de).
  - **My derivation:** the elasticity of land value per m² of plot to GFZ is **≈0.45 below GFZ 1 and ≈0.54 above**; over a 6× density range, land per m² of plot rises 2.4×.
  - *Illustration:* a block at GFZ 3 next to a house at GFZ 0.3 (if both densities are lawful) should carry about 10^0.5 ≈ **3×** the house's land per m² of plot. That is far from the **10×** the current model implies, and from the **1×** the crude plot-area test implies.
  - Ahlfeldt & McMillen (REStat 2018, Chicago, *snippets only*) estimate land-price and height elasticities. They are relevant background but not a direct calibration.

### 2.5 Flats in copropriété

- **Practice is consistent.** Value the whole site once, then apportion it among units:
  - NSW: by unit entitlement;
  - Denmark: per flat, from a standardised flat, plus a share of unused floor area;
  - Germany: by Miteigentumsanteil (co-ownership share). This is standard German practice, but I did **not** open a primary source for its BW Grundsteuer treatment.
- **France.** Loi 65-557, art. 5 (seen in snippets; the text was amended with effect from 1 June 2020, so check the current version) makes the share in the common parts, the tantièmes, proportional to each lot's relative value from "consistance, superficie et situation".
- **For this model:** apportioning a building's land by floor area, or by dwelling, is consistent with practice. Because results are published only in aggregate, the within-building split matters only for income fifths (dwelling-weighted). **The issue for flats is the building's total land, not the split.**

---

## 3. French specifics

### 3.1 National accounts (Insee / Banque de France)

*Insee Première* n° 2081 (6 Nov 2025, "Le patrimoine économique national en 2024"; opened):

- Built land ("terrains bâtis"): **€6,729 bn** at end-2024 (−2.7 % in 2024). Households hold €4,043 bn.
- Dwellings: **€5,977 bn**. Households hold €4,807 bn.
- **My derivation:** land share for the household sector ≈ 4,043 / (4,043 + 4,807) = **46 %**. Overall, 6,729 / (6,729 + 5,977) = 53 %, but that mixes land under all buildings with dwellings only.
- Method: "Les plus ou moins-values latentes sur l'immobilier sont imputées aux terrains sous-jacents" (unrealised real-estate gains are imputed to the underlying land). This is residual logic: buildings at replacement cost, land as the remainder. It is a **current-use** concept, so it suits an aggregate plausibility check, not the choice of concept.
- Comparison: Wales 2020 found residential land at 48 % of residential property value, by its own hedonic method. It notes that ONS estimates use "the residual method at an aggregate level".

### 3.2 EPTB (SDES survey of building-plot prices)

- **Scope** (survey page, opened): permits for "un unique logement dans une maison individuelle en secteur diffus" (a single dwelling in an individual house, outside subdivisions). It has been exhaustive since 2010 and is compulsory.
- **2024 national figures** (published 27/11/2025): plot €95,000, 932 m², **€102/m²** (+1.7 %).
- **Availability.** DiDo tables 2006–2024 and regional publications by the DREALs (regional state offices); Bretagne publishes departmental tables for 2022. Answers are covered by "secret statistique". Microdata are reachable only through CASD (secure researcher access; listed, not verified).
- **Fitness for purpose.** Good for a level check of house-plot €/m² by region, and sometimes by department. Its microdata underpin the plot-size curve (Combes et al.). It does **not** cover collective-housing land.

### 3.3 DVF, DVF+ and DV3F

- **DVF (DGFiP, published on data.gouv; opened).**
  - Licence Ouverte 2.0, with two conditions: no indirect re-identification (LPF art. R112 A-3), and no indexing by external search engines.
  - Coverage: 5 rolling years, excluding Alsace, Moselle and Mayotte. Updated twice a year; last update 12 Oct 2026.
  - The geolocated version carries `surface_terrain`, `nature_culture`, `surface_reelle_bati`, Carrez lot areas and `id_mutation`.
  - Caveats: one sale can span several lines and parcels, so sales must be aggregated per `id_mutation`. Cerema's documentation says its `sterr` field is the sum of parcel sub-areas per sale (snippet).
- **DVF+ open data (Cerema / DGALN; opened):** Licence Ouverte 2.0, last updated 29 Oct 2026. Same content as DVF in a structured model; "pas de données exogènes" except cadastral geolocation.
- **DV3F** (DVF enriched with Fichiers fonciers, i.e. property-tax file data): **restricted to "ayants droit"** (eligible public bodies under an OPenIG agreement; snippet), so not available to this project without a partnership.

### 3.4 Permitted density (PLU) as open data

- **GPU (national urban-planning portal):** zone types (U/AU/A/N) are structured. Quantitative rules (height, footprint coefficient (CES), green-space coefficient) are **not** structured nationally.
  - The CNIG standard for structuring urban-planning rules (SRU, level 1, version 2026-03; opened) only splits the written rules into text blocks per zone. It has no regulatory status ("ne présente pas de statut réglementaire").
  - **Level 2**, which would model "les règles qualitatives et les règles quantitatives" for "estimation du potentiel constructible", exists only as a **draft on GitHub**.
- **Exceptions that matter for the panel:**
  - **Paris:** PLU bioclimatique layers ("Plafonds des hauteurs", "Emprises constructibles maximales", "Filets gabarit-enveloppe") are on data.gouv under **ODbL**. "Sans valeur réglementaire". Height ceilings are 18/25/31/37 m (per the PDF snippet). ODbL is share-alike: any *derived database* must also be released under ODbL. Published aggregates are a "produced work" and should be fine, but flag it.
  - **Métropole de Lyon:** PLU-H zones on data.gouv under Licence Ouverte 2.0 (updated Oct 2026), with façade heights (HBCPRINC, HBCSEC, PLAFOND), **CES**, and a green-space coefficient (CPT). Lyon and Villeurbanne carry heights in separate perimeter layers.

### 3.5 Charge foncière (land price per m² of permitted floor area)

I found **no open, systematic series**, either from the Notaires or from Cerema. What exists is scattered:

- the regional land observatory (ORF) for Île-de-France, cited in a Sénat bill: land = **41 %** of social-housing operation costs in 2023 (snippet);
- DGALN flat rates for land in off-plan purchases of social housing: 45 % in zone A bis and 35 % in zone A (snippet);
- consultants' ranges.

**An open-data proxy is feasible.** DVF includes off-plan sales (VEFA, "vente en l'état futur d'achèvement"). The developer's backwards calculation ("compte à rebours") then gives: new-build €/m² − construction cost (SISAL/DHUP, already in the model) − developer margin and fees ≈ charge foncière per m² of floor. That is a modelling step, not a published statistic.

### 3.6 Permits (for teardown detection)

The SDES lists of building permits (PC), prior declarations (DP), development permits (PA) and **demolition permits (PD)** have been open since 2013, are updated monthly, and are localised to **up to 3 cadastral parcels** (page opened; licence not stated on that page). DVF can therefore be linked to subsequent demolition or new-build permits on the same parcel.

### 3.7 French LVT proposals

These were seen only in snippets or abstracts: Trannoy & Wasmer, *Note du CAE* n° 2 (2013); Bonnet, Chapelle, Trannoy & Wasmer, "Land is back, it should be taxed, it can be taxed", *EER* 2021 (Prix Maurice Allais 2023); and Trannoy & Wasmer's 2022 book (abstract: French land wealth "7 000 milliards d'euros"). I **did not verify** how they propose to assess land, so I make no claim about their method. The Sénat material I found concerns revising the rental values (VLC), not land assessment.

---

## 4. The candidate designs: what practice and literature say

Shorthand: within an IRIS, weight wᵢ = Aᵢ^β × Dᵢ^θ, where A is plot area and D is reference density (floor-area ratio).

| Design | Closest practice | Known biases | Data in France | How to validate | Likely effect on published results |
|---|---|---|---|---|---|
| **(a) Keep each IRIS's residual total; allocate within the IRIS by plot area** (β = 1, θ = 0; zoning and size adjustments optional) | BW Grundsteuer (area × Bodenrichtwert); Wales 2020/2026 (zone €/m² × polygon); NSW components | (1) The IRIS total stays a current-use residual, which understates IRIS full of under-used land (Davis et al. teardown bias). (2) Linear in area ignores plattage: the evidence says β ≈ 0.3–0.5 for house plots. (3) Without a density term, dense blocks and pavillons in the same IRIS get the same €/m², contrary to German conversion coefficients. This produces the observed **cap hits** (land > 95 % of market value). For a house, land cannot sensibly exceed market value plus demolition cost, so mass cap hits are evidence against β = 1, θ = 0. | Fully feasible (cadastre, BD TOPO, GPU zone types, IRIS). | T1, T3, T4, plus the land ≤ market value constraint (§5). | Upper bound for the shift onto houses (the brief's crude test: houses −7 to −15 points, unstable). **A bound, not the central case.** |
| **(a′) As (a), but w = A^β × D^θ** with D = max(actual, zone-typical density) | Germany (Bodenrichtwert + §19 coefficients for GFZ and size + §41); Denmark (curve with plot size; "actual or possible" floor area) | β and θ are borrowed (EPTB/CDG for β; WertR for θ), not estimated on DVF. "Zone-typical" density is itself current-use (the median built density of the PLU zone in the IRIS), so a proxy for permitted density. | Feasible: zone type from GPU; zone-typical density from BD TOPO floor area ÷ cadastral area, by IRIS × zone. Paris and Lyon could use actual height and CES. | T1 to estimate β locally; T3 for the overall shape; T7 for the density term. | Intermediate. Houses on large plots in dense IRIS pay more than today, but far less than under (a). Large blocks change little (θ ≈ 0.5 still gives them more land per m²). |
| **(b) Land = local €/m² of plot (TAB + DVF house sales with `surface_terrain`) × area, reconciled at IRIS** | IAAO "sales comparison, always preferred"; Bodenrichtwert derivation | Building-plot (TAB) sales are thin or absent in dense cores (Paris essentially none) and selected. Deriving €/m² from *house* sales requires subtracting the building first, so it is circular with the residual. EPTB covers diffuse house plots only. Once rescaled to the IRIS residual total, (b) collapses into (a), plus a plattage curve if one is used. | Feasible in peri-urban and house-dominated communes; weak in cores. | Mainly a **level check** (T4, T5) rather than an allocator. | Little beyond (a′) where it is reconciled. Its value is external validation of the land level per m² of plot. |
| **(c) DVF house hedonic with a log plot-area term** | Danish curve (standard house on the actual plot); Davis et al. plattage standardisation; CAMA contribution models (Dye & England) | It estimates the *intensive margin* (Glaeser & Gyourko: possibly about 10 % of average land value in regulated markets), so do not read it as the level. Large plots sit in worse micro-locations within a cell, which biases β down unless fine location effects are used. DVF plot-area quirks (multi-parcel sales, unbuildable parts). It does nothing for flats. | Feasible: `surface_terrain` and `surface_reelle_bati` are in DVF; filter to single-parcel, single-house sales; use 200–400 m cells or IRIS fixed effects. | T2 (out-of-sample price errors by plot-size decile) is decisive and cheap. | It corrects **market value** for houses. Larger plots get higher market value, so a higher residual land value and land share. Moderate shift onto houses on large plots, mostly in suburban communes. **It does not capture unused permitted density**, so it is not site value on its own. |
| **(d) Permitted-density site value: charge foncière × permitted floor area** | Denmark §19 a (land per m² of residential area × actual or possible area, unused rights from Plandata.dk); NSW HBU | Permitted ≠ achievable: setbacks, gabarit envelopes, heritage review by the ABF (Bâtiments de France architects), parking and green-space coefficients; the Wales report stresses that planning assumptions must be stated. It overvalues where the market discounts hope value. No open charge-foncière series exists. | **Paris and Lyon only** (structured height and CES). Charge foncière via the DVF off-plan (VEFA) back-calculation (§3.5). Nationally not feasible: SRU level 2 is a draft. | T3 (teardowns in Paris and Lyon), T7. | The largest move toward true site value in the two big cities: blocks below their permitted envelope, and pavillons in zones that allow flats, gain land. **A pilot or annex only.** |
| **(e) Hybrids and bounding** | Denmark is a hybrid; BW pairs a crude rule with a 30 % appeal valve; Wales calls its output "notional" | — | Feasible. | All of the above. | The honest publication format: central case (a′ with c) plus bounds. |

---

## 5. Validation tests with open data

Ordered by how directly each discriminates between the designs.

1. **T3. Teardown sales: the closest thing to an observed site value.**
   - Method: link DVF sales of built parcels (houses, small buildings) to an SDES demolition permit or a new building permit on the same parcel within, say, 36 months. The price, plus demolition cost, approximates site value.
   - Comparison: each design's imputed land value for those parcels, and their land per m² of plot against neighbours.
   - Precedents: Davis et al. (teardown bias), Haughwout et al. (NYC land sales include parcels "with structures that the buyer intends to remove"), Denmark ("properties bought for demolition"), and Combes et al. (EPTB flags a prior building to be demolished; €/m² is 64 % higher when one exists).
   - Prediction if site value matters: the current model **underpredicts** these parcels most.
2. **T2. House price errors by plot-size decile (DVF).**
   - Method: predict DVF house sales out of sample with the current €/m²-of-floor surface, then with a plot term added.
   - Prediction: the current model shows systematic negative residuals for large plots and positive ones for small plots, within a cell.
   - Cheap, and decisive for (c).
3. **T1. Plot-size gradient within a cell.**
   - Method: on single-house DVF sales, regress log price on log habitable area, log plot area and its square, an age or condition proxy (DPE era), and cell fixed effects. Compare the implied elasticity of land to plot area with the model's imputed elasticity (+0.03 to +0.17 now). Benchmark: EPTB/CDG, about +0.3 at the median plot.
   - Add a zone interaction (dense U zones against pavillon zones): a larger teardown or option premium in densifiable zones is the market signature of site value.
4. **T4. Building-plot (TAB) €/m² against implied land €/m² of plot for built houses nearby.** Under site value they should be similar after a plattage adjustment, as the German Bodenrichtwert assumes.
5. **T7. Charge foncière from off-plan (VEFA) sales.** Compute DVF new-build €/m² − construction cost (SISAL) − margin. Compare with the model's land per m² of floor on collective parcels in the same IRIS. This tests the flats side and the θ assumption.
6. **T8. Do flats price in their building's land?** On DVF flat sales, test whether, controlling for cell, €/m² rises with the building's plot area per dwelling (cadastre ÷ BD TOPO dwellings). A positive gradient supports giving low-density copropriétés more land per flat.
7. **Hard constraint.** For each design, count parcels where land exceeds (market value + demolition cost). Under a correct site-value design these should be rare and confined to teardown candidates. The crude test's 56 % of Paris houses at the 95 % cap fails this test.
8. **T5 and T6. Coarse level checks.**
   - EPTB regional €/m² and plot sizes against the model's land €/m² of plot for recently built houses.
   - The national-accounts household land share (≈46 % derived) against the panel's aggregate. Urban panels should sit higher; THEORY.md already reports 55–76 % in the Paris and Lyon areas.
9. **Robustness of conclusions.** Run every design and report which headline signs are stable. The testing agent's job, but worth stating as a publication rule: publish a category or quintile conclusion only if its sign survives the band.

---

## 6. Ranked recommendation

| Rank | Design | Confidence | Why | Main uncertainties |
|---|---|---|---|---|
| 1 | **(c) Plot-area term in the house market-value model**, as a first, separate PR | **High** that it is an improvement | It fixes an error in the *observable* step, and DVF validates it directly (T2). It keeps the residual logic Insee uses. Practice (Denmark, US CAMA) prices plot size. | DVF plot-area quality. The location confounding of β. It moves toward correct current-use value but **not** to site value. |
| 2 | **(a′) Reallocate each IRIS's land total by A^β × max(actual, zone-typical density)^θ**, with β ≈ 0.3–0.6 (calibrated with T1 against EPTB/CDG) and θ ≈ 0.5 (German coefficients) | **Moderate** | It is the closest open-data analogue of the German and Danish site-value practice. It respects plattage and the sub-proportional density effect, and avoids the cap-hit pathology of (a). | θ is borrowed from German tables (now replaced by regional coefficients). "Zone-typical" density is a proxy for permitted density. IRIS totals still carry the residual's teardown bias, which could be checked with T3 and an uplift added where teardown prices exceed the residual. |
| 3 | **(e) Publish a band: current method (lower bound) and plot-area allocation (a) (upper bound) around (a′)** | **High** as a disclosure practice | It matches the project's "sensitivity as a first-class output" strategy, and Wales's "notional value" honesty. | Readers may treat the band as symmetric. Make clear that the evidence places the truth nearer the centre. |
| 4 | **(b) Vacant-plot €/m² × area** | Low as the main method, **useful as validation** | Thin, selected sales in the cores. It collapses into (a) once reconciled. | — |
| 5 | **(d) Permitted-density site value** | Low nationally, **moderate as a Paris/Lyon pilot** | The truest site-value concept (Denmark §19 a), but there is no national data. The charge foncière must be built from off-plan (VEFA) sales. | Permitted ≠ achievable (envelopes, heritage). Paris's ODbL licence terms. |

**Main uncertainties overall:**

- (i) Whether French market prices for houses in densifiable zones already carry a site-value premium. If they do, (c) captures part of the shift. T1 with the zone interaction, and T3, answer this.
- (ii) The right θ for France: German evidence is the only calibrated source I found.
- (iii) Whether to keep IRIS totals fixed. Site value would also move land *between* IRIS, toward under-used ones. This is second-order for commune-level results, because each commune keeps its own levy.

**Process notes for Patrick.**

- Keep (c) and (a′) as **separate PRs**. Each moves published numbers, which matches the project's one-change-per-PR rule.
- θ and β are economic parameters. Under the global CLAUDE.md they merit a **Gemini check**. I did not call Gemini.

---

## 7. Source register

### Opened and read (full text or the relevant section)

- IAAO, *Standard on Mass Appraisal of Real Property* (approved July 2017, © Feb 2022): iaao.org/wp-content/uploads/StandardOnMassAppraisal.pdf. Search results mention a 2025 partial revision of Section 3 only, which I did not open.
- Dye & England, *Assessing the Theory and Practice of Land Value Taxation*, Lincoln Institute Policy Focus Report, 2010 (PDF).
- Combes, Duranton & Gobillon, "The Costs of Agglomeration: Land Prices in French Cities", IZA DP 7027, Nov 2012 (PDF; Tables 1 and 3). The HAL copy of the REStud 2019 version was blocked.
- Davis, Larson, Oliner & Shui, FHFA Working Paper 19-01 (published in JME 2021) (PDF).
- Glaeser & Gyourko, "The Impact of Building Restrictions on Housing Affordability", FRBNY *Economic Policy Review*, 2003 (PDF).
- Haughwout, Orr & Bedoll, "The Price of Land in the New York Metropolitan Area", FRBNY *Current Issues* 14(3), 2008 (PDF).
- ap Gwilym, Jones & Rogers, *A technical assessment of the potential for a local land value tax in Wales*, Welsh Government SRN 17/2020 (PDF).
- Welsh Government, *Testing land valuation methods: feasibility of statistical models to value land in Wales*, March 2026 (PDF). The companion methodologies report was downloaded but not read in depth.
- Germany: BauGB §196; ImmoWertV 2021 §§12, 16, 19, 40, 41 (gesetze-im-internet.de); WertR 2006 Anlage 11 table (haufe.de); Stuttgart, "Bodenrichtwerte mit Hinweisen zur Grundsteuer B".
- Denmark: *Den Juridiske Vejledning 2026-2*, H.A.5.2.1, H.A.5.2.2, H.A.5.2.3.1.1, H.A.5.5.3.1 (tax.dk).
- NSW: "How land is valued in NSW"; "Objecting to different property types" (nsw.gov.au).
- SDES: EPTB survey page; 2024 results page (27/11/2025); EPTB FAQ; permits open-data page (updated 28 Oct 2026).
- CNIG, *Standard SRU niveau 1*, version 2026-03 (PDF).
- data.gouv.fr: DVF (DGFiP); DVF géolocalisées; DVF+ open-data (Cerema); Zone du PLU-H de la Métropole de Lyon; PLU bioclimatique – Plafonds des hauteurs (Paris); a Plans.fr EPTB-derived regional PDF (2023, not an official source).
- Insee Première n° 2081, "Le patrimoine économique national en 2024" (6 Nov 2025).

### Seen only in search snippets (treat as unverified)

- BW LGrStG §38 text and the 30 % clause; BFH rulings of 20 May 2026 (II R 26/24, II R 27/24).
- Estonian 2022 mass valuation; NZ Rating Valuations Act definition; Mirrlees Review ch. 16.
- Bourassa et al. 2011 (abstract); Albouy, Ehrlich & Shin 2018; Ahlfeldt & McMillen 2018.
- Bonnet et al. 2021; Trannoy & Wasmer 2013 CAE note and 2022 book.
- ORF 41 % land share and DGALN VEFA flat rates.
- Loi 65-557 art. 5 wording.
- DV3F restricted access (OPenIG model agreement).
- Cerema `sterr` definition; Sitadel parcel-localisation rate (~95 % for housing permits).
- Paris height values 18–37 m (from the dataset PDF snippet).

### Tried but not retrievable

- NSW Valuation of Land Act (403); NZ legislation (403); Estonian Land Board (403).
- HAL copies of the Combes et al. and Bonnet et al. papers (bot wall).
- Mirrlees PDF; Danish EVL statute text (retsinformation returned an empty page); BW statute portal.

### Derived by me (please check the arithmetic)

- Plot-price elasticities from the Combes et al. coefficients.
- GFZ elasticities from the WertR table.
- National-accounts land shares.
