# Gemini's reply, 11 November 2026 (verbatim)

**(1) Is this a sound replacement?**
**No, it is flawed.** Your base model defines parcel land value $L_i$ via an IRIS-level site-value allocation, *not* a parcel-level residual ($L_i \neq V_i - B_i$). By shifting $L_i$ by $k B_i$ at the parcel level, you inject building values directly into the land tax base. Under a pure LVT, two identical plots in the same IRIS must pay the same tax regardless of what is built on them. Your proposed band makes the sensitivity of a *land* tax depend on the *building* on that specific plot, violating the core logic of your own model.

**(2) Parcel-level vs. IRIS-level?**
**It must be applied at the IRIS level.** The parcel-level version is a **bad approximation**.
*   *Why:* If an IRIS has homogeneous $B/V$ ratios, scaling $B$ at the IRIS level just scales the IRIS total $L_{IRIS}$ uniformly; within that IRIS, relative tax shares wouldn't change at all (only between-IRIS shares within the commune would shift). Your parcel-level hack, however, creates massive, artificial within-IRIS tax shifts between built and unbuilt plots.
*   *Fix:* You don't need to re-run the site-value sharing. Since within-IRIS weights are fixed, a shock to IRIS building total $B_{IRIS}$ simply scales every parcel's $L_i$ in that IRIS by a uniform factor: $L'_i = L_i \times \frac{\text{clip}(L_{IRIS} + k B_{IRIS}, 0, V_{IRIS})}{L_{IRIS}}$. You only need the IRIS ID in your export to group and sum $L$, $B$, and $V$. (Note: for mono-IRIS communes, this band will still collapse to zero—which is the correct mathematical result for a uniform $B$ shock!).

**(3) +/-10 points of land share vs. +/-X% on building cost?**
**Switch to $\pm X\%$ on building cost (e.g., $\pm 20\%$).** 
Stating it as $\pm 10$ points of land share is a holdover from the split-rate model where the $L/B$ ratio drove the tax. In a pure LVT, targeting a $\pm 10$ point shift in land share across heterogeneous communes is awkward: in rural communes with a 15% land share, a -10pt target requires a massive distortion and mass clipping at zero; in Paris (70% land share), it requires a mild adjustment. Shocking replacement costs by a flat percentage is directly interpretable as construction cost uncertainty and avoids the need for bisection.

**(4) What else does this miss?**
**Everything that matters within an IRIS.** Once you fix Question 2, you will see that $B$ uncertainty only shifts tax *between* rich and poor IRISes within a commune, leaving mono-IRIS communes with zero variance. Under a pure LVT, the dominant uncertainty shifts from the $L/B$ split to **relative land valuation within the commune**:
1.  **The FAR exponent (0.5):** Testing 0.25 vs. 0.75 (or 0 vs 1) will massively shift the tax burden between low-density/vacant plots and dense plots *within* every IRIS. This is now your most important parameter.
2.  **Spatial granularity (MAUP):** The assumption that base land value per $m^2$ is uniform across an entire IRIS. 
3.  **Zone-typical FAR:** Errors in how the regulatory/typical capacity is defined for under-built plots.