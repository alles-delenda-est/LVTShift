Here is a rigorous analysis of the conceptual, methodological, and French data issues raised in your research brief.

*(Note: As an AI, I cannot directly inspect your local repository files at the local repository, so this response relies entirely on the detailed specifications provided in your prompt.)*

---

### 1. Concept: Current Use vs. Highest and Best Use (HBU)

In both public finance theory and mass appraisal practice, **a Land Value Tax (LVT) or split-rate tax must tax Site Value under its Highest and Best Use (HBU) as if vacant (within legal zoning constraints)**, *not* the land’s residual value in its current built density. 

If land value is scaled to existing floor area, the tax ceases to be a tax on land scarcity/location rent and becomes a disguised tax on buildings (capital). That eliminates the neutrality and incentive effects of an LVT (encouraging infill and penalizing land banking or under-utilization).

#### Literature & International Practice:
*   **Dye & England (2009, Lincoln Institute) & IAAO Standards:** The International Association of Assessing Officers (*Standard on Mass Appraisal of Real Property*) explicitly mandates that for property taxation, land must be valued as if vacant and available for development to its highest and best legally permissible use. 
*   **Baden-Württemberg (Germany, 2025 Reform):** Under the pure *Bodenwertmodell*, tax is based strictly on **Plot Area × *Bodenrichtwert*** (Standard Land Value per $m^2$ of land in a given zone). The *Bodenrichtwert* is calibrated to a reference permitted density (Floor Area Ratio / *Geschossflächenzahl* - GFZ) for the zone, completely ignoring the actual building standing on the plot (with a statutory 30% tax rate discount for residential use).
*   **Denmark (*Grundværdi*, 2024 Reform):** The new *Vurderingsstyrelsen* system values land at its best possible economic use under local planning laws (*plangrundlaget*), independent of the current building. For multi-family zones, it taxes the permitted floor area potential; for single-family zones, it taxes the plot size.
*   **New South Wales (Australia) & New Zealand:** The Valuer General determines "Land Value" assuming improvements do not exist, constrained by current zoning/planning controls (with rare carve-outs for heritage restrictions).
*   **Estonia:** Taxes land only, based on zones of equal value and intended land-use designation (*sihtotstarve*) and plot size, ignoring actual built floor area.
*   **UK / Scottish Land Commission Studies (e.g., Hughes et al., 2018; Mirrlees Review):** Consistently define LVT base as "optimum permitted use" value.

---

### 2. Methods & Biases in Mass Appraisal and Literature

#### Standard Methods:
1.  **Land Residual / Abstraction ($\text{Land} = \text{Market Value} - \text{Depreciated Replacement Cost}$):**
    *   *Used in:* Davis & Heathcote (2007), Davis, Larson, Oliner & Shui (2021, FHFA data).
    *   *The High-Density Bias:* As Albouy, Ehrlich & Shin (2018) and Bourassa et al. (2011) demonstrate, **the residual method fails for under-utilized parcels in dense areas.** When a 10-storey building sells, its price captures the full economic rent of the zoning envelope. Subtracting construction cost yields the true HBU land value (plus developer profit/option value). When a 1-storey house on an identical neighboring plot sells, unless it is bought by a developer for teardown, its transaction price only reflects its current use value, or fails to isolate the teardown option. Worse, in your current model, because market price is imputed as $\text{€/m}^2 \times \text{habitable floor area}$, **you are not even observing the market premium of a large plot**—you are mathematically forcing land value to be a function of floor area.
2.  **Hedonic Models with Plot Size:**
    *   *Used in:* Diewert, de Haan & Hendriks (2015); Kuminoff & Pope (2013).
    *   *Functional Form:* A simple log-linear hedonic fails because the price of a property is additive in land and structure ($\text{Price} = P_L \cdot L^\beta + P_S \cdot S$). Standard practice uses either a non-linear hedonic or interacts $\ln(\text{Plot Area})$ with location fixed effects.
    *   *Platt / Lot-Size Adjustment Curves:* Land value per $m^2$ exhibits strong diminishing marginal returns for individual houses (the "plottage" or "depth" curve in IAAO manuals). Typically, $\text{Land Value} \propto (\text{Plot Area})^\beta$, where $\beta \in [0.3, 0.6]$ for suburban single-family lots, approaching $1.0$ only when the plot is large enough to be subdivided or developed into multi-family housing.
3.  **Treatment of Flats (*Copropriété*):**
    *   In mass appraisal (e.g., Denmark, Australia, Germany), the total land value of the mother parcel (*assiette de la copropriété*) is calculated first based on plot area (or permitted density). It is then apportioned to individual flats according to their ownership shares (*tantièmes de copropriété*), which in open data is accurately proxied by each flat's share of the building's total habitable floor area.

---

### 3. French Specifics & Open Data Realities

#### How French Institutions Value Land:
*   **INSEE / Banque de France (National Accounts, Patrimoine non financier):** Following the Eurostat/OECD *Compilation Guide on Land Estimations* (2015), France uses the **hedonic/residual method at the macro level**. Total housing stock value is estimated from transactions; total structure value (AN.111) is calculated via the Perpetual Inventory Method (PIM) using construction cost indices and geometric depreciation; Land (AN.2111) is the macro residual. In France, land accounts for **~50% to 60% of total residential wealth** in the national accounts.
*   **Notaires / Developer Practice (*Compte à rebours*):** In dense urban zones (Zones UA/UB of the PLU), land does not trade per $m^2$ of plot; it trades in **€/m² SHON / SDP (Surface de Planche Développée)**—known as the *charge foncière*. However, **the *potentiel constructible* belongs to the plot, not the existing building.** If a zone allows a *Coefficient d'Emprise au Sol* (CES) of 0.5 and a height of 4 storeys ($\text{FAR} \approx 2.0$), a $500\text{ m}^2$ plot can host $1,000\text{ m}^2$ of floor area. Its site value is $1,000 \times \text{Charge Foncière}$, regardless of whether a $100\text{ m}^2$ bungalow currently sits on it.
*   **French Economic Literature (CAE, Trannoy & Wasmer 2013, Sénat):** French LVT proposals (e.g., *Conseil d'Analyse Économique* Note n°7, 2013; Trannoy & Wasmer's *La mobilisation du foncier*) explicitly target the taxing of *rentes foncières* to combat land retention (*rétention foncière*) and urban sprawl. A model that taxes existing floor area instead of plot/constructible area contradicts the core mechanism advocated by the CAE.

#### Is PLU Permitted Density Available in French Open Data?
**No, not nationwide in structured form.**
*   The **GPU (Géoportail de l'urbanisme)** provides standardized polygons for general zone types (`TYPEZONE`: `U`, `AU`, `A`, `N`) under the CNIG standard.
*   However, since the **ALUR Law (2014)** abolished the *Coefficient d'Occupation des Sols* (COS / Floor Area Ratio), permitted density in France is governed by a combination of 3D rules: maximum height (*hauteur maximale*), footprint ratio (*Coefficient d'Emprise au Sol* - CES), and setback rules (*reculs*). In the GPU, these rules are locked inside unstructured PDF documents (*règlements écrits*) or inconsistent local attributes. **Therefore, Candidate Design (d) using direct PLU permitted floor area is currently unfeasible at national scale using open data alone.**

---

### 4. Evaluation of Candidate Designs

Given the open data constraints, here is how your candidate designs compare:

#### Design (a): IRIS Residual Total Allocated by Plot Area (German *Bodenrichtwert* proxy)
*   **Mechanism:** Compute total land value of the IRIS via your current residual method ($\sum V_{\text{land, IRIS}}$). Then redistribute this pool across parcels in the IRIS proportional to $A_{\text{plot}}^\beta$, where $\beta$ is a lot-size elasticity (e.g., $\beta = 1.0$ in dense urban cores where land is subdividable/redevelopable for flats, and $\beta \approx 0.5$ in peripheral single-family zones).
*   **Feasibility:** Very high. Uses existing DVF, Cadastre (`contenance`), and IRIS boundaries.
*   **Biases:** Assumes the current built stock in the IRIS as a whole captures the aggregate land rent of the IRIS. If an entire IRIS is under-built relative to zoning, the IRIS total is slightly too low, though within-IRIS incidence between houses and flats is fixed.
*   **Impact on Results:** Solves the Paris house cap issue if you stop capping land share at the *current* building's market value! (Note: In Paris, a house on a $300\text{ m}^2$ plot *should* have a site value that is 95%+ of its current-use value, because the teardown land value for an apartment block dwarfs the value of the house structure).

#### Design (b): Direct Land €/m² from *Terrain-à-bâtir* (TAB) & DVF
*   **Mechanism:** Estimate land price per $m^2$ from vacant land sales (DVF/DV3F + EPTB).
*   **Feasibility & Biases:** **Fails in dense urban cores.** There are virtually zero vacant *terrain-à-bâtir* sales in Paris or inner Lyon/Marseille. Those that exist are anomalous micro-plots or unbuildable slivers. Relying on TAB will massively under-estimate urban center land values or require extreme spatial extrapolation from the suburbs.

#### Design (c): Hedonic Model with Plot Area + Copropriété Apportionment
*   **Mechanism:** 
    1. For houses, estimate a hedonic model on DVF: $\text{Price} = f(\text{Floor Area}, \text{Plot Area}, \text{Location})$. Specifically, estimate the local marginal value of plot area vs. structure.
    2. For flats, estimate the residual land value at the building/parcel level, and divide by the parcel's plot area to get the implied multi-family land value per $m^2$ of plot.
*   **Feasibility:** High, as DVF (`surface_reelle_bati`, `surface_terrain`) or Cerema DV3F (`sbati`, `sterr`) link house sales to their plot size.
*   **Biases:** A house hedonic measures the *consumption value of a garden* in current use, not the *redevelopment option value* for an apartment building. In a suburb, garden value $\approx$ site value. In central Paris, a house hedonic might still understate the true HBU site value if zoning allows a 6-storey block, unless you allow the multi-family land €/m² to price the plot of neighboring houses.

#### Design (d): Permitted-Density Site Value
*   **Feasibility:** Infeasible from GPU open data (see Section 3). However, you *can* approximate permitted density using **realized density of surrounding modern buildings** (e.g., 90th percentile of Floor-to-Plot ratio of buildings in the IRIS from BD TOPO / Majic/FF).

---

### Recommended Solution: A Hybrid "Zoned Bodenrichtwert" Approach (Combining (a), (c), and empirical FAR)

To solve your problem rigorously with open data, you should separate **Single-Family Dominated Zones** from **Multi-Family / Dense Urban Zones** at the IRIS level:

1.  **Keep the IRIS Total Land Value Pool from the Residual:** At the aggregate IRIS level, the sum of residuals ($\sum \text{Market} - \sum \text{DRC}$) is a robust anchor that matches National Accounts methodology.
2.  **Determine the Local "Reference Density" (Implied Zoning):** Within each IRIS (or 400m cell), compute the share of flats vs. houses, or the 80th percentile of observed Floor-to-Plot ratios ($\text{FAR} = \text{Floor Area} / \text{Plot Area}$).
3.  **Allocate the IRIS Land Pool to Parcels using a Lot-Size Curve:**
    *   Assign each built residential parcel an **Effective Plot Weight** $W_i = (\text{Plot Area}_i)^\beta$.
    *   In **dense/multi-family IRIS** (where flats > 50% of units), set $\beta \in [0.8, 1.0]$. Here, land trades on development potential proportional to plot surface. A house sitting on a $500\text{ m}^2$ plot in Paris gets the same land value as a 6-storey apartment block sitting on a $500\text{ m}^2$ plot next door. **(Crucial: Remove or relax the 85%/95% land share cap for houses in dense zones; under HBU, it is normal for a low-density building's site value to exceed 85% of its current-use value).**
    *   In **suburban/rural IRIS** (houses > 80%), set $\beta \approx 0.45$ (calibrated via a DVF hedonic on houses: $\ln(\text{Price} - \text{DRC}) = \alpha_{\text{IRIS}} + \beta \ln(\text{Plot Area})$). This captures the diminishing marginal value of large gardens where subdivision is either not permitted or lacks demand.
4.  **Apportion to Units:** For a single house on a parcel, it takes 100% of the parcel's land value. For a *copropriété* (flats), each flat takes a share of the parcel's land value equal to $\frac{\text{Flat Floor Area}}{\text{Total Building Floor Area}}$.

---

### 5. Validation Tests Against Observable Data

You can prove this hybrid method is superior to the floor-area residual using four observable tests:

1.  **The DVF House Plot-Size Gradient Test (Internal Validity):**
    *   Run a regression on DVF house sales: $\text{Sale Price} - \text{Imputed DRC} = \alpha_{\text{cell}} + \gamma \cdot f(\text{Plot Area}) + \delta \cdot \text{Floor Area}$.
    *   Under your current model, $\gamma \approx 0$ and $\delta$ is large. In actual DVF data, once DRC is subtracted, $\gamma$ will be strongly positive and statistically significant, giving you the exact empirical value for the lot-size elasticity $\beta$ (typically $0.35 - 0.55$ in suburban France).
2.  **The Teardown / Vacant Land Boundary Test (External Validity via DVF & EPTB):**
    *   Compare your model's imputed land value per $m^2$ of plot for houses in suburban/peri-urban IRIS against actual DVF *Terrain-à-bâtir* (TAB) sales in the same commune, and against **SDES EPTB** department averages (adjusted for plot size).
    *   The floor-area residual method will show massive dispersion in land €/m² of plot within the same neighborhood (varying wildly with house size). A plot-based allocation will converge closely to observed TAB €/m² and EPTB departmental benchmarks.
3.  **The Copropriété vs. House Parity Test in Dense Zones:**
    *   In urban transition zones (e.g., *petite couronne* of Paris, inner suburbs of Lyon), compare the imputed land value per $m^2$ of plot for a $400\text{ m}^2$ parcel with a small apartment building vs. a $400\text{ m}^2$ parcel with a house. Under an LVT, these must be roughly equal.
4.  **Macro Calibration (INSEE / Banque de France Comptes Nationaux):**
    *   Check that the national aggregate residential land share ($\frac{\sum V_{\text{land}}}{\sum V_{\text{market}}}$) remains in the **50%–60% range** published by INSEE (Table *Comptes de patrimoine - AN.2111 Terrains bâtis*). Because Design (a) preserves IRIS totals, your macro calibration will remain intact while fixing the micro-incidence across property types and income deciles.