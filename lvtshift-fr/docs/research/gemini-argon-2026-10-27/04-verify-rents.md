# Verification: taxes on individuals' rental income (scenario S3)

Status key: VERIFIED = I read the number in the primary document or dataset myself. DERIVED = my own arithmetic on verified numbers. UNVERIFIED = not found in a primary source.
All downloads are in `scratchpad/argon/dl_rents/`.

## Headline
- The CPO's 8,3 Md€ is the SDES Compte satellite du logement (CSL) 2022 line **"Impositions sur les revenus immobiliers" = 8 264 M€**. It breaks down **exactly** as IR 4 198 + PS 2 399 + CSG 1 093 + CRL 107 + **IS (corporate landlords) 467** = 8 264 (CPO rapport particulier n°1). The "missing 0,5" is corporate-landlord income tax (IS), not minor items.
- CSG 1,1 is **additive** to PS 2,4 in this accounting (separate lines that sum to the total). So S3 as built (4,2 + 2,4) **omits 1,09 Md€ of CSG**. On this point Gemini (a) is right.
- All these figures are **housing only** and the IR is **net of Pinel/Scellier etc.** (CSL methodology, VERIFIED).

## Q1. CPO p. 23: what it says, and what the 8,3 is
**Text, CPO "Pour une fiscalité du logement plus cohérente", Dec. 2023, p. 23 (VERIFIED):**
> « … l'impôt sur le revenu des personnes physiques lié aux revenus immobiliers (4,2 Md€), les prélèvements sociaux sur les revenus fonciers (2,4 Md€), la contribution sociale généralisée (CSG) sur les revenus immobiliers (1,1 Md€) ou encore la contribution sur les revenus locatifs (100 M€) y sont associés. En 2022, l'ensemble de ces impositions sur les revenus immobiliers représente 8,3 Md€. »

- That sentence has no footnote of its own. Footnote 6 (p. 19) covers the whole section: the 2022 data come "soit du CSL, soit des données budgétaires annexées au PLF 2024".
- CPO Graphique n° 2 (p. 19), "Location" block: IR 4,2 / PS 2,4 / CSG 1,1 / CRL 0,1 / TS (taxe de séjour) 0,4 (VERIFIED, rendered page). TS is not part of the 8,3.
- **SDES, Rapport du compte du logement 2022 (Sept. 2023), partie 6, Tableau 1, p. 62** (https://www.vie-publique.fr/files/rapport/pdf/291193.pdf): "Impositions sur les revenus immobiliers*" = **8 264 M€ (2022)**. Footnote: "*CRL, IR, IS, CSG, CRDS, prélèvements sociaux, prélèvements sur les profits immobiliers des personnes domiciliées hors de France." (VERIFIED)
- **CPO rapport particulier n°1, "Panorama budgétaire et juridique de la fiscalité du logement"** (https://www.ccomptes.fr/sites/default/files/2023-12/20231218-Fiscalite-du-logement-rapport-particulier-1.pdf):
  - p. 47 table "Impôts et taxes rattachés à la mise en location d'un logement", yield in 2022 (M€): IR lié aux revenus immobiliers 4 198; PS sur les revenus fonciers 2 399; CSG sur les revenus immobiliers 1 093; Taxe de séjour 679; CRL 107; Impôt sur les sociétés 467 (VERIFIED).
  - p. 95, Tableau n° 28 "Prélèvements sociaux sur le logement": "Le compte satellite du logement les présente selon trois classifications". CSG sur revenus immobiliers: 2017 87, 2018 1 016, 2019 1 051, 2020 1 105, 2021 1 103, 2022 1 093. PS sur revenus fonciers: 2 164 / 2 229 / 2 305 / 2 424 / 2 419 / 2 399. PS sur plus-values immobilières: 699 / 832 / 833 / 772 / 1 055 / 1 249. Total 2022: 4 741 = the sum of the three lines (VERIFIED).
- DERIVED: 4 198 + 2 399 + 1 093 + 107 + 467 = **8 264**, exactly the CSL line. So the CPO's "8,3" is the CSL total, and the 0,46 Md€ its listed items leave out is **IS paid by corporate landlords**.
- **CSG inside or outside the 2,4?** Outside. In both the CSL and the CPO it is a separate, additive line (VERIFIED by the exact sum).
  - Caveat (DERIVED): the CSG line jumps from 87 M€ (2017) to 1 016 M€ (2018) while PS barely moves. The +1,7 pt CSG rise in 2018 can explain only about 0,3 Md€ of that, so the PS/CSG split is a CSL allocation convention with a 2018 break. Only the **sum** (3,49 Md€ in 2022) should be trusted.
- **Gemini (b):** the source is right (CSL 2022). The table reference "20.3" is wrong: it is partie 6, Tableau 1. "~0,5 Md€ minor items" is also wrong: it is IS on corporate landlords (467 M€).

## Q2. Best primary figures for IR and the 17,2 % levies on rental income
| Item (housing, individuals) | 2022 | Source | Status |
|---|---|---|---|
| IR on revenus fonciers (net of Pinel etc.) | 4 198 M€ | CPO RP1 p. 47, from CSL | VERIFIED |
| PS on revenus fonciers | 2 399 M€ | CPO RP1 p. 47 / Tab. 28 | VERIFIED |
| CSG on revenus immobiliers | 1 093 M€ | same | VERIFIED |
| **Sum, individuals** | **7 690 M€** | DERIVED | |
| CRL (paid by IS entities, not individuals) | 107 M€ | same | VERIFIED |
| IS on corporate landlords | 467 M€ | same | VERIFIED |

- **Scope:** housing only (compte du *logement*); all private landlords; IR net of tax advantages. CSL 2024 p. 75: "Les prélèvements sont retracés nets des avantages fiscaux. Par exemple, l'imposition des revenus fonciers au titre de l'IR pour les ménages bailleurs est net des avantages fiscaux liés aux dispositifs d'investissement locatif (« Besson », « Borloo », « Scellier », « Pinel », etc.)" (VERIFIED).
- **Whether furnished lets (LMNP, taxed as BIC) are included:** the CSL describes the IR component as "imposition des revenus fonciers", so LMNP is probably excluded (UNVERIFIED).
- **Most recent year:** no published component breakdown exists after 2022. The CSL only gives the aggregate (see Q3).
  - DERIVED 2024 estimate: the individual-only share in 2022 was 7 690 / 8 264 = 93,1 %. Applied to the 2024 aggregate of 8 895 M€, that gives **≈ 8,3 Md€**.
  - Alternatively, applying the 2022→2024 growth within the CSL 2024 vintage (+4,1 %) to 7,69 gives ≈ 8,0 Md€.
  - Range for 2024: **8,0–8,3 Md€** (IR ≈ 4,4; PS+CSG ≈ 3,6).

## Q3. Compte du logement 2024: the 8,9 Md€
- SDES, **Rapport du compte du logement 2024** (Nov. 2025), partie 6, **Figure 6.1** (https://www.statistiques.developpement-durable.gouv.fr/media/8828/download?inline), and xlsx Figure 6.1 / long series T321 (media/8839, media/8833) (VERIFIED):
  - "Impositions sur les revenus immobiliers*" = **8 895 M€ in 2024**, 9,0 % of housing levies.
  - Growth: +0,6 % (2022/21), +0,9 % (2023/22), +3,2 % (2024/23).
- Footnote, same as before: "CRL, IR, IS, CSG, CRDS, prélèvements sociaux, prélèvements sur les profits immobiliers des personnes domiciliées hors de France".
- **No breakdown is published**, either in the PDF or in the two xlsx files.
- Scope: housing only, all landlords including legal persons (IS), net of tax-expenditure reductions. IFI (2 644) and TFPB are separate lines.
- T321 series (CSL 2024 vintage, M€): 2019 8 185,7; 2020 8 499,8; 2021 8 493,5; **2022 8 541,1**; 2023 8 619,9; **2024 8 894,9**. The 2022 figure has been revised up from 8 264 (2022 edition) to 8 541 (+3,4 %).
- CSL 2023 edition (Oct. 2024, vie-publique 295731): 2023 = 8 539 M€ (VERIFIED).

## Q4. Net taxable revenus fonciers declared, and reconciliation at 17,2 %
- **DGFiP, "L'impôt sur le revenu : les déclarations nationales"** (data.economie.gouv.fr dataset `ir-declarations-2042-nat`, updated 2026-04-07), national totals by form box (VERIFIED, API query).
- "annee" is the income year. I infer this because the attached brochures run to "revenus 2024" and the last year in the data is 2024 (inference).

| Box (M€) | 2022 | 2023 | 2024 |
|---|---|---|---|
| 4BA revenus fonciers imposables (réel) | 33 923 (2,82 M foyers) | 34 101 | 34 953 |
| 4BE micro-foncier gross receipts | 8 671 (1,50 M) | 8 502 | 8 482 |
| 4BB deficit carried on future RF | 1 580 | 1 578 | 1 530 |
| 4BC deficit charged on global income | 1 778 | 1 867 | 1 819 |
| 4BD prior deficits not yet used (stock) | 8 545 | 6 492 | 8 515 |

- DERIVED net taxable base, all revenus fonciers, 2022: 4BA + 0,7 × 4BE − prior deficits actually used = 33,9 + 6,1 − (0 to 8,5) ≈ **31,5–40,0 Md€**. 4BB and 4BC belong to households with a zero result, so they do not reduce 4BA.
- At 17,2 %, that base gives **5,4–6,9 Md€** of PS on *all* revenus fonciers. This includes commercial premises, farmland rents, parking and SCI shares taxed under IR.
- CSL housing-only PS+CSG = 3,49 Md€ → implied housing base 20,3 Md€ (≈ 50–65 % of the fiscal total). If PS 2,4 alone were the full 17,2 %, the implied base would be only 14 Md€; that is less consistent with the IR figure, but it cannot be excluded.
- **Gemini (c)**: "net taxable revenus fonciers ≈ 20–21 Md€ (DGFiP)" is **contradicted** as a DGFiP total: declared net revenus fonciers are ≥ 31 Md€. 20,3 Md€ is only the housing base *implied* by the CSL, not a DGFiP statistic.
- So the PS figure does reconcile with 17,2 %, but only as a housing share of a larger fiscal base. The housing share is not published.

## Q5. LMNP/BIC furnished lets; commercial lettings by individuals
- **No official revenue (yield) figure found** for IR+PS on LMNP. The IGF / "rapport Le Meur" figure Gemini cites (0,5–0,8 Md€) was **not found** (UNVERIFIED).
- Tax expenditures that are verified (PLF 2026 VM tome II):
  - 110250 Censi-Bouvard: 39 / 35 / 37 M€ (2024 / 25 / 26).
  - 180310 micro-BIC extra 21 % abatement for classified rural tourist lets: ≈ 2 M€.
- DGFiP 2042 boxes, 2022, M€ (VERIFIED):
  - micro-BIC furnished lets 5ND+5OD gross = 4 280 + 821 = **5 101**
  - classified tourist lets / chambres d'hôtes 5NG+5OG = 942 + 285 = **1 227**
  - réel profits 5NA+5NK+5OA+5OK = **412**
  - réel deficits 5NY+5NZ+5OY+5OZ = 768 (cannot be charged on global income)
  - 2024: 5ND+5OD = 6 064 gross; 5NA+5OA = 516.
- DERIVED LMNP taxable income 2022: 0,5 × 5,10 + 0,29 × 1,23 + 0,41 ≈ **3,3 Md€**.
  - PS at 17,2 % ≈ 0,57 Md€.
  - IR at an assumed 20–30 % average marginal rate ≈ 0,65–1,0 Md€.
  - **Total ≈ 1,2–1,6 Md€** (rising by about 2024). This is an order of magnitude only. Gemini's 0,5–0,8 looks low.
- **Commercial lettings by individuals:** these are revenus fonciers, so they sit inside 4BA/4BE but outside the CSL's housing scope. No official split was found (UNVERIFIED).
  - DERIVED residual for all non-housing revenus fonciers (commercial, land, parking): about 1,9–3,4 Md€ of PS, plus IR, depending on prior-deficit use. That is larger than Gemini's 0,5–0,8 for commercial lettings, but the residual also includes farmland and parking.

## Q6. Pinel-type reductions, and whether the CPO's IR figure is net
- **PLF 2026, Évaluation des voies et moyens, tome II** (https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/x.pdf) (VERIFIED). M€, 2024 actual / 2025 forecast / 2026 forecast:
  - **110261 Duflot+Pinel: 1 469 / 1 459 / 1 349** (384 000 ménages)
  - 110251 Scellier: 34 / 30 / 38
  - 110252 Scellier intermédiaire: 189 / 169 / 176
  - 110259 Scellier intermédiaire outre-mer: 41 / 37 / 37
  - 110250 Censi-Bouvard: 39 / 35 / 37
  - 110265 Denormandie: 5 / 5 / 7
  - 110269 Loc'Avantages: 5 / 10 / 10
  - deductions 130215 Borloo ancien 46 / 43 / 41; 130218 Cosse 26 / 22 / 17; 130214 Robien/Besson-type 20 / 16 / 16
  - Total for rental-investment reductions and deductions ≈ **1,85 Md€ (2024)**, of which reductions alone ≈ 1,78.
- Other years:
  - PLF 2025 VM II: 110261 realised 2023 = 1 396 M€ (VERIFIED).
  - 2022: 110261 = 1 375 M€ (CPO RP1, Annexe 2, p. 117, VERIFIED).
  - Also in that annex: 130201 "déduction des dépenses de réparations et d'amélioration" 1 650 M€ (2022).
- **Is the CPO's 4,2 Md€ net?** Yes. It is the CSL component (the exact sum check in Q1), and the CSL states that IR on revenus fonciers is net of Besson/Borloo/Scellier/Pinel (VERIFIED).
  - DERIVED gross equivalent for 2022 ≈ 4,2 + 1,375 + about 0,3 (Scellier lines) ≈ 5,9 Md€.
  - Caveat: these reductions are charged against total IR, not only the IR attributable to rents. "Gross" is therefore a notional figure.
- **Gemini (f)** "1,5–2,0 Md€": consistent (≈ 1,7–1,85 Md€ incl. Scellier/Censi-Bouvard; Pinel alone 1,4–1,5).

## Gemini claims: verdict
| Claim | Verdict |
|---|---|
| (a) PS 2,4 and CSG 1,1 are additive; S3 omits 1,1 | **Confirmed** (exact CSL sum). The implied "20,3 Md€ base" holds only as a housing-only implied base. |
| (b) 8,3 = CSL 2022 total incl. ~0,5 minor items | Source **confirmed** (8 264 M€). Table number wrong (it is partie 6 Tableau 1). The 0,5 is **IS of corporate landlords (467)**. |
| (c) Net taxable revenus fonciers ≈ 20–21 Md€ (DGFiP) | **Contradicted.** DGFiP declared 4BA 33,9 + micro 8,7 gross (2022); net ≈ 31–40 Md€ for all RF. |
| (d) LMNP ≈ 0,5–0,8 Md€ (IGF/Le Meur) | **Source not found.** My derived estimate from DGFiP boxes is ≈ 1,2–1,6 Md€. |
| (e) Commercial lettings ≈ 0,5–0,8 Md€ | **No official figure.** Non-housing RF residual looks larger (≈ 2–3+ Md€ PS alone), but it includes land and parking. |
| (f) Pinel etc. 1,5–2,0 Md€; CPO IR gross or net? | Cost **confirmed** (≈ 1,8 Md€ in 2024). CPO IR is **net**. |

## Recommendation for S3
1. **Base figure (housing, individuals, 2022, fully sourced):** IR 4,20 + PS 2,40 + **CSG 1,09** = **7,69 Md€**. Add the CSG line.
   - Exclude CRL (0,107: paid by IS entities) and IS (0,467: corporate landlords). They are not taxes on *individuals'* rental income.
   - Cite CPO RP1 p. 47 and Tab. 28, and CSL 2022 Tab. 1.
2. **If S3 should be at 2024 levels:** scale with the CSL aggregate to ≈ **8,0–8,3 Md€** (DERIVED). Label it as an estimate, because no 2024 breakdown is published.
3. Keep the IR **net** of Pinel (that is what is actually collected). Mention in a note that ≈ 1,4–1,5 Md€/yr of Pinel/Duflot reductions run until 2038 and are tied to rental investment.
4. **Scope decisions for Patrick** (not data questions):
   - (i) Whether furnished lets (LMNP) are in scope. If so, add a separately labelled ≈ 1,2–1,6 Md€ DERIVED estimate as a sensitivity.
   - (ii) Whether non-housing revenus fonciers (commercial premises, farmland, parking) are in scope. If so, the full fiscal base suggests PS alone of 5,4–6,9 Md€ on all RF; there is no official IR split.

## What remains uncertain
- How the CSL splits PS from CSG (break in 2018). Only the sum is reliable.
- Whether CSL IR includes LMNP/BIC. It probably does not.
- The housing share of revenus fonciers (not published). It explains the gap between the DGFiP base and the CSL levies.
- How many prior deficits (4BD) are actually used each year.
- The LMNP yield: no official figure; my estimate depends on assumed marginal rates.
- The 2023–2024 breakdown of the CSL aggregate.
