# Gemini review of the unbuilt-land estimate, 29 October 2026

## Prompt

You are an expert in French land markets and national accounts. Please critique, in under 500 words, an estimate used in a French land value tax model. Say clearly where it is wrong, and give sources (title, publisher, year) for any figure you propose; say "I am not sure" rather than guess.

The national indicative rate divides a yield by taxable land: INSEE AN.2111 (terrains supportant des bâtiments, end-2025 provisional, T_8200_2025) 7 032 Md€ minus 941 public = 6 091 Md€. INSEE's method note (fiche méthodologique 24, base 2020, July 2026) says the buildable part of unbuilt land is valued at housing prices, inside unbuilt-land lines (AN.2119 "autres terrains", 712 Md€, of which 147 public), not split out. Building plots are in the reform (only zones A/N are excluded), so we add an estimate:
- AU zones: Cerema (Nov 2023, "Consommation d'espaces et documents d'urbanisme") counts 144 976 ha of unbuilt AU land in 12 051 communes, an under-count. We use 145 000 / 185 000 / 250 000 ha at 10 / 20 / 40 €/m² (raw, unserviced land).
- Vacant plots in U zones: no national stock found. We assume 100 000 / 150 000 / 250 000 ha at 50 / 100 / 150 €/m² (SDES EPTB 2024: serviced plots for houses averaged 102 €/m²).
- 80-90 % privately held.
Result: central 159 Md€ (range 58-380), i.e. +2.6 % on the base; S1 rate 1.06 % (1.02-1.08).

Questions: (1) Is the U-zone stock assumption plausible? Any published measure (Cerema "gisements fonciers", "dents creuses", Fichiers fonciers studies, ZAN reports, IGEDD)? (2) Are the €/m² plausible, especially for vacant U plots in expensive cities (Paris region plots trade far above 102 €/m²)? (3) Is there double counting with AN.2111 (e.g. INSEE AN.2111 including land around houses / gardens that a cadastre would call a separate vacant plot)? (4) Would you present this as a central estimate in the base, or only as a sensitivity?


## Reply

**Where the estimate is wrong**

1. **Double counting with AN.2111 (Question 3):** This is the main conceptual flaw. Under ESA 2010 (*System of National Accounts*, Eurostat, 2013, Annex 7.1), AN.2111 includes not just building footprints, but all surrounding gardens, yards, and curtilage forming part of the residential property’s market value. In the French cadastre (*Fichiers fonciers*), a residential garden is frequently split into a contiguous, separate *parcelle non bâtie* (often buildable in zone U). Adding a bottom-up estimate of U-zone "vacant" plots to AN.2111 double-counts residential gardens and potential *divisions parcellaires* already priced into AN.2111 via hedonic housing models.
2. **Misalignment with AN.2119:** Private AN.2119 is 565 Md€ (712 minus 147). Because INSEE already values buildable unbuilt land at housing-linked prices inside non-built lines, your 565 Md€ ceiling includes recreational land, quarries, and private buildable land. A top-down deduction from AN.2119 is safer than a bottom-up addition, though your 380 Md€ upper bound is uncomfortably close to the 565 Md€ total.
3. **Price weighting (Question 2):** Applying SDES’s *Enquête sur le prix des terrains à bâtir* (EPTB) average (~102 €/m²) to the *entire* U-zone stock is wrong. EPTB measures only **flows** of plots bought specifically for **single-family houses** (diffuse or *lotissements*). It suffers from two opposite biases when applied to the stock:
   * *Downward bias:* It excludes land bought by developers for collective housing in dense U zones (e.g., Île-de-France, major *métropoles*), where land residual values per m² of ground are orders of magnitude higher due to floor-area ratios (PLU *gabarits*).
   * *Upward bias:* EPTB is transaction-weighted toward dynamic markets, whereas the *stock* of unbuilt U/AU land is heavily skewed toward rural or shrinking communes (*détendus*) where prices are <30 €/m². Whether these biases cancel out is unknown; I am not sure of the true stock-weighted national mean price.

**U-zone stock plausibility (Question 1)**

Your 100k–250k ha assumption for vacant U-zone land is plausible as an order of magnitude for total unbuilt U-zone surfaces, but likely overstates *strictly vacant, standalone* plots (excluding contiguous residential gardens). While Cerema, the *Observatoire de l'artificialisation*, and IGEDD publish local or regional *études de densification* and *dents creuses* analyses using *Fichiers fonciers* and the *GPU (Géoportail de l'urbanisme)*, **I am not sure** of any published report providing a consolidated national hectare figure specifically for standalone vacant U-zone *dents creuses* across all 35,000 communes.

**Recommendation (Question 4)**

Present this **only as a sensitivity**, not in the central base. 
* **Reason:** The risk of double-counting contiguous gardens already captured in AN.2111 is high, the national U-zone stock is unverified, and the fiscal impact is tiny (+2.6% on the base, shifting the rate by ~0.03 percentage points, well within the margin of error of INSEE’s provisional AN.2111). 
* **Alternative:** For the central base, use AN.2111 alone, or take a simple top-down share of private AN.2119 (565 Md€) to avoid cadastral/SNA boundary mismatches.


## What was done

- Double counting with AN.2111 (gardens sold with the house): accepted. INSEE values land under dwellings through house prices, so a garden on its own cadastral parcel is in AN.2111 when sold with the house. Vacant U plots moved out of the base into a sensitivity.
- EPTB price bias for the stock: noted; it only concerns the U part, now a sensitivity.
- Top-down share of private AN.2119 instead: not done. AN.2119 mixes buildable, recreational and other land with no published split, so any share would be as arbitrary as the bottom-up estimate.
- AU zones stay in the base: they are counted (Cerema) and are not gardens of existing houses.
