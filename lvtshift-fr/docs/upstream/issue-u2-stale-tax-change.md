# [ready-to-post] calculate_category_tax_summary silently reuses a stale/uncoerced `tax_change` column

**Repo:** gregmiller00/LVTShift · **File:** `lvt/lvt_utils.py` (~l.190–202) ·
**Severity:** high (published summaries undercount)

## What happens

`calculate_category_tax_summary` coerces and `fillna(0)`s
`current_tax_col`/`new_tax_col`, but only computes `tax_change`
**if the column doesn't already exist**:

- `model_split_rate_tax` (~l.698–706) always creates `tax_change` earlier —
  *without* coercing nulls — so the guarded recompute never runs;
- any notebook running multiple scenarios into the same dataframe silently
  reuses scenario 1's `tax_change` for scenarios 2 and 3 (e.g.
  charlottesville's 2:1 / 4:1 / 10:1 runs per run_report.md) unless the caller
  manually drops the column.

## Evidence already committed in this repo

The st_paul notebook's own committed outputs show it firing:

- cell 15's category summary counts **72,399** parcels, while cells 9/11/30
  establish **72,437** — 38 parcels with null county `TotalTax1` (never
  null-guarded in cell 7) silently vanish from `property_count`,
  `total_tax_change_dollars`, and every mean/median;
- the same 38-row shortfall recurs independently in cell 24's quintile tables
  (70,145 vs Q1–Q5 summing to 70,107), cross-checking the diagnosis.

So every city notebook with any null current-tax values publishes category and
quintile tables that undercount and misstate dollar totals, with no warning.

## Suggested fix

Recompute `tax_change` unconditionally from the just-coerced columns (they are
computed two lines above anyway):

```python
df[tax_change_col] = coerced_new - coerced_current
```

or, minimally, recompute whenever `current_tax_col`/`new_tax_col` differ from
the defaults. A regression test: frame with one null `TotalTax1` row + a
pre-existing stale `tax_change` column → summary must count every row and
match `new − current` recomputed.

*(Found during an external review of the French fork, which inherits this
function; happy to send a PR if useful.)*
