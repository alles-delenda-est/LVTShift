# Non-residential building valuation for LVTShift-FR: sourced parameters (2025 €)

Research date 2026-10-22. Each figure cites a source in §9 by tag, e.g. [N4]. Markers:
**fetched live** (I downloaded the page, PDF or API today and read the figure myself),
**snippet** (seen only in a search-result summary), **judgement** (my inference). The cost
arithmetic is in `nonres_costs_calc.py` next to this note. The probe scripts (BD TOPO WFS
storey coverage, the storey rule, open DVF business premises and activity land) are in
`nonres_probes/`; each takes an output directory and fetches public open data only.

## 0. Summary for a non-coder economist

- **The storey rule is the biggest error.** It matters more than the cost per m². BD TOPO
  leaves `nombre_d_etages` empty on 40–60 % of shed-type buildings. In six warehouse
  communes, the current "height ÷ 3 m" fallback **doubles the floor area of
  shed-nature buildings (×2.0–2.7) and inflates all non-residential floor area by ×1.87**
  [N2]. Where the storey count *is* known, 90 % of shed footprint area has one level [N2].
- **Costs are much lower than housing for sheds and close to housing for offices and
  gyms.** Logistics or industrial sheds cost about ¼ of the residential cost per m². Retail
  boxes cost about ½. Offices cost about 0.8×. Sports halls cost about 1×. Farm sheds and
  greenhouses cost under 0.1×. All figures are on our gross-area basis, with fees included.
- **Leave VAT out for business buildings.** Keep it for household annexes. Firms recover
  VAT, and the RICS valuation guidance (DRC is depreciated replacement cost) adds VAT only
  "where this is an irrecoverable cost" [N16 §8.14].
- **Activity land sells at about 0.3–0.6× residential building land** in the same areas.
  Open DVF matched to land-use maps gives medians of 93: ~380 vs ~660 €/m²; 94: ~280 vs
  ~770; Lyon: ~130 in business zones (ZAE) vs ~330–450 outside [N22–N24]. Samples are small.
- **Rural buildings, including greenhouses, are exempt from TFPB** under CGI art. 1382 6°
  [N17]. Industrial premises carry roughly halved values since 2021 [N18, N19]. Sharing the
  TFPB produit by floor area therefore over-taxes farms, greenhouses and factories in the
  baseline.

## 1. Storey heights and the storey-count rule

**What BD TOPO says (v3.5, July 2026, fetched live [N1], pp. 70–76):**
- **`nombre_d_etages`** is "Calculé à partir de l'attribut Dnbniv des fichiers fonciers".
  It is "non obligatoire" and "**n'est pas rempli sur les bâtiments d'Usage 1="Annexe" ou
  les constructions légères, ni sur les bâtiments qui n'ont pas pu être appariés**".
  Matching quality is in `appariement_fichiers_fonciers`. The documentation warns that some
  administrative and agricultural buildings are absent from the fichiers fonciers
  altogether.
- **`hauteur`** runs from the lowest ground point to the gutter, or to the wall top if the
  roof is flat. The value 0 means unknown.
- **Nature "Industriel, agricole ou commercial" (IAC)** is defined as a "grand bâtiment dont
  l'architecture générale révèle une fonction industrielle, agricole ou commerciale". It
  covers entrepôt, hangar, usine, hypermarché, supermarché, centre commercial and
  coopérative. The nature is "not required exhaustively below 1 000 m²", so small sheds can
  appear as "Indifférenciée".
- **"Indifférenciée"** explicitly includes bureaux, gymnase, écoles and hospitals.
- **`usage_1` "Commercial et services"** mixes bureaux with parc des expositions, entrepôt
  commercial and hypermarché.
- **`construction_legere`** marks a structure without foundations or open on at least one
  side. It comes from the cadastre and defaults to false for buildings that are not matched
  to it.

**Empirical probe (fetched live, IGN WFS [N2]).** The sample is Villepinte, Vaujours,
Santeny, Périgny, Rungis and Corbas: 23 820 buildings.

| nature × usage_1 | share of footprint | storeys null | height median / p90 | m height per known storey |
|---|---|---|---|---|
| IAC × Industriel | 30 % | 56 % (area 40 %) | 8.0 / 14.0 m | 7.6 |
| IAC × Commercial et services | 17 % | 42 % | 7.2 / 11.0 | 7.0 |
| Indifférenciée × Commercial et services | 7 % | 58 % | 5.7 / 10.2 | 5.0 (1 level); **3.05** (≥2 levels, n=61) |
| Serre × Agricole | 3 % | 100 % | 3.7 / 5.1 | n/a |
| Indifférenciée × Sportif | 1 % | 68 % | 6.6 / 9.4 | 6.9 |
| Indifférenciée × Résidentiel (≥2 levels) | 32 % | 24 % | 5.2 / 7.5 | 2.65 |

- Among IAC buildings *with* a storey count, 89.6 % of the area has 1 level. The median
  height of a 1-level IAC building is 7.2 m (p10 3.3, p90 11.0).
- Heights per storey measured to the gutter run below design floor-to-floor heights, which
  is consistent with the 3.05 m above.
- **Design references.** Class-A logistics needs ≥ 9.3 m usable height; class B needs
  ≥ 7.5 m [N3, fetched live]. Standard logistics is built with 10–12 m clear height, large
  platforms with 12–14 m [N4, fetched live]. Listings show 10–11.6 m (snippet). New offices
  have 2.65–3.0 m ceilings under a false ceiling, and 3.40 m under the slab in one Lille
  building (snippets). No primary source for a 3.5–4 m office floor-to-floor was found.
  3.3–3.6 m for modern offices is **judgement**.

**Recommended imputation** when `nombre_d_etages` is null or 0 (judgement, tested in the
probe). It cuts non-residential floor area to 1/1.87 of the current figure in the sample.
1. Nature IAC, Serre or Silo, or `construction_legere`, or usage Annexe, Agricole,
   Industriel or Sportif → **1 level**, whatever the height.
2. Usage "Commercial et services" with nature Indifférenciée → 1 level if height < 7 m,
   else **round(height ÷ 3.5 m)**. (Use ÷ 3.0 m if you prefer the measured 3.05 m.)
3. Religious and monuments (Eglise, Chapelle, Château…) → 1 level, and flag them; they are
   mostly exempt or unpriceable.
4. Everything else, mainly residential → keep height ÷ 3 m (measured 2.65 m).

Caveat: a few IAC buildings carry 5–7 storeys (2 % of area) at about 2.8 m per storey.
These are probably factories with office wings, or mismatches. Keep any known count.

## 2. Construction cost per m² of gross floor area, 2025 €

Basis: building only, turnkey, fees included, no developer margin. VAT is per the rule
below.

**Cost sources:**
- **One cost guide covers all the main types on a single basis.** Quostra, fetched live:
  values are January 2026 €, HT, hors honoraires, VRD and foncier, at the "province"
  coefficient 1.00 [N4–N8].
  - Geographic coefficients: Paris 1.20–1.35, Île-de-France 1.15–1.30, grande couronne
    1.10–1.20, Lyon 1.05–1.15.
  - Ratios: entrepôt simple 360–560; logistique standard 510–710; plateforme 610–870;
    atelier de production légère 710–1 220; retail box 1 220–2 550 per m² of *sales area*;
    centre commercial 1 840–3 270; gymnase 1 840–2 860; bureaux "blanc A" 1 630–2 240 per
    m² SUB (shell only 920–1 430); collectif social 1 630–2 040 per m² SDP.
- **Cross-checks:**
  - Logistics: 480–800, storage 400–600 €HT/m² [N9, live]; 350–400 €/m², basis unstated
    [N10, live].
  - Gymnasium projects: 2 070 and 2 480 €HT/m² of works at design stage [N11, snippet].
  - Farm storage shed: 138 €/m² with earthworks and foundations, cladding extra at 35–72
    €/m² of wall. This is the Chambres d'agriculture Indre/Creuse figure for 2023 (88 in
    2018), via [N12, live, secondary]. A 720 m² flat-storage shed cost 130 €/m² [N13, live].
  - Glass Venlo greenhouse: 250–450 €HT/m² including growing equipment, plus foundations
    15–30 and connections 10–25 [N14, live].
  - Garage, Île-de-France: blockwork 550–1 000, precast 400–750, timber 450–900 €/m²,
    VAT basis unstated [N15, live].

**Method** (`nonres_costs_calc.py`):

    guide base (HT, province) × geographic coefficient × fees × VAT treatment
      × BT01 2026→2025 (0.99) × (SDP ÷ gross)

- Sheds take half the geographic premium (judgement: steel and precast sheds are bought
  on a national market).
- Fees: sheds 5–8 %, workshops and retail 10–12 %, offices and halls 15 %.
- This "direct" figure is then **anchored**: it is multiplied by the ratio of the model's
  calibrated residential cost to the same guide's social-housing line, run through the
  same chain (k = 0.90 Paris, 0.85 inner ring, 0.79 Lyon, 0.76 Lyon ring).
- The anchoring keeps each type in the guide's proportion to housing while inheriting the
  model's lower, official-data residential level (`construction-costs-2025.md`). The
  unanchored direct figure is about 15–30 % higher and serves as the upper check.

**VAT rule.**
- **HT for business, farm and greenhouse types.** The owner recovers VAT. A business
  premises sale is usually VAT-free, or the VAT is recoverable, so the DVF price is
  effectively HT too. RICS: "Allowance for VAT is made only where this is an irrecoverable
  cost", and no developer's profit is added [N16 §8.14, live].
- **Sports halls are effectively HT.** Communes get the FCTVA back (16.404 %), so the net
  VAT cost is 1.2 × (1 − 0.16404) ≈ 1.003. The FCTVA rate is judgement from known law and
  was not fetched.
- **Household annexes are TTC**, like the house they serve.

## 3. Findings table by building type

Costs are €/m² gross floor area, 2025 €. Central values are anchored; the range follows in
brackets.

| Type (BD TOPO key) | Storey rule | Paris inner ring (93/94) | Paris | Lyon | Lyon ring | VAT | Life (yrs) | Floor |
|---|---|---|---|---|---|---|---|---|
| Logistics / industrial shed (IAC × Industriel, IAC × Indiff.) | 1 level | **600** (515–690) | 645 | 520 | 490 | HT | 40 | 15 % |
| Light industrial / workshop (Indiff. × Industriel) | 1 level | **850** (745–1 010) | 920 | 745 | 705 | HT | 40 | 15 % |
| Retail box / commercial hall (IAC × Commercial et services) | 1 level | **1 120** (935–1 415) | 1 235 | 935 | 865 | HT | 40 | 15 % |
| Offices (Indiff. × Commercial et services) | h ÷ 3.5 m if h ≥ 7 m | **1 980** (1 750–2 240) | 2 190 | 1 655 | 1 530 | HT | 60 | 20 % |
| Agricultural shed (any × Agricole, not Serre) | 1 level | **175** (145–225) | 190 | 155 | 145 | HT | 30 | 10 % |
| Greenhouse, glass (Serre) | 1 level | **195** (125–280) | 215 | 170 | 165 | HT | 25 | 10 % |
| Sports hall (any × Sportif) | 1 level | **2 480** (2 245–2 800) | 2 740 | 2 070 | 1 915 | ≈HT (FCTVA) | 50 | 20 % |
| Annex: garage, storage shed (any × Annexe) | 1 level | **545** (370–725) | 605 | 455 | 420 | TTC | 50 | 20 % |
| *Reference: residential collective (current)* | h ÷ 3 m | 2 400 | 2 650 | 2 000 | 1 850 | TTC | 80 | 25 % |

**Notes on the table:**
- **Plastic tunnels** are not separated by BD TOPO. They are probably flagged
  `construction_legere`, and if so should take about ¼ of the glass cost (judgement).
- **Lives and floors** are judgement, bracketed by:
  - Fiscal *durées d'usage*: industrial buildings 20 years (some sources 20–40), commercial
    20–50, offices 25 [N28, live (bailfacile) and snippet]. Fiscal lives are short because
    they cover accounting depreciation, not physical survival.
  - Component accounting: gros œuvre 50–80 years, technical installations 15–30 [N28,
    live].
  - BOFiP worked example: 20 years for a livestock building [snippet].
  - Glass greenhouses: 25–40 years, glazing 20–30 [N14, live].
  - RICS: straight-line is "the most commonly adopted" method for buildings, but it is
    right only at the start and end of life [N16 §9.28–9.29, live].
- **The floors are lower than housing's 25 %** because sheds suffer functional
  obsolescence (clear height, floor load, dock ratio: class C stock [N3]) that maintenance
  cannot cure.
- **Ages are mostly missing.** The model dates buildings from DPE logement, which does
  not cover these types. Default to mid-life: depreciation factor ≈ (1 + floor) ÷ 2 ≈ 0.55
  to 0.6. A later PR could try the DPE tertiaire dataset (judgement; not checked).

## 4. Valuation method: is the cost approach standard?

- **RICS DRC guidance (UK, 1st edition April 2026, fetched live [N16]).**
  - DRC is used "where there is no active market … due to the specialised nature of the
    asset" (§3.1).
  - The specialised-property definition, "rarely, if ever, sold in the market…" (§3.2),
    extends to conventional buildings whose size or location leaves no reliable sales
    evidence. A Villepinte-scale exhibition hall qualifies.
  - DRC is "inappropriate" if there is no demand for the use (§3.4).
  - Land is the "least expensive site that would realistically be suitable" (§7.1). For
    "a specialised industrial property … land with an industrial planning consent … would
    provide the best comparable evidence" (§7.12).
  - Land is valued at prevailing uses in the locality and "the lowest amount that a
    prudent purchaser would pay" (§7.13–7.14). This is **existing or prevailing-use value,
    not alternative (residential) use**.
  - The UK Treasury bans lower-value "alternative site" assumptions for UK public-sector
    accounts from 2028/29 (§1.6, §7.3).
- **French practice.** The *Charte de l'expertise en évaluation immobilière* (5th edition
  2017) lists a cost-based *méthode par le coût de remplacement net* or *sol + construction*
  for properties without a market. I **could not fetch the Charte** (it is not freely
  online), so this point is judgement. IVS 105 (cost approach) was not fetched either.
- **Implication.**
  - For specialised or very large sheds, DRC with activity-land comparables is the
    textbook method.
  - For ordinary shops, offices and small activity premises, a market comparison exists,
    so our residual (market value − depreciated cost) is legitimate, *if* the market price
    is a business-premises price and not the flat residential price used today.
  - An LVT model wants the land's value under its permitted (highest) use. DRC's
    existing-use land value is therefore a **floor**, not the target. For parcels inside
    business zones (ZAE) the two coincide.

## 5. Activity-land prices (€/m² of land)

**No public observatory gives a clean figure.** I checked:
- ORF Île-de-France: its commune map aggregates every land type, in €/ha [N31, live].
- Institut Paris Région / DRIEAT pages: no prices.
- Cerema DV3F: a methodology note only, with the price defined as TTC, excluding notary
  fees (snippet).
- Métropole de Lyon: ZAE boundaries only [N24].

**My own probe (fetched live: geo-DVF 2023–24 [N22]).** It takes land-only "Vente"
mutations of 1–3 parcels, at least 200 m² and at least €10k, and classifies each by the
land-use class at its location: MOS 2021 in Île-de-France [N23], or the Lyon ZAE polygons
[N24].

| Area | Activity land (median, p25–p75) | Residential land, same area | Ratio | n (activity) |
|---|---|---|---|---|
| Seine-Saint-Denis (93): MOS ZAE, industrial sites, storage, logistics | **381** (213–991) | 658 (461–844) | **0.58** | 23 |
| Val-de-Marne (94) | **282** (119–993) | 771 (478–1 186) | **0.37** | 20 |
| Métropole de Lyon, 23 communes with a ZAE sale: inside ZAE | **130** (60–299) | 329 outside ZAE (all); 454 ("terrains à bâtir") | **0.29–0.40** | 80 |

**Market cross-checks:**
- Lyon asking prices: Meyzieu commercial-zone plot 273 €/m², Chasselay 160 €/m²
  [N27, live].
- Rough check (judgement): a 93 warehouse sold at about 1 000 €/m² built (§6), less a
  depreciated cost of about 300, with 2 m² of land per m² of floor, implies about 350 €/m²
  of land. That agrees with the 381 median.

**Recommendation.** Use activity land at **0.45× residential land in the inner ring and
0.35× in the Lyon area**, as a prior or a check. Do not use these as hard parameters:
n ≈ 20 a year per département, and MOS shows current land use, not zoning.

## 6. Business-premises prices in open DVF

**What the DVF fields mean** (DVF notice, fetched live [N21]):
- `valeur_fonciere` is one price per disposition, repeated on every line. It *includes*
  any VAT and seller-paid agency fees.
- `surface_reelle_bati` is floor area between walls, from the fichiers fonciers, with
  dependencies excluded.
- Lots and locaux do not correspond one-to-one.

**Probe results (2023–24, mutations whose only premises type is "Local industriel.
commercial ou assimilé") [N22]:**

| | 93 | 94 | Métropole de Lyon (ZAE communes) |
|---|---|---|---|
| Mutations | 1 091 | 1 230 | 1 550 |
| Surface missing | 2 % | 1 % | 1 % |
| Several premises under one price | 21 % | 19 % | 35 % |
| Single-premises €/m² built, median | 2 616 | 3 281 | 2 521 |
| ≥ 1 000 m² (n=80/73/74), median (p25–p75) | **1 000** (321–1 825) | **934** (255–1 826) | **888** (340–2 191) |

- Small shops in copropriété dominate the overall median. Large premises sell for about
  900–1 000 €/m², consistent with CBRE's 1 000–2 000 €/m² for second-hand warehouses in 93
  [N25, live, asking prices]. BureauxLocaux gives a mean of 2 127 €/m² in 93, also asking
  [N26, live].
- **The data are usable for a per-m² price surface by size band, not for one flat price.**

**Pitfalls:**
- About 20–35 % of mutations sell several premises under one price.
- Portfolio and share deals are invisible: big logistics trades go through company
  shares, which DVF does not record (judgement).
- Sale-and-leaseback prices capitalise the lease, not the property. Lettre M2 lists such
  deals in Genas and Saint-Ouen-l'Aumône [N30, live].
- VAT is included when the sale opts into it.
- Industrial sites valued under the comptable method can carry inaccurate surfaces.
- The p25 of 250–340 €/m² for large premises signals mis-matched surfaces or bundled sales.
  Trim the tails.

## 7. Tax law

- **CGI 1382 6° a (rural buildings).** Fetched live via BOI-IF-TFB-10-50-20-10, 8 June
  2022 [N17]:
  - Text: "les bâtiments qui servent aux exploitations rurales tels que granges, écuries,
    greniers, caves, celliers, pressoirs et autres, destinés, soit à loger les bestiaux …
    soit à serrer les récoltes". The exemption is **permanent**.
  - Conditions: use must be "**de manière permanente et exclusive**" for agriculture (§10,
    §280, §330). That means the biological production cycle, or processing the farm's own
    produce (§100–200). Housing is excluded except for the stockman's (§210–230).
  - What counts is **the occupant's use, not the owner's status**: tenants, finance
    leases and companies subject to corporation tax qualify (§370–400).
  - Greenhouses growing flowers and plants count as agricultural (§140; CE 12/05/1971
    n° 79765). **The land under agricultural greenhouses is outside TFPB** (art. 1381 4°,
    §20).
  - An accessory-activity tolerance of ≤ 10 % of receipts was added by the 2019 finance
    law (snippet). Légifrance returned 404 and bofip.impots.gouv.fr refused the connection,
    so the doctrine was read on doctrine.fr.
- **Industrial establishments, art. 1499 (comptable method).** BOI-IF-TFB-20-10-50-40,
  14 June 2023, fetched live [N18]:
  - Rental value = cost price × **4 %** for land, and × **6 %** for buildings and
    installations, reduced by ¼ (bought before 1976) or by ⅓ (after), giving 4.5 % or 4 %
    "en pratique".
  - Art. 29 of LF 2021 (law 2020-1721) **halved** these values for TFPB and CFE: −1.54 bn
    TF, −1.75 bn CFE, with communes compensated at frozen 2020 rates [N19, live]. Before
    2021 the rates were 8 % and 12 % (snippet [N29]).
  - **Correction to the brief:** the reduction since 2021 is ≈50 %, not 30 %. The 30 %
    figure is the separate CFE abatement on industrial bases (snippet).
- **RVLLP.** Fetched live [N20]:
  - In force since **2017**: value = weighted area × category tariff of the rental sector ×
    location coefficient, with tariffs based on actual rents.
  - It excludes housing, industrial premises under the comptable method and barème
    premises.
  - The first six-yearly update was **postponed to 1 January 2027** (LF 2026 art. 106).
    The housing revision (RVLH) slipped to 2031.
- **Implication for the baseline.** Spreading the commune's TFPB produit by floor area,
  with no weights:
  - It wrongly taxes farm buildings and greenhouses, which should pay 0 (Périgny, Santeny).
    `exemptions.py` handles only 1382 1° public property.
  - It over-taxes industrial premises, whose comptable values were halved in 2021.
  - It mis-weights shops and offices, which are on 2017 market-rent tariffs, against
    housing, which is on 1970 values.
  - With the current storey rule it doubles the floor area of sheds as well. Together, the
    baseline over-allocates TFPB to warehouse communes' sheds.
  - **Minimum fix:** zero-weight 1382 6° buildings (usage Agricole or nature Serre) and
    fix storeys. **Better:** category weights from the DGFiP REI produits, if the
    commune-level split is available (not checked).

## 8. Recommendations and caveats

**Recommendations:**
1. **Fix storeys first** (§1 rule). It is the largest and least uncertain correction.
2. **Add per-type cost, life and floor** from §3. Use HT for business types and TTC for
   annexes.
3. **Value non-residential buildings with a business-premises price surface from DVF**
   (size bands, trimmed). Where no comparables exist (exhibition halls, very large sheds),
   switch to DRC with activity-land comparables. Treat that land value as a floor.
4. **Exempt rural buildings** (1382 6°) in the baseline TFPB allocation.

**Caveats:**
- **The costs rest on one commercial guide** [N4–N8] cross-checked against blogs. No
  Moniteur, Untec, BatiPrix, Afilog or Chambre d'agriculture primary document was
  reachable. Statista and Turner & Townsend gave no numbers. Uncertainty is ±25 %.
- **The anchoring factor (k = 0.76–0.90) is a modelling choice.** Without it, costs are
  15–30 % higher.
- **Lives and floors are judgement**, as are the shed half-premium and the office height.
- **The land-price samples are tiny** (n ≈ 20) and MOS shows land use, not zoning.
- **The BD TOPO probe covers 6 communes only.** Re-run it on the territory before
  adopting the rule.
- **Not fetched:** the Charte de l'expertise, IVS 105, BOFiP durées d'usage
  (BOI-BIC-AMT-10-40-30) and Légifrance articles 1381, 1382 and 1499.

## 9. Sources

- [N1] IGN, *BD TOPO v3.5 Descriptif de contenu*, July 2026. https://data.geopf.fr/annexes/ressources/documentation/DC_BDTOPO_3-5.pdf. **Fetched live.** The old geoservices.ign.fr DC_BDTOPO_3-3/3-4 PDFs now redirect to cartes.gouv.fr and were skipped.
- [N2] IGN Géoplateforme WFS `BDTOPO_V3:batiment`, https://data.geopf.fr/wfs/ows, for 93078, 93074, 94070, 94056, 94065 and 69273. **Fetched live**; own computation.
- [N3] Unemplacement, *Classes d'entrepôt*. https://unemplacement.com/guide/immobilier-dentreprise/immobilier-industriel/entrepots/quelles-sont-les-classes-dentrepot. **Fetched live.**
- [N4] Quostra, *Coût construction entrepôt logistique*. https://quostra.com/fr-fr/blog/cout-construction-m2-france/cout-construction-entrepot-logistique-m2. **Fetched live.**
- [N5] Quostra, *bureaux*. https://quostra.com/fr-fr/blog/cout-construction-m2-france/cout-construction-bureaux-m2. **Fetched live.**
- [N6] Quostra, *ERP*. https://quostra.com/fr-fr/blog/cout-construction-m2-france/cout-construction-erp-m2. **Fetched live.**
- [N7] Quostra, *logement collectif*. https://quostra.com/fr-fr/blog/cout-construction-m2-france/cout-construction-logement-collectif-m2. **Fetched live.**
- [N8] Quostra, index and geographic coefficients. https://quostra.com/fr-fr/blog/cout-construction-m2-france/. **Fetched live.**
- [N9] Thibault Bâtiment Industriel, *coût entrepôt 2025*. https://www.thibaultbatimentindustriel.fr/actualites/guide-complet-2025-cout-de-construction-dun-entrepot-logistique-par-m%C2%B2-prix-delais-et-reglementation/. **Fetched live.**
- [N10] Unemplacement, *coûts de localisation d'un entrepôt*, 28 Nov 2025. https://unemplacement.com/guide/immobilier-dentreprise/immobilier-industriel/entrepots/quels-sont-les-couts-a-considerer-pour-choisir-la-localisation-de-votre-entrepot. **Fetched live.**
- [N11] Gymnasium projects at Coulounieix-Chamiers and Mauregard. **Snippet.** The Haute-Vienne "Construction de gymnases 2023" PDF returned 404.
- [N12] stabulation.fr, *Hangar à fourrage*, citing Chambres d'agriculture Indre and Creuse via Web-agri, May 2023. https://stabulation.fr/hangar-stockage-fourrage/. **Fetched live** (secondary). Réussir's article returned 404.
- [N13] Terre-net, *Stockage à la ferme*, 2022, updated 2024. https://www.terre-net.fr/observatoire-technique-culturale/strategie-technique-culturale/article/stockage-a-la-ferme-bien-reflechir-son-projet-avant-de-se-lancer-217-206003.html. **Fetched live.**
- [N14] Hellopro, *Guide d'achat serre en verre professionnelle*. https://conseils.hellopro.fr/guide-d-achat-d-une-serre-en-verre-professionnelle-5080.html. **Fetched live.**
- [N15] Construires.fr, *Prix construction garage (IdF)*. https://www.construires.fr/prix-construction-garage/. **Fetched live.**
- [N16] RICS, *Depreciated replacement cost method of valuation for financial reporting*, UK 1st edition, April 2026. https://www.rics.org/content/dam/ricsglobal/documents/standards/drc_method_of_valuation_for_financial_reporting_1st_edition_rics.pdf. **Fetched live.**
- [N17] BOI-IF-TFB-10-50-20-10, 8 June 2022, via https://www.doctrine.fr/pc/bofip/409-PGP. **Fetched live.**
- [N18] BOI-IF-TFB-20-10-50-40, 14 June 2023, via https://www.doctrine.fr/pc/bofip/4806-PGP. **Fetched live.**
- [N19] Banque des Territoires, *PLF 2021 impôts de production*. https://www.banquedesterritoires.fr/que-prevoit-le-projet-de-loi-de-finances-pour-2021-concernant-les-impots-dits-de-production. **Fetched live.**
- [N20] collectivites-locales.gouv.fr, *Réforme des valeurs locatives*. https://www.collectivites-locales.gouv.fr/gerer-les-finances-publiques-locales/fiscalite-locale/fiscalite-directe-locale/reforme-des-valeurs-locatives. **Fetched live.**
- [N21] DGFiP, *Notice descriptive du fichier DVF*, Oct 2022. https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20221017-153319/notice-descriptive-du-fichier-dvf-20221017.pdf. **Fetched live.**
- [N22] Etalab geo-DVF 2023 and 2024, départements 93, 94 and 69. https://files.data.gouv.fr/geo-dvf/latest/csv/. **Fetched live**; own computation.
- [N23] Institut Paris Région, MOS 2021/2025 in 79 classes. https://data.iledefrance.fr/explore/dataset/mos-occupation-du-sol-2025-and-2021-en-79-postes-de-la-region-ile-de-france/. **Fetched live.**
- [N24] Métropole de Lyon, ZAE (WFS `adr_voie_lieu.adrzae`). https://data.grandlyon.com/geoserver/metropole-de-lyon/ows. **Fetched live.**
- [N25] CBRE, *Vente entrepôts Seine-Saint-Denis*. https://immobilier.cbre.fr/vente-entrepots/ile-de-france/seine-saint-denis.aspx. **Fetched live.**
- [N26] BureauxLocaux, *Prix entrepôts 93*, Oct 2026. https://www.bureauxlocaux.com/prix-marche/entrepots/seine-saint-denis-93. **Fetched live.**
- [N27] Arthur Loyd Lyon, *Terrains à vendre*. https://www.arthur-loyd-lyon.com/terrains-vente. **Fetched live.**
- [N28] Bailfacile, *Amortissement immeuble*, https://www.bailfacile.fr/guides/amortissement-immeuble (**fetched live**). Clementine durées-d'usage table (**snippet**). Legifiscal's table is paywalled.
- [N29] RSM, *LF 2021 réduction des impôts locaux*. https://www.rsm.global/france/fr/node/261. **Snippet.**
- [N30] Catella, *Lettre M2*, Nov 2022. https://www.catella.com/globalassets/global/mix-france-corporate-finance/lettre_m2_novembre-2022.pdf. **Fetched live**; no cost figures.
- [N31] ORF Île-de-France, *Valeurs foncières* and *Chiffres clés*. https://www.orf.asso.fr/valeurs-foncieres/. **Fetched live**; no activity-land figures.
- **Skipped or failed:**
  - Légifrance (404) and bofip.impots.gouv.fr (connection refused).
  - impots.gouv.fr (maintenance page).
  - Statista and Turner & Townsend, Arcadis (no figures visible).
  - data.iledefrance.fr ZAE 2013 (dataset withdrawn; MOS used instead).
