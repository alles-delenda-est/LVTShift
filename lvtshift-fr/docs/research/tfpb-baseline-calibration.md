# TFPB baseline by property category: open data for calibration (REI 2025)

> **Adopted (branch `baseline-weights`).** The model uses option (a), per-commune
> calibration (§7), with the professional proxy scaled by **k = 2.5** (§9.4) and
> industrial + professional capped at **75 %** of the base, both shares scaled
> down proportionally (`config.BASELINE_MODEL`, `run_pipeline._baseline_weights`;
> see METHODOLOGY.md §3.5). k = 1.0 is reported as the lower bound. The probe
> script `tfpb_baseline_probe.py` differs from the pipeline: it defaults to
> `--pro-scale 1.0` and caps professional + industrial at **90 %** by trimming
> the professional share only, so its output does not reproduce the payload
> targets unless run with `--pro-scale 2.5`, and even then not in communes above
> 75 %. The "floor housing at residential floor × 0.5" guard in §9.4 was not
> adopted.

Research dates 2026-10-22 and 23. Each figure cites a source in §8 by tag, e.g. [T1]. Markers:
**fetched live** (I downloaded the page, file or API myself and read the value), **snippet** (seen
only in a search-result summary), **judgement** (my inference). The probe script is
`tfpb_baseline_probe.py` next to this note. It takes an output directory, fetches only public
aggregates from OFGL and writes a CSV of the split for any list of INSEE codes.

## 0. Summary for a non-coder economist

- **No open source publishes a commune's TFPB base split into housing, business premises and
  industry.** This holds for both the OFGL `rei` dataset and the full DGFiP REI (1 044
  variables) [T1, T2, T3]. Fichiers fonciers/MAJIC, which hold that detail, are not open.
- **Two REI lines let us rebuild the split per commune.** This is a reconstruction, not a
  published figure.
  1. **Industrial base, near-exact.** The state compensates each commune for halving
     industrial values in 2021 (`WC75`). By law, the compensation equals the base lost
     multiplied by the 2020 rate [T4]. The base lost equals the base that remains, so
     `WC75 ÷ rate₂₀₂₀` gives the commune's current industrial (art. 1499) TFPB base. A second
     variable, the CFE industrial abatement `X503`, confirms it within about 0–25 %.
  2. **Business-premises base, approximate.** The CFE (business property tax) uses the same
     rental values. Its gross base for non-industrial premises (`T29_1`, or `T29 − X503`)
     divided by 2 approximates the TFPB base of locaux professionnels. This is a proxy, with
     known biases (§3.3).
  3. **Housing and other = what remains.** One TFPB rate applies to all categories in a
     commune, so each category's share of the base is also its share of the produit, up to
     the RVLLP lissage line.
- **Examples, 2025 (share of the commune's TFPB base) [T1, own computation]:**

| Commune | Industrial (art. 1499) | Professional (CFE proxy) | Housing + other |
|---|---|---|---|
| Saint-Fons (69199) | **26.1 %** | 13.3 % | 60.7 % |
| Saint-Priest (69290) | 12.6 % | 15.8 % | 71.6 % |
| Vénissieux (69259) | 11.5 % | 11.0 % | 77.5 % |
| Santeny (94070) | 10.3 % (see §6) | 8.9 % | 80.8 % |
| Vitry-sur-Seine (94081) | 8.7 % | 7.1 % | 84.2 % |
| Saint-Denis (93066) | 4.7 % | 14.5 % | 80.8 % |
| Nanterre (92050) | 3.2 % | 17.7 % | 79.1 % |
| Lyon (69123) | 1.6 % | 10.9 % | 87.5 % |
| Paris (75056) | 1.4 % | 9.9 % | 88.6 % |
| Villepinte (93078) | **0.2 %** | 13.9 % | 85.9 % |

- **Update 2026-10-23 (§9).**
  - The 0.5 factor and the 2020 rate are both confirmed from the legal texts.
  - The industrial method matches the Cour des comptes national 5.7 % exactly.
  - The CFE professional proxy **undercounts about 2.5×** nationally: 8.6 % against the
    Cour's 22–23 %.
  - So the professional column in the table below is a **lower bound**. Central case: scale
    it by k = 2.5 (Paris ≈ 25 %).
- **Recommendation: (a) per-commune calibration.** For each commune, scale the modelled
  industrial, commerce/office and residual floor-area bases so that each category's share of
  the produit matches the shares above. Use (b)/(c) weights only as a within-category prior
  and as a fallback. Villepinte shows why this matters: a "logistics town" pays almost no
  *industrial* TFPB, because warehouses are mostly valued as locaux professionnels (DEP).
  Uniform national weights would get this wrong.

## 1. What the REI carries (question 1)

**OFGL `rei`** (`https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei`, fetched live)
[T1]:
- **Years:** only 2024 and 2025 (`group_by=annee`).
- **Fields:** `annee, libreg, libdep, gfp_ept, libcom, optepci, forjepci, strate,
  dispositif_fiscal, categorie, destinataire, varlib, valeur, secret_statistique, z08, reg,
  dep, idcom, sirepci, var`.
- **Format:** long, one row per (commune, year, variable). `var` is the DGFiP code.
- **FB categories:** Base, Compensation, Degrevement, Exoneration, Lissage, Produit, Taux.
- **FB variables found:** E11/E12/E13/E14 (base, rate, montant réel, number of articles),
  E16/E16NB (lissage), E21–E36 (syndicat, GFP), E00 (state fees), G13–G74, and the WC*/WE*
  compensations.
- **No variable splits FB bases** by habitation / professionnel / industriel, and none gives
  "bases des établissements 1499". The DGFiP trace file of the full REI 2025 (1 044
  variables) confirms the same FB list [T2, T3].

**Relevant variables (2025 values, fetched live):**

| var | label (abridged) | Villepinte | Santeny | Saint-Fons | Paris |
|---|---|---|---|---|---|
| E11 | FB commune base nette | 69 316 322 | 10 534 788 | 27 775 419 | 8 980 537 164 |
| E12 | FB taux net % | 48.84 | 29.92 | 36.20 | 20.50 |
| E13 | FB montant réel € | 33 822 711 | 3 141 206 | 10 053 788 | 1 840 896 539 |
| E16 / E16NB | RVLLP lissage € / no. of articles | −31 265 / 260 | −10 787 / 86 | −892 / 398 | −110 534 / 86 966 |
| WC75 | Alloc. comp. abattement 50 % VL EI (commune) | 66 998 | 325 919 | 2 620 765 | 17 143 138 |
| X503 | CFE abattement 50 % EI (méthode comptable), on commune territory | 184 887 | (blank) | 9 862 492 | 0 |
| ZX3 | no. of EI articles with X503 | 7 | (blank) | 27 | – |
| T29 | CFE bases brutes totales | 19 444 085 | 1 875 746 | 17 239 799 | 1 934 880 949 |
| T29_1 / T29_3 | CFE gross base: locaux pro / EI (méthode comptable) | – | – | – | 1 786 942 370 / 138 167 747 |

**Other related variables:**
- `TSEFBDOTVLEI`, `SYNFBDOTVLEI` and `GEMAPIFBDOTVLEI` are dotations for the EI halving.
  The GEMAPI value is 14 038 in all three MGP communes, which shows it is duplicated at
  group level and is not a commune figure.
- `WE75` (EPCI) is "dupliquée sur toutes les communes membres" [T3]. Do not use it per
  commune.
- `T29_1…T29_6` split CFE gross bases by premises type: locaux pro, habitation, EI comptable,
  barème, non bâti, other. They are filled for only **169 communes nationwide**. Within our
  area these are Paris, Lyon, Caluire, Givors, Vénissieux, Saint-Priest, Meudon, Saint-Cloud,
  Saint-Denis, Charenton, Créteil and Vitry (full REI 2025 CSV, fetched live [T2]).

**Lissage and planchonnement.**
- E13 = E11 × E12 + E16 (lissage) ± rounding. The lissage spreads the 2017 RVLLP shock over
  10 years and is reported up to 2025 [T3].
- In our communes it is tiny: under 0.1 % of produit.
- E16NB counts the communal TFPB articles that carry a lissage. It is a rough lower bound on
  the number of professional premises that existed in 2017.
- Planchonnement and the neutralisation coefficient are not published per commune in the REI.

**Vintage.** REI 2025 was published on OFGL on 2026-05-29 and on data.gouv.fr in May 2026
[T1, T2]. It reflects 1 January 2025 situations, so we use 2025 with roughly a 17-month lag.
Licence: Licence Ouverte v2.0 (DGFiP). OFGL redistributes it under the same terms
(judgement; the OFGL metadata licence field is empty).

## 2. The industrial base from WC75 (method, verified)

**The law.** LFI 2021 art. 29 III A 2 (Légifrance, fetched live [T4]):
- The compensation equals "la perte de bases résultant, chaque année, de [l'abattement]"
  × "le taux de TFPB appliqué en 2020 dans la collectivité".
- For communes, the rate is "majoré[] des taux appliqués en 2020 dans les départements".
- Métropole de Lyon communes use "le taux appliqué en 2014 au profit du département du
  Rhône" (11.03 %; REI 2020 E42 for dep 69, fetched live [T5]).
- The same article sets art. 1499 rates at 4 % for land and 6 % for buildings, previously
  8 % and 12 %.

**The formula.** The halving removes exactly half of each value, so lost base = remaining
base (judgement). Therefore

`B_EI(2025) = WC75 / (t_commune,2020 + t_département,2020)`

The 2020 rates come from OFGL `base-fiscale-simplifiee` (exer=2020, TFPB, Commune and
Département), fetched live [T6]. They agree with REI 2020: Villepinte 31.55 + 16.29;
Santeny 16.17 + 13.75; Saint-Fons 25.17 + 11.03; Paris 13.50 + 0 [T5].

**Trap.** For Métropole communes, `base-fiscale-simplifiee` gives 11.58 as the "département"
rate, which is the Métropole's 2020 rate. The law requires 11.03. The probe forces 11.03.

**Cross-check against an independent CFE line.**
- The CFE industrial base is VL × (1 − 30 %) under art. 1467. TFPB is VL × 50 %.
- So `X503 ≈ B_EI × 2 × 0.7`.
- Observed ratio X503 / implied: Saint-Fons 0.97, Nanterre 0.96, Villepinte 0.94,
  Saint-Priest 0.91, Meudon 0.88, Créteil 0.82, Vitry 0.75, Vénissieux 0.73, Lyon 0.61,
  Saint-Denis 1.13.
- Ratios below 1 are expected. CFE falls on occupants, so vacant or exempt-occupier
  industrial sites drop out (judgement).
- Agreement this close from two independent tax lines makes the industrial share the most
  solid figure in this note.

**Scope.** It covers only establishments valued by the *comptable* method (art. 1499). Small
industrial firms valued by the tariff method (art. 1500), and industrial premises that
belong in locaux pro, are not halved. They sit in the professional or residual bucket
(judgement, from the wording of WC75 in [T3]).

## 3. Professional-premises base from the CFE (proxy)

**3.1 Definition.**
- `T29_1` is the "montant total des bases brutes de CFE (locaux professionnels, commerciaux
  et assimilés)" [T3].
- Where it is blank, use `T29 − X503`. Over the 12 communes with T29_1, T29_3 ≈ X503
  (97–100 % outside Paris and Lyon), so the subtraction leaves almost exactly the
  non-industrial CFE base.
- CFE bases are full rental values. TFPB bases are VL × 50 %. Hence `B_pro ≈ 0.5 × CFE_pro`.

**3.2 Results.** See the table in §0. The professional share ranges from 7 % to 18 % of the
TFPB base in the sample.

**3.3 Known biases (all judgement):**
1. **CFE falls on the occupant; TFPB falls on the owner.** Vacant offices and shops pay TFPB
   but no CFE, so the proxy understates them, most in high-vacancy office markets such as
   La Défense-Nanterre and Saint-Denis.
2. **Premises used by CFE-exempt occupiers drop out of CFE gross bases.** Examples are
   associations and some public bodies. Their owners may still pay TFPB.
3. **The neutralisation coefficients differ by tax.** RVLLP values are multiplied by one
   coefficient per tax and per collectivity, so that the professional share of each base is
   unchanged by the 2017 reform. The TFPB-commune and CFE-EPCI coefficients are computed on
   overlapping but different premises sets, so the ratio is close to 1 but not exactly 1.
   The coefficients are not in the REI.
4. **Paris looks low.** Professional premises come out at 9.9 % of the TFPB base, which is
   surprising for Paris's office stock. This should be validated against an independent
   figure before we rely on it. Neither the OFGL *Cap sur n°20* note on business tax
   contributions [T9] nor the impots.gouv technical sheets could be fetched, because the
   gouv.fr sites were in maintenance.
5. **T29_2** (habitation used professionally) is small. In Paris it is €9.6 M against
   €1.79 bn for locaux pro.

## 4. Other open sources (question 2)

| Source | Per-commune category split? | Status |
|---|---|---|
| DGFiP REI 1982–2025 zips on data.gouv.fr [T2] | No FB split; CFE T29_x for 169 communes | fetched live |
| DGFiP *Tarifs des locaux d'habitation 2024* (`descriptif-tarifs-des-locaux-d-habitation_2024`) [T7] | 1970 VL tariffs €/m² by category 1–8 per commune; not a base | fetched live |
| DGFiP *Fichiers des locaux et des parcelles des personnes morales* [T8] | One row per premises with legal-person owner name and SIREN; no VL | metadata fetched live; **not downloaded, by instruction** |
| Cerema Fichiers fonciers / DV3F | Restricted (convention); open data.gouv items are DREAL parcel aggregates (2016, WFS, licence "notspecified") | search fetched live; no open commune VL-by-category aggregate found |
| OFGL *Cap sur n°20* [T9], DGCL *Collectivités locales en chiffres*, impots.gouv RVLLP pages | National or departmental shares at most | **not fetched**: gouv.fr maintenance page (2026-10-22/23) |
| Fipeco *Impôts locaux* (2025) [T10] | National only: local taxes fall 55 % on households, 34 % on firms, 11 % on public bodies; TFPB €43.1 bn in 2025 | fetched live |

**MAJIC open extracts.** None exist with values. MAJIC is restricted, and the open
"personnes morales" file carries no rental values. **Fichiers fonciers commune aggregates:**
I found no open Cerema aggregate of VL by local type. The commune-level indicators that
Cerema publishes openly concern land use, not tax bases (judgement; not exhaustively
searched after the search quota ran out).

## 5. Per-m² tariffs from the literature (question 3): weak and only partly verified

**Housing (1970 VLC, fetched live [T7]).** Weighted-surface tariffs for 2024, in €/m² before
the statutory update coefficients:

| Commune | Flats AA | Houses MA | Outbuildings DA |
|---|---|---|---|
| Villepinte | 5.08–7.17 (cat. 4–7) | 4.51–7.17 | 2.74–6.86 |
| Santeny | 5.14–6.48 (AA) | 4.42–8.31 (MA, cat. 2–8) | – |
| Saint-Fons | 2.29–6.48 (AA) | 2.55–7.62 (MA) | – |

Paris is stored under its arrondissement codes; the `code_commune=56` query returns nothing.
These tariffs must still be multiplied by the actualisation and revaluation coefficients
and by weighted surface (dependencies, equivalences), so they do not translate directly into
€ of base per m² of BD TOPO floor area.

**Professional premises (RVLLP).** Departmental grids by sector and category (MAG, BUR, DEP,
ATE, ...) are published in each préfecture's RAA (recueil des actes administratifs). The
only figure seen: Hauts-de-Seine 2023, BUR1 €154.5–428 /m² by sector (**snippet**, RAA of
2 December 2022 [T11]). The RAA PDFs (92, 75) and the impots.gouv tariff service returned a
maintenance page.

**Not established.** Typical pondération coefficients for storage and parking (in the
RVLLP, reserves and parking are weighted below the main area; judgement) and 1970-to-2025
cumulative coefficients. A defensible *national* ratio of "TFPB per m² for office/shop,
warehouse and industry relative to housing" is **not** established here.

**Recommended route instead (judgement).** Derive ratios from §2–3 per commune:
`w_cat = (B_cat / A_cat) / (B_resid / A_housing)`, with A the BD TOPO floor area by usage.
Then pool by département where communes have little business floor area. This is option
(b), but built from bases rather than tariffs.

## 6. Mapping DGFiP categories to BD TOPO usages (question 4, judgement)

| DGFiP | Legal basis | Likely BD TOPO usage | Where they disagree |
|---|---|---|---|
| Local d'habitation | art. 1496, 1970 VLC | Résidentiel; Annexe (garages and cellars are housing dependencies) | Social housing exemptions (WC12/WC76) shrink the housing base; mixed shops at ground floor carry both |
| Local professionnel | art. 1498, RVLLP | Commercial et services; Industriel when it is a warehouse/workshop without heavy equipment (DEP, ATE); Sportif (SPE); some Indifférencié (clinics, private schools) | Logistics sheds tagged "Industriel" in BD TOPO are usually DEP here: Villepinte is 0.2 % EI despite large sheds |
| Établissement industriel, comptable | art. 1499 | Industriel; sometimes Commercial et services | Big automated warehouses, data centres and energy plants can be 1499 even when BD TOPO says commercial; firm-owned stores can be 1499 by caselaw on "rôle prépondérant des installations techniques" |
| Industrial, tariff method | art. 1500 (small firms) | Industriel | Not halved, so it falls in the "pro/residual" bucket of §2–3 |
| Exempt | art. 1382 (public non-productive), farm buildings | Indifférencié (schools, hospitals), Agricole | Floor area with zero base; exclude it before calibrating |

**Santeny anomaly.** The industrial base is 10 % of the commune base (€1.09 M) but there is
no CFE X503 or ZX3. A single large art. 1499 site with an exempt or absent occupier, or
statistical secrecy, is likely. Check the parcels before trusting this commune's split.

## 7. Recommendation (question 5)

1. **(a) Per-commune calibration to REI-reconstructed totals. Feasible now; strongest.**
   - **Fetch:** OFGL `rei` vars `E11, E13, E16, WC75, T29, T29_1, T29_3, X503, ZX3` for the
     188 communes (one API call per commune, or one `where idcom in (...)`), plus OFGL
     `base-fiscale-simplifiee` 2020 TFPB rates.
   - **Updates:** annually in May–June, with a lag of about 17 months.
   - **Licence:** Licence Ouverte v2.0.
   - **Method:** set the modelled industrial share to the WC75 share, the commerce/office
     share to the CFE proxy, and the rest to housing and other. Exempt categories (farm,
     public) get zero.
   - **Confidence:** high for industry, medium for professional premises.
2. **(b) Per-département weights.** Pool the (a) results by département (75, 92, 93, 94,
   69) to give €-base per m² ratios. Use them for communes with secrecy or anomalies (blank
   X503, very small business floor area). The tariff grids themselves need RAA scraping,
   which was blocked during this research.
3. **(c) National literature weights.** Use only as a last resort. No defensible verified
   per-m² ratio was found.
4. **Before adopting (a):** validate the professional proxy against one independent figure,
   for example a Paris or Lyon budget document giving the business share of TFPB. Store the
   probe output with the REI vintage.

## 9. Follow-up checks (2026-10-23)

### 9.1 The 0.5 factor: confirmed, applies to all built property

**Art. 1388 CGI** (Légifrance, version in force since 11 January 1980, read for 23 October
2026, fetched live [T13]):

> « La taxe foncière sur les propriétés bâties est établie d'après la valeur locative
> cadastrale de ces propriétés […] conformément aux principes définis par les articles 1494
> à 1508 […] sous déduction de 50 % de son montant en considération des frais de gestion,
> d'assurances, d'amortissement, d'entretien et de réparation. »

- Articles 1494–1508 cover housing (1496), locaux professionnels (1498), industrial
  establishments (1499–1501), and the rest.
- So the 50 % deduction applies to **every** propriété bâtie, not only housing. Gemini's
  claim is wrong.
- **CFE side:** art. 1467 takes the full rental value, with a 30 % reduction for 1499
  industrial premises only, and no 50 % deduction (BOFiP/CMS summaries, **snippet** [T14]).
  The REI data agree: X503 ≈ 2 × 0.7 × the TFPB industrial base (§2).
- **Keep `B_pro ≈ 0.5 × CFE_pro`.**

### 9.2 WC75 rate year: 2020, not 2017

LFI 2021 art. 29 III A 2 (Légifrance, fetched live [T4]):
- The compensation equals the lost base « par le taux de taxe foncière sur les propriétés
  bâties appliqué en 2020 dans la collectivité territoriale ».
- « Les taux à prendre en compte pour les communes […] sont majorés des taux appliqués en
  2020 dans les départements ».
- For Métropole de Lyon communes, « le taux appliqué en 2014 au profit du département du
  Rhône ».

There is no 2017 rate anywhere in the article. Gemini's claim is wrong.

**Empirical confirmation (own computation, [T2], [T5]).** Applying `WC75 / (t_com,2020 +
t_dep,2020)` to all 34 955 communes, using REI 2025 and the REI 2020 rates (14 communes had
no 2020 rate), gives a national industrial share of **5.7 %** of the TFPB base. The Cour des
comptes reports industrial premises at **5.7 % of TFPB receipts in 2021** [T15].

### 9.3 Open RVLLP tariffs and coefficients de localisation (Gemini's suggestion)

- No open dataset of RVLLP sector tariffs, sector maps or coefficients de localisation was
  found on data.gouv.fr (searches "tarifs locaux professionnels", "secteurs locatifs",
  "révision valeurs locatives", "RVLLP") or on data.economie.gouv.fr (fetched live). One
  data.gouv.fr search ("coefficient de localisation") returned no readable response, so it
  was not checked.
- Tariffs are published as **PDF decisions in each préfecture's RAA**, one per département
  per year (search results, **snippet** [T11]). The impots.gouv tariff service was in
  maintenance.
- Per-parcel sector assignment and coefficients de localisation sit in MAJIC/fichiers
  fonciers, which are restricted (judgement).
- Gemini's claim that they are open data per parcel is **not supported**.

### 9.4 Paris professional share: the CFE proxy undercounts by about 2.5x

**Independent benchmark.** Cour des comptes, *Les taxes foncières*, 27 February 2023, p. 33
(fetched live [T15]):
- « La part des locaux professionnels dans la base d'imposition de la TF a progressé entre
  2016 et 2021, passant de 21,6 % à 23,4 %. Celle du rendement a également progressé
  (20,1 % en 2016 contre 22 % en 2021). »
- Corrected for the change in the number of premises: 20.5 % of the base and 19.3 % of the
  receipts.
- Other figures: industrial premises are 5.7 % of receipts; 3.6 M locaux professionnels make
  up 6.4 % of all premises; individuals (personnes physiques) pay 65.5 % of TFPB.
- No Paris or Lyon figure was found. Ville de Paris budget pages and the
  paris.fr/APUR searches gave rates only (**snippet**). OFGL *Cap sur n°20* was not
  fetched (§8).

**The same proxy applied nationally** (REI 2025, all communes, own computation [T2]):

| Total, 2025 | € bn |
|---|---|
| ΣE11 (TFPB base) | 108.0 |
| ΣT29 (CFE gross base) | 25.3 |
| ΣX503 (CFE industrial abatement) | 6.9 |
| 0.5 × (T29 − X503) | 9.2 |

The proxy gives **8.6 %** of the base nationally, against the Cour's **20.5–23.4 %** (base)
or **22 %** (receipts). The proxy therefore captures only about 37–42 % of the
professional base. By area, it gives Paris 9.9–10.8 %, the petite couronne 10.3 % and the
Rhône 9.9 %.

**Known reasons for the undercount** (judgement unless marked):
1. **Vacancy.** Office vacancy is 6.4 % in Paris intra-muros (T1 2025 and T1 2026) and
   11.2 % in Île-de-France at end-2025 (Arthur Loyd/Immostat, **snippet** [T16]). Retail
   vacancy is similar. This explains about ×1.07–1.12.
2. **Occupiers outside the CFE.** These include the State, local authorities and public
   bodies renting private premises, non-profit associations, private schools under
   contract, farmers, and activities exempt by nature (art. 1449–1460). They are likely
   significant in Paris (ministries, hospitals' leased space), but I found no open figure.
3. **The 0.5 factor is not the cause** (§9.1).
4. **Unexplained remainder.** Items 1–2 plausibly account for ×1.2–1.5, not ×2.5. Either
   the CFE gross bases (T29) omit more than the categories listed, or the Cour's category
   covers more than RVLLP premises. Neither could be settled with open data.

**E16NB lissage counts do not help.** E16NB counts TFPB *articles* (owner-commune bundles)
that carried an RVLLP lissage. The totals are 1.53 M nationally against 3.6 M professional
premises, and 86 966 in Paris against 137 894 CFE articles for locaux pro (TB1_1). There is
no matching value variable, so no average rental value per article can be derived. No REI
variable gives the number or value of professional FB articles.

**Recommendation (judgement): bounded sensitivity, with a national scale factor as central
case.**
- `share_pro = k × 0.5 × CFE_pro / E11`.
- **Low:** k = 1 (raw proxy; Paris 9.9 %).
- **Central:** k = **2.5**. This is the national calibration to the Cour figures:
  22 / 8.6 = 2.56 on receipts, 20.5 / 8.6 = 2.38 on the corrected base. Paris then
  comes out at **about 25 %**.
- **High:** k = 2.7 (raw 23.4 % base share; Paris about 27 %).
- **Floor and caps.** Keep the WC75 industrial share fixed. Cap pro + EI at 90 % of the
  base, and floor housing at the commune's residential share of floor area × 0.5
  (judgement guard). Applied with the central k, Saint-Fons becomes about 33 % professional,
  26 % industrial and 41 % housing.
- **Caveat:** a single national k assumes the undercount is uniform across communes. It
  probably is not: it should be higher where public and non-profit occupiers are many, as
  in Paris. Report the low and high cases alongside the central one.

## 8. Sources

- [T1] OFGL, *(REI) Fiscalité directe locale 2024–2025*, dataset `rei`, Opendatasoft API v2.1. https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei. **Fetched live** (schema, years, FB/CFE vars for 93078, 94070, 69199, 75056 and 9 others).
- [T2] DGFiP, *Impôts locaux : fichier de recensement des éléments d'imposition (REI)*. https://www.data.gouv.fr/datasets/impots-locaux-fichier-de-recensement-des-elements-dimposition-a-la-fiscalite-directe-locale-rei-4. REI_2025.csv (112 MB) and REI 2020 zip. **Fetched live**; own computation.
- [T3] DGFiP, *TRACE_REI_2025.xlsx* (variable definitions, inside the [T2] zip). **Fetched live.**
- [T4] Loi 2020-1721 (LFI 2021), art. 29. https://www.legifrance.gouv.fr/jorf/article_jo/JORFARTI000042753620. **Fetched live.**
- [T5] DGFiP REI 2020 (`REI_COMPLET_2020.xlsx`, cols E11/E12/E41/E42), departments 69, 75, 92, 93 and 94. **Fetched live**; own extraction.
- [T6] OFGL, *Fiscalité directe locale 2012–2025 – base simplifiée*. https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/base-fiscale-simplifiee. **Fetched live.**
- [T7] DGFiP, *TFPB – Tarifs des locaux d'habitation 2024*. https://data.economie.gouv.fr/explore/dataset/descriptif-tarifs-des-locaux-d-habitation_2024/. **Fetched live.**
- [T8] DGFiP, *Fichiers des locaux et des parcelles des personnes morales*. https://data.economie.gouv.fr/explore/dataset/fichiers-des-locaux-et-des-parcelles-des-personnes-morales/. Metadata **fetched live**; data not downloaded.
- [T9] OFGL, *Cap sur n°20 – contribution fiscale des entreprises*, March 2023. https://www.collectivites-locales.gouv.fr/files/OFGL_cap_sur_20_contribution_fiscale_entreprises_services_publics_locaux_6-03-2023.pdf. **Not fetched** (maintenance page).
- [T10] Fipeco, *Les impôts locaux*. https://www.fipeco.fr/pdf/Imp%C3%B4tsLocaux.pdf. **Fetched live.**
- [T11] Préfecture des Hauts-de-Seine, *RAA spécial DDFIP du 2 décembre 2022* (tariffs 2023). https://www.hauts-de-seine.gouv.fr/contenu/telechargement/21631/135113/file/2022-12-02%20RAA%20sp%C3%A9cial%20DDFIP%20du%202%20d%C3%A9cembre%202022.pdf. **Snippet**; the PDF returned a maintenance page.
- [T12] collectivites-locales.gouv.fr, *Réforme des valeurs locatives*. **Fetched live.** The RVLLP six-yearly update is postponed to 1 January 2027 and the housing revision (RVLLH) to 2031 (LF 2026 art. 106).
- [T13] CGI art. 1388. https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006311555. **Fetched live.**
- [T14] CGI art. 1467 (CFE base; 30 % reduction for industrial establishments only), via BOFiP BOI-IF-CFE-20-20-20-10 and CMS Francis Lefebvre 2017 summaries. **Snippet.**
- [T15] Cour des comptes, *Les taxes foncières* (observations définitives), 27 February 2023. https://www.ccomptes.fr/sites/default/files/2023-10/20230227-S2023-0028-Taxes-foncieres.pdf. **Fetched live** (115 pp.; quotes on pp. 19–21, 33).
- [T16] Arthur Loyd, *L'Indispensable* T1 2025 and T1 2026 (Immostat/ORIE). https://www.arthur-loyd.com/media/file/7afe8363-l-indispensable-t1-2026-1.pdf. Also press reports of Immostat end-2025. **Snippet.**
- **Skipped or failed:**
  - Paris city budget documents: no TFPB category split found (search only).
  - impots.gouv.fr (node 11406 and the technical sheets): maintenance page.
  - Préfecture RAA PDFs (75, 92): maintenance page.
  - data.economie.gouv.fr REI explore API: no records, attachments only.
