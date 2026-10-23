# Work-item scope — Construction-cost calibration (FFB / BT01)

**Status:** scoped, not started. **Owner:** TBD. **Depends on:** nothing (pure
open-data + config work; does *not* require the Fichiers Fonciers).

## Why this is the highest-value next step

Every parcel's **building value** is a depreciated replacement cost:

```
improvement_value = floor_area × construction_cost_eur_m2 × depreciation
```

and **land value** for built parcels is the residual `market − improvement`. So
`construction_cost_eur_m2` sits directly under the land estimate: **a ±15 % move
in the cost flows linearly into building value and inversely into the land
residual.** Today that input is a single per-commune scalar on a *pilot* regional
gradient (`config.py` §Communes, 1 600–2 150 €/m², comment: "MUST be recalibrated
against a regional FFB cost series before publication").

The symptom is already visible in the ingestion register: **6 of 9 communes sit
above the 40–65 % land-share band** (Montreuil 84 %, La Rochelle 83.5 %,
Villeurbanne 72 %). Some of that is the genuine LVT thesis (land dominates value
in hot cores), but the magnitude points at **under-valued buildings inflating the
land residual** — i.e. the pilot €/m² are too low where they bite. Calibrating
this is the cleanest way to tighten the headline numbers and bring the panel back
toward the INSEE national anchor.

Context: Tax Policy Associates' 2026 England model rests on the *same* lever — a
national construction-cost calibration factor (0.705) plus regional adjustments,
and a forced 55 % land-share anchor. We can do better than a single national
factor by using regional cost series, and we already impute per parcel rather
than per LA×band cell.

## Objective

Replace the per-commune pilot scalar with a **calibrated construction-cost lookup
by région (and, optionally, building type)**, indexed to the model reference
year, and **validate the resulting land shares against an independent national
anchor** so the calibration is a check, never a target.

## Current state (what changes)

- `config.py`: `CommuneConfig.construction_cost_eur_m2` (single scalar per
  commune, all building types) → replace with a lookup keyed by région/département
  (× building-type class if we go there), plus an index-to-year step.
- `estimate.py`: the improvement-value step reads the scalar; it would read the
  lookup (parcel → commune → région/type → €/m²).
- `validate_external.py` / register: already has the land-share band check — it
  becomes the acceptance test for the calibration.

## Data sources (all open / published; verify live before coding, per house rules)

| Source | What it gives | Role |
|---|---|---|
| **FFB — coût de construction** (Fédération Française du Bâtiment, regional cost references) | Absolute €/m² turnkey construction by region/type | Primary absolute level |
| **SDES — PRLN / "prix de revient des logements neufs"** (Ministère, open) | Construction cost €/m² of new dwellings by région and house/apartment | Cross-check / type split |
| **BT01 & ICC** (INSEE construction-cost *indices*, base 100) | Time evolution of construction cost (relative, not absolute) | Index a base-year absolute figure to the model reference year |
| **INSEE comptes de patrimoine** (national land vs building share, ~45–50 % land) | National land-share benchmark | **Validation anchor** (already cited in `validate_external`) |

Note the division of labour: FFB/SDES fix the **absolute level** by region/type;
BT01/ICC only **index it in time**. Do not use BT01 as an absolute €/m² — it is a
base-100 index.

## Method (proposed)

1. Assemble a base-year absolute €/m² table by **région** (12 métropolitaines) —
   FFB primary, SDES/PRLN cross-check. Keep it turnkey replacement cost (gros +
   second œuvre, hors foncier), consistent with the current definition.
2. Optionally split by **building-type class** (maison individuelle vs collectif
   vs non-résidentiel). v1 may keep a single residential figure and treat
   non-residential with a documented multiplier; flag it (`imp_quality`).
3. **Index** the base-year figure to the model reference year via BT01/ICC.
4. Map each commune → région (→ type) → €/m² in `config.py`; wire `estimate.py`.
5. **Re-run all 9 communes**; recompute the land-share distribution.
6. **Validate**: the register's land-share band check should now place most
   communes within 40–65 %, and the panel mean near the INSEE comptes-de-
   patrimoine ~45–50 % national land share. Report movements per commune; the
   ±10-pt sensitivity band should visibly narrow the residual's exposure.

## Scope boundaries

- **In:** regional absolute €/m², time-indexing, revalidation, config/estimate
  wiring, register update.
- **Out (separate items):** non-residential valuation strata (borrows residential
  €/m² today — a known, separately-tracked gap); depreciation-curve changes (DPE
  era mapping is a different lever); the Fichiers Fonciers baseline work.
- **Non-goal:** hitting the band. The band is a *check*. If a commune legitimately
  has a very high land share after honest calibration, that is a finding, not a
  bug to tune away.

## Risks / open questions

- **Type granularity vs data availability.** SDES/PRLN is strongest for new
  *houses*; apartment and non-residential €/m² are thinner. May need a documented
  collective/individual ratio rather than independent series.
- **Replacement vs new-build cost.** The model wants replacement cost of the
  *existing* stock; depreciation handles age, so the base should be turnkey new-
  build cost — confirm FFB/SDES figures are on that basis (exclude land, VAT
  treatment stated).
- **Regional vs departmental granularity.** Région is likely the honest
  resolution of the published series; département-level precision would over-claim.
- **Anchor interpretation.** Comptes de patrimoine land share is a national
  stock figure; our panel is 9 non-representative communes skewed to hot markets,
  so expect the panel mean *above* the national ~45–50 %. Validate the direction
  and magnitude of the shift, not an exact match.

## Process (per the repo's working conventions)

Setting the actual €/m² values is an **economic-parameter decision**, so:
1. **Research agent** to gather and cite the FFB/SDES regional series + the
   current BT01/ICC index, with sources and vintages.
2. **Gemini review** (France context) of the calibration approach and the chosen
   values before they enter `config.py`.
3. Implement behind the existing `imp_quality`/land-share flags; re-run; record
   the before/after land shares in the register and `THEORY.md`.

## First concrete step

Dispatch a research agent to produce the regional absolute construction-cost
table (FFB primary, SDES cross-check) + the latest BT01/ICC index and base year,
with citations — then bring the proposed `config.py` values back for Gemini review
before wiring `estimate.py`.
