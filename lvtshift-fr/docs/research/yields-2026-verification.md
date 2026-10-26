# Independent verification of `lvtshift-fr/yields.py` (26 October 2026)

*Kept as the audit trail for `yields-2026.md`. Corrections in §2.1–2.7 were applied in `yields.py`; inclusion choices in §3 are listed as open in the note.*

Scope: every figure in `yields.py` and the land base, checked against the cited sources and corroborating sources. No repository file was edited.

**How each source was reached.**
- OFGL Opendatasoft API v2.1 (datasets `rei`, `ofgl-base-departements`, `ofgl-base-regions`, `grand-livre`, `methodologie-ofgl-definitions-agregats-financiers`): queried with `fetch()` from my own tab in the user's built-in browser.
- Cour des comptes open-data ZIP (`Open data_58-2_Imposition des PVI.zip`): read in memory. I also extracted the text of the report PDF (101 pp.) in memory with pdf.js. Nothing was saved to disk.
- Other primary sources read directly:
  - DGFiP Statistiques IFI pages n° 15, 23, 33 and 45 (impots.gouv.fr);
  - INSEE IP2028, IP2081 and the "Chiffres-clés 2025" table;
  - CPO, December 2023 (vie-publique PDF, read in memory);
  - PLF 2026 Voies et moyens, tome I (assemblee-nationale.fr PDF, read in memory);
  - DGCL BIS 190 (WebFetch).

**Verdict vocabulary.**
- **Confirmed**: re-derived from the primary source.
- **Corroborated**: a secondary source agrees.
- **Unverifiable**: not reached.
- **Contradicted**: the primary source disagrees, or the figure does not measure what the line claims.

## 1. Figure-by-figure table (M€)

| Line key | Year | Ours | Mine | Source (exact field) | Verdict |
|---|---|---:|---:|---|---|
| tfpb | 2024 | 41 632 | 39 113.1 + 2 519.0 = 41 632.1 | OFGL `rei`, annee=2024, var E13 "FB - COMMUNE / MONTANT RÉEL" + E33 "FB - INTERCOMMUNALITÉ / MONTANT RÉEL" (summed over communes) | Confirmed |
| tfpb | 2025 | 42 776 | 40 157.3 + 2 619.5 = 42 776.8 | idem, annee=2025 | Confirmed. DGCL BIS 209 via Maire-info (12/05/2026): TFPB "about 43,1 Md€" across all collectivities, +2,8 %. Consistent with 42 777 + syndicates 184 ≈ 42 961 |
| tfpnb | 2024 | 1 296 | 1 007.7 + 189.4 + 4.0 + 90.8 + 4.4 = 1 296.3 | `rei` B13, B33, B13TAFNB, B33TAFNB, B33MGPTAFNB | Confirmed |
| tfpnb | 2025 | 1 188 | 915.7 + 171.7 + 4.0 + 90.8 + 4.7 = 1 186.9 | idem | Confirmed (the gap is rounding). DGCL BIS 209: FNB about −8 % |
| dmto_communes | 2021 | 3 643 | 3 642.9 | OFGL `grand-livre`, categ=commune, cbudg=TOTAL, obnetcre_mt: M14/M14A c/7381 + M57/M57A c/73123 + M57 c/7332 + M57/M57A c/73223 + M14/M14A c/73224 | Confirmed (reproduced exactly; see §2.1 for the Paris overlap) |
| dmto_communes | 2022 | 3 978 | 3 978.7 | idem | Confirmed |
| dmto_communes | 2023 | 3 356 | 3 355.4 | idem | Confirmed |
| dmto_communes | 2024 | 2 882 | 2 883.2 | idem | Confirmed |
| dmto_communes | 2025 | 3 155 | 3 154.2 | idem | Confirmed |
| dmto_departements | 2021 | 16 511 | 16 511.4 as published; **16 259** on the stated scope | `ofgl-base-departements`, agregat "DMTO avant péreq.", Budget principal; minus Paris communal share; plus CTU (`ofgl-base-regions`) | **Contradicted (scope)**: includes Paris's communal tax (397) and excludes Corse, Martinique and Guyane (145) |
| dmto_departements | 2022 | 16 776 | 16 776.0 → **16 538** | idem (Paris communal 392; CTU 154) | **Contradicted (scope)** |
| dmto_departements | 2023 | 13 044 | 13 044.0 → **12 882** | idem (Paris communal 301 by difference; DGCL gives 289; CTU 139) | **Contradicted (scope)** |
| dmto_departements | 2024 | 11 297 | 11 296.7 → **11 145** | idem (Paris communal 268; CTU 116) | **Contradicted (scope)** |
| dmto_departements | 2025 | 13 669 | 13 668.6 → **13 484** | idem (Paris communal 320; CTU 135) | **Contradicted (scope)** |
| dmto_etat | 2021–25 | 391 / 398 / 309 / 268 / 324 (avg 338.0) | 385 / 392 / 305 / 264 / 320 (avg 333.3) | 2,37 % × the corrected departmental series. Rate corroborated by Weblex 2025 ("calculé sur le montant du droit départemental"). Legifrance not reachable | Corroborated (rate). The base is slightly wrong: the frais do not apply to Paris's communal 1,2 %, and the CTU are missing. Effect −4.7 M€ |
| gains_ir | 2020 | 1 049.4 | 944 + 78.724716 + 1.987108 + 24.742358 | Cour des comptes open data `G9+10.csv`, rows IR, Surtaxe, Taxe communale, Taxe nationale | Confirmed |
| gains_ir | 2021 | 1 422.1 | 1 285 + 102.05 + 2.44 + 32.72 | idem | Confirmed |
| gains_ir | 2022 | 1 677.6 | 1 501 + 138.16 + 2.22 + 36.22 | idem | Confirmed |
| gains_ir | 2023 | 1 278.1 | 1 145 + 105.92 + 2.64 + 24.65 | idem | Confirmed |
| gains_ir | 2024 | 995.0 | **907.6** (probably) | `T7.csv`, 2024: IR 907.568; surtaxe 70.039; communal 1.531; national 15.917 | **Contradicted (probable double count)**. In 2023, T7's "IR Produit" (1 277.67) equals G9+10's IR + surtaxe + both land taxes (1 278.2) to within G9's rounding. The surtaxe and land-tax columns of T7 2023 match G9+10 to the euro. So T7's IR column is very likely the all-in IR-side total, and adding the three taxes again in 2024 double counts 87.4 M€ |
| gains_ps | 2020–23 | 2 061 / 2 702 / 3 014 / 2 347 | identical | `G9+10.csv`, row PS | Confirmed |
| gains_ps | 2024 | 1 924.5 | 1 924.476 | `T7.csv`, "Produit.prélèvements.sociaux" 2024 | Confirmed. Provisional: report footnote 36, p. 39, says the 2024 yield is "pas encore stabilisé" |
| ifi | 2022 | 2 100 | **≈ 1 800** | DGFiP Statistiques n° 15 (Apr. 2023): "environ 1,8 milliard d'euros" | **Contradicted** (the 2,1 Md€ is the CPO's, on a different basis). No effect on the reference, which uses only the latest year |
| ifi | 2023 | 1 900 | 1 900 | DGFiP Statistiques n° 23 (Apr. 2024): "1,9 Md€, en hausse de 6 %" | Confirmed |
| ifi | 2024 | 2 200 | 2 200 | DGFiP Statistiques n° 33 (15/04/2025): "2,2 Md€, soit une hausse de 11 %" | Confirmed (primary; the line says "reported") |
| ifi | 2025 | 2 300 | 2 300 | DGFiP Statistiques n° 45 (14/04/2026): "2,3 Md€, en hausse de 8,0 %", 193 600 households | Confirmed (primary). Budget-receipts basis is higher: Voies et moyens PLF 2026, tome I, p. 23, line 1406 gives **2 739 M€ executed in 2024** and **2 965 M€ revised 2025** |
| rents_ir | 2022 | 4 200 | 4 200 | CPO, *Pour une fiscalité du logement plus cohérente*, Dec. 2023, printed p. 23 (PDF p. 35) | Corroborated (the CPO quote is exact). The underlying DGFiP/SDES figure was not reached. Housing-only scope |
| rents_ps | 2022 | 2 400 | 2 400 | idem. Same page lists "CSG sur les revenus immobiliers (1,1 Md€)" and CRL 100 M€; the stated total is 8,3 Md€ while the lines sum to 7,8 | Corroborated. Overlap with the CSG line unresolved |
| land: built_land_total | end-2023 | 6 346 000 | 6 346 Md€ | INSEE IP2028, figure 2, "Terrains bâtis", Ensemble | Confirmed, but **superseded**: national accounts revised; 2023 change now −8,6 %, not −13,7 % |
| land: built_land_public | end-2023 | 916 000 | 916 Md€ | idem, APU column | Confirmed, but **superseded** |
| (newer) land base | end-2024 | — | 6 729 total / 903 APU (taxable 5 826) | INSEE IP2081 (06/11/2025), figure 2 and IP2081.xlsx | Confirmed |
| (newer) land base | end-2025 (prov.) | — | 7 032 total / 941 APU (taxable 6 091) | INSEE Chiffres-clés "Patrimoine national par secteur institutionnel et grand type d'actif", données annuelles 2025, paru 30/07/2026, line "terrains supportant des bâtiments et des ouvrages de génie civil" | Confirmed |

**Tally (37 figures in yields.py, counting each year and the two land figures):**
- **Confirmed: 23**: TFPB 2, TFNB 2, communal DMTO 5, gains IR 2020–23 4, gains PS 5, IFI 2023–25 3, land 2. The two land figures are confirmed but outdated.
- **Contradicted: 7**: departmental DMTO 5 on scope, IFI 2022, gains IR 2024 (probable).
- **Corroborated only: 7**: DMTO frais d'assiette 5, rents IR/PS 2.
- **Unverifiable: 0** at figure level. For the rents, the primary behind the CPO could not be reached.

### Per-line metadata (reference rule, scope, URL)

| Line | Rule | Scope claim | URL | Verdict |
|---|---|---|---|---|
| tfpb | latest (2025) | Commune + EPCI; excludes syndicates (184 ✓), TSE/GEMAPI/TASA "≈ 0,7 Md€" | `data.ofgl.fr/explore/dataset/rei/` resolves; the dataset id exists | Scope confirmed: TSE-FB 202.7 + TSE autres 72.4 + GEMAPI-FB 376.6 + TASA-FB 57.9 = **709.6 M€** (2025). Excluding the State-paid allocations compensatrices is a method choice (§5) |
| tfpnb | latest | Commune + EPCI + TAFNB; excludes syndicates and chambres d'agriculture | ok | Confirmed. Chambres d'agriculture 333.9 + CAAA 11.4 M€ (2025) are excluded |
| dmto_communes | 5-yr avg | Taxe additionnelle + small-commune fund | `grand-livre` resolves | Account choice confirmed and correctly nomenclature-specific. The author avoided M14 c/73223 (FPIC, 524 M€ in 2021) and M14 c/7332 (taxe de balayage). **Includes the Ville de Paris's communal tax** (M57 c/73123): see §2.1 |
| dmto_departements | 5-yr avg | "Y compris Paris et la métropole de Lyon" | `ofgl-base-departements` resolves | Scope contradicted. The OFGL definition says Paris's aggregate contains "la taxe communale additionnelle" (double count). Corse, Martinique and Guyane are in `ofgl-base-regions`, not here (omission) |
| dmto_etat | 5-yr avg | 2,37 % on departmental duty | `legifrance…/LEGITEXT000006069577/` is the CGI root, not art. 1647 | URL too generic: link the article. Rate corroborated (Weblex) |
| gains_ir / gains_ps | 5-yr avg 2020–24 | Individuals; IR at 19 %, surtaxe, land taxes; PS 17,2 % | ccomptes URL resolves to the publication; the open-data ZIP is linked from it | Confirmed. The 17,2 % includes CSG 9,2 % (report fn 3, p. 16), so there is no CSG double count. **Budget label wrong**: the 7,5 % prélèvement de solidarité goes to the State (V&M line 1427: "affectés… à l'État depuis le 1er janvier 2018"), i.e. 43,6 % of the "PS" line |
| ifi | latest | All payers | impots.gouv page n° 23 resolves (2023) | Point the URL to n° 45 (2025). Status should be "verified" |
| rents_* | latest (2022) | Individuals' rental income, excl. BIC/IS | vie-publique PDF resolves; the figures are on printed p. 23 | The CPO text is "fiscalité du logement", so the scope is **housing only**. Commercial lettings by individuals are probably missing |
| LandBase | end-2023 | Built land net of APU | insee.fr/fr/statistiques/8305990 resolves | Superseded (see table) |

## 2. Errors and corrections (exact changes to `yields.py`)

### 2.1 Paris communal DMTO counted twice (−336 M€ on every scenario)

**Evidence of the double count.**
- The OFGL definition of "DMTO avant péreq." (dataset `methodologie-ofgl-definitions-agregats-financiers`) says the aggregate includes, "pour la ville de Paris, de la taxe communale additionnelle aux droits de mutation".
- In `grand-livre` the Ville de Paris sits in categ=commune. Its departmental duty shows there as M57 c/73121: 1 139 M€ in 2020, 1 337 in 2021. Its communal tax is in M57 c/73123, which `dmto_communes` sums.
- DGCL BIS 190, encadré 2, splits Paris 2023 as "part départementale (1 038 M€) et la part communale (289 M€)", total 1 327. OFGL Paris 2023 = 1 327.8.

**Estimate of the Paris communal share.** OFGL Paris aggregate minus grand-livre commune c/73121:

| Year | Paris communal share (M€) |
|---|---:|
| 2021 | 397 |
| 2022 | 392 |
| 2023 | 301 (DGCL: 289) |
| 2024 | 268 |
| 2025 | 320 |
| **Average** | **335.7** |

The DGCL-anchored alternative (ratio 289/1 327.8 applied each year) gives about 319. The DMTO frais base also falls by 2,37 % of this.

### 2.2 Corse, Martinique and Guyane departmental DMTO missing (+138 M€)

`ofgl-base-regions`, agregat "DMTO avant péreq.", Corse + Guyane + Martinique:

| Year | CTU DMTO (M€) |
|---|---:|
| 2021 | 145.4 |
| 2022 | 154.2 |
| 2023 | 139.4 |
| 2024 | 116.4 |
| 2025 | 135.4 |
| **Average** | **138.1** |

Grand-livre region c/73121 agrees: 144.7 / 153.2 / 138.4 / 115.2 / 134.4. DGCL BIS 190 cites "les collectivités territoriales uniques (139 M€)" for 2023.

**Suggested code:**

```python
# OFGL "DMTO avant péreq." (departments dataset) as published
_DMTO_DEP_OFGL = {2021: 16511, 2022: 16776, 2023: 13044, 2024: 11297, 2025: 13669}
# Ville de Paris communal additional tax, included in OFGL's Paris aggregate and
# also in dmto_communes (grand-livre M57 c/73123): OFGL Paris minus c/73121
_PARIS_COMMUNAL = {2021: 397, 2022: 392, 2023: 301, 2024: 268, 2025: 320}
# Collectivités de Corse, Martinique, Guyane (ofgl-base-regions, "DMTO avant péreq.")
_DMTO_CTU = {2021: 145, 2022: 154, 2023: 139, 2024: 116, 2025: 135}
_DMTO_DEP = {y: _DMTO_DEP_OFGL[y] - _PARIS_COMMUNAL[y] + _DMTO_CTU[y] for y in _DMTO_DEP_OFGL}
# -> {2021: 16259, 2022: 16538, 2023: 12882, 2024: 11145, 2025: 13484}; avg 14 061.6
```

Then:
- Update the `dmto_departements` scope to "hors part communale de Paris (comptée dans dmto_communes) ; y compris CTU de Corse, Martinique, Guyane".
- `dmto_etat` then computes on the corrected base (avg 333.3).
- **Net effect on every scenario: −197.6 (departmental) − 4.7 (State) = −202 M€.**

### 2.3 TF frais de gestion omitted while the DMTO frais are included (+1 319 M€ on S1, or −338 for consistency)

- The State adds frais d'assiette, de dégrèvement et de non-valeurs to every TF bill.
- REI var E00 "FB - FRAIS D'ASSIETTE, DÉGRÈVEMENT, NON VALEURS" (destinataire État) = **2 068.3 M€** in 2025. This total includes the TEOM frais. B00 (FNB) = **62.3 M€**.
- Voies et moyens PLF 2026, line 1201 (p. 17) covers "frais de gestion des impôts directs locaux": 2 127 M€ executed in 2024.
- At 3 % on the commune + EPCI TF in scope: 0,03 × (42 776 + 1 188) = **1 319 M€** (2025). The 3 % rate (CGI art. 1641) is from my memory and was not read on Legifrance. It is consistent with the REI E00 total once 8 % on TEOM and on TSE/GEMAPI/syndicates is added: ≈ 2 088 vs 2 068.
- **Fix: either**
  - add a line `tf_frais_etat` (S1, national, État, status derived, values {2024: 1288, 2025: 1319}, source REI E00/B00 and CGI art. 1641); **or**
  - drop `dmto_etat` so that neither State surcharge is counted.

  Keeping one and not the other is inconsistent.

### 2.4 Gains IR 2024 probably double counted (−17.5 M€ on S2/S3)

Set `gains_ir.values[2024] = 907.6`. The T7 IR column appears to already include the surtaxe and the two land taxes (§1). Reword the note: the "rupture de série" for IR is probably an aggregation artefact; only the PS gap (+10,1 % in 2023) is unexplained.

### 2.5 IFI line (no effect on totals unless the basis changes)

- **Values and status:** `values={2022: 1800, 2023: 1900, 2024: 2200, 2025: 2300}`; `status="verified"`.
- **Source:** "DGFiP Statistiques n° 15 (2022), n° 23 (2023), n° 33 (2024), n° 45 (2025)".
- **URL:** `https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-la-fortune-immobiliere-en-2025`.
- **Note to add:** "Montants des avis. Recettes budgétaires (VM PLF 2026, ligne 1406) : 2 739 M€ exécutés en 2024, 2 965 M€ révisés 2025."
- Switching to the budget basis would add **+439 M€** (2024 executed vs avis) or **+665 M€** (2025 revised) to the IFI variants.

### 2.6 Budget attribution of the "PS" lines (no effect on totals)

`gains_ps` and `rents_ps` carry `budget="Sécurité sociale"`. 7,5 of the 17,2 points (the prélèvement de solidarité) go to the State budget:
- `gains_ps`: ≈ 1 051 M€ of the 2 410 average;
- `rents_ps`: ≈ 1 047 M€ of the 2 400.

Either split each line or label it "Sécurité sociale + État". Secondary sources (mysweetimmo, Dec. 2025; actu-juridique) say the 2026 CSG increase on capital income spares real-estate income and gains, so 17,2 % still holds for these lines. This was not checked against the LFSS text.

### 2.7 Land base (rate −11 %)

Replace with the INSEE end-2025 provisional figures:

```python
built_land_total: float = 7_032_000
built_land_public: float = 941_000
year: int = 2025
source = "INSEE, Chiffres-clés « Patrimoine national par secteur institutionnel et grand type d'actif », données annuelles 2025 (provisoires), 30/07/2026"
url = "https://www.insee.fr/fr/statistiques/2830290"
```

- Alternatively, use end-2024 final: 6 729 / 903, IP2081, `https://www.insee.fr/fr/statistiques/8661938`.
- Delete "après une baisse de 13,7 % sur un an". The revised 2023 change is −8,6 %, and 2024 is −2,7 %.
- **Effect:** taxable base 5 430 → 6 091 Md€.

| Scenario | Rate now | Rate with corrected totals | Rate on new base, old totals | Rate on new base, corrected totals |
|---|---:|---:|---:|---:|
| S1 | 1,141 % | 1,163 % (after §2.1–2.3) | 1,017 % | 1,036 % |
| S3 + IFI | 1,373 % | — | 1,224 % | — |

### 2.8 Smaller text corrections in `docs/research/yields-2026.md`

- "The Cour's own average for 2017–2024 (3,5 Md€)" should read **2017–2023**. Report p. 39: "en moyenne à 3,5 Md€ entre 2017 et 2023". My recomputation from G9+10: 3 530.
- "If T7's higher basis applies throughout, the average is understated by ~2 %… under 0,1 Md€" is wrong. Raising 2020–22 by T7/G9 (×1,1018) and using T7 2023 gives an average of 4 011 vs 3 694: **+317 M€ (+8,6 %)**. The G9-basis case is right (−54 M€). The range is asymmetric: −54 / +317.
- "Taking the latest year instead would lower S1 by 0,6 Md€" covers the departmental line only. With communes and frais the drop is **−852 M€**.
- "Matches DGCL BIS 190 (13,0 Md€ in 2023)" is a coincidence of offsetting scope differences. OFGL includes Paris's communal 289 and excludes the CTU's 139. DGCL counts Paris's departmental part only ("se basent uniquement sur la part départementale"). Whether DGCL's 13,0 includes the CTU is not stated.

### Scenario totals after the definite errors (§2.1, 2.2, 2.4) and with the S1 omissions (§2.3, IdF DMTO §3)

| Variant | Now | Errors corrected | + TF frais + IdF DMTO |
|---|---:|---:|---:|
| S1 | 61 964 | 61 762 | 63 127 |
| S2 | 65 658 | 65 439 | 66 804 |
| S2 + IFI | 67 958 | 67 739 | 69 104 |
| S3 | 72 258 | 72 039 | 73 404 |
| S3 + IFI | 74 558 | 74 339 | 75 704 |

## 3. Missing taxes

| Tax | Yield (M€) | Source | Scenario it logically belongs to |
|---|---:|---|---|
| Regional additional DMTO, IdF offices/shops/storage (CGI art. 1599 sexies, 0,6 %) | 55.2 / 53.8 / 43.0 / 39.3 / 41.7 (2021–25; avg **46.6**) | `grand-livre` categ=region: M71 c/7353 (2021–22), M57 c/7332 (2023–25). DGCL BIS 190: "les régions reçoivent 43 M€" (2023) | **S1**: a transfer duty on real property, paid at the same act as the DMTO. Not in any line today |
| TSE, GEMAPI and TASA on the TF bill; syndicates' TF | 2025: TSE-FB 275.1, GEMAPI-FB 376.6, TASA-FB 57.9, syndicats FB 184.3, TSE-FNB 1.5, GEMAPI-FNB 20.5, syndicats FNB 6.7 = **922.6** | REI 2025 (vars E53, E53A, E53gGEMAPI, E53TASA, E23, B53, B53A, B53gGEMAPI, B23) | **S1**: same base and same bill as TF. The note's "≈ 0,7 Md€, à confirmer" is now confirmed at 709.6 for the FB part. TSE funds établissements publics fonciers, so it is arguably the most "land" of all |
| THRS (TH on second homes) + majoration | 2024: 2 208.5 + 1 031.6 + 15.0 = **3 255**; 2025: 1 727.4 + 843.1 + 12.1 = **2 583**. Majoration (MTMAJOTHRS) 436 / 391, possibly already inside the commune figure (not determined). GEMAPI/TSE on THRS 2025: 89 | REI vars H13THS, H33THS, H23THS. The 2025 fall is real: DGCL BIS 209 via Maire-info gives "−19,1 %". CPO: 2,8 Md€ (2022) | **Optional S1 toggle.** It is a recurrent local levy on non-main dwellings, assessed on the same VLC as TF. It is levied on the occupant and used as housing policy (zone tendue surcharges). The largest local item a "replace property taxes" reform must take a position on |
| THLV / TLV (vacant dwellings) | THLV 2024 174.1, 2025 123.5 (REI H13LV + H33LV + H23LV). TLV (State): CPO ≈ 80 M€ pre-2023; post-2023 yield not found | REI; CPO p. 23 | **Stay out.** These are penalty (Pigouvian) taxes; an LVT already penalises vacancy. Small |
| TEOM | 2024: 8 939.7; 2025: **9 164.3** | REI F13. DGCL BIS 209: "about 9,2 Md€" | Out, as stated (a service charge), but legally a tax on the TF base. It would be the single largest addition if the rule were "every levy on the TF bill". Make the exclusion explicit on the site |
| CFE (business premises) | 2025: 573.2 + 7 645.7 = **8 218.9** (+ GEMAPI/TASA/TSE on CFE ≈ 359) | REI P13, P33 | Out of S1–S3 (a tax on business occupancy and activity), but it is the business analogue of TH and assessed on VLC of premises. Must be stated, since "taxe foncière des entreprises" is how many readers see it |
| Chambres d'agriculture TATFNB + CAAA | 2025: 333.9 + 11.4 = **345.3** | REI C13, C33, C43 | **S1 only once agricultural land enters the base (D6)**; otherwise out |
| Contribution sur les revenus locatifs (CRL) | ≈ **100** (2022) | CPO p. 23 | **S3** (a tax on rental income; mostly IS-liable lessors, so partly outside the individuals-only rule D3) |
| Contribution de sécurité immobilière (0,10 % of price, State) | **Not found.** My own order of magnitude, unsourced: 0,1 % × ~250–300 Md€ of transactions ≈ 250–300 | — | **S1** (paid by the buyer at transfer, like the DMTO frais). Unverifiable |
| Taxe sur les bureaux IdF (TSBCS, art. 231 ter) | **Not found.** V&M PLF 2026 p. 101 shows only a +50,5 M€ change in the SGP cap. My recollection of ≈ 1 Md€ is unverified | — | Candidate **S1 toggle**: an annual holding tax on built area in IdF. It taxes floor area (i.e. buildings), which an LVT reform would logically remove |
| Allocations compensatrices on TF (State-paid TF on exempt bases) | 2025, commune level: FB WCOMFB **2 551.5** (of which 50 % industrial VL WC75 2 262.5); EPCI FB ≈ 165 (EPCI variables repeat per member commune: sum of per-EPCI maxima); FNB 113.4 + ≈ 1–33 | REI | Not a tax but a TF yield paid by the State (see §4). It belongs in the S1 revenue-to-replace if the reform removes the exemptions and the State stops paying |

## 4. Method objections (ranked by potential effect on totals, M€)

| # | Objection | Effect | Evidence and recommendation |
|---:|---|---|---|
| 1 | Land base outdated (end-2023, pre-revision) for 2025 yields | Rates −11 % (S1 1,141 → 1,017 %); equivalently, the old base understates taxable land by 661 Md€ | INSEE end-2025 provisional 7 032 / 941; end-2024 6 729 / 903. The note's warning ("if land has recovered, rates are overstated") is borne out, and the revision also restates 2023 itself |
| 2 | TEOM and CFE exclusions undocumented on the page | +9 164 / +8 219 if included | Defensible exclusions, but they must be argued (§3) |
| 3 | THRS not in any scenario | +2 583 (2025) to +3 255 (2024), plus majoration ≈ 0,4 | Add as a toggle |
| 4 | State-paid TF compensations ignored | ≈ +2 700 (FB 2 551.5 commune + ≈ 165 EPCI) + ≈ 146 FNB (2025) | Equal yield for communes means TF paid + compensations, if the LVT taxes industrial land fully and the State stops paying. Decide and document |
| 5 | DMTO 5-year average blends rate regimes | Up to ≈ +1 500 if all departments were at 5 % (own estimate, unsourced); −852 if the latest year is used instead | LF 2025 allows up to 5 % for acts from 1/4/2025 to 31/3/2028 (collectivites-locales.gouv.fr DMTO page). 2021–24 were at ≤ 4,5 %. The average under-represents current law but over-represents a temporary increase. Also nominal (no deflator), and the 2021–22 peak and the 2024 trough fall inside the window |
| 6 | TF frais de gestion omitted (see §2.3) | +1 319 | Error-level inconsistency |
| 7 | Rental-income scope | ±1 100 to +1 500 | CPO's IR 4,2 / PS 2,4 are housing-only, for 2022. The "CSG 1,1 Md€" line cannot be reconciled with PS at 17,2 %: if PS included CSG, the CSG share would be ≈ 1,28; if PS excluded it (8 %), CSG would be ≈ 2,76. Commercial lettings by individuals and LMNP BIC are missing. 2022 values are used as "latest" against 2025 elsewhere |
| 8 | TSE/GEMAPI/TASA/syndicates on the TF bill | +923 | Include in S1 (same base, same bill) |
| 9 | IFI basis (avis vs budget receipts) | +439 to +665 on the IFI variants | V&M line 1406. Explain the choice |
| 10 | Splicing Cour G9+10 (2020–23) with T7 (2024) | −54 to +317 on S2/S3 | Defensible on balance: the Cour's own text (p. 41) says first 2024 figures are down "de l'ordre de 19 %", and T7-2024 vs G9-2023 = −19,5 %, so the Cour itself compares them. But T7 2024 is provisional (fn 36), the IR line probably double counts (§2.4), and the note's sensitivity statement is wrong (§2.8). The averaging windows also differ: gains 2020–24 (includes the COVID year) vs DMTO 2021–25 |
| 11 | Excluding public land | Base −941 Md€ (rate +15 %) | Right in principle (CGI art. 1382 exempts public property used for public service). But APU "terrains bâtis" includes land under roads and networks, and the commune-level model must exclude exactly the same land, or national and local rates will not reconcile. Public enterprises (SNCF, OPH, etc.) stay in the SNF column and are taxable, which is consistent. Legally exempt private property (e.g. new social housing for 15–25 years) remains in the base, so the rate is slightly understated |
| 12 | Chambres d'agriculture, CRL, IdF DMTO, CSI | +345 / +100 / +47 / (unverified ≈ 250–300) | See §3 |

## 5. Open points resolved

1. **IFI 2024 and 2025.** Resolved from the primary source.
   - DGFiP Statistiques n° 33 (15/04/2025): 2,2 Md€, +11 %.
   - DGFiP Statistiques n° 45 (14/04/2026): 2,3 Md€, +8,0 %, 193 600 households.
   - The compte du logement's 2,64 Md€ was not located. The closest primary figure is the budget-receipt series (VM PLF 2026, line 1406): 2 739 M€ executed in 2024, 2 965 M€ revised 2025. The gap is therefore avis vs encaissements, not a scope difference. My inference is that rappels and late payments explain it, but the source does not say so.
   - The 2022 value in yields.py (2,1) is the CPO's; DGFiP n° 15 gives ≈ 1,8.
2. **Rental income.** Partly resolved.
   - The CPO lines are confirmed verbatim (printed p. 23). The 4,2 + 2,4 + 1,1 + 0,1 = 7,8 vs "8,3 Md€" gap is confirmed and unexplained in the text.
   - The CPO's scope is housing ("fiscalité du logement").
   - Whether the 1,1 Md€ of CSG is inside the 2,4 of PS cannot be determined from the CPO, and neither fits the 17,2 % arithmetic (§4, #7).
   - The SDES compte du logement 2024 report reached via WebFetch does not break out these lines.
   - Keep `status="reported"`. Do **not** add the CSG line until the split is known.
3. **Communal DMTO, 3 356 vs DGCL 3,1 Md€ (2023).** Resolved: the gap is Paris's communal tax.
   - DGCL encadré 2 gives Paris's "part communale (289 M€)" and DGCL's analysis uses Paris's departmental part only.
   - 3 356 − 289 = 3 067 ≈ 3,1. The small-commune fund is **not** the cause, and it is correctly included.
   - The same 289 is inside OFGL's departmental "DMTO avant péreq." for Paris, hence the double count (§2.1).
   - The small-commune fund does **not** double count with departmental DMTO. OFGL's aggregate definition lists only the departmental TPF/droit, the departmental additional tax and, for Paris, the communal tax. This is corroborated by the definition, not proven from accounts.
4. **TFPB 2025 and TSE/GEMAPI/TASA.**
   - The REI 2025 totals are confirmed from the API (40 157,3 + 2 619,5).
   - DGCL BIS 210 (page modified 28/05/2026) only says commune TFPB is "plus de 40 Md€" in 2025.
   - DGCL BIS 209 (via Maire-info, 12/05/2026) gives about 43,1 Md€ for all TFPB (+2,8 %). That is consistent with commune + EPCI + syndicates (42 961).
   - TSE + GEMAPI + TASA on FB = **709,6 M€** (2025) and 664,4 (2024), confirmed. With the FNB parts and syndicates the total is 922,6 M€.
5. **Agricultural and natural land (D6).** Not resolved.
   - Neither IP2028, IP2081 nor the 2025 Chiffres-clés isolate agricultural land.
   - "Autres actifs non produits" (1 982 Md€ end-2024; 1 866 end-2023) contains agricultural land among other non-produced assets. It is an upper bound only, not a usable figure.
   - The DRAAF Pays-de-la-Loire note points to Agreste national tables, which I did not reach.
   - Route: the INSEE detailed patrimoine account (AN.2112 "terrains cultivés"), or Agreste prix × SAU.
6. **LMNP / furnished lets (D7).** Not resolved; no yield found.
   - Searches returned only practitioner guides.
   - The CPO's wording ("IR lié aux revenus immobiliers") may or may not include BIC meublés.
   - Unverifiable. Keep D7 open.

## 6. Notes on what could not be checked

- Legifrance (CGI art. 1641 and 1647 V) was not read directly. The 2,37 % / 2,14 % rates are corroborated by Weblex. The 3 % TF frais rate is from my memory, consistent with REI E00.
- A small residual remains in reconciling the OFGL departmental aggregate with grand-livre account sums (≈ 140 M€ in 2024). I did not resolve it, and it does not change the corrections above.
- The PLF 2027 Voies et moyens (which would give 2025 executed IFI) was not reachable at the URL pattern tried.
