# House (maison individuelle) construction costs for LVTShift-FR: sourced recommendation (2025 €)

> Research note, October 2026. It builds on `construction-costs-2025.md` (§1, §6 caveat 5, sources S7–S12) and does not redo it. Tags [H1]… refer to §8. "Fetched live" = I downloaded the page or PDF on 2026-10-21/22 and read the figure myself. "Snippet" = seen only in a search-result summary. "Judgement" = my estimate, not a sourced number. The arithmetic is in `house_costs_calc.py`, next to this note; running it reproduces every figure.

---

## 0. Summary for a non-coder economist

- **The question.** The model values every building at the cost of building new collective social housing. For houses that looks too high in the Paris inner ring. The best official house cost is the SDES survey EPTB, which records what households who built a house in 2024 say it cost, per m² of *surface de plancher* (SDP).
- **Where the house cost comes from.** We start from the EPTB price per m² SDP. Five adjustments then put it on the model's basis:
  1. Index it from 2024 to 2025 €.
  2. Add the finishing works that most new houses leave to the household ("prêt à décorer").
  3. Add fees, insurance and studies.
  4. Add a premium for rebuilding on a tight urban plot.
  5. Convert from SDP to habitable area.
- **Result (2025 €, per habitable m², turnkey, building only, fees and 20 % VAT included):**

| Area | Central | Plausible range | Per true-gross m² (×0.82) | Current per habitable m² | Change |
|---|---|---|---|---|---|
| **Paris inner ring** (92/93/94, incl. Montreuil) | **2 550** | 2 100 – 3 050 | **2 100** (1 750 – 2 500) | 2 927 | **−13 %** |
| **Paris** intra-muros | **2 800** | 2 300 – 3 400 | **2 300** (1 900 – 2 800) | 3 232 | −13 % |
| **Lyon and Villeurbanne** | **2 950** | 2 500 – 3 450 | **2 400** (2 050 – 2 850) | 2 439 | **+21 %** |
| **Lyon Métropole ring** | **2 750** | 2 400 – 3 250 | **2 250** (1 950 – 2 650) | 2 256 | **+22 %** |

- **What this means.**
  - In the **Paris area** the hypothesis holds. A house costs about 13 % less to rebuild than the collective-housing figure implies, so land shares in house-dominated communes (Santeny, Périgny, Villepinte…) will rise.
  - In the **Lyon area** it does **not** hold. The local house survey (Rhône 2 127 €/m² SDP) is *dearer* than the collective-housing figure, so house values there would go *up*.
  - Lyon ending up above the Paris inner ring is partly a quirk of which houses happen to be in each sample (§6, caveat 2). If you would rather keep the usual Paris > Lyon ordering, the alternative is in §5.

---

## 1. EPTB 2024: the most local figures published (fetched live)

Cost "hors foncier" and average SDP for houses whose 2024 permit was in the survey [H1][H2]. The €/m² for each département is my own division: the page gives only euros and m², and the surfaces are rounded to the nearest m², so each ratio is only accurate to about ±0.5 %.

| Area | Houses | Mean cost € | Mean SDP m² | **€/m² SDP** | Note |
|---|---|---|---|---|---|
| 75 Paris | s | s | s | **s** | Suppressed ("secret statistique ou fiabilité insuffisante") |
| 92 Hauts-de-Seine | s | s | s | **s** | Suppressed |
| 93 Seine-Saint-Denis | 157 | s | 150 | **s** | Cost suppressed, surface published |
| 94 Val-de-Marne | 168 | 291 388 | 170 | **1 714** | Inner ring. Large houses, so cost per m² is low (scale) |
| 77 / 78 / 91 / 95 | 640 / 484 / 466 / 310 | 239 300 / 280 071 / 262 288 / 288 012 | 130 / 140 / 139 / 150 | 1 841 / 2 001 / 1 887 / 1 920 | Outer départements |
| **Île-de-France** | 2 296 | 266 356 | 143 | **1 863** (published) | 5th cheapest region |
| 69 Rhône | 629 | 289 216 | 136 | **2 127** | Département figure. The page does not say whether 69 includes the Métropole de Lyon (69M); I assume it does |
| **Auvergne-Rhône-Alpes** | 6 697 | 252 110 | 122 | **2 066** (published) | 3rd most expensive region |
| France | — | 225 500 | 118–119 | 1 914 | [H3] |

- **No EPTB 2025 yet.** `…/eptb/2025/ile_de_france/…` returns HTTP 404. The 2024 national release came out on 27/11/2025, so 2025 results are likely in late November 2026.
- **The SDES national page could not be read.** It was "en cours de mise à jour" when fetched, so the national figures are taken from the previous note [S12] and from a search snippet.

---

## 2. What the EPTB price includes and excludes

| Item | Status | Evidence |
|---|---|---|
| **VAT** | **De facto TTC.** Households cannot recover VAT and declare their contract price. | Inference, also Gemini's view. Only the land price is stated as TTC [H4][H5]. |
| **Basis of the price** | A *forecast* cost declared by the household (the Normandie report calls it "coût moyen prévisionnel déclaré par les particuliers"). It reflects 2024 quotes, not final accounts. | [H5] fetched live |
| **Builder (CMI) margin** | Included, since it is part of the contract price. This matches our basis: the SISAL "bâtiment" cost is also what is paid to contractors, so it includes their margin. Only a *promoteur's* margin is excluded from our basis, and that is irrelevant here. | Judgement |
| **Finishing works** | **Often excluded.** Only **27–44 %** of houses are delivered "totalement terminée". Houses from a constructeur are mostly "prêt à décorer, avec donc des coûts restant à venir": Normandie 27 % finished, Pays de la Loire 39 %, Hauts-de-France 29 % for all houses. The survey records "niveau de finition", but 64 % of that variable is imputed in IdF. | [H5][H6][H7][H4] fetched live |
| **External works** (fences, pools) | Excluded ("hors aménagement extérieur"). | 2025 questionnaire Q12 [H8], snippet only (the PDF download hit a maintenance page) |
| **VRD / viabilisation** | Excluded from the land price. Whether connections are in the house price is not stated. Our basis excludes VRD anyway. | [H4][H8] |
| **Architect / fees** | An architect is compulsory only above **150 m² SDP** (it was 170 m² in the 2012 brochure [H9], and the 2016 LCAP law lowered it, *from memory*). Constructeur houses include design and site supervision. Insurance (dommages-ouvrage) and the G2 soil study are only partly in the contract. | [H9], judgement |
| **Garage, cellar, unconvertible attic** | The **cost** of these is in the price, but their **area** is excluded from SDP. So the €/m² SDP already spreads the annex cost over the living floor area. | [H2][H5] definitions, fetched live |
| **Surface** | SDP, measured "au nu intérieur des façades". Deductions: embrasures, stair voids, parking, unconvertible attics, areas ≤1.80 m high. The 10 % deduction for internal circulation applies **only to collective housing**, and so do the cellar and technical-room deductions. | [H9] DGALN/DHUP brochure, fetched live |

**By who manages the build** (€/m² SDP; share of houses delivered fully finished), from DREAL tables [H5][H6][H7]:

| | Constructeur | Architecte | Self-managed (particulier) |
|---|---|---|---|
| Normandie | 1 809 (27 %) | 2 059 (68 %) | 1 523 (48 %) |
| Pays de la Loire | 2 016 (39 %) | 2 380 (63 %) | 1 733 (51 %) |
| Hauts-de-France | 1 849 (s) | 2 108 (39 %) | 1 467 (48 %) |

Architect-led houses cost **+14–18 %** per m² more than constructeur houses. The IdF and ARA pages do not publish this table.

---

## 3. Indexation to 2025 (fetched live, INSEE BDM [H10][H11])

- **BT01** annual mean: 2024 131.22, 2025 133.01, a factor of **×1.014**. Latest value: Aug-2026 139.4.
- **ICC** quarterly: 2024 Q1–Q4 2 227 / 2 205 / 2 143 / 2 108, mean 2 171. 2025 Q1–Q4 2 146 / 2 086 / 2 056 / 2 058, mean 2 087. That is a factor of **×0.961**. Since 2022 the house component of the ICC is itself estimated from EPTB data [H12].
- **Central ×1.014 (BT01), range 0.961–1.03.** The ICC fall reflects lower builder margins in a weak market. That is real, but it is a market-cycle effect rather than a change in the cost to rebuild.

---

## 4. SDP to habitable area for houses

- **Definitions.**
  - Surface habitable (CCH R.156-1) = "surface de plancher construite, après déduction des surfaces occupées par les murs, cloisons, marches et cages d'escaliers, gaines, embrasures". Cellars, garages, unconvertible attics and areas <1.80 m are excluded [H13, snippet].
  - SDP for a *house* deducts much less: it keeps interior walls, partitions and the steps on the lowest floor, and keeps cellars and storerooms (celliers), which are deducted only in collective housing [H9].
- **What goes into the habitable ÷ SDP ratio** (judgement):
  - interior partitions and load-bearing walls: 5–8 % of SDP;
  - staircase footprint: 2–3 % in a two-storey house;
  - closed cellars or storerooms counted in SDP: 0–5 %.
  - Together that gives **0.86–0.92**, central **0.90**. One practitioner range of 0.85–0.92 was seen in a search snippet with no source, and is not relied on.
- **Upper bound raised to 0.97.** Households sometimes declare habitable area instead of SDP. The DREAL Normandie text itself calls the EPTB figure "surface habitable projetée" [H5]. Where that happens, the ratio is close to 1.
- **Consistency with the model's 0.82 (habitable ÷ true gross).**
  - True gross adds the external walls. With a 30–40 cm insulated wall, SDP ÷ gross is about 0.85 for a two-storey house of ~70 m² per floor and about 0.89 for a single-storey 130 m² house. Central 0.87 (judgement).
  - So habitable ÷ gross ≈ 0.90 × 0.87 ≈ **0.78 (0.73–0.84)**.
  - **The model's 0.82 sits inside that range, at the upper side.** It is acceptable. Note that the per-habitable figure (§5) is the one that matters. The per-gross figure is only the parameter ×0.82 that reproduces it.

---

## 5. Recommendation and arithmetic

Chain: `€/m² habitable = EPTB €/m² SDP × index × finishing × fees × site premium ÷ (habitable/SDP)`. Central (low–high):

- **Index:** 1.014 (0.961–1.03).
- **Finishing:** 1.06 (1.03–1.10). That is 56–73 % of houses unfinished × reserved works worth 8–12 % of the contract.
- **Fees, insurance, soil study:** 1.05 (1.00–1.10) in urban areas, where houses are larger and more often architect-led; 1.03 (1.00–1.06) in the Lyon ring.
- **Site premium (infill, modern equivalent, *not* reproduction):** Paris 1.20 (1.10–1.35); inner ring 1.10 (1.00–1.20); Lyon city 1.10 (1.00–1.20); Lyon ring 1.05 (1.00–1.15).
- **Annex allowance:** 1.00 (1.00–1.05).
- **Habitable ÷ SDP:** 0.90 (0.97–0.86).
- **Bases:** IdF 1 863 (range 1 714–2 001) for Paris and the inner ring; Rhône 2 127 (range 2 066–2 250) for Lyon.

| Step | Paris | Inner ring | Lyon + Villeurbanne | Lyon ring |
|---|---|---|---|---|
| EPTB €/m² SDP, 2024 | 1 863 | 1 863 | 2 127 | 2 127 |
| × 1.014 index | 1 889 | 1 889 | 2 157 | 2 157 |
| × 1.06 finishing | 2 002 | 2 002 | 2 286 | 2 286 |
| × fees (1.05 / 1.05 / 1.05 / 1.03) | 2 103 | 2 103 | 2 400 | 2 355 |
| × site premium (1.20 / 1.10 / 1.10 / 1.05) | 2 523 | 2 313 | 2 641 | 2 473 |
| ÷ 0.90 → **per habitable m²** | **2 803** | **2 570** | **2 934** | **2 747** |
| Outer bound (all lows / all highs) | 1 924 – 4 110 | 1 749 – 3 654 | 2 108 – 4 108 | 2 108 – 3 794 |
| Plausible range (geometric midpoint between central and outer) | 2 322 – 3 395 | 2 120 – 3 064 | 2 487 – 3 472 | 2 407 – 3 229 |
| **× 0.82 → per true-gross m² (model parameter)** | **2 299** | **2 107** | **2 406** | **2 253** |

These are rounded in §0. The per-gross figures replace, for houses only, the collective values of 2 650 / 2 400 / 2 000 / 1 850.

**Alternative for Lyon, if you want to keep Paris > Lyon.** Use the regional ARA figure (2 066) and no site premium in the ring:
2 066 × 1.014 × 1.06 × 1.03 ÷ 0.90 ≈ **2 540 per habitable m²** (2 080 gross). Lyon city would then be ≈ 2 540 × 1.05/1.03 × 1.10 ≈ 2 850 (2 340 gross). Both remain above the current collective-based values.

---

## 6. Caveats (ranked)

1. **The finishing uplift is the most important and least-sourced step.** The share of houses delivered unfinished is sourced (27–44 % fully finished). The euro value of the reserved works (8–12 %) is judgement, and Gemini agreed. Each ±4 points on it moves every figure by ±4 %.
2. **Sample composition, not construction cost, drives the regional gap.**
   - EPTB covers *new diffuse* houses: in IdF mostly outer départements (77/78/91/95: 1 900 of 2 296 houses); in Rhône probably bespoke houses on scarce, hilly land (Monts d'Or, west Lyon), per Gemini, unverified.
   - This is why Lyon comes out dearer than the Paris inner ring, the opposite of the collective-housing evidence (SISAL: IdF +40 % over ARA).
   - Treat the Lyon figures with more caution, and consider the §5 alternative.
3. **Département 94 points the other way from a "petite couronne premium".** Its EPTB is 1 714 €/m² on 170 m² houses: the cheapest in IdF per m², though the largest houses. Large houses are cheaper per m² because fixed costs (kitchen, bathrooms, foundations) are spread over more area. That cost advantage does not carry over to the smaller pavillons that make up most of the existing stock. Hence the +10 % central premium, not 0 and not 15 %.
4. **SDP or habitable as declared.** If households report habitable area, the ratio is ≈0.97 and every figure falls by about 7 %.
5. **EPTB is a forecast cost** taken at permit stage. Final costs may overrun it. Self-managed builds (22–29 % of houses) bring the average down by ~15–20 % per m², because households coordinate the trades themselves and absorb unpriced labour. That is a further reason to read the EPTB average as a slight *under*statement of a professional turnkey rebuild.
6. **Demolition is excluded.** Asbestos removal and demolition, roughly 100–200 €/m² (Gemini, unsourced), are a site cost. This is consistent with leaving land and VRD out of the building value.
7. **No 2025 EPTB yet.** It is expected in late November 2026. When it lands, update the base figures and drop the index step.

---

## 7. Gemini review (`gemini-4-argon`, 2026-10-21/22) and how I weighed it

Gemini's replies were not kept in the repository; the points are summarised below.

| Gemini point | Decision and reason |
|---|---|
| (a) The household's reserved works (~10–12 %) and studies/insurance/architect (~3–5 %) mean adding +15–20 % to reach turnkey. | **Partly accepted.** The 10–12 % applies only to the 56–73 % of houses delivered unfinished, so the weighted effect is ~6–8 %. Fees +3–5 % are accepted. Combined central: ×1.11 urban, ×1.09 Lyon ring. The high end (×1.21) covers Gemini's figure. |
| (b) Index +1.5–2 % for 2024→2025. | **Accepted at +1.4 %** (BT01, fetched). The ICC (−3.9 %) sets the low end. |
| (c) Habitable ÷ SDP for houses ≈ 0.90–0.92. In its first reply it said 0.85–0.88 technically, with the declaration confusion pushing the figure up. | **Accepted 0.90 central.** I widened the range to 0.86–0.97 to cover both the technical value and households declaring habitable area. |
| (d) No meulière reproduction premium; but a +10–15 % spatial premium for the petite couronne. | **No-reproduction: accepted.** **Spatial premium: accepted at +10 % (0–20 %).** It is not higher because the dept-94 figure (1 714) contradicts "IdF is dragged down by outer départements" (caveat 3). Gemini's first reply also suggested basing the inner ring on dept 78 (2 001) and reaching 2 900–3 100. I **rejected** that: 78 is an outer département, and its labour-cost argument was unsourced. |
| (e) DVF prices include garages and basements that SDP excludes, so add ~+10 % to cost. | **Rejected for the central value; up to +5 % in the high range.** The EPTB contract price *already* includes the cost of the garage and cellar while excluding their area. The €/m² SDP is therefore already loaded with annex costs, and +10 % would double-count. The remaining real gap is the full sous-sol common in older pavillons, which new builds rarely have. |
| Demolition should be excluded explicitly. | **Agreed** (caveat 6). |
| Lyon ring above the Paris inner ring is a statistical artefact. | **Partly agreed** (caveat 2). The §5 alternative is offered, but I kept the local Rhône figure as central because it is the most local *sourced* number. |

---

## 8. Sources (accessed 2026-10-21/22)

- **[H1]** SDES/DRIEAT, EPTB 2024 Île-de-France, ch.3, dept table. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/ile_de_france/caracteristiques_maisons_contruites.html (fetched live)
- **[H2]** SDES/DREAL, EPTB 2024 Auvergne-Rhône-Alpes, ch.3, dept table. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/auvergne_rhone_alpes/caracteristiques_maisons_contruites.html (fetched live)
- **[H3]** SDES, *Le prix des terrains et du bâti pour les maisons individuelles en 2024*. https://www.statistiques.developpement-durable.gouv.fr/le-prix-des-terrains-et-du-bati-pour-les-maisons-individuelles-en-2024 (**not fetched**: site under maintenance; figures from [S12] of the earlier note and a search snippet)
- **[H4]** SDES, *EPTB – Méthodologie de l'enquête* (Nov. 2025): coverage, imputation rates for "niveau de finition". https://data.statistiques.developpement-durable.gouv.fr/dido/api/files/50fd9f39-9e4a-44e3-9265-e51989c6c641 (fetched live)
- **[H5]** DREAL Normandie, *Les prix du terrain et du bâti… en 2024* (publ. 14/01/2026): table 3.2 by maître d'oeuvre, finishing text, §5.2 definitions. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/normandie/EPTB_prix_terrain_bati_Normandie_2024.pdf (fetched live)
- **[H6]** DREAL Pays de la Loire, EPTB 2024 ch.3. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/pays_de_la_loire/caracteristiques_maisons_contruites.html (fetched live)
- **[H7]** DREAL Hauts-de-France, EPTB 2024 ch.3. https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/hauts_de_france/caracteristiques_maisons_contruites.html (fetched live)
- **[H8]** SDES, EPTB 2025 questionnaire (Q6 land, Q12 house "hors aménagement extérieur"). https://www.statistiques.developpement-durable.gouv.fr/media/8463/download (**not fetched**: maintenance page; via search snippet)
- **[H9]** DGALN/DHUP, *La réforme de la surface de plancher de référence en urbanisme* (Jan. 2012). https://www.excideuil.fr/sites/excideuil.fr/IMG/pdf/reforme_de_la_surface_de_plancher.pdf (fetched live; the ain.gouv.fr copy was under maintenance)
- **[H10]** INSEE BDM, BT01 (idbank 001710986). https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001710986 (fetched live)
- **[H11]** INSEE BDM, ICC (idbank 000008630). https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/000008630 (fetched live)
- **[H12]** INSEE, ICC methodology (hedonic variables incl. wall/floor coverings, paint, kitchen). https://www.insee.fr/fr/metadonnees/source/indicateur/p1626/documentation-methodologique (fetched live). Its use of EPTB since 2022 is from a search snippet of the ICC process page.
- **[H13]** CCH art. R.156-1 (surface habitable), quoted in https://www.construires.fr/surface-de-plancher/surface-habitable/ and Assemblée nationale amendments (via snippet; Legifrance not fetched)
- **[H14]** Pôle Habitat FFB, press kit 27/02/2025: CMI average house price 207 000 € / 113 m² **SDP** in 2024 (≈1 832 €/m²); 2023 216 000 € / 116 m² (≈1 862); source CGI Bâtiment/Caron Marketing. https://www.polehabitat-ffb.com/media/dossier-de-presse-pole-habitat-ffb-2025-02-27.pdf (fetched live). 2025: 198 000 € (−4.3 %) per Batiweb/Économie Matin and https://batiamenagement.fr/nos-conseils-immobiliers/quelles-perspectives-sur-le-marche-de-la-maison-individuelle-pour-2026/ (fetched live). The 2026 press kit was not reachable.
- **[H15]** Gemini `gemini-4-argon`, 2026-10-21/22 (model output, not a source of fact).

**Corroboration summary.**
- The FFB/Caron Marketing national builder-contract price is **≈1 830 €/m² SDP (2024)** and ≈1 770 (2025, using an unverified 112 m²). That is ~4 % below EPTB national (1 914). Builder contracts are mostly "prêt à décorer" and exclude household-procured items, which is consistent with the finishing uplift.
- No regional FFB figure, no CAPEB figure and no Untec figure was found openly. Untec and Batiprix are paywalled.
- Commercial constructeur price bands for IdF (1 500–2 000 €/m², simulateur-prix-construction-maison.fr, snippet) are consistent with EPTB but are marketing figures, not statistics.
