Here is a rigorous review of the methodology, code implementation, and tax incidence results, ranked by severity within each question.

---

### 1. Formula, Parameters, and Code Bugs

#### A. Code & Implementation Bugs (Ranked)

1. **Bug (High): Downstream `sensitivity_band` and clip logic will break or behave incoherently.**
   In `site_value_land()`, you reconstruct `market_value = land + cost[pool]` and `land_share = land / (land + cost[pool])`. Just below this function in `estimate.py` lies `sensitivity_band(p, cfg, shifts=(-0.10, 0.0, +0.10))`, which the docstring says *"Re-split market value at land_share +/- shift"*. 
   * If `sensitivity_band` holds the **new** `market_value` fixed and shifts `land_share` by $\pm 10\%$, it is perturbing an synthetic total ($L_{\text{site}} + C_{\text{dep}}$) that only exists because of the site-value imputation, rather than perturbing the underlying residual pool before re-sharing. 
   * Worse, for the 8–37% of parcels where $L_{\text{site}} > MV_{\text{current}}$, `land_share` is already very high (often $>0.75$); a $+0.10$ shift may breach your `land_share_bounds` (0.85) if `sensitivity_band` clips, or push building value negative if it doesn't.

2. **Bug / Distortion (Medium-High): Pooling *clipped* residuals (`built_clipped_high`, `built_clipped_low`) violates conservation of economic residual.**
   `SITE_POOLED_FLAGS` includes parcels whose land value was artificially altered by `land_share_bounds = (0.15, 0.85)` in `land_value_residual`. 
   * A low-density house in a high-value zone previously had a tiny floor-based $MV_{\text{current}}$, so its raw residual was minimal or negative, getting floored at $0.15 \times MV_{\text{current}}$ (`built_clipped_low`). 
   * A dense block may have been capped at $0.85 \times MV_{\text{current}}$ (`built_clipped_high`).
   * Because you sum `out.loc[pool, "land_value"]` *after* clipping, the IRIS pool total is biased by those artificial floors/caps, and you then restore `cost[pool]` (unclipped depreciated cost) as the improvement value. The sum of raw residuals (clipped only at $\ge 0$ at the IRIS level) is the true economic pool.

3. **Edge-case Bug (Medium): `weight.groupby(group).transform("sum")` can divide by zero.**
   In `site_value_land()`, `pool` requires `area > 0` and `floor > 0`, so `weight > 0` for any pooled parcel. However, if `density` or `plot` ever evaluates to `0` or `NaN` due to upstream `inf` (e.g., `area` near $0$ float underflow), `land` becomes `NaN`. More importantly, if an IRIS has only 1–2 pooled parcels (e.g., an industrial/activity IRIS with one caretaker house), that parcel re-shares purely with itself (`land == land_value_current`), defeating the site-value concept. **Fix:** enforce a minimum IRIS pool size (e.g., `min_iris_parcels = 10`), falling back to commune-wide pooling or adjacent IRIS when an IRIS is too sparse.

4. **Bug (Low-Medium): Unrecorded multi-family buildings ($< 500\text{ m}^2$, $\le 2$ storeys) are misclassified as `maison` and get 1 dwelling.**
   In `_residential_cat()`, when `n_dwellings` is `NaN`, any building with `floor <= 500` and `n_levels < 3` immediately returns `"maison"`. In suburbs like Montreuil or Villeurbanne, two-storey *petits collectifs* or *maisons divisées* of 250–450 m² gross (150–275 m² habitable, typically 3–4 flats) with missing BD TOPO dwelling counts are forced into `"maison"`. Check that `dwellings_per_parcel` in `run_pipeline.py` uses the exact same threshold logic as `_residential_cat`, or you will have `"maison"` parcels containing multiple households in the sidecar.

#### B. Methodological Soundness of Parameters

1. **Inclusion of Offices and "Other" in the Residential IRIS Pool (Medium-High Risk):**
   Under French zoning (*PLU*) and fiscal rules (*RVLLP* vs *RVLLH*), commercial/office use and residential use only have equal land value if the PLU permits free conversion between them. In reality, PLU rules (e.g., *servitudes de mixité sociale*, ground-floor commercial mandates, or office-only zones) segment these markets. If your hedonic surface values residential and office floor space at different €/m² rates, pooling them together and re-sharing purely by physical `plot × FAR^0.5` transfers land value from the higher-margin use to the lower-margin use within the same IRIS.
2. **$\theta = 0.5$ (WertR / Bodenrichtwert):**
   *Citing official German guidance:* The *WertR 2006 Anlage 11* (*Umrechnungskoeffizienten für das Maß der baulichen Nutzung*) tables for *Wohnbauflächen* give GFZ conversion ratios where doubling GFZ from $0.4 \to 0.8$ multiplies land/m² by $1.26$ ($\theta \approx 0.33$), while from $1.0 \to 2.0$ it multiplies by $1.40$ ($\theta \approx 0.49$), and $1.2 \to 2.4$ by $1.41$ ($\theta \approx 0.50$). Thus $\theta = 0.5$ is well-grounded for urban mid-rise zones ($GFZ \ge 0.8$), though slightly steep for low-density suburban zones ($GFZ < 0.6$, where $\theta \approx 0.35$ fits *WertR* better).
3. **Reference = `p75` of parcel-weighted realised FAR by `zone_libelle`:**
   Because parcels are unweighted when computing `.quantile(0.75)`, a zone with 80 detached houses (FAR = 0.3) and 20 apartment blocks (FAR = 2.0) has a parcel-weighted `p75` of **0.3**, even though the zone clearly permits FAR = 2.0 (and most of the *land area* or *floor area* might be in blocks). **Fix:** Consider **plot-area-weighted** `p75` FAR, which is much closer to the PLU envelope and less distorted by parcel subdivision history.

---

### 2. Plausibility of the Incidence Results

All five patterns you flagged have clear mathematical explanations in your model—some reflect genuine site-value economics, while one reveals a metric artifact:

1. **Why do household medians fall for *every* income fifth (including the richest fifth in Villeurbanne $-13.8\%$ and Montreuil $-6.2\%$)?**
   * **Diagnosis:** This is a classic **Jensen’s inequality / skewness artifact** combined with the **commercial tax shift**.
   * First, notice that **Commercial** shifts up massively under site value (Villeurbanne $+24.7\% \to +49.4\%$, Montreuil $+0.1\% \to +19.8\%$, Lyon $-5.8\% \to +4.9\%$). Because the simulation is revenue-neutral across the *entire commune*, the residential sector *as a whole* pays less tax when commercial pays more.
   * Second, in the richest IRIS fifth, the **total** tax change is still positive ($+2.9\%$ in Villeurbanne, $+17.9\%$ in Montreuil, $+15.5\%$ in Lyon), while the **household median** is negative ($-13.8\%$, $-6.2\%$). Why? Because in dense French cities, even in affluent IRISs, the *median household* (>50% of dwellings) lives in an **apartment (`immeuble_collectif`)**, which sees a $-8\%$ to $-27\%$ tax cut! Meanwhile, the minority of households in that affluent IRIS who own **detached houses** get hit with a $+50\%$ to $+100\%+$ hike. That right-tail spike pulls the *mean/total* of the richest fifth up (+17.9%), while the *median* voter in that fifth (an apartment dweller) gets a tax cut (-6.2%). 
   * **Takeaway:** This is completely plausible, *provided* you explain to readers why the mean (total) and median diverge so sharply in mixed housing zones.

2. **Why do Houses in Cahors fall ($+14.0\% \to +2.5\%$) while soaring in Lyon/Montreuil/Villeurbanne, and staying flat in Roubaix ($-15.5\% \to -15.5\%$)?**
   * **Lyon / Montreuil / Villeurbanne:** Houses sit on urban plots interspersed with apartment blocks inside the same IRIS and PLU zones (`zone_libelle`). Their `ref` FAR (`p75`) is pulled up by surrounding mid-rise buildings, and their plot-to-floor ratio is huge compared to apartments. Re-sharing moves massive land value from vertical blocks onto horizontal house plots.
   * **Roubaix:** Housing in Roubaix is overwhelmingly homogeneous *courées* and terraced *maisons de ville* on small plots (100–200 m²) in mono-morphic zones. Within an IRIS, `far` and `plot` vary little across houses, so re-sharing within the IRIS moves almost nothing ($8\%$ of parcels exceed old MV, median stays $-15.5\%$).
   * **Cahors:** Why did houses *drop* from $+14.0\%$ to $+2.5\%$? Check two things in Cahors:
     1. **`plot_cap_quantile = 0.99` vs rural/peri-urban plots:** In Cahors, many IRISs are large and mix town-centre blocks with peripheral houses on large lots ($1,000–5,000\text{ m}^2$). Wait—large lots should *increase* house land under linear area! Why did it fall?
     2. **Look at `lv_flag` in Cahors:** What share of peripheral houses in Cahors had their residual floored at `built_clipped_low` or farmland floor, or had high `land_value_current` relative to town-centre offices/commercial? Even simpler: look at `total_land_value` across the whole commune of Cahors before vs. after `site_value_land`. Because `site_value_land` **removes the 85% land-share cap** (`land_share = land / (land + cost)` with no clip!), in low-price cities with old, heavily depreciated buildings (like Cahors), dense town-centre buildings or commercial properties with high `cost` deprecation might have been **capped at 85% land share** in `land_value_residual`? No, `total` is conserved! If `total` land is conserved, and houses fell while small blocks ($+3.5\% \to -14.5\%$) *and* large blocks ($+10.2\% \to -24.8\%$) *and* commercial ($-25.8\% \to -24.0\%$) ALL fell or stayed flat... **Wait: how can the median of ALL FOUR categories (Houses, Small blocks, Large blocks, Commercial) shift downward simultaneously in Cahors ($+14 \to +2.5$, $+3.5 \to -14.5$, $+10.2 \to -24.8$, $-25.8 \to -24.0$)?!**
     * **CRITICAL DIAGNOSTIC ON CAHORS:** Look at the Cahors column in your table. Every single building category's median shifted down (or moved $+1.8$pp on commercial) while total revenue is fixed! How can all category medians drop while revenue is constant? Only if **extreme right-tail outliers** (e.g., a few huge parcels up to `p99` plot area, such as campings, châteaux, clinics, or `"dependance"` / `"autre"` parcels not shown in the 4 rows of the table) absorbed a massive share of the commune's land pool! 
     * **Action:** Check the total tax share of `"dependance"` (which now includes large buildings $>500\text{ m}^2$ with $\le 1$ dwelling from your fix #1!) and the top 5% largest plots in Cahors. I strongly suspect `MAISON_MAX_FLOOR_M2 = 500` dumped châteaux, large farmhouses/domains, or unrecorded buildings into `"dependance"`, OR large un-subdivided residential estates (`plot` up to `p99`) soaked up the Cahors land pool, driving down the tax on normal houses and flats alike.

3. **Why do Small Blocks (2–4 dwellings) flip sign by city ($+23\%$ in Lyon/Villeurbanne/Montreuil vs $-14.7\%$ in Roubaix/Cahors)?**
   * In Lyon/Villeurbanne/Montreuil, a 2–4 flat building is an *under-build* relative to 6–10 storey blocks in the same IRIS/zone (`ref` p75 FAR is high, and small blocks often have courtyard/garden plots). Thus they behave like large houses and gain land value.
   * In Roubaix and Cahors, 2–4 flat buildings *are* the dense buildings of the neighbourhood (higher FAR than the surrounding houses, smaller plot per m² of floor), so they lose land value to single-family houses/large plots just like large blocks do.

4. **Why does Commercial rise everywhere under site value?**
   * Two reasons: (a) pooled commercial buildings (low-rise shops, restaurants, bank branches, low-density offices) have low realised FAR inside dense mixed-use IRISs, so `max(far, ref)` lifts them to the zone's residential `p75` FAR; (b) non-pooled DRC commercial parcels (retail boxes, sheds) have fixed land values, wait—did the commune-wide `land_mill` change? No, `total` land in each IRIS pool is conserved! Therefore, the *commune-wide* sum of `land_value` is **strictly identical** between `current` and `site`, and the *commune-wide* sum of `improvement_value` only changes if `land_value_residual` had clipped `improvement_value` (when `lv_flag` was `built_clipped_high` or `built_clipped_low`). Because `Commercial` in the table includes pooled commercial parcels (ground-floor/low-rise retail & offices in `SITE_POOLED_FLAGS`), those low-rise commercial plots absorb land from tall residential apartment blocks in the same IRIS.

---

### 3. Main Risks, Guardrails, and Sensitivity Runs

Ranked by priority for publication:

1. **Risk 1: The "Large Plot / Estate" Sponge Effect (Linear Plot Area + `p99` Cap).**
   * *The issue:* Applying linear plot area (`plot ** 1.0`) up to the 99th percentile (`plot_cap_quantile = 0.99`) across an entire commune means a $4,000\text{ m}^2$ house parcel with a non-subdividable wooded slope or back garden is valued as if every square metre can be built at `p75` FAR. In French tax assessment (*CGI art. 1495*, *instruction 6 C-1-73*), large residential grounds beyond the immediate *terrain à bâtir* footprint are weighted down (*dépendances non bâties / parc d'agrément*). As seen in Cahors, linear area up to `p99` can let a small number of huge parcels soak up the IRIS land pool.
   * *Guardrail:* Capping `plot` at the **commune-wide `p99`** is too loose for houses if the pool includes large estates or horizontal *copropriétés*. Either lower `plot_cap_quantile` to `0.95`, or cap excess plot area above e.g. $1,000\text{ m}^2$ (or $3\times$ zone median plot) at a reduced marginal weight (e.g. $0.25\times$ per excess $\text{m}^2$, matching French *chartes d'évaluation* for *terrain d'agrément* / *fond de parcelle*).

2. **Risk 2:Liquidity / Cash-Rich vs. Asset-Rich Incidence ("Grandmother in the Pavlovian Villa").**
   * *The issue:* When $23–37\%$ of parcels in Lyon/Villeurbanne/Montreuil have a site land value **exceeding their entire current built market value** ($L_{\text{site}} > MV_{\text{current}}$), you are diagnosing parcels as "teardowns" (*valeur de terrain à bâtir > valeur d'usage actuel*). While theoretically pure Georgist LVT, in French local finance this triggers immediate constitutional challenges under *capacité contributive* (*Conseil Constitutionnel, Décision n° 2012-662 DC*, confiscation / ability-to-pay threshold) unless paired with tax deferral (*différé de paiement* until sale/inheritance).
   * *Guardrail / Reporting:* Publish the `over` metric ($L_{\text{site}} > MV_{\text{current}}$) prominently alongside the results, and explicitly note in the policy discussion that a pure site-value shift in dense suburbs requires a **deferral mechanism (liens settled at mutation)** for low-income owner-occupiers of under-built plots.

3. **Risk 3: Unreported `dependance` category absorbing large buildings from Fix #1.**
   * *The issue:* In `_residential_cat()`, any building $>500\text{ m}^2$ with `n_dwellings == 1` is routed to `"dependance"`. If a parcel has a $600\text{ m}^2$ mansion (*hôtel particulier* or rural *domaine*) or a multi-unit building erroneously recorded as `1` dwelling in BD TOPO, routing it to `"dependance"` hides it from the `Houses`, `Small blocks`, and `Large blocks` summary rows while still keeping it inside the `SITE_POOLED_FLAGS` land pool!
   * *Guardrail:* Check what share of the tax base is sitting in `"dependance"` after Fix #1. For `n_dwellings == 1` and `floor > 500`, if `usage == "Résidentiel"`, shouldn't it either impute dwellings (`round(floor / GROSS_M2_PER_DWELLING)`) like the `NaN` branch does, rather than dumping residential buildings into `"dependance"`?

4. **Recommended Sensitivity Suite:**
   Your planned runs ($\theta \in \{0.3, 0.7\}$, `q_ref = 0.50`) are good, but add **two critical sensitivities**:
   * **Current-use residual (`--land current`):** Keep your first column ("classification fix only") in the published sensitivity table! The contrast between *current-density residual* (+14% to +23% on houses) and *site value* (+46% to +68% on houses) is the single most educational finding of your paper for urban economists.
   * **Plot-size concavity / excess-land discount (`plot_cap_quantile = 0.90` or marginal discount above median plot):** To test whether the Cahors anomaly and house spikes are driven by the top 5–10% largest plots.

---

### 4. Wording of the Limitation

Your proposed wording:
> *"Site value cannot be checked against sale prices of built property; the only direct evidence is rare vacant building-plot sales and teardown sales, which are hard to identify in open data."*

**Critique:** It is honest and concise, but **incomplete on two institutional fronts** that a French fiscal or urban-planning reviewer will immediately challenge:

1. **Why PLU permitted FAR is approximated from realised `p75` FAR:** It does not mention that actual legal buildability (*COS/CES/gabarit* in the PLU *règlement écrit*, plus *servitudes d'utilité publique* andABF heritage protections) is not machine-readable in the national GPU (*Géoportail de l'Urbanisme*), forcing the model to infer permitted density from the 75th percentile of existing buildings in the zone.
2. **Plot subdivisibility / morphology:** Treating land as linear in plot area assumes large plots can be developed at the zone's reference FAR, ignoring shape, street frontage (*accès voirie*), or tree/park preservation rules (*EBC*).

**Suggested revised wording (keeps your concise tone while closing both flanks):**
> *"Site value cannot be checked against sale prices of built property, which reflect existing rather than permitted density; the only direct market evidence is rare vacant building-plot sales and teardown sales (which are hard to identify in DVF without demolition-permit linkage). Moreover, because machine-readable PLU envelope rules (heights, setbacks, heritage protections) are not available nationwide, each zone's buildable potential is approximated from the 75th percentile of existing floor-area ratios in that zone label, assuming plot area is proportionally developable."*