# Collectif €/m² — evaluation & synthesis of the multi-model research

**What this is.** The task was to research an authoritative *collectif* (multi-family)
construction cost for the model's `construction_cost_eur_m2`, using **three models**
(Opus, Sonnet, Gemini) and to evaluate the best response or a mix. This note compares
the passes, diagnoses exactly where they diverge, scores them, and gives a single
synthesized recommendation for the downstream review + config decision.

- **Opus** → `collectif-opus.md` — recommends **≈ 1 950 €/m²** (range 1 750–2 200).
- **Sonnet** → `collectif-sonnet.md` — recommends **≈ 2 300 €/m²** (range 2 000–2 600).
- **Gemini** → *pending* (no Gemini CLI/API in this environment; prompt in
  `PROMPT-for-gemini.md`, to be run by the maintainer → `collectif-gemini.md`).
  When it lands, slot it into §2/§3 below.

All figures are **hors foncier, per m² of the model's `floor_area` (gross, walls
included), 2025 vintage, for a dense Île-de-France Zone-A-bis core (Montreuil)**.

---

## 1. Where the two models AGREE (high-confidence, sourced)

Both anchored on the same authoritative open series and reached the same structural
picture — this part is solid:

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
- **Verdict: Sonnet.** This alone lifts the social-anchored figure ~9 % above Opus's.

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

## 4. Open gaps (for the Gemini pass and/or a browser-equipped follow-up)
- **The single highest-value verification:** pull the exact Zone-level PdR + charge-
  foncière split from the CDC and IdF open-data endpoints (both 403 here, but browser-
  reachable): replaces the `[DERIVED]` A-bis level and split — the biggest uncertainty
  in every pass.
  - CDC: `opendata.caissedesdepots.fr/explore/dataset/constructionrehabilitation_logementsocial_surface_prix/`
  - IdF: `data.smartidf.services/explore/dataset/financement-et-cout-des-logements-sociaux-construits/`
- **ARA collectif** (Villeurbanne/Grenoble, Zone A/B1): neither pass sourced it; both
  infer a *smaller* collectif uplift than Montreuil. Directionally ~1 700–1 950 floor-area.
- **Gemini pass:** run `PROMPT-for-gemini.md`; if it surfaces an official private-collectif
  series or an exact A-bis level, it could tighten §3 materially.

## 5. Scorecard
| Dimension | Opus | Sonnet |
|---|---|---|
| Source authority / anchoring discipline | **stronger** (social anchor, trade as bracket) | leans on trade path for the central number |
| Travaux-growth arithmetic (Div. A) | understated (~9 % low) | **correct** |
| A-bis trend application (Div. C) | **correct** (pro-rated) | over-applied (full +24 %) |
| Surface-basis rigor (Div. D) | **stronger** (explicit chain) | looser, same magnitude |
| Trade-figure vintage (Div. B) | mis-dated as current | **correct** (2019 → indexes up) |
| Honesty about the weak link | strong | strong |
| **Net** | Best *method/discipline* | Best *arithmetic on two sub-steps* |

**Best mix = Opus's backbone + Sonnet's travaux correction → ≈ 2 100 €/m² (1 900–2 400).**
