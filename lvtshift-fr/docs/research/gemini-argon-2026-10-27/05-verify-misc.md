# Verification of Gemini (argon) numeric claims — misc items

Status: COMPLETE (items 1–7). Date of checks: 27 Oct 2026.
Downloads: scratchpad/argon/dl_misc/ (all parsed with `python -I` / pdftotext)

---

## 1. TSBCS (CGI art. 231 ter) — Île-de-France office/commercial/storage/parking tax

Gemini: ≈ 0,95–1,10 Md€/yr. **Verdict: plausible, but no primary source found that publishes the TOTAL
yield for 2023–2025; the total below is reconstructed from the per-beneficiary amounts (VERIFIED
components, DERIVED total).**

The tax has three earmarked beneficiaries plus the State budget for any overflow above caps
(Cour des comptes, S2024-0234 *La Société du Grand Paris*, footnote 85, p. 45: "Trois affectataires
bénéficient de la TSB. Les parts du FNAL et de la région Île-de-France ont un plafond fixe depuis
plusieurs années. La SGP bénéficie de tout le dynamisme de la taxe.")
https://www.ccomptes.fr/sites/default/files/2024-04/20240425-S2024-0234-Societe-Grand-Paris_0.pdf — VERIFIED

Per-beneficiary amounts (M€):

| Beneficiary | 2023 | 2024 | 2025 | 2026 | Source |
|---|---|---|---|---|---|
| SGP (Société des grands projets) — product of its fraction | 655,1 (exec.) | 757,2 (fcst; plafond 718,0, reversement to State 39,2) | 782,0 (fcst; plafond 782,0) | plafond raised +50,5 to 832,5; expected yield 793 | PLF 2025 V&M tome I, "Taxes affectées classées par bénéficiaire", SGP block, and "affectations plafonnées" table (LFI 2012 block, line 21/14) — VERIFIED. 2026: PLF 2026 V&M tome I p.101-102 "Taxes dont le plafond augmente" (+50,5) — VERIFIED; Sénat rapport général PLF 2026 (l25-139-310-2) "rendement attendu … 793 M€" — VERIFIED |
| SGP — as reported in SGP/Sénat tables (accrual-ish) | 664 | 718 (actual) | 782 (fcst) | 793 (PLF) | Sénat, rapport général PLF 2026, Écologie/mobilité, table "Synthèse des recettes fiscales affectées à la SGP (2023-2026)" https://www.senat.fr/rap/l25-139-310-2/l25-139-310-27.html — VERIFIED (via fetch) |
| Région Île-de-France (fixed share, art. L4414-7 CGCT) | 212,9 (exec.) | 212,9* | 212,939 (BP 2025) | 212,939 (BP 2026) | 2023: PLF 2025 V&M t.I, Région IdF block (and data.economie.gouv.fr dataset plf2024-v-and-m-t1-liste-des-taxes-affectees: 212 938 000 €) — VERIFIED. 2025/2026: CESER IdF Avis 2025-14 on BP 2026 Région, "Reversement de la part régionale de la TSB : 212,939 M€ (idem au BP 2025)" https://www.iledefrance.fr/sites/default/files/2025-12/avis_2025-14_budget_primitif_2026_region_ile-de-france.pdf — VERIFIED |
| FNAL | 66,2 | 24,2 | 0 (affectation suppressed in LFI 2025, replaced by subsidy) | 0 | PLF 2025 V&M t.I, FNAL block + text "L'affectation … de la taxe annuelle sur les locaux à usage de bureaux … au FNAL est supprimée" — VERIFIED |

*Caveat: PLF 2025 V&M prints "Néant" for the Région's TSB share in 2024 and 2025 (forecast columns),
yet the Région's own budgets (BP 2025, BP 2026) still book 212,939 M€. I treat the "Néant" as a
presentation quirk (not forecast for a non-capped, fixed-amount local share), but this is UNRESOLVED.

Derived total TSBCS (Île-de-France only), M€:
- 2023: 655,1 + 212,9 + 66,2 ≈ **934** (all executed figures)
- 2024: ≈ 757 (SGP fraction incl. 39 overflow to State) + 213 + 24 ≈ **≈ 994** (SGP 2024 is a PLF 2025 forecast; SGP actual booked 718 = cap, overflow to State not separately confirmed)
- 2025: ≈ 782 + 213 + (former FNAL 66/24 now in State budget, amount unknown) ≈ **≈ 1,0–1,06 Md**
- So Gemini's 0,95–1,10 Md€ is consistent with the components for 2024–2025; 2023 is slightly below (0,93).
- The State's own share (overflow + former FNAL portion) sits inside DGFiP's "Autres taxes" aggregate and is not published separately (DGFiP *recettes_fiscales_brutes.xls* has no TSB line) — UNVERIFIED.
- Note: the PACA extension (CGI 231 quater, Bouches-du-Rhône/Var/Alpes-Maritimes, since 2023) is a separate tax and is not included above.
- Not found: a single official "total yield of art. 231 ter" figure for 2024/2025. The PLF 2026 "Liste des taxes affectées" annex (spreadsheet, budget.gouv.fr) would have it but budget.gouv.fr blocked automated download (Incapsula).

## 2. CSI — contribution de sécurité immobilière (CGI art. 879)

Gemini: ≈ 0,25–0,30 Md€/yr. **Verdict: WRONG — actual yield is ≈ 0,7–0,9 Md€/yr (roughly 2,5–3× Gemini).**

DGFiP, *Recettes fiscales brutes* (montants en M€, données de recouvrement), row
"17 – Enregistrement… / 6. Contribution sécurité immobilière" (State budget):
https://www.impots.gouv.fr/sites/default/files/media/9_statistiques/0_etudes_et_stats/1_statistiques/4_autres/recettes_fiscales_brutes.xls
(file last saved 9 March 2026) — VERIFIED (read directly)

| 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 547,2 | 549,4 | 593,3 | 632,5 | 701,5 | 736,2 | 789,6 | 759,5 | 898,1 | 921,9 | 783,1 | 692,3 | 745,0 |

State budget line: 1707 (PLF 2025 V&M tome I, commentary on line 2613: "contribution de sécurité
immobilière … perçue au profit du budget général en recettes fiscales (ligne 1707)") — VERIFIED.
The V&M tome I PDFs (2025, 2026) do not print a per-line amount for 1707 (only commentaries for
major lines); the line-by-line état A was not retrieved. The DGFiP series is the primary figure.
Why bigger than "0,10 % × transaction value": CSI also applies to mortgage/privilege inscriptions
(0,05 %), other publications at fixed fees, and to all deeds published, not only sales.

## 3. IFI — gap between DGFiP "émission" figure and budget line 1406

Figures (all VERIFIED, read directly):

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| IFI on tax notices (émission), DGFiP Statistiques | 1 800 (n°15, via Cour) | — | 2 159 | 2 332 |
| Budget receipts line 1406 / DGFiP "ISF/IFI" gross receipts | 2 353 | 2 354 | 2 739 | **2 771 (actual, provisional)** |
| PLF 2026 V&M forecast for 2025 | | | | 2 965 |

Sources:
- DGFiP Statistiques n°45 (avril 2026) *L'IFI en 2025*, Tableau 1: IFI payé 2 159 M€ (2024), 2 332 M€ (2025). https://www.impots.gouv.fr/sites/default/files/media/9_statistiques/0_etudes_et_stats/0_publications/dgfip_statistiques/2026/num45_04/dgfip_stat_45_ifi_2025.pdf
- Same publication, methodological note (p. 6): "Les données budgétaires publiées par ailleurs correspondent aux données des avis émis mais aussi à celles non recouvrées d'avis antérieurs ainsi qu'à celles relatives aux contrôles fiscaux." — **this is the official explanation of the gap.** (Identical wording in n°33, IFI 2024.)
- DGFiP *recettes_fiscales_brutes.xls*, row "3. Impôt de solidarité sur la fortune / Impôt sur la fortune immobilière": 2022 2 353,1; 2023 2 354,3; 2024 2 739,3; 2025 prov. 2 770,7.
- DGFiP Statistiques n°43 (mars 2026) *budget 2025*, xlsx Tableau 1: IFI 2,739 Md€ (2024), 2,771 Md€ (2025), prévision LFI 2025 2,589, 100 % État. https://www.impots.gouv.fr/sites/default/files/media/9_statistiques/0_etudes_et_stats/0_publications/dgfip_statistiques/2026/num43_03/dgfip_stat43_budget_2025.xlsx
- PLF 2026 V&M tome I p. 23, "Impôt sur la fortune immobilière (ligne 1406)": 2 739 M€ (2024), 2 965 M€ (2025 révisée), 3 095 M€ (2026).
- Direction du budget, *Exécution budgétaire 2024 des recettes fiscales nettes de l'État*, line 1406: 2 354 (exéc. 2023) … 2 739 (exéc. 2024). https://www.budget.gouv.fr/documentation/file-download/30369
- Cour des comptes, *L'impôt sur la fortune immobilière, exercices 2018-2022* (S2023-1489, Jan 2024), p. 5 & 21-22, footnote 9, and Tableau 13 (p. ~68):
  https://www.ccomptes.fr/sites/default/files/2024-02/20240125-S2023-1489-Impot-sur-la-fortune-immobiliere.pdf
  - 2022: notices 1,8 Md€; budget IFI receipts 2,1 Md€ "en incluant l'IFI recouvré au titre des déclarations complémentaires et du contrôle fiscal"; **"Un reliquat d'ISF de 0,3 Md€ est recouvré la même année, essentiellement issu de contrôles, portant l'ensemble des recettes budgétaires IFI et ISF à 2,4 Md€ en 2022."**
  - IFI in droits constatés 2022 (Compte général de l'État): 2 308 M€, including control results and complementary declarations of 197 M€, and grossing up 271 M€ of reductions (dons, plafonnement) that are booked separately as moindres recettes.
  - IFI control yields (droits nets rappelés): 11,9 M€ (2020), 61,2 M€ (2021), 100,8 M€ (2022).

Assessment of Gemini's claim ("gap is mostly audit recoveries on IFI and old ISF + late declarations, ≈ 400–600 M€/yr"):
- **Size: VERIFIED-ish.** Gap budget − émission = ~550 M€ (2022), ~580 M€ (2024), ~440 M€ (2025). In range.
- **Composition: PARTLY WRONG / overstated for "audit".** For 2022 (the only year decomposed officially):
  ISF residual ≈ 300 M€ (mostly audits) + IFI complementary declarations & controls ≈ 197 M€ (of which IFI controls ≈ 100 M€) + collection of prior-year notices/timing. IFI audits alone are only ~0,1 Md€. ISF residual (from pre-2018 years) should decline over time (ISF assessment period mostly lapsed), so the composition in 2024–25 is likely shifting toward timing/complementary declarations — UNVERIFIED (no official decomposition for 2024–25 found).
- **Does line 1406 include ISF residuals? YES (VERIFIED by reconciliation):** DGFiP's gross-receipts row is explicitly labelled "ISF / IFI", and its 2022 value (2 353) equals line 1406's order of magnitude and the Cour's "IFI + ISF = 2,4 Md€"; the 2023 DGFiP value 2 354,3 equals the line 1406 2023 execution (2 354) exactly. No separate ISF line exists in état A.
- **Important correction for the model:** 2 965 M€ for 2025 is a *forecast* (PLF 2026). The *actual* 2025 collection is **2 771 M€** (DGFiP, March 2026). Use 2 771 if you want an executed 2025 figure.
- Cour des comptes NEB 2024 "Recettes fiscales" (https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Recettes-fiscales.pdf) only gives IFI 2,4 → 2,7 Md€ (2023→2024) in a table, no gap explanation.

---

## 4. Agricultural and natural land value

Gemini: INSEE AN.2112 + AN.2113 ≈ 170–230 Md€; price-based estimate ≈ 200–250 Md€.
**Verdict: the INSEE claim is WRONG. INSEE does publish AN.2112, and it is ≈ 900 Md€, about 4× Gemini's figure.
The price-based estimate is broadly right for farmland if forests are excluded.**

### 4a. INSEE publishes "Terrains cultivés" (AN.2112) — VERIFIED
INSEE, *Les comptes de la Nation en 2025*, "Comptes de patrimoine" (published 4 June 2026, base 2020),
https://www.insee.fr/fr/statistiques/8988859?sommaire=8988934
- Table **T_8201** (8.201 Comptes de patrimoine de l'économie nationale S1, Md€, end of year), file T_8201_fr.xlsx:

| Md€, end of year | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 (prov.) |
|---|---|---|---|---|---|---|
| N211 Terrains | 8 208,2 | 8 833,2 | 9 512,5 | 8 666,6 | 8 597,3 | 8 651,9 |
| N2111 Terrains bâtis | 6 863,3 | 7 361,4 | 7 913,5 | 7 151,0 | 7 044,0 | 7 032,4 |
| **N2112 Terrains cultivés** | 731,0 | 799,9 | 877,4 | 839,6 | 865,8 | **902,1** |
| N2113 Terrains et plans d'eau de loisirs | 4,8 | 4,7 | 4,9 | 4,9 | 5,2 | 5,4 |
| N2119 Autres terrains et plans d'eau | 609,1 | 667,1 | 716,7 | 671,1 | 682,3 | 712,0 |

- Table **T_8200_2025** (by sector, end-2025): N2112 = 902,1 Md€, of which **S11 709,6, S14 192,5**
  (nothing in S12/S13/S15). N2119 = 712,0 (S11 113,0; S13 147,1; S14 451,9). N2113 = 5,4 (all S13, local government).
- AN.2112 + AN.2113 (end-2025) = **907,5 Md€**, against Gemini's 170–230.
- Note: the earlier vintage (*Comptes de patrimoine en 2024*, https://www.insee.fr/fr/statistiques/8574720, T_8201 created 17 Oct 2025) gave N2112 = 839,4 (2024), so the order of magnitude holds across vintages.
- Puzzle (UNVERIFIED, worth an INSEE methodology check): 902 Md€ / 28,6 Mha of SAU is about 31 500 €/ha,
  roughly 5× the SAFER price for free farmland. I did not find INSEE's base-2020 method note for AN.2112.
  Possible reasons, none confirmed: vineyards are valued at very high prices (Champagne); the valuation
  method may differ from transaction prices; the allocation of "sols" between AN.2111 and AN.2112 for
  farm buildings. Also striking: INSEE puts 79 % of cultivated land in non-financial corporations (S11).

### 4b. Prices — SAFER/SSP, *Le prix des terres 2025* (published May 2026) — VERIFIED
Groupe Safer, *L'essentiel des marchés fonciers ruraux en 2025* (synthèse, p. 6–8),
https://www.le-prix-des-terres.fr/app/uploads/2026/05/2026-LPDT-synthese.pdf (the series is produced with the SSP/Agreste).
Detail: …/2026-PDT2025-03-TerresPres.pdf, …/2026-PDT2025-04-Vignes.pdf, …/2026-PDT2025-05-Forets.pdf (same folder)
- Terres et prés **libres** non bâtis: **6 460 €/ha** (+0,9 %). Grandes cultures 8 150; élevage bovin 4 740.
- Terres et prés **loués** non bâtis: **5 350 €/ha** (+2,5 %). Grandes cultures 6 800; élevage bovin 4 040.
- Vignes AOP: **171 400 €/ha** (−2,9 %); AOP excluding Champagne **87 400 €/ha** (−6,8 %); vignes à eaux-de-vie AOP 23 200 €/ha (−54,5 %); hors AOP 12 800 €/ha (−7,7 %).
- Forêts: **4 950 €/ha** (+2,5 %; this price includes standing timber, which national accounts record separately as a biological resource, not as land).
- Gemini's "≈ 6 100–6 200 €/ha" is out of date: it matches roughly 2023 (2024 was 6 400, +3,2 %).
- Official 2024 schedule: "Barème indicatif de la valeur vénale moyenne des terres agricoles en 2024", decision of 26 Aug 2025 (JORF 29 Aug 2025). Not read in detail.

### 4c. Areas — VERIFIED
- SAU: Agreste, *Statistique agricole annuelle 2025, chiffres provisoires*, Chiffres et données n°5, May 2026 (revised version), tables "Répartition de la surface agricole utilisée" (France p. 20; France hors DROM p. 37). Read from the PDF via https://draaf.pays-de-la-loire.agriculture.gouv.fr/IMG/pdf/cd2026-5_saa2025-provisoirev2-1.pdf
  - France hors DROM: SAU des exploitations **26 682 673 ha (2024), 26 638 633 ha (2025)**; total SAU incl. non-farmers' gardens and STH hors exploitations 28 442 545 / 28 403 470 ha; vines 774 682 / 747 976 ha; terres arables 16,87 Mha; STH des exploitations 8,79 Mha.
  - France incl. DROM: SAU des exploitations 26 821 033 (2024), 26 795 726 (2025).
  - So "SAU ≈ 26,7 Mha" = SAU des exploitations, metropolitan France. Correct. The Teruti-based SAU (28,4–28,7 Mha) is a different concept.
- Forest: IGN, *Inventaire forestier national, Mémento édition 2024*, p. 12: "La forêt en France hexagonale et Corse couvre **17,5 millions d'hectares**, soit 32 % du territoire" (13,1 Mha private; 1,55 Mha domaniale; 2,8 Mha other public). https://inventaire-forestier.ign.fr/IMG/pdf/memento_2024.pdf. The 2025 edition reportedly gives 17,6 Mha (Fransylva citing IGN). Not read directly.
- Gemini's "forests ≈ 17 Mha" is slightly low (17,5–17,6).

### 4d. Price × area estimate (my method, rough)
- Arable land and grassland = SAU des exploitations 2025 (26,64 Mha) minus vines, orchards, nurseries and other permanent crops = 25,65 Mha.
  At 5 350–6 460 €/ha, that is **≈ 137–166 Md€**.
- Vines, 0,748 Mha: at 87 400 €/ha (AOP excluding Champagne) it is ≈ 65 Md€; at 171 400 €/ha (AOP including Champagne) it is ≈ 128 Md€.
  The realistic mix (Cognac/Armagnac and non-AOP vines are much cheaper) is likely **≈ 50–100 Md€**. The split of vine area by type is not verified.
- Farmland subtotal: **≈ 190–270 Md€**. Gemini's 200–250 Md€ falls inside this range, but its 6 100–6 200 price is stale.
- Forests: 17,5 Mha × 4 950 €/ha ≈ **87 Md€**, an upper bound for the land alone because the price includes timber.
- Total agricultural and natural land at market price: **≈ 280–360 Md€**.
- Bottom line: the price-based farmland value (≈ 0,2–0,27 Tn€) is **3,5–4,5× smaller** than INSEE's AN.2112 (0,90 Tn€).
  Before the model uses either figure, choose one deliberately and document why.

## 5. INSEE patrimoine national: built land (terrains bâtis, AN.2111) by sector, end-2025

**Verdict: Gemini's "corporations ≈ 1 800–2 000 Md€" is CORRECT (S11 + S12 = 1 901 Md€). VERIFIED.**

Source 1: INSEE, *Patrimoine national par secteur institutionnel et grand type d'actif*, Chiffres-clés, published 30/07/2026,
end-2025 provisional, file econ-gen-patrimoine-nat.xlsx, row "terrains supportant des bâtiments et des ouvrages de génie civil":
https://www.insee.fr/fr/statistiques/2830290
Source 2 (gives S14 and S15 separately): INSEE T_8200_2025_fr.xlsx, row N2111, https://www.insee.fr/fr/statistiques/8988859?sommaire=8988934

| Sector | Md€ end-2025 |
|---|---|
| S14 Ménages | 4 136,1 |
| S15 ISBLSM | 53,9 |
| (S14+S15, as shown in Chiffres-clés) | 4 190,0 |
| S11 Sociétés non financières | 1 700,7 |
| S12 Sociétés financières | 200,3 |
| S13 Administrations publiques | 941,4 (central 222,6, of which État 100,6 and ODAC 121,9; local 718,8; ASSO 0) |
| **Total S1** | **7 032,4** |

- Your base: 7 032 − 941 (S13) = 6 091 Md€ = households + NPISH + corporations. Consistent.
- Corporations (S11+S12) = 1 901,0 Md€, inside Gemini's 1 800–2 000.

## 6. CPI (INSEE, IPC ensemble, annual averages)

**VERIFIED.** INSEE BDM series **idbank 001764363**, "Indice annuel des prix à la consommation – Base 2015 – Ensemble des
ménages – France – Ensemble – Séries arrêtées" (last update 15/01/2026), read via
https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001764363. I cross-checked it against the 12-month average of the monthly
series 001759970; the values match to 2 decimals.

| Year | Index (2015=100) | Factor to 2025 € |
|---|---|---|
| 2020 | 104,73 | 1,1549 |
| 2021 | 106,45 | 1,1362 |
| 2022 | 112,01 | 1,0798 |
| 2023 | 117,47 | 1,0296 |
| 2024 | 119,82 | 1,0094 |
| 2025 | 120,95 | 1,0000 |

- Caveat: base 2015 was discontinued ("séries arrêtées") after December 2025 and replaced by base 2025 (dataflow IPC-2025).
  For 2020–2025 ratios the 2015-based series is the right one. Do not mix bases within one calculation.
- For a tax-yield deflator, an alternative is the GDP deflator. CPI is fine for "2025 euros of household purchasing power".

## 7. THRS in the REI (OFGL dataset `rei`, fiscal year 2025)

**Verdict: the 2 583 M€ does NOT include the second-home surcharge. Gemini's variable name and amount
(MTMAJOTHRS ≈ 391 M€) are CORRECT. VERIFIED** via the OFGL Explore API
(https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei/records, dataset "(REI) Fiscalité directe locale 2024–2025", modified 29/05/2026).

National sums, 2025 (dispositif "TH"):

| Var | Label | M€ |
|---|---|---|
| H13THS | TH – commune / montant réel THS | 1 727,42 |
| H33THS | TH – intercommunalité / montant réel THS | 843,14 |
| H23THS | TH – syndicats / montant réel THS | 12,10 |
| **Sum = THRS excluding surcharge** | | **2 582,66** (your 2 583) |
| **MTMAJOTHRS** | Montant réel de la majoration des résidences secondaires | **390,92** |
| **THRS including surcharge** | | **2 973,58** |
| H01 | Frais de gestion THS (State) | 93,47 |
| H13LV + H33LV + H23LV | THLV (vacant homes, communal/EPCI) | 123,53 |
| VLMAJOTHRS | Base nette susceptible de majoration | 6 481,3 |
| NLOCMAJOTHRS / J13C | Premises liable to surcharge / premises actually surcharged | 2 940 215 / 2 204 684 |
| TXMAJOTHRS | Surcharge rate (per commune) | n/a (summing it is meaningless) |

Proof that H13THS excludes the surcharge (VERIFIED by recomputation):
- Paris 2025: H11THS 789 170 445 × H12 rate 20,32 % = 160,36 M€ = H13THS (160 355 262). Separately, VLMAJOTHRS 617 683 003 × 20,32 % × 60 % = 75,31 M€ = MTMAJOTHRS (75 307 540).
- Bordeaux 2025: 26 252 536 × 24,13 % = 6,335 M€ = H13THS; 20 621 833 × 24,13 % × 60 % = 2,986 M€ = MTMAJOTHRS.

2024 for comparison: H13THS 2 208,5 + H33THS 1 031,6 + H23THS 15,0 = **3 255,1 M€**, plus MTMAJOTHRS **436,3 M€**.
- The roughly 20 % fall from 2024 to 2025 is broad-based (Paris −28 %, Hauts-de-Seine −37 %, Rhône −47 %, with the same number of communes).
  It probably reflects corrections to second-home status after the "Gérer mes biens immobiliers" declaration problems, but this is UNVERIFIED.
  It deserves a check against DGFiP Statistiques' THRS publications before 2025 is used as the base year.

---

## Summary scorecard
| # | Gemini claim | Result |
|---|---|---|
| 1 | TSBCS ≈ 0,95–1,10 Md€ | Plausible. Rebuilt from beneficiary shares: ≈ 0,93 (2023), ≈ 0,99 (2024), ≈ 1,0–1,06 (2025). No official total found (partly UNVERIFIED) |
| 2 | CSI ≈ 0,25–0,30 Md€ | **WRONG**: 0,69–0,92 Md€ (2021–2025); 692 M€ (2024), 745 M€ (2025, provisional) |
| 3 | IFI gap ≈ 0,4–0,6 Md€, mostly audits and old ISF | Size right. Official explanation: prior-year notices + tax audits (+ complementary declarations). Line 1406 includes ISF residuals. IFI audits alone ≈ 0,1 Md€. 2025 actual is 2 771, not 2 965 |
| 4 | INSEE AN.2112+2113 ≈ 170–230 Md€ | **WRONG**: 907,5 Md€ (end-2025). Price-based farmland ≈ 190–270 Md€ (OK); land price is stale (2025: 6 460) |
| 5 | Corporations' built land ≈ 1,8–2,0 Tn€ | **CORRECT**: 1 901 Md€ |
| 6 | CPI restatement | Index values supplied (idbank 001764363) |
| 7 | MTMAJOTHRS ≈ 391 M€, not in 2 583 | **CORRECT**: 390,9 M€, excluded; THRS incl. surcharge = 2 973,6 M€ |
