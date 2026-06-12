# LVTShift-FR — Quick Start (plain-English)

A no-jargon guide to actually running this on your own machine. If a step
errors, copy the red text and ask — don't guess.

> **What it does, in one sentence:** it estimates, parcel by parcel, who would
> pay more or less if a French commune shifted its *taxe foncière* onto the
> **value of the land** (a Land Value Tax), keeping total revenue unchanged —
> and writes the answer as a spreadsheet (CSV) plus a few charts.

---

## 1. What you need first (one-time)

- **Python 3.11+** — get it from python.org. During install, tick
  **"Add Python to PATH"**.
- **Git** — from git-scm.com (you already have this).

To check they're installed, open **PowerShell** and run:

```powershell
python --version
git --version
```

Both should print a version number.

---

## 2. Set it up (one-time, ~3 minutes)

Copy-paste these into PowerShell, one block at a time:

```powershell
# Get the project (this fork already contains the US engine it builds on)
git clone https://github.com/alles-delenda-est/LVTShift.git
cd LVTShift

# Create a private sandbox for its Python libraries (keeps your PC clean)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install the libraries it needs
pip install pandas numpy geopandas matplotlib seaborn
```

You'll know the sandbox is active when your prompt shows `(.venv)` at the start.

> **Windows blocks the `Activate.ps1` line?** If you see *"...Activate.ps1 cannot
> be loaded because running scripts is disabled on this system"*, that's a
> default Windows safety setting, not a project problem. Fix it **once**, for
> your account only (no admin needed):
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Answer `Y` if prompted, then re-run the `Activate.ps1` line. (`RemoteSigned`
> lets scripts on your own machine run while still blocking unsigned ones
> downloaded from the internet — the standard developer setting.)
>
> **Prefer to change nothing?** Skip activation and call the sandbox's Python
> directly instead: use `.\.venv\Scripts\python.exe` in place of `python` for
> the install, and `..\.venv\Scripts\python.exe` once you're inside
> `lvtshift-fr/`.

---

## 3. See it work in 2 minutes (no data needed)

The project ships with a **synthetic ("pretend") commune** so you can watch the
whole machine run end-to-end without downloading anything:

```powershell
cd lvtshift-fr
python test_synthetic.py
```

You should see it finish with **`ALL CHECKS PASSED`** and a line confirming
**revenue neutrality within 1%** (the key sanity check: total tax collected is
unchanged — the tax is only *redistributed*).

---

## 4. What you get, and where

After a run, look inside `lvtshift-fr/output/`:

- **`grenoble.csv`** — one row per parcel: its land value, building value, old
  tax, new tax, and the change. This is the real deliverable.
- **`reports/grenoble/*.png`** — charts (in euros):
  - `category_impact.png` — who wins/loses by property type
  - `income_quintile_*.png` — impact across neighbourhood income levels
  - `ten_pct_share.png` — share of parcels that move more than ±10%
  - `distribution.png` — the spread of changes across all parcels

> Two charts you might expect (ethnicity-based) are deliberately **not**
> produced: France doesn't collect ethnic statistics, so the analysis is done
> on **income** instead.

---

## 5. Running it for a *real* commune

This is the honest part. The synthetic test works today. For a **real**
commune, the data-download step (`ingest.py`) is still a stub — fetching BDNB
buildings, REI tax totals, and Filosofi incomes needs to be completed first.
Until then, real runs aren't a one-click affair. When that's ready, the flow is:

1. In `config.py`, pick the commune — `GRENOBLE` and `ANNEMASSE` are pre-defined
   (change the one line `from config import GRENOBLE as CFG` in `run_pipeline.py`).
2. Run the ingest functions to download that commune's open data.
3. Call `run_pipeline.run(...)` with the prepared data — same as the synthetic
   test does at the bottom of `test_synthetic.py`.

If you want to model a specific commune, tell me which and I'll wire up the
ingest for it.

---

## 6. Reading the results sensibly (important)

- **Trust the aggregates, not the individual bills.** The per-parcel numbers
  rely on imputations; publish results **by property category or income
  quintile**, never as one household's bill.
- The current-tax baseline is the weakest input — see the README's *Limites
  connues* before quoting any figure.

---

## 7. If something breaks

- `running scripts is disabled on this system` (on the `Activate.ps1` line) →
  run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
  once, then retry. See the callout in section 2.
- `'python' is not recognized` → Python isn't on PATH; reinstall and tick the
  PATH box.
- `ModuleNotFoundError` → the sandbox isn't active (re-run
  `.\.venv\Scripts\Activate.ps1`) or a `pip install` was skipped.
- A red `Traceback` → copy the **last few lines** and send them over.
