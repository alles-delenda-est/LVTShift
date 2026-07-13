# Decision — Surface-concept mismatch (SHOB-like × SHON/habitable prices): no factor yet

**Date:** 2026-07 · **Status:** documented hold — disclosure retained, no
correction factor applied · **Source of the decision point:** external review
F4 (flagged by the pilot's own founding review, PR #1); STRATEGY §S4.

## The problem (unchanged, and disclosed)

`floor_area = footprint × storeys` is a **gross, walls-included (SHOB-like)**
surface. It multiplies two prices referenced to *smaller* surface concepts:

- the construction cost (`config.construction_cost_eur_m2`, stated €/m² SHON),
- the hedonic €/m² (estimated on DVF `surface_reelle_bati`, habitable).

Both value *levels* are therefore overstated (order 10–25 % depending on
building type), and the residual land value inherits the bias. Since PR #14
this is register item 11 in METHODOLOGY/METHODOLOGIE §6.

## Decision: keep the disclosure, do NOT apply a factor yet

A correction factor (e.g. ×0.8 gross→habitable for collective housing) was
considered and **deliberately not applied**, because:

1. **No sourced factor is currently on file.** The gross→habitable ratio varies
   by building type (maison vs collectif vs activité), era, and wall thickness;
   applying a single unsourced number would trade a *documented* approximation
   for an *invented* correction — worse under this project's sourcing rules
   ("every constant cited to a document").
2. **The headline result is partially self-correcting.** The top-down §5
   validation (land share vs INSEE comptes de patrimoine) inflates numerator
   and denominator together, so *land shares* move far less than euro *levels*.
   The published caveat says exactly this.
3. **Changing every published euro level is a maintainer call**, not an
   autonomous one: it re-bases every chart and infographic figure.

## Adoption criteria (apply the factor when these hold)

1. A **citable source** for per-type gross→habitable ratios (e.g. CSTB/ADEME
   surface-ratio studies, or notaires' SHOB/SHAB conversion tables), transcribed
   with title/date into `config.py` as a per-`category_fr` dict.
2. Apply it **symmetrically** to both the market side (`estimate.market_value`)
   and the improvement side (`estimate.improvement_value`) — correcting one side
   only would corrupt the residual worse than the current consistent bias.
3. Re-run the §5 top-down validation and the published-commune exports; note the
   level shift in the changelog and register (the before/after euro levels are
   not comparable).
4. Land with or before the sensitivity-band wiring (spec 0002), which publishes
   euro levels.

## Where this is disclosed

METHODOLOGY §6 item 11 / MÉTHODOLOGIE §6 point 11 (since PR #14); the config
comment on `construction_cost_eur_m2`.
