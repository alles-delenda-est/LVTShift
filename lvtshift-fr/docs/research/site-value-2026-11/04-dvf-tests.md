# Land value of built parcels: an empirical test of designs (a)–(d)

Data agent, 2 November 2026. Aggregates only: every group shown holds at least 11 parcels, and no per-parcel figure appears anywhere. The repo was not modified. Scripts and private per-parcel working files are in `the working folder (not kept)`.

## 0. What was done, and whether it reproduces the published numbers

- **Rebuilt the per-parcel model frame for 9 communes from the download cache** (`rebuild.py`). It replays `run_commune.prepare` and `run_pipeline.run` read-only and captures the frame handed to the solver. That frame holds floor area, hedonic €/m², market value, building value at depreciated replacement cost (DRC), the TAB €/m², IRIS, cell and PLU zone.
  - Communes: Paris, Lyon, Villeurbanne, Montreuil, Roubaix, Aulnay-sous-Bois (a ring commune with many houses), Ormesson-sur-Marne (85 % of dwellings are houses), Cahors and Figeac.
  - **Reproduction is exact.** The rebuilt `new_tax` and `current_tax` match the published export to 0.0000 € on every parcel in all 9 communes.
  - Re-solving with the upstream `lvt.lvt_utils.model_split_rate_tax` (4:1, `outside_levy` flag) on the published land and building values also reproduces the bills to 0.0000 €.
  - Only one download was not in the cache. It was fetched live into a private working cache, not into `output\cache`.
- **DVF and `surface_terrain`.** `ingest.fetch_dvf` reads the Etalab geo-DVF per-commune CSVs, which do carry `surface_terrain` and `id_parcelle`. It then aggregates to the mutation and drops both columns. All 2021–2025 files for the 9 communes are in `output\cache`.
  - I rebuilt mutations from the raw cached files (`dvf_plot.py`). Kept: sales of exactly one house with no flat or business premises (outbuildings allowed), at most 4 parcels, no building-plot row. Prices are deflated with the pipeline's own house index.
  - Plot area from DVF matches the cadastre `contenance` of the parcels sold: the median ratio is 1.000, and 93–99 % of sales agree within 5 %.
  - Usable sales: 8,591 house sales and 190,000 single-flat sales.
- **Privacy.** All sale-level and parcel-level frames stay in `a private working folder (not kept)`. The report shows only regression coefficients, medians and group totals.

## 1. Test 1: the plot-size gradient in DVF house sales

Regressions within the 400 m cell (the hedonic's own cell), with year dummies and standard errors clustered by cell. The full tables are in `test1_houses.csv`, `test1c.csv` and `test1d.csv`.

**1a. The market prices plot area, concavely.** Elasticity of house price with respect to plot area, holding the DVF habitable area fixed:

| | Paris | Lyon | Villeurb. | Montreuil | Roubaix | Aulnay | Ormesson | Cahors | Figeac | Pooled |
|---|---|---|---|---|---|---|---|---|---|---|
| Plot elasticity | 0.33 | 0.17 | 0.22 | 0.15 | 0.32 | 0.19 | 0.19 | 0.13 | 0.12 | **0.23** (s.e. 0.011) |
| Same, IRIS fixed effects | 0.30 | 0.16 | 0.21 | 0.15 | 0.32 | 0.19 | 0.18 | 0.10 | 0.06 | 0.20 |
| Same, plus building-age bands | 0.34 | 0.17 | 0.23 | 0.17 | 0.33 | 0.21 | 0.20 | 0.15 | 0.12 | 0.24 |

- **The curve flattens as plots get larger.** Pooled slope by plot size:
  - below 300 m²: 0.29;
  - 300–600 m²: 0.18;
  - 600–1,200 m²: 0.11;
  - above 1,200 m²: 0.04.
- **The extra m² of garden is worth far less than a building plot.** The marginal value of one more m² of plot (in levels, within cell), against the TAB price per m²:

| Commune | Marginal value, €/m² of plot | TAB median, €/m² |
|---|---|---|
| Lyon | 106 | 735 |
| Montreuil | 250 | 1,791 |
| Aulnay | 160 | 584 |
| Ormesson | 189 | 825 |
| Cahors | 6 | 38 |
| Paris | ≈4,100 | 5,200 |

**1b. The test that matters for imputation: the model's own variables.** The test is run on BD TOPO habitable area (Fm) and the cadastre plot (A), which are what a design can use on the whole stock. Two quantities are compared:
- the market land residual on each sale, deflated price − the pipeline's DRC for the parcel sold;
- the model's land value for the same parcels.

| Elasticity of land, within cell | Paris | Lyon | Villeurb. | Montreuil | Roubaix | Aulnay | Ormesson | Cahors | Figeac | Pooled |
|---|---|---|---|---|---|---|---|---|---|---|
| **Market**, with respect to plot (γ) | 0.43 | 0.53 | 0.35 | 0.17 | 0.65 | 0.36 | 0.33 | 0.36 | 0.33 | **0.46** (0.03) |
| **Market**, with respect to floor area Fm (φ) | 0.10 | −0.30 | −0.12 | 0.19 | −0.17 | −0.15 | −0.16 | −0.46 | −0.33 | **−0.13** (0.03) |
| **Published model**, with respect to plot | 0.00 | 0.01 | 0.03 | 0.00 | −0.05 | 0.01 | −0.01 | 0.12 | −0.08 | **0.00** |
| **Published model**, with respect to floor area | 1.00 | 0.99 | 0.94 | 0.99 | 1.07 | 0.99 | 0.99 | 1.02 | 1.09 | **1.01** |
| Market price elasticity with respect to Fm (the model assumes 1) | 0.18 | 0.21 | 0.27 | 0.38 | 0.29 | 0.26 | 0.24 | 0.29 | 0.31 | 0.28 |

- **Gemini's diagnosis is confirmed, and is sharper than it first looked.**
  - The market's land under a house is driven by the plot (γ ≈ 0.3–0.5) and not by the building's floor area (φ ≈ 0).
  - The published residual is the exact opposite: φ ≈ 1 and γ ≈ 0.
- **Not the whole story, though.** Holding the *DVF* habitable area fixed, the model's market value does rise with plot (elasticity 0.11–0.33 against the market's 0.14–0.37). BD TOPO gross floor area includes annexes and garages and correlates with the plot.
  - So the model gets the average plot gradient of house *values* roughly right, by accident.
  - It splits them badly: too much on floor area and too little on plot.
  - It is also too steep in floor area: elasticity 1 against 0.2–0.4.
- **The level is right.** On the sales, the median land share from (price − DRC)/price matches the published land share of the same parcels: 0.62 against 0.62 pooled, and within 4 points in every commune. Flat sales show the same (`test1e.py`), for example Paris 0.73 against 0.73 and Lyon 0.56 against 0.59. Keeping each IRIS's residual land *total* is therefore supported. What is wrong is the allocation within the IRIS.

**1c. Flats: the market does not pay for "land per m² of floor".** Flat price per m² was regressed on the parcel's plot m² per m² of building floor, within cell, controlling for flat size and building-age bands:

| | Paris | Lyon | Villeurbanne | Montreuil | Aulnay | Cahors | Pooled (190k sales) |
|---|---|---|---|---|---|---|---|
| Elasticity | +0.001 (0.003) | −0.003 (0.008) | −0.029 | −0.012 | +0.07 | +0.05 | **−0.005 (0.003)** |

- **In big cities it is zero.** A flat in a low, garden-rich copropriété sells for the same price per m² as one in a dense block in the same 400 m cell.
- **What this means for copropriété.** In current use, buyers capitalise the shared plot in proportion to floor area, which is exactly what the residual does implicitly. How a copropriété plot is shared among its units does not change any published figure. All units on a parcel get the same percentage change when land is shared by tantièmes, which are roughly floor area.

**1d. A data problem found along the way: "houses" that are not houses.**
- In the cities, a large share of parcels in the `Single Family Residential` category are big one-dwelling buildings, with habitable area above 300 m² and typically 4 storeys in Paris:

| | Paris | Lyon | Villeurbanne | Montreuil | Roubaix | Aulnay | Cahors | Figeac |
|---|---|---|---|---|---|---|---|---|
| Share of "house" parcels | 37 % | 20 % | 19 % | 9 % | 3 % | 2 % | 4 % | 4 % |
| Share of the category's tax today | **90 %** | 79 % | 77 % | 61 % | 22 % | 22 % | 22 % | 21 % |
| Median habitable area | 909 m² | 811 m² | 820 m² | 621 m² | | | | |

- These parcels almost never appear among DVF house sales. They are probably buildings whose BD TOPO dwelling count is 0, 1 or missing, which `run_commune._residential_cat` maps to `maison`.
- **So the published "Houses" total in Paris (+18.4 %) is essentially a figure for large buildings.** Houses of 300 m² or less show +36 % in total and +33 % at the median. I call houses of 300 m² or less "plausible houses" below. This is outside the land-value question but it materially changes the house story.
- In all house-specific designs below, these large parcels are treated like blocks and keep the residual.

## 2. Designs tested

Every design was re-solved with the upstream solver on the published parcel set: 4:1, revenue-neutral at the same levy, with exempt parcels and excluded farmland outside. Only built residential parcels valued by the residual change; all other parcels keep their published values.

| Code | Family | What it does |
|---|---|---|
| **R** | published | Land = market value − DRC (the residual) |
| **A1-clip** | (a) site value | IRIS residual land total for all residential parcels, shared ∝ plot area; land capped at 95 % of market value, with the excess re-shared within the IRIS (the brief's earlier bracketing test) |
| **A1-sum** | (a) site value | Same sharing, but value = land + DRC ("summation", no cap) |
| **A1-type** | (a) site value | Same, with separate IRIS pools for houses and for blocks |
| **D** | (d) proxy | IRIS total shared ∝ plot × max(own floor-area ratio (FAR), 75th percentile of realised FAR in the same PLU zone label). This proxy stands in for permitted density, which is not available as structured national open data (§5). |
| **B-raw / B-rec** | (b) comparables | TAB €/m² × plot, unreconciled / rescaled to the IRIS residual total |
| **AH-γ** | (a) within houses | Plausible houses only: the IRIS *house* residual total shared ∝ plot^γ (γ = 1, 0.5, 0.3, 0.15); blocks keep the residual; summation |
| **E** | (a)+(c) market-calibrated | AH with γ = the commune's market γ from 1b (pooled 0.46 where the commune's s.e. is at least 0.06) |
| **E-cal** | (c) | Plausible houses: land = κ_IRIS × plot^γ, with κ from sale residuals (price − DRC), shrunk to the commune; this changes the house *level* |
| **C / C-pw** | (c) hedonic | House value = published value × plot term (log-linear / pooled piecewise from 1a); land = value − DRC with the published 15–85 % bounds; blocks keep the residual |

Variants dropped, and why:
- **A with a concave γ pooled across houses and blocks.** It shares land almost per parcel, so a 1-storey house gets the same land as a 60-flat block. Its own definition makes it incoherent.
- **C with the per-commune log-linear slope.** It double-counts the plot effect that BD TOPO floor area already carries (1b) and raises Paris house values by about 60 %. C-pw is shown instead.
- **B-rec mostly equals A1-sum.** The pipeline's `constructible_eur_m2` is a single commune-wide value almost everywhere (too few TAB sales per cell), so B adds no within-IRIS information.

## 3. Out-of-sample validation against DVF sale prices (`validate.py`)

**Method.** Each design's total value for the parcels actually sold was compared with their deflated price. For houses the value is land + building of the parcel; for flats it is the parcel's value per habitable m² × the flat's m². Within cell, I measured two things:
- whether the remaining error still trends with plot (houses) or with plot per m² of floor (flats); 0 means the design captures the market gradient;
- the typical size of the error.

E-cal is validated two-fold: κ is estimated on half the sales and tested on the other half.

| Pooled, 9 communes | R | A1-sum | A1-type | D | B-rec | AH1 | AH.5 | **AH.3** | **E** | E-cal | C-pw |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Houses: error slope on log plot (target 0) | +0.02 | −0.40 | −0.35 | −0.32 | −0.40 | −0.35 | −0.14 | **−0.03** | −0.11 | −0.13 | −0.23 |
| Houses: median \|log error\| within cell | 0.246 | 0.223 | 0.221 | 0.227 | 0.223 | 0.221 | 0.185 | **0.180** | **0.181** | 0.182 | 0.262 |
| Houses: median price ÷ value | 1.04 | 0.97 | 1.13 | 1.07 | 0.97 | 1.13 | 1.03 | 1.02 | 1.03 | 0.98 | 1.04 |
| Flats: error slope on log plot per floor (target 0) | −0.01 | −0.60 | −0.62 | −0.49 | −0.60 | −0.01 | −0.01 | −0.01 | −0.01 | −0.01 | −0.01 |
| Flats: median \|log error\| within cell | **0.124** | 0.195 | 0.195 | 0.179 | 0.195 | 0.124 | 0.124 | 0.124 | 0.124 | 0.124 | 0.124 |

(Per-commune results are in `validate_out.txt` and point the same way in every commune.)

Reading:
1. **Within-house reallocation by plot^γ with γ ≈ 0.3–0.5, valued by summation (land + DRC), predicts house prices 27 % more accurately than the published residual.** The error falls from 0.246 to 0.180, with no level bias and no remaining plot gradient. Per commune: Paris 0.18 → 0.11, Lyon 0.23 → 0.15, Aulnay 0.24 → 0.12, Ormesson 0.24 → 0.13, Cahors 0.24 → 0.17.
2. **Linear sharing by plot (γ = 1: A1, AH1, D, B) overshoots the plot gradient for houses.** In plain terms, it charges big gardens as if every m² were building land.
3. **Every design that moves land between flats and houses by plot (A1, D, B) makes flat prices worse**: the error rises from 0.12 to 0.18–0.20, with a strong spurious gradient. For flats, the residual is what the market supports *in current use*.
4. **Implied price elasticity with respect to plot,** within cell, holding model floor area (table in `tables_by_commune.md`):

| | Market (1b) | R | AH.3 | AH.5 | E | A1 and D |
|---|---|---|---|---|---|---|
| Elasticity | 0.12–0.42, pooled 0.29 | 0 | 0.18–0.24 | 0.28–0.39 | 0.13–0.39 | 0.40–0.89 |

**Taken together, γ between 0.3 and 0.5 is supported.** The error slope crosses zero at about γ = 0.25–0.3 (−0.03 at 0.3, −0.14 at 0.5); the elasticity match prefers about 0.45.

## 4. Effects on the published results (re-solved 4:1)

- "tot" is the group total change in %, against today's central-case tax. "hh" is the dwelling-weighted household median in %, as the site publishes it.
- Income fifths are shown only where there are at least 10 IRIS incomes (not for Ormesson, Cahors or Figeac).
- The full tables by commune and design are in `tables_by_commune.md`. They also give land-share percentiles, the % of parcels at the cap, the under-used group, and the implied gradients.

**Houses, household median (hh)**

| design | Paris | Lyon | Villeurb. | Montreuil | Roubaix | Aulnay | Ormesson | Cahors | Figeac |
|---|---|---|---|---|---|---|---|---|---|
| R (published) | +29.6 | +20.6 | +17.7 | +10.5 | −14.1 | +28.4 | −3.6 | +12.9 | +14.5 |
| A1-clip | +32.9 | +49.1 | +50.1 | +27.2 | −12.8 | +48.8 | +5.3 | +24.3 | +37.2 |
| A1-sum | +67.0 | +55.8 | +52.8 | +39.0 | −22.6 | +38.6 | −15.2 | −2.9 | −1.1 |
| A1-type | +15.5 | −4.5 | −2.0 | −4.7 | −30.7 | +23.8 | −18.4 | −17.9 | −16.7 |
| D | +65.0 | +11.1 | −4.7 | +12.2 | −22.8 | +11.0 | −14.1 | −4.9 | −10.3 |
| AH.5 | +26.2 | +17.1 | +18.0 | +18.4 | −15.1 | +30.4 | −7.1 | +10.3 | +12.2 |
| **AH.3** | +27.4 | +19.4 | +19.8 | +21.6 | −11.6 | +32.3 | −6.2 | +17.3 | +17.6 |
| **E** | +26.5 | +16.9 | +18.7 | +22.2 | −18.8 | +31.9 | −6.8 | +12.0 | +13.3 |
| E-cal | +36.2 | +21.2 | +17.0 | +23.8 | −4.6 | +25.6 | −4.9 | +25.2 | +23.3 |
| C-pw | +27.2 | +18.5 | +15.2 | +9.3 | −18.3 | +28.1 | −3.7 | +10.1 | +13.9 |

**Houses, group total (tot)**

- **The total does not move under AH and E, by construction**: they keep each IRIS's house land total.
- **E-cal is the real test of the house *level*.** It raises the total in Paris (+18.4 → +23.3), Roubaix (−3.8 → +8.9), Cahors (+12.9 → +24.9) and Figeac (+14.7 → +26.7). These are the communes where published house values sit below sale prices: the median ratio of price to published value is 1.29 in Paris and 1.14–1.15 in Cahors and Figeac.
- **Site-value designs** give Paris +12 to +58, Lyon +8 to +49, and Villeurbanne −5 to +21.

**Large blocks (5+), tot**

| design | Paris | Lyon | Villeurb. | Montreuil | Roubaix | Aulnay | Ormesson | Cahors | Figeac |
|---|---|---|---|---|---|---|---|---|---|
| R, AH*, E | −0.5 | +2.0 | −1.2 | −4.9 | −1.6 | −15.0 | −20.7 | +0.6 | +3.9 |
| E-cal | −0.8 | +1.6 | −1.1 | −5.0 | −9.6 | −12.6 | −24.4 | −11.1 | −10.6 |
| A1-clip | −0.3 | +1.5 | −0.8 | −1.7 | −6.1 | −21.7 | −22.7 | −11.5 | −12.8 |
| A1-sum | −5.5 | −8.6 | −9.5 | −15.0 | −16.7 | −36.4 | −47.6 | −21.2 | −30.5 |
| D | −3.7 | −5.1 | −4.6 | −9.3 | −11.6 | −14.8 | −28.7 | −8.5 | −13.8 |

**Small blocks (2–4), tot**
- **Under R and the current-use designs:** −3 to +16.
- **Under the site-value designs:** +20 to +92 in the cities (A1-type in Lyon +92, Villeurbanne +85). These are the most design-sensitive figures on the site.

**Commercial and industrial**
- **They do not move** except under B-raw. Every other design leaves the commune's built-residential land total unchanged.
- B-raw cuts residential land to 11–27 % of the residual in the big cities and so pushes the levy onto commercial premises (Paris +101 %, Villeurbanne +201 %).

**Income fifths**
- **Group totals (tot) are identical across all A, AH, E and D designs**, because IRIS totals are kept and the fifths are built from IRIS.
- **Household medians:**

| design | Paris Q1 / Q5 | Lyon Q1 / Q5 | Villeurb. Q1 / Q5 | Montreuil Q1 / Q5 | Roubaix Q1 / Q5 | Aulnay Q1 / Q5 |
|---|---|---|---|---|---|---|
| R | −19.9 / +13.9 | −13.4 / +22.4 | −6.1 / +9.6 | −25.3 / +21.0 | −28.3 / +41.1 | −5.3 / +31.2 |
| AH.3 / E | −19.9 / +13.9 | −13.5 / +22.4 | −7.8 / +9.6 | −28.1 / +23.3 | −21.6 to −23.0 / +36.9 to +40.5 | −6.2 / +25.2 |
| E-cal | −20.1 / +13.5 | −13.8 / +21.9 | −8.4 / +9.6 | −28.5 / +23.2 | −18.6 / +37.9 | −5.3 / +21.3 |
| A1-sum | −30.5 / +3.7 | −34.5 / +5.4 | −18.1 / **−6.3** | −26.7 / **−8.4** | −34.4 / +16.6 | −31.8 / +24.3 |
| D | −27.9 / +4.1 | −30.7 / +6.1 | −13.9 / **−9.8** | −31.7 / **−2.5** | −33.6 / +14.9 | −28.6 / +12.9 |

**The share cap, honestly**
- **How often plot-based land exceeds today's market value.** Under the site-value designs, the plot-based land of a house is above the published market value of the whole property (house and land) in:

| | Paris | Lyon | Villeurb. | Montreuil | Aulnay | Roubaix | Small towns |
|---|---|---|---|---|---|---|---|
| A1-sum, % of houses | 69 | 51 | 49 | 49 | 29 | 8 | 16–21 |

  With the 95 % cap (A1-clip), 66–82 % of city houses hit it, and 10–20 % of the IRIS land total has to be re-shared onto blocks.
- **Even within houses only, at γ = 0.3, it happens for:**

| | Paris | Lyon | Villeurb. | Montreuil | Aulnay | Ormesson | Roubaix | Cahors–Figeac |
|---|---|---|---|---|---|---|---|---|
| AH.3, % of plausible houses | 40 | 25 | 22 | 35 | 24 | 25 | 8 | 16–23 |

- **What it means.** The published market value is hedonic €/m² × floor area, with elasticity 1 in floor area against the market's 0.2–0.4. It undervalues small houses on reasonable plots.
  - Summation (land + DRC) removes the need for a cap.
  - The validation in §3 shows that summation predicts those houses' sale prices better, not worse.
  - So hitting the cap is a symptom of the floor-proportional hedonic, not of over-assessed land.
  - Clipping, as in AH.3-clip, hides it and pushes the excess onto other houses. I recommend against clipping.

**Under-used plots**
- **Definition.** Residential parcels in the lowest fifth of the commune by floor-area ratio, located in the third of IRIS with the highest price.
- **Total change for this group:**

| design | Paris | Lyon | Villeurb. | Montreuil | Roubaix | Aulnay | Ormesson | Cahors | Figeac |
|---|---|---|---|---|---|---|---|---|---|
| R | +21 | +12 | +15 | +27 | +41 | +30 | −5 | +20 | +24 |
| AH.3 | +21 | +21 | +59 | +112 | +58 | +108 | +53 | +124 | +364 |
| E | +21 | +25 | +66 | +100 | +74 | +110 | +60 | +167 | +437 |
| A1-sum | +157 | +190 | +451 | +792 | +171 | +200 | +106 | +462 | +1165 |
| D | +133 | +128 | +301 | +460 | +148 | +157 | +84 | +326 | +1286 |

- **Their share of the levy** rises from 0.2–8 % (R) to 0.9–9 % (AH.3) and 2.6–16 % (A1-sum).
- **Paris barely moves under the house-only designs**, because its under-used parcels are mostly the large "houses" of §1d, which keep the residual.

**Land-share distribution (built residential)**
- **The published land share is compressed:**

| | Paris | Lyon | Aulnay |
|---|---|---|---|
| p10–p90 | 68–82 % | 53–65 % | 52–71 % |

- **AH.3 widens it moderately** (Lyon 50–70 %, Aulnay 51–80 %).
- **A1-clip pushes 30–62 % of residential parcels to the 95 % cap** in the cities.

## 5. Data feasibility for (b) and (d)

- **(b) Comparables.** The model's TAB €/m² is a single commune value in most cities, because cells have too few sales. Its level against the IRIS residual for built residential land:

| | Paris | Lyon | Villeurb. | Montreuil | Aulnay | Roubaix | Ormesson | Cahors | Figeac |
|---|---|---|---|---|---|---|---|---|---|
| TAB × plot ÷ residual | 0.27 | 0.24 | 0.11 | 0.54 | 0.82 | 0.93 | 1.42 | 0.55 | 1.14 |
| Spread across IRIS (p10–p90) | | 0.07–0.79 in Lyon | | | | | | 0.07–1.37 in Cahors | |

  - **Why the levels differ.** TAB prices plots for individual houses, at low density. They approach the residual in house suburbs but are 4–9× too low for dense cities.
  - **For houses specifically, TAB is close to the published house land per m² of plot in the suburbs:**

| €/m² | Montreuil | Roubaix | Aulnay | Ormesson |
|---|---|---|---|---|
| TAB | 1,791 | 394 | 584 | 825 |
| Published house land per m² of plot | 2,007 | 389 | 642 | 747 |

    It is half or less in the city centres and small towns (Paris 5,204 against 11,339; Villeurbanne 214 against 903).
  - **So TAB is usable as a level check for houses outside dense cores, not as the land price of built parcels.**
- **(d) Permitted density.**
  - **Nationally:** the GPU/CNIG PLU standard carries zone type and label, but no structured height, CES or FAR attribute. Some prescriptions carry local text attributes; for example, Paris "gabarits-enveloppes" put "HAUTEUR" in `LIB_ATTR2`.
  - **Paris is the exception.** The bioclimatic PLU publishes "Hauteur maximale constructible" (16 June 2026 version) and "Emprise constructible maximale" as open data. The ceilings are 18, 25, 31 and 37 m and are nearly uniform within an IRIS, so D in Paris would behave like A1 within each IRIS.
  - **So D is feasible only as a proxy (realised density by PLU zone) outside Paris.** It fails the flat validation, like A1.
  - Sources: [CNIG PLU standard v2024-01](https://cnig.gouv.fr/IMG/pdf/231220_standard_cnig_plu_v2024-01.pdf), [Paris prescriptions (GPU)](https://opendata.paris.fr/api/v2/catalog/datasets/plu-dans-le-geoportail-de-lurbanisme-prescriptions-lineaires/attachments/plu_gpu_prescriptions_lineaires_pdf), [PLU bioclimatique, hauteur maximale constructible](https://www.data.gouv.fr/datasets/plu-bioclimatique-hauteur-maximale-constructible), [plafonds des hauteurs](https://www.data.gouv.fr/datasets/plu-bioclimatique-plafonds-des-hauteurs), [emprise constructible maximale](https://opendata.paris.fr/api/datasets/1.0/plub_ecm/attachments/emprise_constructible_maximale_pdf), [APUR, PLU emprise](https://geocatalogue.apur.org/catalogue/srv/api/records/urn:apur:plu_emprise_od).

## 6. Robustness: what keeps its sign

Sign agreement with R by commune (`signs.csv`), excluding B-raw, which is rejected because it is unreconciled:

| Published conclusion | Current-use designs (AH.3–.5, E, E-cal, C-pw) | Site-value designs (A1*, D, B-rec) |
|---|---|---|
| Poorest fifth pays less (total and household median), in all 6 communes with fifths | **holds** | **holds** |
| Richest fifth pays more, total | **holds** (identical) | **holds** (identical) |
| Richest fifth pays more, household median | **holds** | flips in Villeurbanne and Montreuil; falls to +4/+5 in Paris and Lyon |
| Q5 − Q1 gap, household | 16–62 points, close to R | 4–56 points |
| Commercial and industrial pay less | **holds** | **holds** |
| Houses pay more in Paris, Lyon, Aulnay, Cahors, Figeac (household median) | **holds** | flips in Lyon, Villeurbanne, Montreuil, Cahors and Figeac under A1-type / D |
| Houses pay less in Roubaix and Ormesson | **holds** | mixed |
| Large blocks about flat in Paris, Lyon, Villeurbanne (within ±5) | **holds** | becomes −3 to −15 |
| Small blocks (2–4) | holds (sign) | +20 to +90 points: not robust |
| Size of the shift onto under-used plots | 1.5–15× R in the suburbs and small towns | 5–50× R |

**Parameter sensitivity within the recommended family:**
- **γ from 0.3 to 0.5 moves the house household median by 1–6 points**: Lyon 17–19, Paris 26–27, Montreuil 18–22, Roubaix −15 to −12, Cahors 10–17.
- **Income-fifth household medians move by at most 2 points**, except Roubaix Q1 (−28 published, −22 under AH) and Montreuil Q1 (−25 → −28).
- **γ = 1 is outside the validated range.**
- **Under-used figures scale with γ**: Cahors +124 (0.3) to +178 (0.5).
- **E-cal shifts the house *level*** by +5 points (Paris) to +12 points (Roubaix, Cahors, Figeac).

## 7. Recommendation

**Design "E": current-use land, with a plot-based allocation for houses, validated on DVF.**

1. **Keep the residual for flats and blocks** (categories 2–4 and 5+, and one-dwelling parcels over 300 m² habitable).
   - DVF shows zero price premium for plot per m² of floor in copropriétés (190,000 sales, −0.005 ± 0.003).
   - Every plot-based alternative degrades flat price prediction by 45–60 %.
2. **For plausible houses (≤ 300 m² habitable),** share each IRIS's residual house land total by plot^γ, with **γ = 0.35**: between 0.3, preferred by the error slope, and 0.46, the direct pooled estimate. Use commune γ only where its s.e. is below 0.06. Publish γ = 0.3 and 0.5 as the sensitivity band.
3. **Value houses by summation**, building = DRC and value = land + DRC, with no land-share clip. Report the share of houses whose plot-based value exceeds the floor-proportional hedonic: 8–40 %.
4. **Check the IRIS house level with sale residuals (E-cal)** and show it as a second band where it differs (Paris, Roubaix, Cahors, Figeac).
5. **Fix the classification of large one-dwelling buildings before publishing house figures for Paris, Lyon and Villeurbanne.** In Paris they are 90 % of the category's tax.

**Validation evidence.**
- House price error falls by 27 % out of sample (0.246 → 0.180), with no level bias and no remaining plot gradient.
- Flat accuracy is unchanged.
- The implied plot elasticity (0.13–0.39) matches the market's (0.12–0.42).

**What this does and does not settle.** This is the best *current-use* land value the open data support. It is not the site value at highest-and-best or permitted use that a pure LVT targets. That concept (A1 / D) can't be validated against sale prices of existing buildings: buyers of flats demonstrably don't pay for unused development rights in a copropriété.
- **If the project wants the site-value concept, publish it as an explicit upper band**, using A1-type (separate house and block pools, summation). Do not use A1-clip: the cap is what made the earlier bracketing test's house sign unstable.
- **Say plainly what that band does.**
  - It moves 5–20 points of levy off large blocks onto small blocks and houses with gardens.
  - It multiplies the charge on under-used plots several times over.
  - It narrows, and in Villeurbanne and Montreuil reverses, the richest fifth's household increase.

## Files

The scripts and working files were kept outside the repository (not published).

| File | Contents |
|---|---|
| `rebuild.py` | Read-only replay of the pipeline; exact reproduction check |
| `dvf_plot.py` | DVF mutations with `surface_terrain` |
| `test1.py`, `test1b.py`, `test1c.py`, `test1d.py`, `test1e.py` | Test 1: plot gradients, robustness, sale-level residuals, flats |
| `designs.py` | All designs and re-solves through `lvt.lvt_utils.model_split_rate_tax` |
| `validate.py` | Out-of-sample sale-price validation |
| `summary.py` | Builds `tables_by_commune.md`, `cross.csv` and `signs.csv` |
| `frames\` | Private per-parcel and per-sale working files; never publish |

Not done:
- No Gemini review of these parameter choices; the parent may want one (`GEMINI_API_KEY` not checked).
- Permitted density for Paris was not joined, only its feasibility assessed.
- The lower-bound baseline (TH-2017 variant) was not re-run under the designs.
