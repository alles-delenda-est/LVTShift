# Collectif €/m² — evaluation & synthesis of the multi-model research

> **Read the erratum at the end first** (October 2026): the IdF EPTB figure is 1 863 €/m², not 1 914, and EPTB is per m² of surface de plancher, not habitable area.

**What this is.** The task was to research an authoritative *collectif* (multi-family)
construction cost for the model's `construction_cost_eur_m2`, using **three models**
(Opus, Sonnet, Gemini) and to evaluate the best response or a mix. This note compares
the passes, diagnoses exactly where they diverge, scores them, and gives a single
synthesized recommendation for the downstream review + config decision.

- **Opus** → `collectif-opus.md` — recommends **≈ 1 950 €/m²** (range 1 750–2 200).
- **Sonnet** → `collectif-sonnet.md` — recommends **≈ 2 300 €/m²** (range 2 000–2 600).
- **Gemini** → `collectif-gemini.md` — **no single recommendation** (answered largely
  off-brief — mostly a generic missing-data-methodology essay), but surfaced one
  genuinely new, useful table that neither other pass had: the **MOD (direct-management)
  travaux / foncier / autres decomposition** from Éclairages n°33 — i.e. the exact
  *hors-foncier* construction series that both other passes flagged as their biggest
  `[DERIVED]` gap. Its own routes bracket **~1 935–2 375, centring ~2 100** — so it
  **corroborates** the mix below rather than moving it. See §2 (Div. A refinement) and §4.

All figures are **hors foncier, per m² of the model's `floor_area` (gross, walls
included), 2025 vintage, for a dense Île-de-France Zone-A-bis core (Montreuil)**.

> **UPDATE (primary source obtained).** The maintainer supplied the full
> Éclairages n°33 PDF. Its **Graphique 4** gives the exact hors-foncier MOD
> construction series — **national MOD travaux 2023 = 1 790 €/m² surface utile**
> — which **verifies Gemini's table to the euro** and turns the biggest
> `[DERIVED]` gap into a **sourced** anchor. This tightens the recommendation to
> **≈ 2 050 €/m² (range ~1 950–2 250)**, toward the lower half of the triangulated
> ~2 100 below. Full working: **`collectif-eclairages33-verified.md`** (authoritative).
> The triangulation below is retained as the reasoning trail that led there.

---

## 1. Where the models AGREE (high-confidence, sourced)

Opus and Sonnet both anchored on the same authoritative open series and reached the same
structural picture — and Gemini's on-topic section independently corroborates every
headline below (2 290→2 550 +11 %; travaux +22 %; A-bis +24 %). This part is solid:

- **Authoritative anchor = social-housing *prix de revient*** (Banque des Territoires
  / CDC *Éclairages* n°33 (Dec 2024) + n°25 / Le Moniteur for the 2020 zone levels).
  National PdR **2 300 → 2 550 €/m² surface utile, avec foncier** (2019→2023, +11 %);
  **travaux (construction) rose +22 %** while total rose +11 %; **Zone A bis +24 %/5 y**,
  the fastest-rising zone; 2020 zone levels **A bis 3 400 / B1 2 200 / C < 2 000 €/m² Su**;
  national component split **67 % travaux / 21 % foncier / 12 % autres** (2020).
- **Montreuil is officially Zone A bis** (both verified against the DHUP Annexe 11 /
  zonage) → the A-bis series, not the national average, is the right anchor.
- **FPI figures are SALE prices, not construction cost** (5 643 €/m² IdF) — both
  correctly **excluded** them.
- **No open *institutional* private-collectif construction-cost series exists** — both
  fell back to trade sources (Cabinet Franck Verdelet SDP ratios; one Cerema case study
  2 403 €HT/m² SDP), correctly flagged `[UNVERIFIED – secondary]`.
- **Same weakest link, honestly flagged by both:** the *exact* 2023–24 **Zone A bis**
  €/m² level is `[DERIVED]` (2020 level × the +24 % trend — not published in a readable
  form; the CDC/IdF open-data endpoints that carry it were 403-blocked), and the
  **A-bis-specific travaux/foncier split** is reasoned, not sourced.
- **Direction:** both confirm collectif in a dense core costs **more per floor-area**
  than the EPTB individual-house figure (~1 914 €/m² habitable → ~1 650–1 750 floor-area),
  i.e. EPTB understates Montreuil — the hypothesis holds.

So the disagreement is **not** about sources or the big picture. It is two specific
modelling choices inside the derivation.

## 2. Where they DIVERGE — and who is right

### Divergence A — computing national 2023 *travaux* (Sonnet is right)
- **Opus (cross-check):** `0.67 × 2 550 (2023 PdR) ≈ 1 710 €/m² Su`. This applies the
  **2020** 67 % share to the **2023** total — but travaux grew **+22 %** while total grew
  only **+11 %**, so travaux's share **rose to ~74 %** by 2023. Applying the stale 67 %
  **understates** 2023 travaux by ~9 %.
- **Sonnet:** `0.67 × 2 300 (2019) × 1.22 (travaux +22 %) ≈ 1 880 €/m² Su`. Grows the
  2019 travaux *component* by the actual travaux growth — **methodologically correct**.
- **Verdict: Sonnet — refined by Gemini.** Sonnet's *form* is right (grow the travaux
  component, don't apply a stale share to a moved total). But Gemini's MOD table gives
  the number *directly* — **national MOD travaux 2023 = 1 790 €/m² Su** (`[UNVERIFIED]`
  cell; structure verified real) — landing just **below** Sonnet's 1 880. Reason:
  within a consistent build type (MOD) the travaux *share* is stable ~67–68 %, not risen
  to ~74 %; the whole-sample "+11 %" total that made the share look like it jumped is
  **composition-distorted** by the cheaper-VEFA mix shift (MOD alone rose +18 %). So the
  cleanest hors-foncier construction anchor is the **direct MOD figure ≈ 1 790**, with
  Sonnet's 1 880 as the upper edge of that step. Immaterial to the final number (~2 100).

### Divergence B — the "attractive urban zone" trade figure: vintage & indexation (Sonnet likely right on the fact, Opus right on the weight)
- The Cabinet Franck Verdelet SDP figure ("zones urbaines attractives" **1 900–2 000
  €/m² SDP**) is dated **2019** in Sonnet's citation (the article titles name 2019);
  Opus labelled the same source "2024–26" and used ~2 000 as a *current* value.
- If it is 2019 (Sonnet), it needs ~**+26–28 %** indexation to 2025 → **~2 430–2 560
  €/m² SDP**; if current (Opus), it stays ~2 000. **Sonnet's vintage reading is more
  likely correct** (explicit year in the source title), which pushes the *private*
  figure up.
- **But** this is a `[UNVERIFIED – secondary]` trade source. **Opus's discipline is
  right that it should bracket, not anchor.** Sonnet built its central number by
  *blending up* toward this indexed trade path (its Path 2, 2 430–2 640); that leans
  the recommendation on the weakest evidence. **Verdict: split — Sonnet on the fact,
  Opus on the weighting.**

### Divergence C — applying the +24 % Zone A bis trend (Opus is right)
- **Sonnet** applied the **full +24 %** (a 2019→2024, 5-year figure) to a **2020** base
  to reach 2024 → A bis 4 216 €/m² Su — double-counting ~1 year and slightly **over**-
  stating the level.
- **Opus** pro-rated the trend to the 2020→2023 window (~+14 %) → ~3 800 €/m² Su —
  more defensible. **Verdict: Opus.**

### Divergence D — surface-basis chain (Opus is more rigorous; both land similarly)
- **Opus** derived the chain explicitly (Su ≈ 1.08–1.10·Shab; SDP ≈ 1.087·Shab ⇒
  **Su ≈ SDP**; `floor_area` gross ≈ +10 % over SDP ⇒ **×0.90** Su→floor-area) — clean
  and auditable.
- **Sonnet** used a looser "~10–15 % haircut" but in the **same direction and rough
  magnitude**. **Verdict: Opus on rigor; immaterial to the number.**

## 3. Synthesis — the best *mix*

Take **Opus's sourcing discipline and surface-basis rigor** (anchor on the authoritative
social series; treat trade/private as an upper bracket; ×0.90 Su→floor-area; pro-rate the
A-bis trend), and **correct it with Sonnet's travaux-growth arithmetic** (Divergence A):

```
National travaux 2023      = 0.67 × 2 300 × 1.22            ≈ 1 880 €/m² Su
Dense-core premium +15–25% = 1 880 × 1.15–1.25             ≈ 2 160–2 350 €/m² Su
Index 2023→2025 (+3–4%)                                     ≈ 2 230–2 440 €/m² Su
Su → gross floor_area ×0.90                                 ≈ 2 010–2 200 €/m² floor
```
Cross-check via the A-bis-level route (Opus, with the corrected higher travaux share):
A bis 2023 PdR ~3 900 €/m² Su × travaux share ~0.55–0.60 ≈ 2 145–2 340 Su → ×0.90 ≈
**1 930–2 105 €/m² floor**. The two routes overlap at **~2 000–2 150**.

Third, independent cross-check via **Gemini's direct MOD travaux** (a hors-foncier
construction figure, not share-derived):
```
National MOD travaux 2023 ≈ 1 790 €/m² Su × A-bis premium (+20–35%) ≈ 2 150–2 415 Su
Su → gross floor_area ×0.90                                          ≈ 1 935–2 175 €/m² floor
```
And via Gemini's SDP-gamme route (standard collectif ≈ 1 412 €/m² SDP 2019 × +22 %
travaux × +2 % to 2025 × A-bis premium) ≈ **2 110–2 375 €/m² SDP ≈ floor**. All three
routes now overlap tightly at **~2 000–2 150**.

> ### Synthesized recommendation — Montreuil collectif `construction_cost_eur_m2`
> ### **≈ 2 100 €/m²** (hors foncier, per gross floor_area), range **~1 900–2 400**.

This sits **between** Opus (1 950) and Sonnet (2 300): above Opus because Sonnet's
travaux-growth correction is right; below Sonnet because the jump to ~2 300 leans on the
indexed trade path, which should bracket (upper end ~2 400), not anchor. A modest private
uplift for Montreuil's mixed (social + private co-ownership) stock is included; the
Cerema 2 403 €HT/m² SDP case study (non-IdF) sits at the top of the range and supports it.

### Two things the config decision must not miss
1. **The band is a check, never the tie-breaker.** All three figures (1 950 / 2 100 /
   2 300) are above the EPTB-individual floor-area figure, so all pull Montreuil's land
   share **down** — but we must pick on **sourcing quality**, not on which best hits the
   40–65 % band. On sourcing quality the answer is ~2 100.
2. **Montreuil's high land share may be legitimate, not a miscalibration.** The prior
   review explicitly noted the dense Grand-Paris core can *legitimately* sit near the top
   of the land-share band (land genuinely dominates value there). The sourced collectif
   cost (~2 100) is **close to the current config guess (2 150)** — so for **Montreuil
   specifically the current value is already about right**, and its over-band land share
   should probably be **accepted as real**, not "fixed" by inflating construction cost.
   The larger, better-sourced corrections from this whole exercise are on the **ARA
   (up ~2 065) and Occitanie (up ~1 796)** *individual*-house figures (see
   `construction-cost-calibration-data.md`), not on Montreuil.

## 4. Open gaps (for a browser-equipped follow-up)
- **The single highest-value verification (now concrete):** open the Éclairages n°33
  full PDF in a browser and read off (a) the **MOD travaux/foncier/autres cells** —
  confirms Gemini's `[UNVERIFIED]` Table — and (b) any **Zone-A-bis-specific** level.
  That one check converts the central estimate from "triangulated ~2 100" to "sourced
  ~2 100". Browser-reachable (403 only to this automation environment):
  - PDF: `banquedesterritoires.fr/sites/default/files/2025-01/Exe brochure Eclairages 33 A4 2024 vdef.pdf`
  - USH mirror: `union-habitat.org/.../eclairages_33_a4_2024_vdef_sommaire.pdf`
  - CDC open data: `opendata.caissedesdepots.fr/explore/dataset/constructionrehabilitation_logementsocial_surface_prix/`
  - IdF open data: `data.smartidf.services/explore/dataset/financement-et-cout-des-logements-sociaux-construits/`
- **ARA collectif** (Villeurbanne/Grenoble, Zone A/B1): no pass sourced it; all
  infer a *smaller* collectif uplift than Montreuil. Directionally ~1 700–1 950 floor-area.
- **Gemini did not** surface an official *private*-collectif construction series or an
  exact A-bis level — those remain the only genuinely unsourced links.

## 5. Scorecard
| Dimension | Opus | Sonnet | Gemini |
|---|---|---|---|
| Answered the actual deliverable | **yes** | **yes** | **no** (off-brief essay) |
| Source authority / anchoring discipline | **stronger** (social anchor, trade as bracket) | leans on trade path for the central number | anchors on the real report |
| Travaux-growth arithmetic (Div. A) | understated (~9 % low) | **correct** (form) | **best** (direct MOD figure) |
| A-bis trend application (Div. C) | **correct** (pro-rated) | over-applied (full +24 %) | n/a |
| Surface-basis rigor (Div. D) | **stronger** (explicit chain) | looser, same magnitude | **inconsistent** (self-contradicts) |
| Trade-figure vintage (Div. B) | mis-dated as current | **correct** (2019 → indexes up) | n/a |
| New sourced data surfaced | zone levels, split | travaux-growth path | **MOD travaux/foncier/autres table** |
| Honesty about the weak link | strong | strong | n/a (didn't reach a number) |
| **Net** | Best *method/discipline* | Best *arithmetic on two sub-steps* | One valuable *data table*, no synthesis |

**Best mix = Opus's backbone + Sonnet's travaux correction, with Gemini's direct MOD
travaux (1 790) as the cleanest hors-foncier anchor → ≈ 2 100 €/m² (1 900–2 400).**
All three models' routes now overlap at ~2 000–2 150.

---

## Erratum and decisions recorded (October 2026)

**Erratum, verified live on 2026-10-19 against the SDES/DREAL EPTB 2024 pages.**
- The Île-de-France EPTB 2024 house cost is **1 863 €/m²** (266 356 € / 143 m²;
  "5e rang des régions les moins chères"), not 1 914: **1 914 €/m² is the
  national figure** (SDES release of 27/11/2025, 118 m²). The 252 222 € quoted
  for IdF is the house price only in projects *with* a land purchase (chapter 4).
- EPTB costs are per m² of **surface de plancher**, not habitable area (EPTB
  methodology: « exprimée en surface de plancher »). The "habitable → floor
  area" haircut proposed in §5.2 therefore does not apply as written.
- EPTB covers **individual houses only**. The Untec per-height-band tables cited
  in the sub-reports come from a members-only référentiel, not an open series,
  and should not be quoted as sourced.
- Why EPTB ranks IdF below ARA: IdF house permits are concentrated in outer-ring
  greenfield estates by volume builders, while ARA's include mountain sites
  (slopes, snow loads, seismic zones). For dense collectif cores, the social
  housing cost series rank IdF highest.

**Decision 1: construction costs.** The pilot values are **not** replaced by raw
EPTB figures. Paris, the Paris inner ring (incl. Montreuil), Lyon (incl.
Villeurbanne) and the Lyon ring are recalibrated on the DHUP/SISAL *Bilan des
logements aidés* 2021-22 **building-only** cost of new social housing (per m² of
surface utile, hors foncier and VRD), indexed to 2025 with INSEE BT01 and
converted to gross area, plus fees and 20 % VAT:

| Area | 2025 €/m² gross | Range |
|---|---|---|
| Paris | 2 650 | 2 350-3 100 |
| Paris inner ring (incl. Montreuil) | 2 400 | 2 150-2 700 |
| Lyon (incl. Villeurbanne) | 2 000 | 1 750-2 300 |
| Lyon ring | 1 850 | 1 600-2 100 |

The other panel communes keep their pilot values. A later review suggested
keeping the old 1 650-2 300 values on the grounds that they already matched
EPTB per gross m²; that was not adopted, because it rested on the 1 914 error
above and on treating the model's floor area as true gross area (next point).

**Decision 2: one cost per commune, both sides on habitable area.** Measuring
habitable area ÷ the model's floor area (BD TOPO footprint × storeys) on 35
communes (DPE habitable surfaces matched to BD TOPO buildings by RNB id) gives
**0.64 for flats and 0.61 for houses**: BD TOPO counts attics, raised basements
and technical levels as storeys, so the model's area overstates even true gross
area. The model now puts both sides of the residual on habitable area: market
value = DVF €/m² × habitable area, building value = cost per habitable m² ×
habitable area, with cost per habitable m² = commune cost ÷ habitable-to-gross
(flats 0.71, houses 0.82). There is still one cost scalar per commune and no
other per-category multiplier.

**Decision 3: non-residential multipliers deferred.** There is no open French
cost series for industrial or retail buildings, and BD TOPO's usage tags mix
warehouses with laboratories and Haussmann shopfronts. Non-residential parcels
are still priced like flats. This is a known bias, bounded by the ±10 pt
land-share sensitivity band published with every result.
