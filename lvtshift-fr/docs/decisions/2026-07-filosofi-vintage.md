# Decision — Filosofi income vintage: hold 2021, criteria for adopting 2023

**Date:** 2026-07 · **Status:** documented hold (revisit at next publication or
before the sensitivity band goes public) · **Source of the decision point:**
external review F6/A4; STRATEGY §S3.

## Facts

- The pipeline's income layer (quintile charts) runs on **Filosofi 2021**
  (`BASE_TD_FILO_IRIS_2021_DISP`, `DISP_MED21`), pinned when "2022 not
  published" was true.
- That justification **expired in May 2026**: INSEE published a **« Filosofi 2 »
  2023 vintage with IRIS-level indicators** (insee.fr/fr/statistiques/8984752),
  carrying a **methodological break** — not directly comparable with the 2021
  series. *(Fact as search-verified by the 2026-07 external review, Phase 8/F6;
  direct re-verification from the automation environment was not possible —
  insee.fr returns 403 to non-browser clients — so the file/variable names below
  must be confirmed by hand before any switch.)*

## Decision

**Hold on 2021 for now**, explicitly and with a date, rather than adopting 2023
blind. Reasons:

1. **Methodology break.** Filosofi 2 changes the production methodology; level
   comparability with 2021 is not guaranteed. Adopting without a side-by-side
   validation run would violate the project's own discipline (every input
   change validated, every drop documented).
2. **What the pipeline actually uses is *relative***: within-commune income
   quintile assignment of IRIS. A methodology break distorts levels more than
   within-commune *ordering*, which weakens the urgency of switching — but that
   intuition is exactly what the validation run must confirm, not assume.
3. The switch itself is mechanically small (config URL + key/variable name +
   join check), so holding costs little once disclosed.

## Adoption criteria (do the switch when all four hold)

1. Hand-verify the 2023 IRIS file: name, separator, IRIS key format (9-digit
   `code_iris`), and the median variable (expected `DISP_MED23`-style).
2. Run both vintages on one commune (Montreuil — most IRIS): compare quintile
   *assignments* of IRIS between vintages; report the share of IRIS changing
   quintile. If the distributional chart's shape is stable, the break is
   presentational; if not, say so in the register when switching.
3. Update `config.py` (`filosofi_iris_csv` URL + variable), `ingest.
   fetch_filosofi_iris` docstring, METHODOLOGY/METHODOLOGIE §2 + §6.8, and the
   source manifest will pick up the new URL automatically.
4. Note the switch (and the break) in the limitations register — the quintile
   series before/after the switch are not comparable.

## Where this is disclosed

`config.py` (Filosofi comment), `ingest.fetch_filosofi_iris` docstring,
METHODOLOGY/METHODOLOGIE §6 item 8 — all already state "2021 retained pending
evaluation" (PR #14). This note is the evaluation record and the trigger list.
