# Collectif €/m² — Gemini pass (extracted + evaluated)

**Author / date.** Gemini pass, run by the maintainer from the prompt in
`PROMPT-for-gemini.md`, pasted back 2026-07-15. This file is my (Opus)
*extraction and critical read* of that output — the raw Gemini text is kept
in the chat transcript; only the on-topic signal is distilled here.

---

## 0. Delivery verdict — mostly off-brief

Gemini answered a **different question than the one asked**. ~80 % of its
output is a generic methodology essay on *missing-data mechanisms* (MCAR /
MAR / MNAR, MICE/FIML, GAIN/EGAIN imputation, the GRACE satellite gap,
LSTM-BCNN climate reconstruction, FAIR data repositories) — it appears to
have latched onto the word "missing" in "missing collectif figure" and written
a survey of statistical missing-data theory. **It never produced the core
deliverable**: a single recommended collectif €/m² for Montreuil with a range.
On the task as set, Gemini **under-delivered** vs both Opus and Sonnet.

**But** its one on-topic section ("Microeconomic Modeling of French Residential
Real Estate") contains a **genuinely new, useful data table that neither Opus
nor Sonnet surfaced** — worth extracting.

## 1. The valuable contribution — the MOD cost decomposition

Gemini surfaced the **maîtrise d'ouvrage directe (MOD)** breakdown from
Éclairages n°33 — direct-project-management operations, where the land /
construction / other-charges split is *transparent* (unlike turnkey VEFA,
where the developer does not disclose it). This is **exactly the hors-foncier
construction series** both prior passes flagged as their biggest `[DERIVED]`
gap.

**Structure independently verified as real.** A WebSearch of the primary
report (banquedesterritoires.fr/eclairages-n-33; USH mirror) confirms
Éclairages n°33 *does* analyse MOD-vs-VEFA separately and *does* decompose
cost into **foncier / travaux / autres charges**. So Gemini's table maps onto
a real feature of the report — it is not an invented framing. The **cell
values below remain `[UNVERIFIED]`** at the individual-number level (not
quoted verbatim in any indexed page; the source PDF is browser-reachable but
403-blocked to this environment — see §4).

**MOD cost price, €/m² surface utile (Gemini, `[UNVERIFIED]` cells):**

| Year | Travaux (construction) | Foncier | Autres | Total MOD |
|---|---|---|---|---|
| 2019 | 1 470 | 480 | 260 | 2 210 |
| 2023 | **1 790** | 520 | 320 | 2 630 |

- **MOD travaux (hors foncier) 2023 ≈ 1 790 €/m² SU**, national, all-zone.
- Growth 2019→2023 = 1 790/1 470 = **+21.8 %** — matches the verified **+22 %
  travaux** headline exactly. Good internal corroboration.
- MOD total rose **+18 %** (2 210→2 630) vs the **+11 %** whole-sample average
  → confirms cheaper VEFA increasingly diluted the sample mean (relevant to
  Divergence A below).
- **Travaux share is stable ≈ 66–68 %** within MOD (1 470/2 210 = 66.5 % →
  1 790/2 630 = 68 %) — it did **not** jump to ~74 %.

**Secondary (2019, social, per SDP):** Gemini also gives gamme-level
construction costs — PLAI 1 180 / Standard PLUS-PLS 1 412 / Standing 1 620
€/m² SDP — and states a standard collective social apartment cost **≈ 1 250–
1 400 €/m² SDP (2019)**. These are directly on an **SDP basis** (≈ our
`floor_area`), so they need no Su→floor haircut — a useful cross-check route.

## 2. What Gemini corroborates (raises confidence in the synthesis)

- National anchor **2 290→2 550 €/m² SU, +11 %** (2019→2023) — matches Opus /
  Sonnet / the verified report.
- **Travaux +22 %; Zone A bis +24 %** (report attributes A-bis to construction
  cost, not land) — matches.
- Private collectif ~4 000 €/m² is a **SALE** price, not construction — Gemini
  labels it as such, agreeing with both prior passes' exclusion of FPI/sale
  figures.

## 3. What to distrust in the Gemini output

- **It did not answer the deliverable** (no Montreuil €/m², no A-bis-specific
  construction level, no uncertainty range).
- **Internal inconsistency on surface conversion:** the prose says collectif
  SHAB/SDP ≈ 0.92–0.97 (⇒ SDP ≈ +3–9 % over SHAB), but its Table 5 implies an
  SDP/SHAB "efficiency ratio" of **1.18–1.20** (⇒ SDP ≈ +20 %). These
  contradict; **do not rely on Gemini's surface-conversion factors** — use
  Opus's explicit chain instead.
- **Cell-level `[UNVERIFIED]`:** the MOD per-year values are plausible and the
  table structure is real, but the exact numbers are not quoted in any indexed
  secondary page. Treat as indicative until checked against the PDF (§4).
- Much of the surrounding essay (imputation algorithms, climate data, repo
  comparison) is **irrelevant** and was ignored.

## 4. Impact on the recommendation

Running Gemini's *direct* MOD travaux figure through the same chain as the
synthesis gives an **independent third route**, and it lands on the same place:

```
National MOD travaux (hors foncier) 2023   ≈ 1 790 €/m² SU        [Gemini, UNVERIFIED]
A-bis premium over national (+20–35%)      ≈ 2 150–2 415 €/m² SU
Su → gross floor_area  ×0.90               ≈ 1 935–2 175 €/m² floor
```
Cross-check via the SDP-gamme route (no surface haircut needed):
```
Standard collectif 2019   ≈ 1 412 €/m² SDP
× travaux +22% (→2023) × +2% (→2025)       ≈ 1 760 €/m² SDP  (national)
× A-bis premium (+20–35%)                   ≈ 2 110–2 375 €/m² SDP ≈ floor
```
Both Gemini routes bracket **~1 935–2 375, centring ~2 100–2 150** — i.e. they
**corroborate the Opus+Sonnet synthesis (≈ 2 100)** and, if anything, firm up
the conclusion that **Montreuil's current config value (2 150) is about right**.

Notably, Gemini's stable ~67–68 % MOD travaux share slightly **refines
Divergence A**: Sonnet's arithmetic *form* is right (grow the travaux
component, don't apply a stale share to a moved total), but the cleaner path
is Gemini's **directly-tabulated MOD travaux (1 790)** rather than
`share × sample-total` — because the sample total is composition-distorted by
the VEFA mix shift. Net effect on the number: negligible (~2 100 either way).

## 5. Highest-value next step this pass unlocked

The verification that would replace the last `[UNVERIFIED]` is now **concrete
and browser-reachable** (403 only to this automation environment):

- **Éclairages n°33 full PDF:**
  `banquedesterritoires.fr/sites/default/files/2025-01/Exe brochure Eclairages 33 A4 2024 vdef.pdf`
- **USH sommaire/mirror:**
  `union-habitat.org/.../eclairages_33_a4_2024_vdef_sommaire.pdf`

Open either in a browser and read off the **MOD travaux/foncier/autres cells**
(to confirm Gemini's Table 4) and any **Zone-A-bis-specific** level. That
single check would convert the central estimate from "triangulated ~2 100" to
"sourced ~2 100".
