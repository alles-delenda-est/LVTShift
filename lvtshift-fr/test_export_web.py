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


def test_sensitivity_brackets_base_through_real_solver():
    from lvt.lvt_utils import model_split_rate_tax
    # _toy_df()'s new_tax/tax_change are hand-crafted for the pure-arithmetic
    # tests (Tasks 2-3). The sensitivity check needs a *solver-consistent*
    # frame, because in production new_tax IS the solver's output. So re-solve
    # the toy land/improvement values through the real solver and rebuild the
    # change columns before asserting. (Do NOT change _toy_df itself.)
    df = _toy_df()
    _lm, _im, _rev, solved = model_split_rate_tax(
        df=df.copy(), land_value_col="taxable_land_value",
        improvement_value_col="taxable_improvement_value",
        current_revenue=float(df["current_tax"].sum()), land_improvement_ratio=4.0)
    df["new_tax"] = solved["new_tax"].to_numpy(dtype=float)
    df["tax_change"] = df["new_tax"] - df["current_tax"]
    df["tax_change_pct"] = 100.0 * df["tax_change"] / df["current_tax"]

    s = ew.build_headline_sensitivity(df, ratio=4.0, delta_pt=10.0)
    assert set(s) == {"delta_pt", "base", "low", "high"}
    # land share ordering: low < base < high
    assert s["low"]["land_share_pct"] < s["base"]["land_share_pct"] < s["high"]["land_share_pct"]
    # re-solving at the base share reproduces the headline gross within rounding
    h = ew.build_headline(df)
    assert abs(s["base"]["gross_pct_of_levy"] - h["gross_pct_of_levy"]) < 1.0
    for leg in ("base", "low", "high"):
        assert "median_change_pct_residential" in s[leg]
        assert "share_paying_more_pct" in s[leg]


def test_resolve_at_land_share_rejects_degenerate_share():
    # all-land (s==1) or all-improvement (s==0) makes uniform tilting undefined;
    # the guard must raise rather than silently propagate NaN through the solver.
    df = _toy_df()
    df["taxable_improvement_value"] = 0.0   # s == 1
    with pytest.raises(ValueError):
        ew._resolve_at_land_share(df, 0.5, 4.0, float(df["current_tax"].sum()))
