# [ready-to-post] Cross-city rollups silently cover a subset of cities (19/22); README roster stale

**Repo:** gregmiller00/LVTShift · **Files:** `analysis/cross_city.ipynb`
(cell 1), `analysis/build_metrics_rollup.py` (~l.21–27), `lvt/metrics.py`
(~l.210–215); root `README.md` · **Severity:** medium (silent coverage claims)

## What happens

The cross-city artifacts discover inputs by presence
(`glob('*.csv')`), failing only if *zero* exports exist. Scranton, Denver and
Morgantown never export (TODO stubs in their notebooks), so every cross-city
table/chart quietly covers **19 of 22 cities** with no missing-city warning.
The only artifact disclosing this is `analysis/run_report.md`, which is stale
(April, pre-rename paths) and referenced by nothing.

Separately, the root README's city roster has drifted (lists Seattle, misses
Tulsa) and the architecture list names 5–6 modules where 9 exist.

## Suggested fix

One line of defence at the top of the rollup/notebook: diff the found CSVs
against `ls cities/` and print the gap —

```python
expected = {p.name for p in Path('cities').iterdir() if p.is_dir()}
found    = {Path(f).stem for f in csvs}
missing  = expected - found
if missing:
    print(f"WARNING: cross-city outputs exclude {sorted(missing)}")
```

— plus either finishing or explicitly excluding the three stub cities, and a
README roster/module-list refresh (or generating the roster from `cities/`).

*(Found during an external review of the French fork.)*
