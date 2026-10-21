# Construction-cost parameters for LVTShift-FR: sourced recommendation (2025 €)

> **Archived research report** (October 2026), kept as the evidence behind the
> model's parameters. Working files it mentions (downloads, scripts, intermediate
> tables) were kept outside the repository. The decisions taken from it are in
> METHODOLOGY §3.1 and §4.

> **Superseded on one point.** The unit mismatch in §0 and §6 was resolved by
> putting *both* sides of the residual on habitable area, after measuring
> habitable ÷ the model's floor area at 0.64 (flats) and 0.61 (houses): see
> `net-to-gross-measurement.md`. The cost per habitable m² divides these gross
> costs by 0.71 for flats (the 0.74 SU ÷ gross used here, ÷ SU/habitable ≈ 1.04)
> and 0.82 for houses.

Research date 2026-10-19 (some late fetches ran past midnight into 10-20). Every number below cites a source in §9 by its tag, e.g. [S1]. "Fetched live" means I downloaded the primary document or API today and read the figure myself. "Via search snippet" means I only saw it quoted in a search result. Downloads are in `scratchpad/cc_dl/` (treated as untrusted data and text-extracted only). The arithmetic is in `scratchpad/cc_scripts/calc2.py`. No repository file was edited.

---

## 0. Plain-language summary (for a non-coder economist)

- **What the parameter is.** It is the cost of rebuilding today a modern building equivalent to the existing one. Land is excluded. It is expressed per m² of the model's own floor-area measure, which is the building's outside footprint × number of storeys (a *gross* area).
- **The best official evidence is social housing.** Private builders do not publish their costs. Social landlords must report every new-build operation to the State, split into **building works / land / fees**. The ministry's *Bilan des logements aidés* tabulates these costs by region [S1][S2]. This is the only official, open "building-only" cost for *apartment blocks* in France. All its figures are excluding VAT (HT) and per m² of *surface utile* (≈ the floor area of the flats).
- **Two corrections to the earlier research (PR #16).**
  1. The house-cost survey (EPTB) measures surface de plancher, not habitable area [S10].
  2. Its Île-de-France figure is 1 863 €/m², not 1 914. The 1 914 figure is the national number [S7][S12].
- **Getting to our basis** takes three steps:
  1. Bring the 2021–22 figures to 2025 with INSEE's building-cost index (≈ +6–13 %) [S5].
  2. Convert from "per m² of flat" to "per m² of gross building", which is a much smaller number (×≈0.74, because walls, stairwells and corridors count in gross area but not in flat area).
  3. Add architects' and engineers' fees (+15 %) and the 20 % VAT that a private rebuild would pay [S1].
- **Recommended values** (2025 €, per m² gross floor area, VAT and fees included):

| Area | Central | Plausible range | Current config | Current inside range? |
|---|---|---|---|---|
| **Paris** (75056) | **2 650** | 2 350 – 3 100 | 2 300 | **No.** Slightly below; raise it. |
| **Paris inner ring** (92/93/94, incl. Montreuil) | **2 400** | 2 150 – 2 700 | 2 150 | Only just, at the bottom edge |
| **Lyon** (69123, incl. Villeurbanne) | **2 000** | 1 750 – 2 300 | 1 950 | **Yes** |
| **Lyon Métropole ring** | **1 850** | 1 600 – 2 100 | 1 950 | **Yes** (upper half) |
| **Marseille** (13055) | **1 900** | 1 650 – 2 200 | (not set) | n/a |

  Gemini's independent central figures, built from the same evidence, were 2 660 / 2 350 / 2 060 / 1 910 / 1 950 €/m². They are within ~3 % of these (see §7).
- **The most important finding is not a cost number but a unit mismatch in the code.** The model computes market value as a price *per m² of habitable area* (from DVF) × *gross* floor area (`estimate.py` L157–165). That overstates market value by roughly 1/0.74 ≈ 35 %. The building is then valued per *gross* m², so the land residual absorbs the excess and **land shares come out too high, whatever the cost parameter**. There are two ways to fix this:
  - (a) Scale market value by a net-to-gross factor (≈0.74 for flats; Gemini also recommends this).
  - (b) Use the cost *per habitable m²* (≈ ×1.40: Paris ≈ 3 700, Lyon ≈ 2 800).

  Option (a) is cleaner because it also gets the euro *level* of land right. This is a modelling decision for you, and it belongs in its own PR.

---

## 1. Re-verification of PR #16 figures (EPTB, individual houses)

| Item | PR #16 said | Primary source says (fetched live) | Verdict |
|---|---|---|---|
| IdF house cost €/m² 2024 | 1 914 | 266 356 € / 143 m² = **1 863 €/m²**, "5e rang des régions … les moins chères" [S7] | **Wrong.** 1 914 is the national figure [S12]. The 252 222 € used by PR #16 is the house price only in projects *with land purchase* (chapter 4) [S11]. |
| ARA €/m² 2024 | 2 063–2 066 | 252 110 € / 122 m² = **2 066 €/m²**, 3e plus chère [S8]. Rhône dept: 289 216 / 136 = 2 127 | Confirmed |
| PACA €/m² 2024 | "?" | 270 840 € / 126 m² = **2 150 €/m²**, "1e rang … les plus chères" [S9]. Bouches-du-Rhône: 253 433 / 125 = 2 027 | New |
| National 2024 | 1 927 | SDES national release (27/11/2025): **1 914 €/m²**, 118 m² [S12]. Revised DREAL tables: 229 570 € / 119 m² ≈ 1 929 [S7] | Small revision gap |
| Surface basis | "surface habitable" (§5.2 haircut proposed) | "Elle est exprimée en **surface de plancher** (SDP)" [S10] | **Wrong basis.** No habitable→SDP haircut is due on EPTB. |
| HT/TTC | not stated | Methodology states TTC explicitly only for land [S10]. House price is household-declared, and households pay non-recoverable 20 % VAT. | De facto TTC (my inference) |
| BT01 monthly values | via aggregators | INSEE BDM API (fetched live): Dec-2024 131.7, Aug-2025 133.7, Oct-2025 133.2, Feb-2026 135.1, Apr-2026 137.5 [S5] | All five confirmed. Latest: Aug-2026 139.4 |
| Éclairages n°33 Graph 4 (MOD construction 1 470→1 790 €/m² SU) | verified from user-supplied PDF | Re-read from the live PDF [S3] | Confirmed |

**Why EPTB is not used as the main anchor for the dense metros.** It covers only individual houses in diffuse settings: 2 296 houses in all of IdF, with Paris and 92 suppressed ("s") [S7]. Its regional ranking (PACA > ARA > IdF) reflects the mix of houses built (Riviera/Alpine villas, large IdF suburban houses), not the cost of apartment blocks. It is still a useful anchor for house-dominated outer-ring communes (§6, caveat 5).

---

## 2. Collective-housing (logement collectif) evidence

### 2.1 Primary anchor: DHUP/SISAL "Coût des logements ordinaires neufs" (fetched live)

Table 6.12 of the *Bilan 2022 des logements aidés* [S1] (p.57) covers PLAI/PLUS/PLS new ordinary dwellings, direct construction only (**hors VEFA**). Figures are in **€ HT per m² of surface utile**. The cost is split into 3 items per the arrêté of 17/10/2011. Acquisition-improvement, ANRU and residential-home operations are excluded.

| Region | n dwellings (MOD) | SU/dwelling | Total | **Bâtiment** | Charge foncière | Prestations intellectuelles | VEFA share |
|---|---|---|---|---|---|---|---|
| Île-de-France | 5 466 | 60 | 3 694 | **2 236** | 1 070 | 388 | 56.8 % |
| Auvergne-Rhône-Alpes | 3 921 | 70 | 2 445 | **1 571** | 594 | 279 | 52.5 % |
| PACA | 1 246 | 63 | 2 606 | **1 508** | 818 | 280 | 79.4 % |
| France | 32 474 | 65 | 2 537 | **1 700** | 570 | 267 | 52.4 % |
| France excl. IdF | 27 008 | 66 | 2 324 | 1 601 | 478 | 244 | 51.4 % |

The same table in the *Bilan 2021* [S2] (p.67, € HT/m² SU) gives bâtiment of IdF **2 200**, ARA **1 642** and PACA **1 561**. Totals were 3 670 / 2 696 / 2 555.

How the table was read:
- The PDF's table layout scrambles columns in `pdftotext -layout`. I re-extracted it in reading order (`-raw`).
- Every row checks: bâtiment + foncier + prestations = total.
- The VEFA share reproduces from the dwelling counts. For example, IdF: 7 173 / (7 173 + 5 466) = 56.75 %.

Definitions and basis:
- **SU** = "surface habitable … augmentée de la moitié de la surface des annexes" (Bilan glossary, fetched live [S1]). The annexes are listed in the arrêté of 9 May 1995: cellars, balconies, loggias; terraces up to 9 m² [S17, via search snippet].
- **Foncier** = terrain + VRD + dépollution + other land charges, in the Banque des Territoires decomposition [S3]. "Bâtiment" is therefore **hors foncier and hors VRD**, which is what the model needs.
- **Prestations intellectuelles** = fees (architect, engineering, control, etc.). They are 16–19 % of bâtiment in the table: IdF 17.4 %, ARA 17.8 %, PACA 18.6 %, France 15.7 % [S1].
- **HT.** Social landlords pay 10 % VAT (PLUS/PLS) or 5.5 % (PLAI). The Bilan itself states that the "coût TTC véritable = coût HT × 1,20" [S1]. Excluding VAT makes social and private costs comparable.

### 2.2 Corroboration (all fetched live)
- **Éclairages n°33** [S3]. National MOD *construction* component per m² SU: 1 470 (2019), 1 540, 1 580, 1 690 (2022), 1 790 (2023). Its 2022 value (1 690) is within 1 % of the SISAL national bâtiment figure for 2022 (1 700 HT). That suggests both are on the same HT basis, although the brochure does not state HT/TTC.
  - Construction costs rose +22 % from 2019 to 2023 while BT01 rose +17 % [S3][S5].
  - Zone A bis all-in cost is "environ 50 % de plus qu'en zone A". That figure includes land, and the report gives no per-zone construction split.
- **CDC open data** [S4]. Median all-in prix de revient (land included, MOD + VEFA), € per m² SU:

  | Region | 2022 | 2023 | 2024 | 2025 |
  |---|---|---|---|---|
  | IdF | 3 280 | 3 413 | 3 752 | 3 813 |
  | ARA | 2 331 | 2 371 | 2 565 | 2 538 |
  | PACA | 2 448 | 2 452 | 2 775 | 2 882 |

  The cost-structure columns ("construction/acquisition" %) include VEFA purchase prices, so they are not a clean building share. I used them only as a trend check.
- **Case projects** [S15] (architecture press, fetched live via WebFetch summary; anecdotal). Works cost HT per m² SDP, 2024–25:
  - Paris XIIIe, 36 social dwellings: 8.10 M€ / 2 668 m² = **3 036**
  - Paris XIXe, 34 social dwellings + crèche: 5.0 M€ / 2 081 m² = **2 403**
  - Vincennes, 24 dwellings: 3.64 M€ / 1 140 m² = **3 193**
  - Toulouse, 238 student/family dwellings: 14 M€ / 8 700 m² = 1 609 (contrast)
- **Arcadis International Construction Costs 2025** [S13] (fetched live). City index (Amsterdam = 100): **Paris 136, Marseille 133, Lyon 133**. This is an all-building-types blend, but it says the factor-cost gap between the three metros is small.

### 2.3 What I could not find (searched)
- No open zone-A-bis-specific or département-specific *bâtiment* cost. The DRIHL/AORIF/CRC searches returned totals or nothing.
- No 2023/2024 edition of the Bilan online. The rubrique page is empty and the file names carry random suffixes.
- No official private-promoter construction-cost series. FPI publishes *sale* prices only.
- UNTEC/OPQTECC, Batiprix and CSTB ratio books are paywalled.
- Legifrance returned 403 for R.111-22, so it is cited via snippet [S16].

---

## 3. Time-indexing to 2025 (fetched live)

Annual averages of INSEE **BT01** (all trades, input costs, base 2010) [S5]: 2021 117.50, 2022 125.77, 2023 130.12, 2024 131.22, **2025 133.01**. Factors to 2025: from 2021 ×1.132, from 2022 ×1.058, from 2023 ×1.022, from 2024 ×1.014.

**ICC check.** Gemini suggested INSEE **ICC** instead, because ICC includes contractor margins. I fetched it live [S6]. Annual means: 2021 1 854, 2022 2 001, **2025 2 087**. That gives a 2022→2025 factor of ×1.043, which is *lower* than BT01 (ICC fell through 2025). So BT01 does not under-index. I apply BT01 with a ±2–3 % "excess" band, centred at 0 (range −2 % to +3 %). The upper side reflects Éclairages' finding that social construction costs outran BT01 over 2019–23 [S3].

Base 2025 bâtiment, € HT/m² SU, computed as the mean of the 2021 and 2022 values, each indexed with BT01:

| Region | 2021 indexed | 2022 indexed | Mean |
|---|---|---|---|
| IdF | 2 490 | 2 365 | **2 428** |
| ARA | 1 859 | 1 661 | **1 760** |
| PACA | 1 767 | 1 595 | **1 681** |

Averaging the two years damps sample noise. This matters for PACA, where the MOD sample is small.

---

## 4. Conversion to the model's basis (per m² gross external floor area, 2025 €)

Chain: `cost/GEA = bâtiment_SU × local premium × (1 − parking) × SU/GEA × (1 + fees) × VAT`. Values are given as central (low–high).

1. **Local premium over the regional average.**

   | Area | Premium | Comment |
   |---|---|---|
   | Paris | ×1.15 (1.05–1.30) | Upward because of the case projects above (≈2 400–3 200 HT/SDP) and tight infill sites |
   | Inner ring | ×1.03 (0.97–1.10) | |
   | Lyon | ×1.20 (1.08–1.30) | Raised after Gemini review, see §7 |
   | Lyon ring | ×1.10 (1.00–1.20) | |
   | Marseille | ×1.20 (1.05–1.32) | Raised after Gemini review, see §7 |

   The Lyon and Marseille premia are deliberately large. SISAL shows IdF bâtiment ≈ +40 % over ARA/PACA, but Arcadis shows only ~2 %. The ARA/PACA MOD samples are biased toward easy peri-urban sites; in PACA, 79 % of output goes through VEFA, which removes the complex urban sites [S1]. The premia close roughly half of that gap, which leaves Paris/Lyon ≈ 1.32. *This is a judgement call, not a sourced number.*

2. **Basement parking strip.** ×(1 − 7 %) (0–12 %). SISAL bâtiment includes the cost of underground parking, but parking is excluded from SU, and BD TOPO's gross area is above ground only. Applying the raw figure would charge a modern garage to every pre-1948 walk-up. Gemini estimates parking adds 250–400 € HT/m² SU (judgement, not sourced). I take a smaller central figure because Paris's PLU limits new parking.

3. **SU → gross external area: 0.74 (0.70–0.79).** The legal definitions:
   - **SDP** (Code de l'urbanisme R.111-22 [S16], via snippet) is measured from the inside face of external walls. It deducts stair and lift voids, areas ≤1.80 m high, parking, technical rooms, and cellars served by common parts. It then deducts **a further 10 % of residential floor area when flats are served by interior common parts**.
   - So SDP/GEA ≈ 0.78–0.82 for blocks: external walls with modern insulation take ~6–10 % of footprint, and shafts/technical rooms ~3–5 %, before the 10 % forfait.
   - Practitioner SHAB/SDP ratios for collectif are 0.80–0.92 [S18, secondary, via snippets]. SU/SHAB ≈ 1.03–1.05 (annexes counted at half).
   - Gemini adds that BD TOPO counts Parisian mansard/attic storeys as full floors, which pushes the ratio down for pre-1948 Paris (≈0.67).
   - This is the least-sourced factor. A direct calibration (§8) is the best next step.

4. **Fees: ×1.15 (1.12–1.18)**, from the SISAL prestations-intellectuelles share (16–19 % of bâtiment) [S1]. Part of that share is social-landlord project management, so I sit slightly below it.

5. **VAT: ×1.20** [S1]. Replacement cost is measured from a *private* rebuilder's viewpoint: households cannot recover VAT. This is also consistent with how national accounts value dwellings (household GFCF at purchasers' prices incl. non-deductible VAT; ESA 2010 principle, *from my knowledge, not fetched*), and those dwelling values underpin the INSEE ~46 % land-share anchor.
   - **Not included:** developer/entrepreneur margin (+5–8 % per Gemini). This is an upside risk.

Result (`calc2.py`). "Plausible range" = geometric midpoint between the central value and the all-extremes bound. All-extremes is the outer bound, shown in brackets.

| Area | Bâtiment HT/m² SU, ex-parking | Works only, HT per m² GEA | **Full (TTC + fees) per m² GEA** | Per m² *habitable* (full) |
|---|---|---|---|---|
| Paris | 2 596 | 1 921 | **2 651** (2 342–3 105; outer 2 068–3 636) | ≈ 3 730 |
| Inner ring | 2 325 | 1 721 | **2 375** (2 130–2 703; outer 1 911–3 077) | ≈ 3 340 |
| Lyon | 1 964 | 1 454 | **2 006** (1 759–2 300; outer 1 542–2 636) | ≈ 2 820 |
| Lyon ring | 1 801 | 1 332 | **1 839** (1 620–2 115; outer 1 428–2 434) | ≈ 2 580 |
| Marseille | 1 876 | 1 388 | **1 916** (1 656–2 213; outer 1 432–2 557) | ≈ 2 690 |

On the narrow "works only, HT" basis (config comment: "gros oeuvre + second oeuvre"), current values would sit *above* the central values everywhere: Paris 2 300 vs 1 920, Lyon 1 950 vs 1 450. The basis choice matters as much as the data. I recommend the full basis because:
- the EPTB-based values used for the other pilot communes are already turnkey and de facto TTC, so this keeps the communes consistent;
- the replacement cost that a market buyer avoids includes fees and VAT.

---

## 5. Recommendation

| Area | Central | Plausible range | Current | Inside? |
|---|---|---|---|---|
| Paris | **2 650** | 2 350–3 100 | 2 300 | No (≈2 % below the floor) |
| Inner ring 92/93/94 (and Montreuil) | **2 400** | 2 150–2 700 | 2 150 | At the floor |
| Lyon (and Villeurbanne) | **2 000** | 1 750–2 300 | 1 950 | Yes |
| Lyon Métropole ring | **1 850** | 1 600–2 100 | 1 950 | Yes |
| Marseille (13055, arr. 13201–13216) | **1 900** | 1 650–2 200 | — | — |

Basis: 2025 €, per m² of BD TOPO gross floor area (footprint × storeys), building only, hors foncier and hors VRD, **TTC (20 %) incl. honoraires, excl. developer margin**.

**Knock-on effect on depreciation.** Raising the cost lowers q = local €/m² ÷ cost, so slightly fewer buildings count as "maintained stock". With the Paris price around 10 000 €/m², q falls from ~4.3 to ~3.8, still far above the 2.5 ramp ceiling. Paris and the inner ring are therefore unaffected. Lyon-ring IRIS near q ≈ 2–2.5 could move partly out of the maintained regime, which would partly offset the cost increase through older effective ages.

---

## 6. Caveats (ranked)

1. **Unit mismatch in market value (load-bearing).** Market value = DVF €/m² (*habitable*) × *gross* area, while building value uses gross area too [repo `estimate.py` L157–165, L92, L112]. The land share is right only if the cost is per habitable m² (≈ ×1.40 the table above), or if market value is scaled by the net-to-gross factor (~0.74 flats; houses ~0.80–0.85, a Gemini judgement). Until this is fixed, *any* cost in the gross-basis table will overstate land shares. This alone could explain much of the "land share too high in hot markets" pattern in THEORY.md.
2. **The SU→gross factor (0.74) is the least-sourced link** and the second-largest lever. ±0.05 moves every value by ±7 %. BD TOPO storey counts (attics, ground-floor commercial, courtyards) add further noise in pre-1948 Paris.
3. **Social housing is a proxy for the private stock.** It is a reasonable "modern equivalent asset" (Gemini: neutral to slightly high, because social landlords build to hold). It will understate the cost of prime or listed stock, where a stone-for-stone replica would cost far more. Valuation practice uses the modern equivalent, not a replica.
4. **Regional gradient uncertainty.** SISAL (IdF +40 %), Arcadis (≈+2 %) and EPTB (IdF *cheapest*) disagree. My Lyon/Marseille premia are judgement calls, and the PACA MOD sample (1 246 dwellings, 79 % VEFA) is thin.
5. **Houses.** Lyon-ring and some inner-ring communes have many houses. For those the right anchor is EPTB per m² SDP [S7][S8]: IdF 1 863, ARA 2 066, Rhône 2 127, Bouches-du-Rhône 2 027 (TTC, incl. builder margin, mostly excl. architect). Multiplied by SDP/GEA for houses (~0.85–0.90, judgement), that gives ≈1 600–1 900 per m² GEA. A per-type cost would be better than a single commune value.
6. **Vintage.** The latest open bâtiment split is 2022. 2023–24 cost growth is taken from BT01 and Éclairages. The CDC data show a sharp 2024 jump in all-in costs (IdF +10 %), mostly land/VEFA composition.

---

## 7. Gemini critique (model `gemini-4-argon`, 2026-10-19) and how I responded

The full reply is in `scratchpad/cc_scripts/gemini_reply.md`. Its main points and my response:

| Gemini point | My response |
|---|---|
| Fix the market-value denominator (net-to-gross ≈0.72) rather than inflating cost. Otherwise multiply cost by ≈1.43. | **Agreed.** This is promoted to caveat 1, with both options presented. |
| The SISAL IdF +40 % gap is mostly composition (rural/easy MOD sites in ARA/PACA; PACA 79 % VEFA). The true factor gap is 10–15 %. Compress the spread. | **Partly adopted.** I raised the Lyon premium (1.10→1.20) and the Marseille premium (1.05→1.20). Paris/Lyon is now ≈1.32 vs Gemini's ≈1.29. I did not accept its claim that wages are "nationally gridded": construction wage agreements are regional and IdF wages are higher. |
| SU/GEA 0.77 is too high; use 0.72 (SHAB/SDP 0.82–0.85, SDP/GEA 0.82–0.85). BD TOPO counts mansard storeys. | **Partly adopted: central 0.74 (0.70–0.79).** I **rejected** its claim that the 10 % collectif deduction no longer exists in modern SDP: R.111-22 8° still provides it [S16]. Because that deduction is already in SDP, SHAB/SDP should be *higher* than Gemini's 0.82–0.85. The product still lands near 0.70–0.75. |
| Strip basement parking (−10–12 %) from SISAL bâtiment. | **Adopted, smaller:** −7 % (0–12 %), because the Paris PLU restricts new parking. Gemini's €/place figures are unsourced. |
| Fees 15–17 %; VAT 20 % yes; developer margin +5–8 %. | Fees 15 % and VAT 20 % **adopted**. The margin is **excluded** from the central value and flagged as an upside risk. |
| Prefer ICC over BT01. | **Checked live:** ICC gives a *lower* 2022→2025 factor (×1.043 vs ×1.058). BT01 is kept, with an excess band. |
| Better sources: UNTEC/OPQTECC référentiel, OLAP/CGEDD/CSTB studies, FPI. | UNTEC/Batiprix are paywalled. FPI publishes sale prices, not costs. I did not find the OLAP/CGEDD study and did not verify that it exists. These remain leads (§8). |
| Gemini's own centrals: Paris 2 660, inner ring 2 350, Lyon 2 060, ring 1 910, Marseille 1 950 (TTC + fees, per GEA). | My final values are within 3 % of each. That is convergence, not independence: both used the same evidence pack. |

---

## 8. Suggested next steps (each its own PR, not done here)
1. **Calibrate net-to-gross empirically** for the market-value fix. Option: compare BD TOPO GEA with DPE surfaces (*surface habitable logement* in the ADEME DPE open data) for the same buildings, which is open and covers millions of flats. This would replace the 0.74 judgement with a measured ratio per commune.
2. Request SISAL extracts (DHUP) for **zone A bis / dépt 75, 92–94, 69, 13** bâtiment costs for 2022–2025. The ministry has them by operation.
3. Split the cost parameter by building type (collectif vs individuel). EPTB covers houses well.

---

## 9. Sources (access date 2026-10-19 unless stated)

- **[S1]** DHUP/DGALN, *Bilan 2022 des logements aidés*: table 6.12 p.57; glossary (SU definition); TVA note under 6.13. https://www.financement-logement-social.logement.gouv.fr/IMG/pdf/bilan_2022_des_logements_aides_cle7819a4.pdf (fetched live)
- **[S2]** DHUP/DGALN, *Bilan 2021 des logements aidés*: table 8.1 p.67. https://www.financement-logement-social.logement.gouv.fr/IMG/pdf/bilan_2021_des_logements_aides_cle7111c2.pdf (fetched live)
- **[S3]** Banque des Territoires, *Éclairages n°33*, Déc. 2024: Tableau 1, Graphiques 3–6, decomposition box. https://www.banquedesterritoires.fr/sites/default/files/2025-01/Exe%20brochure%20Eclairages%2033%20A4%202024%20vdef.pdf (fetched live)
- **[S4]** Caisse des Dépôts open data:
  - *Coûts et surfaces moyens des logements sociaux financés par la CDC depuis 2018*: https://opendata.caissedesdepots.fr/explore/dataset/constructionrehabilitation_logementsocial_surface_prix/ (API, fetched live)
  - *Financement et coût des logements sociaux construits…*: https://data.smartidf.services/explore/dataset/financement-et-cout-des-logements-sociaux-construits/ (API, fetched live; metadata modified 2026-06-15)
- **[S5]** INSEE BDM, Index BT01 tous corps d'état (idbank 001710986). https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001710986 (fetched live)
- **[S6]** INSEE BDM, Indice du coût de la construction ICC (idbank 000008630). https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/000008630 (fetched live)
- **[S7]** SDES/DRIEAT, EPTB 2024 Île-de-France, ch.3. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/ile_de_france/caracteristiques_maisons_contruites.html (fetched live)
- **[S8]** SDES/DREAL, EPTB 2024 Auvergne-Rhône-Alpes, ch.3. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/auvergne_rhone_alpes/caracteristiques_maisons_contruites.html (fetched live)
- **[S9]** SDES/DREAL, EPTB 2024 PACA, ch.3. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/paca/caracteristiques_maisons_contruites.html (fetched live)
- **[S10]** SDES, EPTB 2024 methodology and definitions (house surface = surface de plancher; land price TTC). https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/ile_de_france/methodo.html (fetched live)
- **[S11]** SDES/DRIEAT, EPTB 2024 IdF, ch.4 *Coût total du projet* (252 222 €). https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/ile_de_france/cout_total_projet.html (fetched live)
- **[S12]** SDES, *Le prix des terrains et du bâti pour les maisons individuelles en 2024* (publ. 27/11/2025): 1 914 €/m², 118 m². https://www.statistiques.developpement-durable.gouv.fr/le-prix-des-terrains-et-du-bati-pour-les-maisons-individuelles-en-2024 (fetched live)
- **[S13]** Arcadis, *International Construction Costs 2025*: city index. https://www.arcadis.com/contentassets/9c69333169054e2ba8bb8fabf1a80df9/international-construction-costs-2025.pdf (fetched live)
- **[S14]** DDT Saône-et-Loire / DGALN training, *Instruction d'une opération de construction de logements sociaux PLUS-PLAI* (2018): 3 cost components; VEFA land forfait 45 % A bis … 20 % C. https://www.financement-logement-social.logement.gouv.fr/IMG/pdf/ifls-macon-2018-06_lo_instruction_cle07a437.pdf (fetched live)
- **[S15]** Chroniques d'architecture, tag "logement social": project cost/SDP figures. https://chroniques-architecture.com/tag/logement-social/ (fetched live via WebFetch summariser, figures quoted; individual articles linked therein not opened)
- **[S16]** Code de l'urbanisme art. R.111-22 (SDP definition incl. 10 % collectif deduction), reproduced at https://www.mouans-sartoux.net/wp-content/uploads/2025/09/CU-R111-22-def-Surface-de-Plancher.pdf and https://www.inc-conso.fr/content/urbanisme-la-definition-et-le-calcul-de-la-surface-de-plancher (via search snippet; Legifrance returned HTTP 403)
- **[S17]** Arrêté du 9 mai 1995 (annexes counted in SU; terraces limited to 9 m²). https://www.financement-logement-social.logement.gouv.fr/IMG/pdf/03_arrete_du_9_mai_1995_cle07b13b.pdf (via search snippet)
- **[S18]** Practitioner SHAB/SDP ratios for collectif (0.80–0.85; 0.82–0.87; "0.92"). Sources: https://quostra.com/fr-fr/blog/cout-construction-m2-france/cout-construction-logement-collectif-m2 , https://lalyonnaise.fr/faq-la-lyonnaise/surface-de-plancher-shab-difference/ , https://cabinetfranckverdelet.com/archives/4811 (via search snippet; secondary/trade, unverified)
- **[S19]** Gemini `gemini-4-argon` critique, 2026-10-19 (model output, not a source of fact). Saved at `scratchpad/cc_scripts/gemini_reply.md`.
- **[Repo]** `lvtshift-fr/estimate.py` L92 (floor_area = footprint × n_levels), L112 (imp_value), L157–165 (market_value = eur_m2 × floor_area_m2); `ingest.py` L182 (DVF floor_area_m2 = surface_reelle_bati). Read 2026-10-19.
