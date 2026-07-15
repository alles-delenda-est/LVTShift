# Construction-cost calibration data (`construction_cost_eur_m2`)

**Purpose.** Sourced, open-data French construction-cost figures (€/m², turnkey,
*hors foncier*) to recalibrate the model's `construction_cost_eur_m2` parameter,
which sits directly under the land residual (`land = market − floor_area ×
construction_cost × depreciation`). A ±15 % move in this parameter flows linearly
into building value and inversely into land value, so it is a first-order
sensitivity.

**Scope of this document.** Data-gathering and citation only. No code was changed,
no numbers were reverse-engineered to hit a land-share band. Proposed values are
**what the sources support**; the individual-vs-collectif and habitable-vs-floor-area
questions (below) are flagged for the downstream Gemini review, not resolved here.

**Author / date.** Research agent, 2026-07-15. Model reference year = **2025**.

---

## 0. Access / verification note (read first)

In this environment, direct machine access to the primary hosts was blocked:

- `curl` through the egress proxy returns **403 CONNECT** for *all* external hosts
  (including `example.com`), so no scripted download was possible.
- `WebFetch` returns **HTTP 403** for `insee.fr`, `statistiques.developpement-durable.gouv.fr`,
  the `dreal.statistiques…` sub-domain, `data.gouv.fr`, `ffbatiment.fr`, `anil.org`
  and several aggregators (they block non-browser clients).
- `WebSearch` **does** reach and quote the content of those exact primary pages.

Consequently, the figures below are cited to their **primary SDES/INSEE/DREAL URL**
(verifiable by a human in a browser) and were **read via WebSearch of that page**.
Where only a secondary aggregator carried a number, that is stated and the figure is
marked accordingly. Nothing here is invented; anything I could not pin to a primary
source is marked `[PARTIALLY VERIFIED]` or `[UNVERIFIED – secondary]`.

---

## 1. Regional €/m² construction-cost table

**Primary series: SDES – EPTB** (*Enquête sur le prix des terrains et du bâti*).
EPTB is a mandatory statistical survey of people authorised to build an **individual
house**; it reports, per region, the **average construction cost of the house alone
(hors terrain / hors foncier)** and the average habitable surface, hence a
**construction €/m²**. This is exactly "gros œuvre + second œuvre, hors foncier",
which is the parameter's definition. **Caveat: individual houses only** — see §5 for
the collectif question and the habitable-vs-floor-area question.

### 1a. EPTB **2024** vintage (latest published) — construction cost, hors foncier

| Region (covers pilot dépts) | Construction €/m² (habitable) | Avg cost / surface | Source |
|---|---|---|---|
| **National (métropole)** | **1 927 €/m²** | surface 118 m² | [S1] |
| **Île-de-France** (75/77/78/91/92/93/94/95 → Montreuil 93) | **1 914 €/m²** | cost ≈ 252 222 € | [S2] |
| **Auvergne-Rhône-Alpes** (01/03/07/15/26/38/42/43/63/69/73/74 → Villeurbanne 69, Grenoble 38, Annemasse 74) | **2 063–2 066 €/m²** | cost 252 110 € / 122 m²; "3rd most expensive region" | [S3] |
| **Occitanie** (…/46/… → Cahors 46, Figeac 46) | **1 796 €/m²** | — | [S1][S4] |
| **Hauts-de-France** (59/62/… → Roubaix 59) | **1 795 €/m²** | surface 126 m² | [S1][S5] |

### 1b. EPTB **2023** vintage (prior year, for trend / cross-check)

| Region | Construction €/m² (habitable) | Detail | Source |
|---|---|---|---|
| National (métropole) | ≈ 1 846 €/m² | 221 500 € / 120 m² | [S6] |
| Île-de-France | 1 861 €/m² | 253 061 € / 136 m² ("7th least expensive") | [S6][S7] |
| Auvergne-Rhône-Alpes | 2 008 €/m² | surface 123 m² ("3rd most expensive") | [S8] |
| Occitanie | 1 734 €/m² | 202 880 € / 117 m² ("3rd least expensive") | [S6] |
| Hauts-de-France | < 1 800 €/m² | "among the least expensive" | [S6] |

National trend: construction cost **+5.6 % in 2023**, then **+1.4 % in 2024**
(€/m² **+2.1 %** in 2024, as habitable surface shrank slightly) — the market has
plateaued, consistent with the flat BT01 in §3. [S1][S6]

**Reading for calibration.** The sourced EPTB regional gradient is
**ARA (~2 065) > national (~1 927) > Île-de-France (~1 914) > Occitanie (~1 796)
≈ Hauts-de-France (~1 795)**. Note this **inverts** the intuition baked into the
current config (which set Île-de-France highest and Occitanie/Nord lowest): for
**detached houses**, ARA is the dearest region and Île-de-France is mid-pack,
because IdF's cost premium is overwhelmingly in **land**, not construction. The
collectif caveat (§5) is where an IdF/dense-core construction premium could
re-enter — but it is **not** captured by EPTB and I could not source it officially.

---

## 2. Per-pilot-commune table (current vs proposed vs source)

Proposed value = the EPTB **2024** regional construction €/m² covering that commune
(the best-sourced figure of the right definition). These are **not** tuned to any
land-share target. Notes flag where the individual-house basis is a known limitation.

| Commune | Dépt / Region | Current config €/m² | Proposed (sourced) €/m² | Source | Notes |
|---|---|---|---|---|---|
| **Montreuil** | 93 / Île-de-France | 2150 | **≈ 1 914** | EPTB 2024 IdF [S2] | Dense collectif suburb; EPTB is individual houses → likely **understates** collectif here. See §5. Current value is ~+12 % above the sourced individual figure. |
| **Villeurbanne** | 69 / ARA | 1950 | **≈ 2 065** | EPTB 2024 ARA [S3] | Sourced value is **higher** than current (raises building value → **lowers** land share). |
| **Grenoble** | 38 / ARA | 1900 | **≈ 2 065** | EPTB 2024 ARA [S3] | Same regional figure; +~9 % vs current. |
| **Annemasse** | 74 / ARA | 1900 | **≈ 2 065** | EPTB 2024 ARA [S3] | Haute-Savoie is a **high-cost sub-region** of ARA (Genevois); region-level EPTB is the sourced floor, a dépt-level figure would likely be higher (not separately sourced here). |
| **Roubaix** | 59 / Hauts-de-France | 1750 | **≈ 1 795** | EPTB 2024 HdF [S5] | Close to current; +~3 %. |
| **Cahors** | 46 / Occitanie | 1650 | **≈ 1 796** | EPTB 2024 Occitanie [S4] | Sourced value **higher** than current; +~9 %. |
| **Figeac** | 46 / Occitanie | 1600 | **≈ 1 796** | EPTB 2024 Occitanie [S4] | Same regional figure; +~12 %. |

**Direction check (not a calibration target).** For 5 of 7 communes the sourced
figure is **higher** than the current guess (ARA and Occitanie especially). Higher
construction cost → higher building value → **lower** land residual/share. Since the
stated problem is that 6 communes run *above* the 40–65 % land band (land too high),
the sourced EPTB values move land share **downward**, i.e. in the corrective
direction — obtained purely by reading EPTB, not by targeting the band. Montreuil is
the exception (sourced individual figure is *below* the current guess); its resolution
depends on the collectif question in §5.

---

## 3. Time-indexing basis — INSEE **BT01** (Index du coût de la construction – tous corps d'état)

- **Series:** INSEE *Index du bâtiment BT01 – Tous corps d'état*, **base 2010 = 100**
  (série 001710986). Monthly, published ~4 months in arrears; also relayed in the
  *Journal officiel*. [S9]
- **Latest published value:** **137.5** for **April 2026** (JO of 14 June 2026). [S10]
- **Recent monthly values (base 2010):**
  - Dec 2024 = **131.7** (published by INSEE 16 Feb 2025) [S11]
  - Aug 2025 = **133.7** [S10][S12]
  - Oct 2025 = **133.2** [S12]
  - Feb 2026 = **135.1** [S12]
  - Apr 2026 = **137.5** [S10]

  *(These monthly values are cited to secondary aggregators — ANIL / juristique /
  habitatpresto / celimo — because direct INSEE/ANIL fetch was 403-blocked. The
  authoritative source is INSEE série 001710986 [S9]. One secondary
  (celimo) erroneously calls the base "2015"; the INSEE series base is **2010** —
  treat that secondary's base label as wrong.)*

**Indexation factor, EPTB source year → model year 2025.**
The chosen level source (EPTB **2024**, §1a) is priced on 2024 permits; the model
year is 2025. Using BT01:

- Dec 2024 = 131.7 → mid/late 2025 ≈ 133.2–133.7 ⇒ **factor ≈ 1.01–1.015 (≈ +1–1.5 %)**.

The 2024→2025 BT01 move is **within survey noise** (~1 %). Recommendation for the
review: use the EPTB **2024** regional levels **as-is for 2025**, optionally applying
a **+1.5 %** BT01 nudge. If instead the EPTB **2023** levels are used, apply
131.7/≈128 ≈ +3 % (2023→2024) **plus** the ~1.5 % above; the 2024 vintage is
preferable precisely because it removes that step. *(A precise BT01 2024 and 2025
annual average could not be pulled from the primary INSEE table — direct access
blocked; the monthly points above bound the factor tightly enough for a ~1 %
correction.)* `[PARTIALLY VERIFIED — monthly points via secondary; annual averages not machine-read]`

---

## 4. Independent validation anchor — INSEE land share of household real estate

**Not a construction cost.** Used only to sanity-check the model's national implied
land share (target band ~45–50 %).

- **Publication:** INSEE Première n° **2081**, *« Le patrimoine économique national
  en 2024 »* (INSEE, 2026). [S13]
- **Headline:** real estate (constructions/dwellings + underlying built land) =
  **79.0 % of national wealth**; land value fell **−2.7 %** in 2024 while
  construction (building) value rose. [S13]
- **Household real-estate split (the anchor):** value of **dwellings ≈ 4 807 Md€**
  vs value of **built land (terrains bâtis) ≈ 4 043 Md€** ⇒ **land ≈ 45.7 %** of
  household real-estate value (46 %). [S13] `[PARTIALLY VERIFIED]` — the 79 % / −2.7 %
  headline is confirmed across multiple relays (INSEE, Banque de France [S14]); the
  exact 4 807 / 4 043 Md€ split was surfaced from the INSEE 2081 page via one
  WebSearch read and could **not** be re-fetched directly (INSEE 403). The resulting
  ~46 % is consistent with the config's stated "~45–50 %" and with the prior vintage
  (Insee Première 2028, 2023).

**Use:** the national household land share ≈ **46 %** is the middle of the plausible
40–65 % parcel band; dense cores sit above it, periphery below. If the model's
population-weighted implied land share lands far from ~45–50 % nationally, the
construction cost (this parameter) is the first suspect.

---

## 5. Known limitations the Gemini review must weigh (do NOT silently ignore)

1. **Individual houses only.** EPTB measures *maison individuelle* construction cost.
   Five of the seven pilots (Montreuil, Villeurbanne, Grenoble, Roubaix; partly
   Cahors/Figeac) have substantial **collectif** stock. Multi-family construction
   €/m² is typically **comparable-to-higher** than detached (structure, lifts,
   underground parking, RE2020), so the EPTB regional figure is plausibly a **lower
   bound** for dense collectif cores — most acute for **Montreuil**.
   - **Indicative** (secondary, trade sources — **not** official, **`[UNVERIFIED –
     secondary]`**): standard collectif ≈ **1 340–1 800 €/m² SDP**, up to **~2 000
     €/m²** in attractive urban zones (Paris/Lyon), social ≈ 1 120, high-end > 3 200.
     [S15] More authoritative leads not yet extracted: **Banque des Territoires,
     *Éclairages* n°33** (prix de revient des logements sociaux, Dec 2024) [S16];
     **FPI** *Les chiffres du logement neuf* [S17]. Recommend a follow-up pass to
     source an official collectif €/m² before finalising Montreuil/Villeurbanne/
     Grenoble.
2. **Habitable surface vs floor area (SDP).** EPTB's €/m² denominator is **surface
   habitable**; the model applies `construction_cost_eur_m2` to **floor_area (surface
   de plancher / SHON-like)**, which is **larger** than habitable area (walls,
   circulation, ~+10–20 %). Applying an EPTB *per-habitable-m²* cost to a *floor-area*
   base would **overstate** building value. The per-floor-area cost should be the EPTB
   figure **÷ (SDP/habitable ratio)** — i.e. scaled **down** ~10–20 %. This is a
   definitional adjustment, not sourced to a number here; flag for the review.
   *(These two caveats push in opposite directions for collectif cores — collectif
   uplift vs habitable→SDP haircut — so they partly offset; do not apply only one.)*
3. **Sub-regional variation.** Annemasse (Genevois/Haute-Savoie) and the Lyon core
   (Villeurbanne) are dearer than their region's average; region-level EPTB is a floor.
4. **Vintage.** EPTB 2024 is the latest; a 2025 vintage was not yet published as of
   2026-07-15 (surveys lag ~1 year). BT01 (§3) bridges the ~1 % gap to 2025.

---

## 6. Sources

Primary sources are cited by their canonical URL (verifiable in a browser);
"read via WebSearch" means the figure was surfaced by WebSearch of that exact page
because direct fetch was 403-blocked in this environment (see §0).

- **[S1]** SDES, *Le prix des terrains et du bâti pour les maisons individuelles en
  2024*, Ministère de la Transition écologique (SDES), publ. 2025/2026. National
  1 927 €/m² (surface 118 m²); construction cost +1.4 %, €/m² +2.1 % vs 2023.
  https://www.statistiques.developpement-durable.gouv.fr/le-prix-des-terrains-et-du-bati-pour-les-maisons-individuelles-en-2024
  (PDF: https://www.statistiques.developpement-durable.gouv.fr/media/8888/download?inline= ) — read via WebSearch.
- **[S2]** DRIEAT/DREAL Île-de-France, EPTB 2024, *chap. Coût total du projet* —
  IdF construction 1 914 €/m², coût ≈ 252 222 €.
  https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/ile_de_france/cout_total_projet.html — read via WebSearch.
- **[S3]** DREAL Auvergne-Rhône-Alpes, EPTB 2024 — ARA construction 2 063–2 066 €/m²,
  coût 252 110 € / 122 m², "3rd most expensive region".
  https://www.auvergne-rhone-alpes.developpement-durable.gouv.fr/les-prix-du-terrain-et-du-bati-pour-les-maisons-a28408.html — read via WebSearch.
- **[S4]** SDES EPTB 2024, Occitanie — 1 796 €/m² (regional detail via [S1] national
  release + DREAL Occitanie EPTB 2024 pages under
  https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/occitanie/ ) — read via WebSearch.
- **[S5]** DREAL Hauts-de-France, EPTB 2024 — 1 795 €/m², surface 126 m².
  https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2024/hauts_de_france/ — read via WebSearch.
- **[S6]** SDES, *Le prix des terrains et du bâti pour les maisons individuelles en
  2023* — national coût moyen construction 221 500 € (+5.6 %), surface moy. 120 m²;
  IdF 1 861 €/m², Occitanie 1 734 €/m², Hauts-de-France < 1 800 €/m².
  https://www.statistiques.developpement-durable.gouv.fr/le-prix-des-terrains-et-du-bati-pour-les-maisons-individuelles-en-2023
  (PDF: https://www.statistiques.developpement-durable.gouv.fr/media/7964/download?inline= ) — read via WebSearch.
- **[S7]** DREAL Île-de-France, EPTB 2023, *chap. 3 Caractéristiques des maisons
  construites* — IdF 253 061 € / 136 m² = 1 861 €/m².
  https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2023/ile_de_france/caracteristiques_maisons_contruites.html — read via WebSearch.
- **[S8]** DREAL Auvergne-Rhône-Alpes, EPTB 2023 — ARA 2 008 €/m², surface 123 m²,
  "3rd most expensive".
  https://dreal.statistiques.developpement-durable.gouv.fr/eptb/2023/auvergne_rhone_alpes/caracteristiques_maisons_contruites.html — read via WebSearch.
- **[S9]** INSEE, *Index du bâtiment BT01 – Tous corps d'état – Base 2010* (série
  001710986). https://www.insee.fr/fr/statistiques/serie/001710986 — direct fetch
  403-blocked; series identity/base confirmed via WebSearch.
- **[S10]** INSEE, *Les index Bâtiment, Travaux publics et divers de la construction*
  (Informations rapides) — BT01 April 2026 = 137.5 (JO 14 June 2026); Aug 2025 = 133.7.
  https://www.insee.fr/fr/statistiques/8897485 (Jan-2026 IR) — via WebSearch/aggregators.
- **[S11]** BT01 Dec 2024 = 131.7 (published INSEE 16 Feb 2025) — via monimmeuble /
  aggregator relay of INSEE. https://monimmeuble.com/actualite/indice-batiment-bt-01-pour-lachat-sur-plan-2024
- **[S12]** BT01 2025 monthly values (Aug 133.7, Oct 133.2, Feb-2026 135.1) — ANIL
  (https://www.anil.org/outils/indices-et-plafonds/indice-bt-01/ ), juristique
  (https://www.juristique.org/indices/bt01-2025 ), habitatpresto — secondary
  aggregators; direct fetch 403-blocked.
- **[S13]** INSEE Première n° 2081, *Le patrimoine économique national en 2024*
  (INSEE, 2026) — real estate 79.0 % of national wealth; land −2.7 %; household
  dwellings ≈ 4 807 Md€ vs built land ≈ 4 043 Md€ (⇒ land ≈ 46 %).
  https://www.insee.fr/fr/statistiques/8661938 (EN: https://www.insee.fr/en/statistiques/8666473 ;
  Comptes de patrimoine 2024: https://www.insee.fr/fr/statistiques/8574720 ) — direct
  fetch 403; figures via WebSearch. Md€ split `[PARTIALLY VERIFIED]`.
- **[S14]** Banque de France, *Le patrimoine économique national en 2024 – en hausse
  malgré le léger repli du foncier* (2026) — confirms 79 % real-estate share and land
  decline. https://www.banque-france.fr/fr/publications-et-statistiques/publications/le-patrimoine-economique-national-en-2024-en-hausse-malgre-le-leger-repli-du-foncier
- **[S15]** Secondary trade sources on collectif construction €/m² (indicative, **not
  official**): renovationettravaux.fr, mbg-construction.fr, cabinetfranckverdelet.com.
  `[UNVERIFIED – secondary]`
- **[S16]** Banque des Territoires, *Éclairages* n°33, *Le prix de revient des
  logements sociaux…* (Déc. 2024) — authoritative lead for collectif/social €/m²,
  figures not yet extracted.
  https://www.banquedesterritoires.fr/sites/default/files/2025-01/Exe%20brochure%20Eclairages%2033%20A4%202024%20vdef.pdf
- **[S17]** FPI (Fédération des Promoteurs Immobiliers), *Les chiffres du logement
  neuf* — sale-price series (prix de vente, not construction cost); use with care.

---

## 7. One-line recommendation for the review (no code changed here)

Replace the current unsourced guesses with the **EPTB 2024 regional construction
€/m²** (Montreuil/IdF ≈ 1 914; Villeurbanne/Grenoble/Annemasse/ARA ≈ 2 065;
Roubaix/HdF ≈ 1 795; Cahors/Figeac/Occitanie ≈ 1 796), **after** the review decides:
(a) whether to apply a sourced **collectif uplift** for dense cores (§5.1, needs one
more sourcing pass), and (b) the **habitable→floor-area** haircut (§5.2). BT01 says no
material time-indexation is needed for 2025 (< ~1.5 %).
