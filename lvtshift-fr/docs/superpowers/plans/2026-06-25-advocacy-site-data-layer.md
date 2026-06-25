# Advocacy Site — Data Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the aggregate-only JSON the « Pour une terre productive » site consumes — one `<commune>.json` per modeled commune, an `index.json`, and a `<commune>.validation.json` — from existing model output, plus register the three new communes.

**Architecture:** Two new Python modules in `lvtshift-fr/` — `export_web.py` (reads the authoritative per-parcel standard-export CSV → aggregate JSON) and `validate_external.py` (independent external benchmarks + a cross-source data-quality check). Both call the *unmodified* upstream `lvt` solver where a re-solve is needed. No upstream edits. The site (a separate plan) reads the emitted JSON at build time.

**Tech Stack:** Python 3.11+, pandas, geopandas/shapely (already in `requirements.txt`), the upstream `lvt` package at the repo root, pytest.

## Global Constraints

- **Zero upstream modification.** Import `lvt` from the repo root; never edit it. (`lvtshift-fr/CLAUDE.md`)
- **Aggregate-only output.** Never emit a per-parcel row/array. Honest only at category/quintile level. (`THEORY.md`, spec §2)
- **No `$`/`usd`/US-census token reaches a JSON value.** Emit clean numbers + `"currency": "EUR"`; all formatting happens in the site. Drop `std_geoid`, `minority_pct`, `black_pct`. (spec §5)
- **Headlines are derived from the per-parcel frame** (`output/<name>.csv`), the single source of truth — *not* the `metrics_<commune>.csv`, whose columns are mislabeled `_usd` though values are euros. The metrics CSV is used only as an optional cross-check. (resolves spec §12 open question)
- **Validation is a check, never a calibration target.** Report poor correlation as-is; degrade missing sources to `"non disponible"`, never fabricate. (spec §5b, §11)
- **Verify every external source live before coding against it** — re-confirm the INSEE selector and cadastre URLs at implementation. (`lvtshift-fr/CLAUDE.md`)
- **Windows:** run Python with `PYTHONUTF8=1`.
- **Commune name → slug:** `cfg.name.lower().replace(" ", "")` (matches `run_pipeline.py`). The CSV lives at `output/<slug>.csv`; the JSON key is the `COMMUNES` dict key (e.g. `"larochelle"` config key vs `larochelle.csv`).

---

## File Structure

- `lvtshift-fr/config.py` — **modify**: add Sète, La Rochelle, Mulhouse to `COMMUNES`; add dépts 34/17/68 to `AG_EUR_M2_BY_DEP`.
- `lvtshift-fr/export_web.py` — **create**: pure aggregation functions + JSON assembly + CLI.
- `lvtshift-fr/validate_external.py` — **create**: external benchmarks + cadastre cross-source check + JSON assembly.
- `lvtshift-fr/test_export_web.py` — **create**: unit tests (pytest, plain asserts, matching repo style).
- `lvtshift-fr/test_validate_external.py` — **create**: unit tests.
- Output (gitignored CSVs stay; **JSON ships**): `lvtshift-fr/site/public/data/<commune>.json`, `index.json`, `<commune>.validation.json`; cache in `lvtshift-fr/output/validation_cache/`.

Run all tests with: `PYTHONUTF8=1 python -m pytest test_export_web.py test_validate_external.py -v` from `lvtshift-fr/`.

---

### Task 1: Register the three new communes

**Files:**
- Modify: `lvtshift-fr/config.py` (communes block ~line 113-138; `AG_EUR_M2_BY_DEP` ~line 154-162)
- Test: `lvtshift-fr/test_units.py` (append)

**Interfaces:**
- Produces: `config.COMMUNES["sete"|"larochelle"|"mulhouse"]` → `CommuneConfig`; ten entries total. New `AG_EUR_M2_BY_DEP` keys `"34"`, `"17"`, `"68"`.

- [ ] **Step 1: Write the failing test** — append to `test_units.py`:

```python
def test_commune_slate_is_complete():
    from config import COMMUNES, AG_EUR_M2_BY_DEP
    expected = {
        "roubaix": ("59512", "59"), "montreuil": ("93048", "93"),
        "villeurbanne": ("69266", "69"), "grenoble": ("38185", "38"),
        "annemasse": ("74012", "74"), "cahors": ("46042", "46"),
        "figeac": ("46102", "46"), "sete": ("34301", "34"),
        "larochelle": ("17300", "17"), "mulhouse": ("68224", "68"),
    }
    assert set(COMMUNES) == set(expected), "slate must be exactly the 10 pilot communes"
    for key, (insee, dep) in expected.items():
        assert COMMUNES[key].insee_code == insee
        assert COMMUNES[key].departement == dep
    for dep in ("34", "17", "68"):
        assert dep in AG_EUR_M2_BY_DEP, f"missing agricultural rate for dep {dep}"
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_units.py::test_commune_slate_is_complete -v`
Expected: FAIL — `KeyError`/`AssertionError` (sete/larochelle/mulhouse absent).

- [ ] **Step 3: Add the three communes** — in `config.py`, after the `FIGEAC = ...` line:

```python
SETE = CommuneConfig(               # Méditerranée — port/tourist, second homes
    "34301", "Sète", "34", construction_cost_eur_m2=1850.0)
LA_ROCHELLE = CommuneConfig(        # Atlantique — prosperous tourist port
    "17300", "La Rochelle", "17", construction_cost_eur_m2=1850.0)
MULHOUSE = CommuneConfig(           # Est/Rhin — Alsatian post-industrial, vacant
    "68224", "Mulhouse", "68", construction_cost_eur_m2=1800.0)
```

Replace the `COMMUNES = {...}` dict with:

```python
COMMUNES = {
    "grenoble": GRENOBLE, "annemasse": ANNEMASSE,
    "villeurbanne": VILLEURBANNE, "roubaix": ROUBAIX, "cahors": CAHORS,
    "montreuil": MONTREUIL, "figeac": FIGEAC,
    "sete": SETE, "larochelle": LA_ROCHELLE, "mulhouse": MULHOUSE,
}
```

In `AG_EUR_M2_BY_DEP`, add three rows (SAFER « Le prix des terres » 2024 gradient — verify before publication):

```python
    "34": (0.80, 0.50),        # Hérault — Méditerranée, vignoble/maraîchage
    "17": (0.75, 0.45),        # Charente-Maritime — Atlantique cropland
    "68": (0.95, 0.55),        # Haut-Rhin — rich Alsatian plain
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `PYTHONUTF8=1 python -m pytest test_units.py::test_commune_slate_is_complete -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/config.py lvtshift-fr/test_units.py
git commit -m "Add Sète, La Rochelle, Mulhouse to the commune slate"
```

---

### Task 2: `export_web.py` — headline + improvement-ratio buckets

**Files:**
- Create: `lvtshift-fr/export_web.py`
- Test: `lvtshift-fr/test_export_web.py`

**Interfaces:**
- Produces: `load_parcels(commune_key: str, out_dir: str="output") -> pd.DataFrame`; `build_headline(df: pd.DataFrame) -> dict`; `build_buckets(df: pd.DataFrame) -> list[dict]`.
- Consumes: per-parcel CSV columns `property_category, current_tax, new_tax, tax_change, tax_change_pct, taxable_land_value, taxable_improvement_value, is_fully_exempt, median_income`.

- [ ] **Step 1: Write the failing test** — create `test_export_web.py`:

```python
import json
import numpy as np
import pandas as pd
import pytest
import export_web as ew


def _toy_df():
    return pd.DataFrame({
        "property_category": ["Single Family Residential", "Vacant Land",
                               "Commercial", "Condominium"],
        "current_tax": [1000.0, 50.0, 2000.0, 800.0],
        "new_tax":     [900.0, 400.0, 1900.0, 850.0],
        "tax_change":  [-100.0, 350.0, -100.0, 50.0],
        "tax_change_pct": [-10.0, 700.0, -5.0, 6.25],
        "taxable_land_value":        [50000.0, 80000.0, 120000.0, 40000.0],
        "taxable_improvement_value": [150000.0, 0.0, 180000.0, 110000.0],
        "is_fully_exempt": [False, False, False, False],
        "median_income": [22000.0, 22000.0, 35000.0, 35000.0],
    })


def test_build_headline_basic():
    h = ew.build_headline(_toy_df())
    assert h["parcels_modeled"] == 4
    assert h["land_base_eur"] == 290000.0
    assert h["improvement_base_eur"] == 440000.0
    assert h["tax_base_eur"] == 730000.0
    assert h["neutral_levy_eur"] == 4050.0          # Σ new_tax
    assert h["gross_shifted_eur"] == 600.0          # Σ|Δ|
    assert h["net_shifted_eur"] == 400.0            # Σ Δ>0
    assert h["land_share_pct"] == 39.7
    assert h["gross_pct_of_levy"] == 14.8
    assert h["currency"] == "EUR"


def test_build_buckets_partition_and_sum():
    buckets = ew.build_buckets(_toy_df())
    assert [b["bucket"] for b in buckets] == ["vacant", "lt10", "r10_25", "r25_50", "ge50"]
    assert sum(b["parcels"] for b in buckets) == 4
    # Vacant Land has 0 improvement -> 1 parcel in the vacant bucket
    assert next(b for b in buckets if b["bucket"] == "vacant")["parcels"] == 1
    assert abs(sum(b["value_pct_of_base"] for b in buckets) - 100.0) < 0.5
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'export_web'`.

- [ ] **Step 3: Write the minimal implementation** — create `export_web.py`:

```python
"""Aggregate-only JSON exporter for the « Pour une terre productive » site.

Reads the authoritative per-parcel standard export (output/<slug>.csv) and emits
aggregates by category, income quintile and improvement-ratio bucket, plus a
±10 pt land-share sensitivity band re-solved through the unmodified upstream
solver. Never emits per-parcel rows. See docs/superpowers/specs/
2026-06-24-advocacy-site-design.md §5.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Upstream `lvt` lives at the repo root (parent of lvtshift-fr/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard-category -> French display label (mirrors run_pipeline.CATEGORY_MAP).
CATEGORY_LABELS_FR = {
    "Single Family Residential": "Maison individuelle",
    "Condominium": "Appartement (copropriété)",
    "Large Multi-Family (5+ units)": "Immeuble collectif (5+ logements)",
    "Commercial": "Commerce",
    "Industrial": "Industriel",
    "Vacant Land": "Terrain nu / non bâti",
    "Other": "Autre / dépendance",
    "other": "Autre / dépendance",
}
FR_RESIDENTIAL = {
    "Single Family Residential", "Condominium", "Large Multi-Family (5+ units)",
}


def load_parcels(commune_key: str, out_dir: str = "output") -> pd.DataFrame:
    """Read the per-parcel standard export for one commune (modeled parcels only)."""
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    slug = cfg.name.lower().replace(" ", "")
    path = Path(out_dir) / f"{slug}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"No model output for {commune_key} at {path}; "
            f"run `python run_commune.py {commune_key}` first.")
    df = pd.read_csv(path)
    if "is_fully_exempt" in df.columns:
        df = df[~df["is_fully_exempt"].fillna(False).astype(bool)].copy()
    return df


def _pct(num: float, den: float, ndigits: int = 1):
    return round(100.0 * num / den, ndigits) if den else None


def build_headline(df: pd.DataFrame) -> dict:
    land = float(df["taxable_land_value"].sum())
    imp = float(df["taxable_improvement_value"].sum())
    base = land + imp
    levy = float(df["new_tax"].sum())
    gross = float(df["tax_change"].abs().sum())
    net = float(df.loc[df["tax_change"] > 0, "tax_change"].sum())
    return {
        "parcels_modeled": int(len(df)),
        "tax_base_eur": base,
        "land_base_eur": land,
        "improvement_base_eur": imp,
        "land_share_pct": _pct(land, base),
        "neutral_levy_eur": levy,
        "gross_shifted_eur": gross,
        "net_shifted_eur": net,
        "gross_pct_of_levy": _pct(gross, levy),
        "net_pct_of_levy": _pct(net, levy),
        "gross_bps_of_base": round(10000.0 * gross / base, 1) if base else None,
        "currency": "EUR",
    }


def build_buckets(df: pd.DataFrame) -> list:
    base_series = df["taxable_land_value"] + df["taxable_improvement_value"]
    total_base = float(base_series.sum())
    total_gross = float(df["tax_change"].abs().sum())
    ratio = (df["taxable_improvement_value"] / base_series.replace(0, np.nan)).fillna(0.0)
    specs = [
        ("vacant", "Terrain nu (0 %)", ratio == 0),
        ("lt10", "Très sous-bâti (<10 %)", (ratio > 0) & (ratio < 0.10)),
        ("r10_25", "Sous-bâti (10–25 %)", (ratio >= 0.10) & (ratio < 0.25)),
        ("r25_50", "Sous-bâti (25–50 %)", (ratio >= 0.25) & (ratio < 0.50)),
        ("ge50", "Bâti (≥50 %)", ratio >= 0.50),
    ]
    out = []
    for key, label, mask in specs:
        sub = df[mask]
        val = float((sub["taxable_land_value"] + sub["taxable_improvement_value"]).sum())
        gross = float(sub["tax_change"].abs().sum())
        out.append({
            "bucket": key, "label": label, "parcels": int(mask.sum()),
            "value_eur": val,
            "value_pct_of_base": _pct(val, total_base),
            "share_of_gross_change_pct": _pct(gross, total_gross),
        })
    return out
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -v`
Expected: PASS (both tests).

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/export_web.py lvtshift-fr/test_export_web.py
git commit -m "export_web: headline + improvement-ratio buckets from per-parcel frame"
```

---

### Task 3: `export_web.py` — by-category (win/lose) + income quintiles

**Files:**
- Modify: `lvtshift-fr/export_web.py`
- Test: `lvtshift-fr/test_export_web.py` (append)

**Interfaces:**
- Produces: `build_by_category(df) -> list[dict]` (sorted by parcels desc; each dict has `category, label_fr, parcels, share_of_parcels_pct, median_change_pct, median_change_eur, count_paying_more, share_paying_more_pct`); `build_by_income_quintile(df) -> list[dict] | None`.

- [ ] **Step 1: Write the failing test** — append to `test_export_web.py`:

```python
def test_by_category_win_lose_honest():
    cats = {c["category"]: c for c in ew.build_by_category(_toy_df())}
    sfr = cats["Single Family Residential"]
    assert sfr["label_fr"] == "Maison individuelle"
    assert sfr["count_paying_more"] == 0          # −100 € → pays less
    assert sfr["share_paying_more_pct"] == 0.0
    vac = cats["Vacant Land"]
    assert vac["count_paying_more"] == 1          # +350 € → pays more
    assert vac["share_paying_more_pct"] == 100.0


def test_income_quintile_none_when_no_income():
    df = _toy_df()
    df["median_income"] = np.nan
    assert ew.build_by_income_quintile(df) is None


def test_income_quintile_returns_bins_when_present():
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "property_category": np.where(rng.random(200) < 0.7,
                                      "Single Family Residential", "Commercial"),
        "current_tax": rng.uniform(500, 2000, 200),
        "tax_change": rng.uniform(-200, 200, 200),
        "tax_change_pct": rng.uniform(-20, 20, 200),
        "median_income": rng.uniform(18000, 40000, 200),
    })
    q = ew.build_by_income_quintile(df)
    assert q is not None and len(q) == 5
    assert [r["quintile"] for r in q] == [1, 2, 3, 4, 5]
    assert all("median_change_pct_residential" in r for r in q)
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -k "category or quintile" -v`
Expected: FAIL — `AttributeError: module 'export_web' has no attribute 'build_by_category'`.

- [ ] **Step 3: Write the implementation** — append to `export_web.py`:

```python
def build_by_category(df: pd.DataFrame) -> list:
    n = len(df)
    out = []
    for cat, sub in df.groupby("property_category"):
        chg_pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        out.append({
            "category": cat,
            "label_fr": CATEGORY_LABELS_FR.get(cat, str(cat)),
            "parcels": int(len(sub)),
            "share_of_parcels_pct": _pct(len(sub), n),
            "median_change_pct": round(float(chg_pct.median()), 1) if len(chg_pct) else None,
            "median_change_eur": round(float(sub["tax_change"].median()), 0),
            "count_paying_more": int((sub["tax_change"] > 0).sum()),
            "share_paying_more_pct": _pct(int((sub["tax_change"] > 0).sum()), len(sub)),
        })
    out.sort(key=lambda r: r["parcels"], reverse=True)
    return out


def build_by_income_quintile(df: pd.DataFrame):
    if "median_income" not in df.columns or df["median_income"].notna().sum() == 0:
        return None
    d = df[df["median_income"].notna()].copy()
    try:
        d["_q"] = pd.qcut(d["median_income"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    except ValueError:
        return None
    if d["_q"].nunique() < 5:
        return None
    res = d[d["property_category"].isin(FR_RESIDENTIAL)]
    out = []
    for q in [1, 2, 3, 4, 5]:
        sub = d[d["_q"] == q]
        rsub = res[res["_q"] == q]
        sub_pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        res_pct = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        out.append({
            "quintile": int(q),
            "median_income_eur": round(float(sub["median_income"].median()), 0),
            "median_change_pct": round(float(sub_pct.median()), 1) if len(sub_pct) else None,
            "median_change_pct_residential": round(float(res_pct.median()), 1) if len(res_pct) else None,
            "parcels": int(len(sub)),
        })
    return out
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -v`
Expected: PASS (all tests so far).

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/export_web.py lvtshift-fr/test_export_web.py
git commit -m "export_web: by-category win/lose split and income-quintile gradient"
```

---

### Task 4: `export_web.py` — ±10 pt land-share sensitivity band (re-solve)

**Files:**
- Modify: `lvtshift-fr/export_web.py`
- Test: `lvtshift-fr/test_export_web.py` (append)

**Interfaces:**
- Produces: `build_headline_sensitivity(df, ratio: float, delta_pt: float=10.0) -> dict` with keys `delta_pt, base, low, high`; each of `base/low/high` is a dict with `land_share_pct, gross_pct_of_levy, net_pct_of_levy, median_change_pct_residential, share_paying_more_pct`.
- Consumes: upstream `lvt.lvt_utils.model_split_rate_tax(df, land_value_col, improvement_value_col, current_revenue, land_improvement_ratio) -> (land_mill, imp_mill, revenue, df_with_new_tax)`.

**Why this matters (plain terms):** every published headline must carry a band — "if land is worth 10 points more/less of total value, the picture looks like this." We hold total value and total revenue fixed, tilt the land/improvement split, and re-run the *same* upstream solver, so the band is honest and reproducible.

- [ ] **Step 1: Write the failing test** — append to `test_export_web.py`:

```python
def test_sensitivity_brackets_base_through_real_solver():
    df = _toy_df()
    s = ew.build_headline_sensitivity(df, ratio=4.0, delta_pt=10.0)
    assert set(s) == {"delta_pt", "base", "low", "high"}
    # land share ordering: low < base < high
    assert s["low"]["land_share_pct"] < s["base"]["land_share_pct"] < s["high"]["land_share_pct"]
    # re-solving at the base share reproduces the original gross within rounding
    h = ew.build_headline(df)
    assert abs(s["base"]["gross_pct_of_levy"] - h["gross_pct_of_levy"]) < 1.0
    for leg in ("base", "low", "high"):
        assert "median_change_pct_residential" in s[leg]
        assert "share_paying_more_pct" in s[leg]
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py::test_sensitivity_brackets_base_through_real_solver -v`
Expected: FAIL — `AttributeError: ... 'build_headline_sensitivity'`.

- [ ] **Step 3: Write the implementation** — append to `export_web.py`:

```python
def _resolve_at_land_share(df: pd.DataFrame, target_share: float,
                           ratio: float, current_revenue: float) -> dict:
    """Re-solve the split-rate model with the aggregate land share tilted to
    `target_share`, holding total base and revenue fixed. Uniform per-parcel
    scaling preserves the relative structure of land vs improvement values."""
    from lvt.lvt_utils import model_split_rate_tax
    land = df["taxable_land_value"].to_numpy(dtype=float)
    imp = df["taxable_improvement_value"].to_numpy(dtype=float)
    current = df["current_tax"].to_numpy(dtype=float)
    base = float((land + imp).sum())
    s = float(land.sum()) / base
    f_land = target_share / s
    f_imp = (1.0 - target_share) / (1.0 - s)
    tmp = pd.DataFrame({"_land": land * f_land, "_imp": imp * f_imp})
    _lm, _im, _rev, solved = model_split_rate_tax(
        df=tmp, land_value_col="_land", improvement_value_col="_imp",
        current_revenue=current_revenue, land_improvement_ratio=ratio)
    chg = solved["new_tax"].to_numpy(dtype=float) - current
    gross = float(np.abs(chg).sum())
    net = float(chg[chg > 0].sum())
    res_mask = df["property_category"].isin(FR_RESIDENTIAL).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        res_pct = 100.0 * chg[res_mask] / current[res_mask]
    res_pct = pd.Series(res_pct).replace([np.inf, -np.inf], np.nan).dropna()
    return {
        "land_share_pct": round(100.0 * target_share, 1),
        "gross_pct_of_levy": _pct(gross, current_revenue),
        "net_pct_of_levy": _pct(net, current_revenue),
        "median_change_pct_residential": round(float(res_pct.median()), 1) if len(res_pct) else None,
        "share_paying_more_pct": _pct(int((chg > 0).sum()), len(chg)),
    }


def build_headline_sensitivity(df: pd.DataFrame, ratio: float, delta_pt: float = 10.0) -> dict:
    current_revenue = float(df["current_tax"].sum())
    land = float(df["taxable_land_value"].sum())
    base = land + float(df["taxable_improvement_value"].sum())
    s = land / base
    d = delta_pt / 100.0
    lo = min(0.99, max(0.01, s - d))
    hi = min(0.99, max(0.01, s + d))
    return {
        "delta_pt": delta_pt,
        "base": _resolve_at_land_share(df, s, ratio, current_revenue),
        "low": _resolve_at_land_share(df, lo, ratio, current_revenue),
        "high": _resolve_at_land_share(df, hi, ratio, current_revenue),
    }
```

- [ ] **Step 4: Run the test to confirm it passes**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py::test_sensitivity_brackets_base_through_real_solver -v`
Expected: PASS. (If `model_split_rate_tax` import fails, confirm `lvt/` exists at the repo root and the `sys.path.insert` in `export_web.py` resolves to it.)

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/export_web.py lvtshift-fr/test_export_web.py
git commit -m "export_web: ±10pt land-share sensitivity band via the real solver"
```

---

### Task 5: `export_web.py` — assemble JSON, aggregation guard, index, CLI

**Files:**
- Modify: `lvtshift-fr/export_web.py`
- Test: `lvtshift-fr/test_export_web.py` (append)

**Interfaces:**
- Produces: `build_commune_payload(commune_key, out_dir="output") -> dict`; `assert_aggregate_only(payload) -> None` (raises `AssertionError` on violation); `export_commune(commune_key, out_dir="output", data_dir="site/public/data") -> Path`; `export_all(out_dir="output", data_dir="site/public/data") -> dict`.

- [ ] **Step 1: Write the failing test** — append to `test_export_web.py`:

```python
def test_aggregate_guard_rejects_per_parcel_and_forbidden_tokens():
    good = {
        "commune_key": "x", "insee": "1", "name": "X", "departement": "1",
        "reference_year": 2025, "model_type": "split_rate:4.0",
        "headline": {"currency": "EUR"}, "headline_sensitivity": {},
        "by_category": [], "by_income_quintile": None,
        "by_improvement_ratio": [], "provenance": {}, "currency": "EUR",
    }
    ew.assert_aggregate_only(good)                 # no raise

    with pytest.raises(AssertionError):
        bad = dict(good); bad["parcels_detail"] = [{"id": 1}]   # stray per-parcel array
        ew.assert_aggregate_only(bad)

    with pytest.raises(AssertionError):
        leak = dict(good); leak["provenance"] = {"note": "std_geoid leaked"}
        ew.assert_aggregate_only(leak)


def test_payload_assembles_for_toy(monkeypatch, tmp_path):
    # write a toy commune CSV and point load_parcels at it via a fake config
    import config
    df = _toy_df()
    (tmp_path / "x.csv").write_text(df.to_csv(index=False), encoding="utf-8")

    class _Cfg:
        insee_code, name, departement, reference_year, split_rate_ratio = \
            "00000", "X", "00", 2025, 4.0
        construction_cost_eur_m2 = 1900.0
        land_share_bounds = (0.15, 0.85)
    monkeypatch.setitem(config.COMMUNES, "x", _Cfg())

    payload = ew.build_commune_payload("x", out_dir=str(tmp_path))
    ew.assert_aggregate_only(payload)
    assert payload["headline"]["parcels_modeled"] == 4
    assert payload["by_income_quintile"] is None   # only 2 distinct incomes
    blob = json.dumps(payload, ensure_ascii=False)
    for bad in ("$", "_usd", "minority_pct", "black_pct", "std_geoid"):
        assert bad not in blob
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -k "guard or assembles" -v`
Expected: FAIL — `assert_aggregate_only` / `build_commune_payload` not defined.

- [ ] **Step 3: Write the implementation** — append to `export_web.py`:

```python
ALLOWED_TOP_KEYS = {
    "commune_key", "insee", "name", "departement", "reference_year",
    "model_type", "headline", "headline_sensitivity", "by_category",
    "by_income_quintile", "by_improvement_ratio", "provenance", "currency",
}
FORBIDDEN_TOKENS = ("std_geoid", "minority_pct", "black_pct", "_usd", "$")


def assert_aggregate_only(payload: dict) -> None:
    """Shape guard: only aggregate keys, bounded lists, no US/per-parcel leakage."""
    extra = set(payload) - ALLOWED_TOP_KEYS
    assert not extra, f"unexpected top-level keys (possible per-parcel leak): {extra}"
    assert len(payload["by_improvement_ratio"]) <= 5
    assert len(payload["by_category"]) <= 10
    if payload["by_income_quintile"] is not None:
        assert len(payload["by_income_quintile"]) <= 5
    blob = json.dumps(payload, ensure_ascii=False)
    for tok in FORBIDDEN_TOKENS:
        assert tok not in blob, f"forbidden token {tok!r} leaked into payload"


def build_commune_payload(commune_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    df = load_parcels(commune_key, out_dir)
    return {
        "commune_key": commune_key,
        "insee": cfg.insee_code,
        "name": cfg.name,
        "departement": cfg.departement,
        "reference_year": getattr(cfg, "reference_year", None),
        "model_type": f"split_rate:{cfg.split_rate_ratio}",
        "headline": build_headline(df),
        "headline_sensitivity": build_headline_sensitivity(df, cfg.split_rate_ratio),
        "by_category": build_by_category(df),
        "by_income_quintile": build_by_income_quintile(df),
        "by_improvement_ratio": build_buckets(df),
        "provenance": {
            "construction_cost_eur_m2": cfg.construction_cost_eur_m2,
            "land_share_bounds": list(cfg.land_share_bounds),
            "note": ("Agrégats uniquement — imputations honnêtes au niveau "
                     "catégorie/quintile, jamais à la parcelle."),
        },
        "currency": "EUR",
    }


def export_commune(commune_key: str, out_dir: str = "output",
                   data_dir: str = "site/public/data") -> Path:
    payload = build_commune_payload(commune_key, out_dir)
    assert_aggregate_only(payload)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(data_dir) / f"{commune_key}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_all(out_dir: str = "output", data_dir: str = "site/public/data") -> dict:
    from config import COMMUNES
    index = []
    for key, cfg in COMMUNES.items():
        slug = cfg.name.lower().replace(" ", "")
        if not (Path(out_dir) / f"{slug}.csv").exists():
            continue
        export_commune(key, out_dir, data_dir)
        h = build_headline(load_parcels(key, out_dir))
        index.append({
            "commune_key": key, "name": cfg.name, "insee": cfg.insee_code,
            "departement": cfg.departement,
            "parcels_modeled": h["parcels_modeled"],
            "land_share_pct": h["land_share_pct"],
            "gross_pct_of_levy": h["gross_pct_of_levy"],
        })
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / "index.json").write_text(
        json.dumps({"communes": index, "currency": "EUR"}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return {"exported": [c["commune_key"] for c in index]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Export aggregate JSON for the advocacy site.")
    ap.add_argument("commune", nargs="?", help="commune key; omit to export all available")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--data-dir", default="site/public/data")
    a = ap.parse_args()
    if a.commune:
        print("wrote", export_commune(a.commune, a.out_dir, a.data_dir))
    else:
        print(export_all(a.out_dir, a.data_dir))
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `PYTHONUTF8=1 python -m pytest test_export_web.py -v`
Expected: PASS (whole file).

- [ ] **Step 5: Generate the real JSON for the already-modeled communes and eyeball it**

Run (from `lvtshift-fr/`): `PYTHONUTF8=1 python export_web.py`
Expected: writes `site/public/data/{grenoble,cahors,montreuil,roubaix}.json` (whichever CSVs exist) + `index.json`. Open `grenoble.json` and confirm: `headline.land_share_pct` ≈ 72, `currency: "EUR"` throughout, no `$`/`_usd`.

- [ ] **Step 6: Commit**

```bash
git add lvtshift-fr/export_web.py lvtshift-fr/test_export_web.py
git commit -m "export_web: payload assembly, aggregation guard, index.json, CLI"
```

---

### Task 6: `validate_external.py` — independent benchmarks + cadastre cross-source check

**Files:**
- Create: `lvtshift-fr/validate_external.py`
- Test: `lvtshift-fr/test_validate_external.py`

**Interfaces:**
- Produces:
  - `land_share_band_check(land_share_pct: float, band=(40.0, 65.0)) -> dict` — `{model_land_share_pct, band, within_band, independence}`.
  - `building_agreement_rate(parcels_gdf, buildings_gdf) -> dict` — pure spatial helper → `{cadastre_built_share_pct, n_parcels, n_buildings}`.
  - `fetch_insee_vacancy(insee_code: str, cache_dir="output/validation_cache") -> float | None` — best-effort; `None` on any failure.
  - `validate_commune(commune_key, df, cfg, cache_dir="output/validation_cache", data_dir="site/public/data", insee_vacancy=None, cadastre=None) -> dict` — assembles + writes `<commune>.validation.json`. Network args are injectable so tests stay offline.
- Consumes: `export_web.build_headline`, `build_buckets`; `config.COMMUNES`.

**Honesty note baked in:** the cadastre check is labelled `"data-quality"`, *not* `"independent"` economic validation — the model already ingests cadastre *parcelles*; only the unused DGFiP `batiments` layer is a genuinely separate building map vs IGN BD TOPO (spec §5b).

- [ ] **Step 1: Write the failing test** — create `test_validate_external.py`:

```python
import json
import pandas as pd
import pytest
import validate_external as ve


def test_land_share_band_check():
    inside = ve.land_share_band_check(50.0, band=(40.0, 65.0))
    assert inside["within_band"] is True
    assert inside["independence"] == "independent"
    outside = ve.land_share_band_check(80.0, band=(40.0, 65.0))
    assert outside["within_band"] is False


def test_building_agreement_rate_on_fixture():
    from shapely.geometry import Polygon
    import geopandas as gpd
    # three unit-square parcels; buildings overlap parcels 0 and 1 only
    parcels = gpd.GeoDataFrame(geometry=[
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
        Polygon([(4, 0), (5, 0), (5, 1), (4, 1)]),
    ], crs="EPSG:2154")
    buildings = gpd.GeoDataFrame(geometry=[
        Polygon([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]),
        Polygon([(2.2, 0.2), (2.8, 0.2), (2.8, 0.8), (2.2, 0.8)]),
    ], crs="EPSG:2154")
    r = ve.building_agreement_rate(parcels, buildings)
    assert r["n_parcels"] == 3 and r["n_buildings"] == 2
    assert abs(r["cadastre_built_share_pct"] - 66.7) < 0.2


def test_validate_commune_degrades_gracefully(tmp_path):
    df = pd.DataFrame({
        "property_category": ["Vacant Land", "Single Family Residential"],
        "current_tax": [50.0, 1000.0], "new_tax": [200.0, 850.0],
        "tax_change": [150.0, -150.0], "tax_change_pct": [300.0, -15.0],
        "taxable_land_value": [80000.0, 50000.0],
        "taxable_improvement_value": [0.0, 150000.0],
    })

    class _Cfg:
        insee_code, name, departement = "00000", "X", "00"

    # both network inputs unavailable -> reported "non disponible", no raise
    out = ve.validate_commune("x", df, _Cfg(), cache_dir=str(tmp_path),
                              data_dir=str(tmp_path), insee_vacancy=None, cadastre=None)
    statuses = {c["benchmark"]: c["status"] for c in out["checks"]}
    assert any(s == "non disponible" for s in statuses.values())
    # land-share band is computable offline -> always present
    assert any(c["independence"] == "independent" and c["status"] != "non disponible"
               for c in out["checks"])
    assert (tmp_path / "x.validation.json").exists()
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `PYTHONUTF8=1 python -m pytest test_validate_external.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'validate_external'`.

- [ ] **Step 3: Write the implementation** — create `validate_external.py`:

```python
"""External validation for the « Pour une terre productive » site.

Confronts the model's aggregates with *independent* open benchmarks (INSEE
housing vacancy, a national land-share band) and a *data-quality* cross-source
check (DGFiP cadastre `batiments` vs IGN BD TOPO — agreement on which parcels
are built). A check, NEVER a calibration target: missing sources degrade to
"non disponible", never fabricated. See spec §5b.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import export_web as ew

INSEE_DOSSIER_URL = "https://www.insee.fr/fr/statistiques/2011101?geo=COM-{insee}"
CADASTRE_BATIMENTS_URL = (
    "https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/"
    "geojson/communes/{dep}/{insee}/cadastre-{insee}-batiments.json.gz")
CADASTRE_PARCELLES_URL = (
    "https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/"
    "geojson/communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz")


def land_share_band_check(land_share_pct: float, band=(40.0, 65.0)) -> dict:
    lo, hi = band
    return {
        "benchmark": "Part du foncier dans la valeur (ancrage national)",
        "independence": "independent",
        "model_land_share_pct": land_share_pct,
        "band": [lo, hi],
        "within_band": (land_share_pct is not None) and (lo <= land_share_pct <= hi),
        "status": "ok" if (land_share_pct is not None and lo <= land_share_pct <= hi) else "flag",
        "note": ("Ancrage INSEE comptes de patrimoine ~45–50 % national ; "
                 "bande élargie (cœurs denses plus haut). Pas de cible par commune."),
    }


def building_agreement_rate(parcels_gdf, buildings_gdf) -> dict:
    """Share of parcels intersecting at least one cadastre building footprint."""
    import geopandas as gpd
    if buildings_gdf.crs != parcels_gdf.crs:
        buildings_gdf = buildings_gdf.to_crs(parcels_gdf.crs)
    joined = gpd.sjoin(parcels_gdf, buildings_gdf, how="left", predicate="intersects")
    built = joined.index_right.notna().groupby(level=0).any()
    n_parcels = len(parcels_gdf)
    return {
        "cadastre_built_share_pct": round(100.0 * float(built.sum()) / n_parcels, 1) if n_parcels else None,
        "n_parcels": int(n_parcels),
        "n_buildings": int(len(buildings_gdf)),
    }


def _read_geojson_gz(url: str):
    """Fetch a gzipped GeoJSON into a GeoDataFrame, or None on any failure."""
    import io, gzip, urllib.request
    import geopandas as gpd
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            raw = gzip.decompress(resp.read())
        return gpd.read_file(io.BytesIO(raw))
    except Exception as exc:  # network / parse / empty — degrade
        print(f"  [validate] cadastre fetch failed for {url}: {exc}")
        return None


def fetch_cadastre_agreement(cfg, cache_dir="output/validation_cache"):
    """Live cadastre batiments-vs-parcelles agreement; None if unavailable."""
    p = _read_geojson_gz(CADASTRE_PARCELLES_URL.format(dep=cfg.departement, insee=cfg.insee_code))
    b = _read_geojson_gz(CADASTRE_BATIMENTS_URL.format(dep=cfg.departement, insee=cfg.insee_code))
    if p is None or b is None or len(p) == 0:
        return None
    return building_agreement_rate(p.to_crs(2154), b.to_crs(2154))


def fetch_insee_vacancy(insee_code: str, cache_dir="output/validation_cache"):
    """Best-effort INSEE housing-vacancy %. None on any failure (degrade).

    NOTE: re-verify the page/selector live before trusting (sources move). The
    parser is intentionally defensive; a miss returns None, never an exception.
    """
    import re, urllib.request
    cache = Path(cache_dir) / f"insee_vacancy_{insee_code}.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        try:
            return float(cache.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
    try:
        req = urllib.request.Request(
            INSEE_DOSSIER_URL.format(insee=insee_code),
            headers={"User-Agent": "lvtshift-fr-validation/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"[Ll]ogements?\s+vacants?.{0,200}?(\d{1,2}[.,]\d)\s*%", html, re.S)
        if not m:
            return None
        val = float(m.group(1).replace(",", "."))
        cache.write_text(str(val), encoding="utf-8")
        return val
    except Exception as exc:
        print(f"  [validate] INSEE vacancy fetch failed for {insee_code}: {exc}")
        return None


def validate_commune(commune_key, df, cfg, cache_dir="output/validation_cache",
                     data_dir="site/public/data", insee_vacancy="__FETCH__",
                     cadastre="__FETCH__") -> dict:
    """Assemble + write <commune>.validation.json. Pass insee_vacancy/cadastre
    explicitly (incl. None) to stay offline in tests; default fetches live."""
    headline = ew.build_headline(df)
    buckets = ew.build_buckets(df)
    underused = sum(b["value_pct_of_base"] or 0 for b in buckets
                    if b["bucket"] in ("vacant", "lt10", "r10_25", "r25_50"))

    if insee_vacancy == "__FETCH__":
        insee_vacancy = fetch_insee_vacancy(cfg.insee_code, cache_dir)
    if cadastre == "__FETCH__":
        cadastre = fetch_cadastre_agreement(cfg, cache_dir)

    checks = []

    # 1) INSEE housing vacancy (independent, directional across communes)
    checks.append({
        "benchmark": "Vacance des logements (INSEE)",
        "independence": "independent",
        "external_value_pct": insee_vacancy,
        "model_comparable_pct": round(underused, 1),
        "model_comparable_label": "part sous-bâtie/vacante de la base (valeur)",
        "status": "non disponible" if insee_vacancy is None else "recorded",
        "note": ("Corrélation directionnelle entre communes (vacance INSEE vs "
                 "foncier sous-utilisé), pas une égalité par commune."),
    })

    # 2) National land-share band (independent)
    checks.append(land_share_band_check(headline["land_share_pct"]))

    # 3) Cadastre vs BD TOPO building map (data quality, NOT economic)
    model_built_share = round(
        100.0 * float((df["property_category"] != "Vacant Land").sum()) / len(df), 1) if len(df) else None
    if cadastre is None:
        checks.append({
            "benchmark": "Carte du bâti (cadastre DGFiP vs BD TOPO)",
            "independence": "data-quality",
            "status": "non disponible",
            "note": "Couche cadastre `batiments` non récupérée.",
        })
    else:
        cad = cadastre["cadastre_built_share_pct"]
        gap = abs((cad or 0) - (model_built_share or 0))
        checks.append({
            "benchmark": "Carte du bâti (cadastre DGFiP vs BD TOPO)",
            "independence": "data-quality",
            "cadastre_built_share_pct": cad,
            "model_built_share_pct": model_built_share,
            "n_parcels_cadastre": cadastre["n_parcels"],
            "n_buildings_cadastre": cadastre["n_buildings"],
            "gap_pt": round(gap, 1),
            "status": "ok" if gap <= 10.0 else "flag",
            "note": ("Accord entre deux cartes du bâti d'agences différentes ; "
                     "contrôle qualité de l'entrée 'bâti', pas de la valorisation."),
        })

    out = {
        "commune_key": commune_key, "insee": cfg.insee_code,
        "name": cfg.name, "departement": cfg.departement, "checks": checks,
    }
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / f"{commune_key}.validation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def validate_all(out_dir="output", cache_dir="output/validation_cache",
                 data_dir="site/public/data") -> dict:
    from config import COMMUNES
    done = []
    for key, cfg in COMMUNES.items():
        slug = cfg.name.lower().replace(" ", "")
        if not (Path(out_dir) / f"{slug}.csv").exists():
            continue
        df = ew.load_parcels(key, out_dir)
        validate_commune(key, df, cfg, cache_dir, data_dir)
        done.append(key)
    return {"validated": done}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="External validation -> validation JSON.")
    ap.add_argument("commune", nargs="?", help="commune key; omit to validate all available")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--data-dir", default="site/public/data")
    a = ap.parse_args()
    if a.commune:
        from config import COMMUNES
        df = ew.load_parcels(a.commune, a.out_dir)
        print(validate_commune(a.commune, df, COMMUNES[a.commune], data_dir=a.data_dir))
    else:
        print(validate_all(a.out_dir, data_dir=a.data_dir))
```

- [ ] **Step 4: Run the tests to confirm they pass**

Run: `PYTHONUTF8=1 python -m pytest test_validate_external.py -v`
Expected: PASS (all three tests).

- [ ] **Step 5: Live smoke-test on one commune (re-verify sources)**

Run: `PYTHONUTF8=1 python validate_external.py roubaix`
Expected: writes `site/public/data/roubaix.validation.json`. Confirm the cadastre check populates `cadastre_built_share_pct` and `n_buildings` (≈37,600 for Roubaix). If INSEE returns `null`, that's acceptable degradation — note it and re-check the selector. **Do not tune anything to the benchmark.**

- [ ] **Step 6: Commit**

```bash
git add lvtshift-fr/validate_external.py lvtshift-fr/test_validate_external.py
git commit -m "validate_external: INSEE vacancy, land-share band, cadastre cross-source check"
```

---

## Self-Review

**1. Spec coverage**

- §3 commune slate (3 new) → Task 1. ✔
- §5 data contract (headline, sensitivity, by_category w/ win-lose, by_income_quintile, by_improvement_ratio, provenance, currency, index.json) → Tasks 2–5. ✔
- §5 aggregation guard (shape check) → Task 5. ✔
- §5 currency cleanliness (no `$`/`_usd`) → Task 5 guard + Task 2 emit. ✔
- §5b external validation (INSEE vacancy independent; land-share band independent; €/m² partially-circular) → Task 6 covers INSEE + land-share + the cadastre data-quality check. **Gap: the market €/m² benchmark is *not* implemented here** — deliberately deferred (spec §12 marks the least-circular source as an open question to resolve with a live probe at implementation; it is bot-tolerance-dependent and partially circular). Flagged for a follow-up task once a source is chosen; the two independent checks plus the cadastre check stand without it.
- §10 testing layer 1 (aggregation-shape guard, headline-vs-source, golden snapshot) → guard ✔; headline-from-frame is the source of truth so the "headline equals metrics CSV" test is replaced by Task 5 Step 5 manual cross-check. **Golden snapshot** deferred to execution (write it once Task 5 produces real Grenoble JSON, to avoid hand-fabricating expected numbers — add as a skip-if-absent test).
- §10 testing layer 2 (external validation table, independent benchmarks within tolerance, €/m² recorded-not-gated) → Task 6 records all; cross-commune correlation test deferred until ≥4 communes validated.

**2. Placeholder scan:** No "TBD"/"add error handling"/"similar to Task N". All steps carry complete code. ✔

**3. Type consistency:** `build_headline` returns dict with `land_share_pct` used by `land_share_band_check` and `export_all` index ✔. `build_buckets` returns list with `bucket`/`value_pct_of_base` consumed by `validate_commune` ✔. `model_split_rate_tax` call matches the verified signature (4-tuple, `new_tax` column) ✔. `build_by_income_quintile` may return `None`, handled by guard ✔.

**Deferred-to-frontend-plan (not gaps here):** the market €/m² benchmark source decision, the cross-commune correlation report, and the golden snapshot are all small follow-ups that need real emitted JSON first; they are listed so they are not forgotten.

---

## Execution Handoff

(Filled by the skill after save.)
