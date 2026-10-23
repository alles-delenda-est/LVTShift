# Upstream contribution pack — gregmiller00/LVTShift

The fork inherits upstream bugs on every merge and has so far contributed
nothing back (STRATEGY §S2). This folder holds **ready-to-post issue texts**
for the three real upstream defects found by the 2026-07 external review, plus
the README-roster staleness. Posting them is a maintainer action (they go on
`gregmiller00/LVTShift`, which this fork's automation cannot write to).

| File | Upstream finding | Severity | FR exposure |
|---|---|---|---|
| [`issue-u2-stale-tax-change.md`](issue-u2-stale-tax-change.md) | `calculate_category_tax_summary` silently reuses a stale `tax_change` column — 38 parcels provably vanish from st_paul's committed summaries | HIGH | none today (FR re-coerces), but inherited on every merge |
| [`issue-u3-zero-base-pct.md`](issue-u3-zero-base-pct.md) | parcels going €0 → positive tax reported as "0 % change" in the category summary/chart | MEDIUM | **yes** — the upstream-rendered category chart ships with FR runs |
| [`issue-u4-silent-city-subset.md`](issue-u4-silent-city-subset.md) | cross-city rollups silently cover 19/22 cities (3 export stubs), no missing-city warning; + README roster staleness | MEDIUM | none (FR doesn't use the rollup) |

## Order and framing

Post **U2 first** — it is a genuine correctness bug in a tool an active research
group publishes with, and the committed st_paul notebook outputs *prove* it
without needing our word. U3 and U4 can follow. Keep the tone of the drafts:
factual, evidence-first, fix suggested but not demanded.

## Fallback if upstream is unresponsive (decided, not yet needed)

Per STRATEGY §S2: carry **thin FR-side overrides** rather than editing upstream
files (the zero-upstream-modification rule stands):

- **U2**: not needed today — the FR pipeline's `current_tax` is never null and
  `save_standard_export` re-coerces before summarising. Revisit only if a
  future FR path feeds nullable tax columns.
- **U3**: the FR infographic already presents vacant land in € (honest caption)
  instead of the meaningless 0 %; since the category split
  (`split_vacant_category`), the residual "0 %" bar concerns constructible
  vacant land only. If upstream declines the fix, add an FR-side annotation to
  the shipped `category_impact.png` or suppress that bar in the FR report call.
