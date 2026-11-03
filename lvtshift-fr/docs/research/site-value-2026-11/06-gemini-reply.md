### 1. Central Case Defensibility: Current-Use vs. Site Value

**Verdict:** Your proposed two-track approach—using an empirically disciplined, current-use land allocation as the central case and publishing a normative "site value" (highest and best use, or HBU) as an upper band—is not only defensible, **it is the only methodologically rigorous option given French open data.**

**The Theoretical vs. Administrative Tension:**
In pure Georgist or public-finance theory (e.g., Dye & England, 2010; Vickrey, 1999), an LVT must tax *site value* (unimproved land at its legally permissible HBU) to preserve the neutrality of the tax with respect to development decisions. If your model’s land value scales with existing floor area (as it does in your current flat methodology), you are legally and economically modeling a property tax with a structural exemption, not a true split-rate LVT, because the marginal tax rate on building *new* floor area is positive.

However, in French administrative reality and international practice, pure HBU is rarely observable without clean, digitized, parcel-level zoning envelopes:
* **International Precedent:** Denmark’s *Grundskyld* and the new German *Bodenwertmodell* (Baden-Württemberg) rely on official land value zones (*Bodenrichtwerte* via BORIS) coupled with legally binding floor-area ratios (*Geschossflächenzahl* - GFZ). Even then, Denmark recently had to overhaul its system (*Vurderingsstyrelsen*) because estimating HBU for built-up urban parcels generated massive legal challenges when theoretical zoning conflicted with physical or heritage constraints.
* **The French Context:** France lacks a harmonized national database of permissible FAR (*Coefficient d’Occupation des Sols* was abolished by the ALUR law in 2014; PLU rules now govern via complex 3D envelopes: height, setback, and *emprise au sol*). In dense French cities, a 19th-century *maison de ville* in a zone that technically permits $R+4$ often cannot be demolished due to *Architectes des Bâtiments de France* (ABF) perimeters, *Plan de Sauvegarde et de Mise en Valeur* (PSMV), or courtyard configurations. 
* **French Tax Law Logic:** The DGFiP’s own valuation revisions (*RVLLP* implemented in 2017 for commercial, and the upcoming *RVLLH* for residential under Article 1496 of the CGI) strictly value properties based on *actual, current use* and physical characteristics, completely ignoring unbuilt zoning potential.

**Recommendation:** Keep the current-use allocation as the baseline because it is anchored to observable market transactions (DVF). However, **you must reframe how you describe the two variants**. Do not frame the site-value band merely as an "uncheckable concept variant." Frame the central case as an **"Administrative Current-Use Split-Rate Tax" (similar to Danish apartment floor-space rules)** and the upper band as an **"Economic HBU Split-Rate Tax."** Explicitly note that the shift in tax incidence for small 2–4 dwelling buildings (+20 to +90 points) between the two models represents the *tax penalty on land underutilization*—which is a feature, not a bug, of a pure LVT, even if it is politically explosive.

---

### 2. Soundness of the $\gamma = 0.35$ Plot Elasticity

**Verdict:** $\gamma = 0.35$ is exceptionally well-grounded in the French urban economics literature and is the right parameter for your central (current-use) case. 

**Theoretical and Empirical Grounding:**
* **Glaeser & Gyourko (2003) Distinction:** You correctly note the distinction between the *extensive* margin (the value of a plot with a permit to build a house) and the *intensive* margin (the value of an extra square meter of garden). Under strict French PLU rules, an extra $100\text{ m}^2$ of garden on a single-family plot rarely confers the right to build a second house (due to minimum lot sizes, frontage rules, or *emprise au sol* caps). Thus,DVF regressions capture the intensive margin (amenity value).
* **French Literature Benchmarks:** Combes, Duranton, and Gobillon (2019, 2021 – *Journal of Political Economy* / *Review of Economic Studies*, using EPTB and DVF) estimate the structural elasticity of land prices with respect to plot size in French urban areas. Because land is traded in discrete bundles, the price per $\text{m}^2$ declines steeply with plot size (concave total value function). Their findings align with a total land value elasticity with respect to lot size between $0.25$ and $0.40$ once location is finely controlled for. 
* **Fixing the Residual Bias:** Your agent’s finding that the residual land value $(P - B)$ has a plot elasticity of $0.46$ and a floor-area elasticity of $-0.13$ is a classic symptom of **measurement error in the building replacement cost ($B$)**. Standard depreciated replacement cost models underestimate both the true economic depreciation of old structures (Davis et al., 2017) and the unobserved quality of large houses. When floor area increases, if your model overstates $B$, then $(P - B)$ is artificially depressed, yielding the $-0.13$ elasticity. 

**Conclusion on $\gamma$:** By stripping out the noisy residual at the parcel level, pooling at the IRIS level, and reallocating via $\text{Plot}^{0.35}$, you effectively purge the parcel-level building cost measurement error while respecting the concavity of urban land pricing. It is a very clean econometric fix.

---

### 3. Holding IRIS House Land Totals Fixed

**Verdict:** Sound in homogeneous suburban/peri-urban IRISes, but **highly fragile in dense urban cores** where the sample of actual houses is small ($N < 20$).

**The Risks:**
1. **Small-Sample Variance and Outlier Contamination:** In Paris, Lyon, and Villeurbanne, an IRIS (roughly 2,000 residents) is overwhelmingly composed of multi-family flats. It might contain only 3 to 10 true single-family houses. If even *one* of those houses has a mismeasured floor area (which inflates the initial hedonic market value) or is a misclassified commercial/institutional building that slipped under your $300\text{ m}^2$ radar, the IRIS "house land pool" will be severely distorted. Every house in that IRIS will inherit that distortion.
2. **Ecological Fallacy of the Pool:** Under your current model, the IRIS house land pool is the sum of $\text{Clipped}(P_{\text{hedonic}} - B)$. Because $P_{\text{hedonic}}$ currently scales purely with *floor area*, an IRIS that happens to have 5 large-floor-area/zero-garden townhomes will generate a massive "land pool," whereas an IRIS next door with 5 small-floor-area cottages on large plots will generate a tiny "land pool." Reallocating *within* the IRIS fixes the intra-IRIS distribution, but locks in the **inter-IRIS error** caused by the original floor-area-based hedonic.

**Required Mitigation (Empirical Bayes / Shrinkage):**
Do not rely strictly on raw IRIS pools when house counts are low. 
* If the number of houses in an IRIS is below a threshold (say, $N < 30$), **pool the land total at the Commune or "Grand Quartier" level**, or use an Empirical Bayes shrinkage estimator that weights the IRIS mean land-per-plot-$\text{m}^{0.35}$ against the commune-level or cell-level apartment land value benchmark.

---

### 4. Removing the Land-Share Cap (15–85%) for Houses

**Verdict:** Removing the 85% *upper* cap is theoretically necessary and empirically validated by your teardown/small-house findings. Removing the 15% *lower* cap is dangerous without a floor guardrail.

**The Risks & Guardrails Needed:**
1. **Upper End (Land Share $> 85\%$):** By reconstructing Market Value as $MV_{\text{new}} = L_{\text{reallocated}} + B_{\text{model}}$, you allow a tiny $60\text{ m}^2$ 1930s bungalow on a $600\text{ m}^2$ plot in Montreuil to have a 92% land share. **This is completely accurate.** Your old model undervalued this parcel because it lacked a plot term; the 85% cap was previously masking that model misspecification. Removing the upper cap is correct.
2. **Lower End (Land Share $< 15\%$ or Negative):** While $\text{Plot}^{0.35}$ is strictly positive (preventing negative land values during reallocation), what happens when you compute the *initial* IRIS pool? If you remove the 15% lower bound during the initial step $(P_{\text{hedonic}} - B)$, houses in depressed markets (e.g., parts of Roubaix or Cahors) where depreciated construction cost $B$ exceeds market price $P$ will contribute *negative* land value to the IRIS pool, collapsing the pool for neighboring houses.
3. **Cadastral Geometries Anomaly (Zero-garden houses):** Some townhouses are built lot-line to lot-line (*en bande*), where $\text{Plot Area} = \text{Building Footprint}$. Others are in horizontal *copropriétés* (common in 1970s suburban developments) where the cadastral parcel in *PCI Vecteur* is huge, and if the parcel-to-building matching isn't divided by the number of lots, one house gets assigned the entire communal green space.

**Guardrails to Implement:**
* **Guardrail 1 (Pool Formation):** Keep a floor (e.g., 10% or 15%) when calculating individual residuals *to form the IRIS pool*, so structural over-valuation of $B$ in weak markets doesn't destroy the aggregate pool. Once the pool is formed and reallocated via $\text{Plot}^{0.35}$, remove the upper cap (85%) on the resulting parcel-level $L / (L+B)$ ratio.
* **Guardrail 2 (Plot-to-Footprint Winsorization):** Winsorize the input plot area for the house category at the 99th percentile of the commune (or cap the ratio of $\text{Plot Area} / \text{Building Footprint}$ at, say, 20) to prevent horizontal *copropriétés* or agricultural parcels attached to a house from soaking up the entire IRIS land pool.

---

### 5. Separating Real Houses from Large Single-Owner Buildings (The $300\text{ m}^2$ Threshold)

**Verdict:** A hard $300\text{ m}^2$ threshold is a blunt instrument that will misclassify large bourgeois houses (*hôtels particuliers*, large rural farmhouses in Cahors/Figeac) while failing to catch smaller commercial/institutional buildings or *immeubles de rapport* (rental apartment blocks owned by a single SCI or family, which in open data often show up without individual *lots de copropriété* and thus get tagged as "1 or 0 dwellings").

**Better Open-Data Signals in the French Ecosystem:**
Since you are already operating on French open data, **the BDNB (Base de Données Nationale des Bâtiments)** produced by the CSTB is by far your best tool here, as it already cross-references *Fichiers Fonciers* (MAJIC), *BD TOPO*, *DPE*, and *DVF*.

1. **Why "0 or 1 dwelling" fails in MAJIC / Fichiers Fonciers:** In the DGFiP *Fichiers Fonciers*, a building’s dwelling count (`nb_log`) is aggregated from the *locaux* file. If a building is purely commercial/office/industrial, `nb_log = 0`. If your pipeline defaults `nb_log <= 1` into "Single Family Residential," you are sweeping every factory, warehouse, clinic, and office building in Paris into the "House" category! Furthermore, some social housing blocks or single-owner rental buildings have quirks in how *lots* are recorded in simplified open extracts.
2. **Use BD TOPO (IGN) `usage_1` and `nature`:** 
   * `usage_1 = "Résidentiel"` vs `"Commercial et services"`, `"Industriel"`, `"Indifférencié"`. **Never classify a building with `nb_log == 0` as a house.** If `nb_log == 0`, it is non-residential (or a garage/annex).
3. **Use BDNB / Fichiers Fonciers Morphological Ratios:**
   *Instead of a flat $300\text{ m}^2$ cutoff*, use a **multi-criteria filter** available in BDNB:
   * **Dwelling count:** Strictly `nb_log == 1` (or `nb_log == 2` if you want to include houses with an attached studio). Move all `nb_log == 0` to commercial/other.
   * **Height and Stories:** In BD TOPO / BDNB, check `hauteur` (height) and `nb_niveau` (floors). A single-family house rarely exceeds $R+2+\text{combles}$ (approx. 10–12 meters). A building in Paris with `nb_log == 1`, floor area of $800\text{ m}^2$, and `hauteur == 18m` is either an embassy, a convent, a clinic, or an *hôtel particulier* converted to offices.
   * **Footprint (*Emprise au sol*):** A house with $350\text{ m}^2$ of floor area over 3 floors has an *emprise* of $\sim 120\text{ m}^2$ (plausible large family home). A building with $350\text{ m}^2$ on a single level (`emprise > 300 m²`) is almost certainly a commercial shed, school, or warehouse.

**Recommended Classification Rule for "House":**
`Usage == Residential` AND `nb_log == 1` AND `Building Footprint < 250 m²` AND (`Floor Area <= 350 m²` OR `Levels <= 3`). Everything else with `Usage == Residential` goes to the "Blocks/Other Residential" residual pool.

---

### 6. Ranked List of What is Missing or Wrong in the Plan

Here is a prioritized critique of conceptual, econometric, and institutional blind spots in your current plan:

#### Rank 1 (Critical): The "House Error" Validation Metric is Circular
In Section 6, you evaluate designs based on the "median absolute log error of modelled value against sale price." Yet in your Proposed Plan (Step 2), for the recommended design, you state: *"set market value = land + building cost."* 
* **Wait:** If $L_{\text{house}}$ is reallocated from the IRIS pool via $\text{Plot}^{0.35}$, and then you redefine $MV_{\text{new}} = L_{\text{reallocated}} + B_{\text{cost}}$, and your validation metric checks how close $MV_{\text{new}}$ is to DVF Sale Price $P_{\text{sale}}$... then of course the error drops from $0.246$ to $0.180$! You have effectively just injected a plot-size term into the market value predictor by the back door. 
* **Why did Design (c) ("House hedonic with a plot term", error 0.262) perform worse than the Recommended Design (error 0.180)?** Econometrically, adding a log(plot) term directly to a hedonic regression *cannot* perform worse in-sample or on clean out-of-sample data than an ad-hoc two-step IRIS reallocation *unless* your direct hedonic in Design (c) was contaminated by the misclassified €1.5m+ Paris buildings! Fix the classification *first* (PR #1), and then re-test Design (c). You may find that a clean hedonic with a plot term and spatial fixed effects outperforms the IRIS pool reallocation, avoiding the IRIS small-sample issues entirely.

#### Rank 2 (High): Tax Incidence Ignorance of French Taxe Foncière (TFPB) Mechanics
Your robustness checks compare your modelled 4:1 LVT against "current tax." How are you computing "current tax"? 
* In France, TFPB is **not** based on market value or physical construction cost. It is based on the 1970 *Valeur Locative Cadastrale* (VLC).
* Crucially, the 1970 VLC calculation uses **coefficients d'entretien** (maintenance), **coefficients de situation** (location), and **équivalences superficielles** (which turn bathrooms, running water, electricity, and garages into virtual square meters!). 
* Because 1970 VLCs have never been rebased (only updated via flat national inflation coefficients and occasional *commissions communales*), **current French TFPB systematically under-taxes high-land-value historic urban cores (like central Paris/Lyon) and over-taxes 1970s/1980s suburban comfort (like Aulnay-sous-Bois or Villeurbanne)** (see Institut des Politiques Publiques - IPP notes by André & Meslin, or Cour des Comptes reports).
* **Implication for your model:** When you shift from Current TFPB to your 4:1 LVT, you are simultaneously modeling **two massive shocks**: (1) a revaluation from 1970 cadastral values to current market values (essentially the upcoming 2028 RVLLH reform), and (2) a shift from a 1:1 property tax to a 4:1 split-rate tax. If you don't decompose these two effects, you are attributing to "LVT" what is actually just the modernization of 1970 tax bases. **You should report the baseline against both actual TFPB and a 1:1 modern Market Value tax.**

#### Rank 3 (Medium-High): Teardown Validation (DVF + Sitadel) Pitfalls
Using DVF sales matched to Sitadel demolition/building permits is a brilliant idea (following Dye & McMillen, 2007), but in France, it has two major traps:
1. **Promoteur (Developer) Sales and VAT:** When a developer buys a teardown to build flats, the transaction is often subject to *TVA sur la marge* or full VAT, and frequently involves multiple cadastral parcels assembled over 2–3 years (*remembrement*). Simple 1-to-1 parcel matching in DVF will miss parcel assemblies, which are the true HBU site-value transactions.
2. **Endogeneity of Teardowns:** As Rosenthal & Helsley (1994) and Munneke & Womack (2015) show, teardowns are not a random sample of houses; they occur specifically where the ratio of existing structure value to HBU land value hits an optimal stopping threshold. If you validate your *current-use* house land model against *teardown* prices, your central model **should** systematically underpredict teardown prices in upzoned areas (because teardown prices reflect HBU option value, i.e., your "site value" upper band, plus demolition costs). Use teardowns to validate your **Step 4 Site Value Upper Band**, not your Step 2 Current-Use Central Case!

#### Rank 4 (Medium): Commercial & Industrial Land Valuation (RVLLP)
You mention that "business and industry pay less" survives every design. Why? 
* If commercial/industrial buildings are valued using the residual method or flat-like floor-area allocations, you are likely **underestimating industrial/commercial land values**. Big-box retail (*zones commerciales* in the periphery of Cahors, Aulnay, or Lyon) and logistics warehouses have massive plot footprints (*emprise foncière* / parking lots) and very cheap, low-density metal-shed structures ($B$ is tiny, Plot is huge). 
* Under a true LVT or site-value tax, single-story suburban retail and surface parking lots experience a **massive tax increase**, whereas downtown multi-story offices see a tax cut. If your model shows business/industry paying less across the board, it suggests your model is still pricing commercial land proportional to *built floor area* rather than *plot footprint*, thereby letting suburban retail parks off the hook.

### Summary of Recommended Execution Order for PRs:
1. **PR 1 (Classification):** Use BDNB/BD TOPO (`nb_log == 1`, `Usage == Résidentiel`, Footprint $< 250\text{ m}^2$) to purge the house pool. Send `nb_log == 0` to commercial/institutional.
2. **PR 2 (Re-test Hedonic vs. IRIS Pool):** On the newly cleaned house dataset, re-run Design (c) (direct hedonic with $\log(\text{plot})$) vs. the IRIS $\text{Plot}^{0.35}$ reallocation (using Empirical Bayes shrinkage for IRISes with $< 30$ houses and a 15% floor during pool formation).
3. **PR 3 (Decomposition & Site Value Band):** Publish the central case alongside the HBU Site Value upper band, and explicitly decompose the incidence results into the "Revaluation Effect" (1970 VLC $\to$ 1:1 Market Value) and the "Split-Rate Effect" (1:1 Market Value $\to$ 4:1 LVT).