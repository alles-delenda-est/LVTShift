# Spec 0002 — Wire the ±10 pt land-share sensitivity band into the pipeline

**Status:** Draft · **Priority:** P0 (HIGH — closes a standing published promise) ·
**Source:** external review BUGS.md F1 (+F9 fixed), A3, PROPOSED_NEXT_STEPS #1 ·
**Est. effort:** ~half a day

---

## 1. Problem

Every methodology document promises that "tout résultat publié [porte] une bande
part-terrain ±10 pts" — the project's stated answer to its single biggest
self-identified weakness (residual-method error amplification). But
`estimate.sensitivity_band` has **no callers**: no pipeline path computes or
publishes the band. PR #14 fixed the function's central-variant edge bug (F9)
and made the docs honest ("exists but not yet wired"); this spec **wires it in**
so the promise becomes executable and the docs can revert to "carries the band".

## 2. Goal

`run_commune` produces, for each commune, the category-level results under the
land-share −10 / +0 / +10 variants, exported and rendered so every published
category/quintile figure carries its band.

## 3. Design

### 3.1 Compute the band in `run_pipeline.run` (or run_commune)

After the base solve, for each variant returned by
`estimate.sensitivity_band(p, cfg)`:

1. Re-solve revenue-neutral with `model_split_rate_tax` on the variant's
   `land_value` / `improvement_value` (three cheap extra solver runs).
2. Summarise the same published aggregates (category-level median tax change,
   win/lose split, income-quintile medians) per variant.
3. Assemble a tidy band table: for each category, `{low, central, high}` of each
   published metric.

`sensitivity_band` already clips once after the shift and leaves out-of-scope
parcels untouched (F9 fix), so the central variant reproduces the base solve
exactly — assert this as a guard (the band's central column must equal the
headline numbers).

### 3.2 Export

- Add a `{commune}_sensitivity.csv` (long format: category × metric × variant)
  alongside the standard export.
- Retain `land_share_raw` (already added in PR #14) in the export so the
  unclipped distribution promised in METHODOLOGY §4/§6.5 is also publishable
  (F5 — the column exists; this spec makes sure it is written out).

### 3.3 Render

- In `make_infographic` / `charts_fr`, draw the category bars with the ±band as
  an error bar / shaded range around each central bar.
- The infographic's headline "X % paient PLUS" card gets a band too (its
  low/high across the three variants).

## 4. Files

| File | Change |
|---|---|
| `run_pipeline.py` | compute band variants (3 re-solves), summarise, return band table |
| `run_commune.py` | write `{commune}_sensitivity.csv`; print the band in the sanity block |
| `estimate.py` | (none — `sensitivity_band` is ready post-F9) |
| `make_infographic.py` / `charts_fr.py` | error-bars / shaded band on category chart + headline card |
| `THEORY.md`, `README.md`, `METHODOLOGY.md`, `METHODOLOGIE.md` | flip band language from "exists but not wired" back to "every published result carries the band" |
| `test_units.py` | band-integration tests (see §5) |

## 5. Tests & acceptance

1. **Central variant is identity** — the +0 % band column equals the base solve
   category numbers to the euro (locks the F9 fix at the pipeline level).
2. **Monotonic band** — the +10 % land-share variant raises land-heavy
   categories' bills and lowers building-heavy ones vs the −10 % variant
   (direction check).
3. **Revenue neutrality per variant** — each of the three solves is
   revenue-neutral (the solver guarantees this; assert it).
4. **Export shape** — `{commune}_sensitivity.csv` has the expected
   category×metric×variant rows; `land_share_raw` present in the main export.
5. `test_synthetic.py` extended to exercise the band path end-to-end.

## 6. Risks

- **Cost** — three extra solver runs per commune is negligible (the solver is a
  closed form for the FR path). No performance concern.
- **Presentation** — bands must not clutter the infographic; use a subtle shaded
  range, not full error bars, on the public card.
- Only wire this **after** confirming F9 is on `main` (it is, via PR #14) so the
  central variant is trustworthy.
