# [ready-to-post] Zero-current-tax parcels reported as "0 % change" in category summaries/charts

**Repo:** gregmiller00/LVTShift · **File:** `lvt/lvt_utils.py` (~l.198–202) ·
**Severity:** medium (chart says the opposite of the finding)

## What happens

```python
tax_change_pct = np.where(current_tax != 0, ..., 0)
```

A parcel going from **$0 to a positive LVT bill** — the entire point of the
under-used-land incentive — is reported as **0 % change** in the category
summary that feeds `category_impact.png`. The chart then shows "Vacant Land:
0 %" precisely where the dollar story is largest.

In the French fork this is structural, not incidental: *all* vacant land has
`current_tax = 0` by design (TFPB is a tax on built property), so the shipped
upstream chart renders the LVT's main target as unaffected.

## Suggested fix

For zero-base parcels report **NaN (excluded from the % aggregate)** instead of
0, and surface them as their own line — e.g. `new_taxpayers: N parcels, $X
total` — in the category summary. That keeps the % column meaningful and makes
the new-taxpayer effect visible instead of hiding it at 0.

*(Found during an external review of the French fork, whose infographic already
works around this by captioning vacant land in € rather than %.)*
