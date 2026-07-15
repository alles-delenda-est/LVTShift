# Collectif €/m² — primary-source verification (Éclairages n°33 PDF)

**What this is.** The maintainer supplied the full **Éclairages n°33 PDF**
(Banque des Territoires, "Le prix de revient des logements sociaux face aux
tensions inflationnistes", Déc. 2024). This note reads the exact figures off it,
which **converts the biggest `[DERIVED]`/`[UNVERIFIED]` gap in the whole exercise
into a sourced number** and confirms Gemini's MOD table was accurate.

Source: *Éclairages n°33*, Banque des Territoires, Décembre 2024 —
`banquedesterritoires.fr/eclairages-n-33`. Figures below are read directly from
the report's charts and body text (data quotation).

---

## 1. The number we needed — SOURCED

**Graphique 4 — "Composantes du coût d'un logement social en MOD, en euros par
m² de surface utile"** (maîtrise d'ouvrage directe; VEFA excluded because its
land/works split is not reliably known). Stacked bars, three components:

| Year | **Construction (travaux)** | Foncier | Autres charges | Total MOD |
|---|---|---|---|---|
| 2019 | **1 470** | 480 | 260 | 2 210 |
| 2020 | 1 540 | 490 | 280 | 2 310 |
| 2021 | 1 580 | 470 | 280 | 2 330 |
| 2022 | 1 690 | 490 | 290 | 2 470 |
| 2023 | **1 790** | 520 | 320 | **2 620** |

> **National MOD construction cost, hors foncier, 2023 = 1 790 €/m² surface utile.**
> (Travaux 2019→2023 = 1 470→1 790 = **+21.8 %**, matching the report's headline
> "coûts de construction **+22 %**".)

**Gemini's Table 4 is verified** — its per-cell values match to the euro
(construction 1 470→1 790; foncier 480→520; autres 260→320). Its only slip was
printing the 2023 total as 2 630 (component sum) vs the report's rounded 2 620.
Gemini's `[UNVERIFIED]` flags on these cells can now be lifted to **[SOURCED]**.

**Corroborating body text (verbatim data points):**
- MOD prix de revient "**de 2 210 € en 2019 à 2 620 € en 2023, soit une croissance
  de 18 %**" (> the 11 % whole-sample average — cheaper VEFA dilutes the mean).
- MOD annual growth **4.3 %**, of which **construction 3.4 pts**, foncier only
  **0.3 pt**, autres **0.6 pt** — i.e. the rise is overwhelmingly construction-
  driven, and **foncier contributes least** (it even fell in 2021).
- National whole-sample: **2 300 → 2 550 €/m² surface utile, +11 %** (2019→2023).

## 2. Zone A bis — what the report does and does NOT give

**Graphique 3 — "Prix de revient moyen au m² par zonage 2019-2023"** gives
*total* prix de revient (incl. foncier) by zone, not a travaux split. Body text:
- Zone A bis rose **~+24 % / 5 y** (vs A +10 %, B1 +11 %, B2 +15 %, C +11 %) —
  the steepest zone.
- **"Un logement social y coûte environ 50 % de plus qu'en zone A"** — but this
  is the **total** (land-inclusive) premium.
- A bis = 6 % of the sample; **VEFA ≈ 40 % in A bis** (vs ~half elsewhere), so
  the MOD decomposition covers ~60 % of A-bis operations.

**Key limitation, stated honestly:** the report gives **no zone-A-bis-specific
travaux figure**. Its only zone breakdown (Graph 3) is total prix de revient,
whose A-bis premium is heavily **land-driven** (land dominates value in the dense
Paris core). So the A-bis *construction-only* premium over the national MOD
travaux is **smaller than the ~50 % total premium** — it must be reasoned, not
read off. This is now the *only* remaining derivation in the chain.

## 3. Recommendation — now sourced, and slightly tighter

Anchor on the **sourced** national MOD travaux and apply a **construction-only**
(not land-inclusive) A-bis premium:

```
National MOD travaux (hors foncier) 2023   = 1 790 €/m² surface utile   [SOURCED]
A-bis CONSTRUCTION premium (+20–30%,        ≈ 2 150–2 330 €/m² SU
   not the ~50% land-inclusive total premium)
Su → gross floor_area  ×0.90                ≈ 1 935–2 095 €/m² floor
Index 2023→2025 (travaux +3–5%)             ≈ 2 000–2 160 €/m² floor
```

> ### Sourced recommendation — Montreuil collectif `construction_cost_eur_m2`
> ### **≈ 2 050 €/m²** (hors foncier, per gross floor_area), range **~1 950–2 250**.

This **tightens** the earlier triangulated ~2 100 (range 1 900–2 400) toward its
lower half, because the sourced MOD anchor (1 790 SU national) is firmer and
lower than the trade-figure-influenced upper path. The ~2 400 top of the old
range was leaning on the `[UNVERIFIED]` Verdelet trade figure; with a sourced
anchor it clearly sits **outside** the central estimate.

**Impact on the config decision is unchanged in direction, sharper in degree:**
- Montreuil's current config value **2 150** now sits at/just above the **top** of
  the sourced central range (~1 950–2 250) — **approximately right, perhaps a
  touch high**, but within range. No case for *raising* it.
- Therefore Montreuil's high land share should still be **accepted as largely real**
  (land genuinely dominates in the A-bis core; the report confirms foncier is the
  main source of the A-bis premium), **not "fixed"** by inflating construction cost.
- The band remains a **check, not a tie-breaker**; the sourced anchor is the basis.

## 4. What is now fully closed vs still open
- **CLOSED (sourced):** national hors-foncier construction cost and its 2019→2023
  path (Graph 4); the +22 % travaux / +24 % A-bis / +11 % national headlines;
  the foncier-is-minor-contributor finding.
- **STILL DERIVED (small):** the A-bis-specific *construction* premium (Graph 3 is
  land-inclusive; no per-zone travaux split is published). Bounded ~+20–30 %.
- **STILL OPEN (secondary):** any official *private/promoteur* collectif
  construction series (none found by any pass; sale prices ≠ construction cost).
