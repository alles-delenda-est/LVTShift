"""Offline tests for the decomposition of the reform into three steps:
housing brought to market values, the land tax with today's exemptions, and
the end of the social housing exemptions (METHODOLOGY §3.6).

Run: python -m pytest -q test_revaluation.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import estimate  # noqa: E402

W = {"industrial": 3.0, "professional": 2.0, "housing": 1.0}


def _parcels():
    # two cheap flats blocks, two dear ones, a shop, a plant, an exempt school,
    # a vacant plot, and a social block exempt today
    return pd.DataFrame({
        "floor_area_m2":      [1000.0, 1000.0, 1000.0, 1000.0, 300.0, 2000.0, 800.0, 0.0, 1000.0],
        "floor_housing":      [1000.0, 1000.0, 800.0, 1000.0, 0.0, 0.0, 0.0, 0.0, 1000.0],
        "floor_professional": [0.0, 0.0, 200.0, 0.0, 300.0, 0.0, 0.0, 0.0, 0.0],
        "floor_industrial":   [0.0, 0.0, 0.0, 0.0, 0.0, 2000.0, 0.0, 0.0, 0.0],
        "market_value":       [2e6, 2e6, 8e6, 8e6, 1.2e6, 3e6, 4e6, 5e5, 2e6],
        "is_exempt_public":   [False] * 6 + [True, False, False],
        "hlm_tax_factor":     [1.0] * 8 + [0.0],
    })


def test_elasticity_zero_is_todays_tax():
    p = _parcels()
    today = estimate.current_tax(p, 1e6, bucket_weights=W)["current_tax"]
    assert np.allclose(estimate.revalued_tax(p, 1e6, 0.0, bucket_weights=W), today)


def test_only_housing_moves_and_dearer_flats_pay_more():
    p = _parcels()
    today = estimate.current_tax(p, 1e6, bucket_weights=W)["current_tax"]
    rev = estimate.revalued_tax(p, 1e6, 0.55, bucket_weights=W)
    assert rev.sum() == pytest.approx(1e6)
    # the plant and the shop keep their bills; the groups keep their amounts
    assert rev[[4, 5]].tolist() == pytest.approx(today[[4, 5]].tolist())
    # the mixed block keeps its professional part; its housing part moves
    # like the dear block's (same price per m², 800 m² of housing vs 1,000)
    prof2 = today[2] * (200 * W["professional"]) / (200 * W["professional"] + 800)
    assert (rev[2] - prof2) / rev[3] == pytest.approx(0.8)
    # four times the price per m² → 4^0.55 ≈ 2.1 times the housing weight
    assert rev[3] / rev[0] == pytest.approx(4 ** 0.55)
    assert rev[0] < today[0] and rev[3] > today[3]
    # exempt today stays exempt: the school, the vacant plot, the social block
    assert (rev[[6, 7, 8]] == 0).all()


def test_plain_baseline_and_missing_prices():
    p = _parcels().drop(columns=["floor_housing", "floor_professional", "floor_industrial"])
    rev = estimate.revalued_tax(p, 1e6, 0.5)
    assert rev.sum() == pytest.approx(1e6) and (rev[[6, 7, 8]] == 0).all()
    # a parcel without a usable price takes the median price, never zero
    q = p.assign(market_value=[np.nan] + list(p["market_value"][1:]))
    assert estimate.revalued_tax(q, 1e6, 0.5)[0] > 0
    for bad in (-0.1, 1.5, float("nan")):
        with pytest.raises(ValueError):
            estimate.revalued_tax(p, 1e6, bad)
    assert estimate.revalued_tax(p, 0.0, 0.5).sum() == 0.0


def test_taxable_share_today():
    p = _parcels().assign(hlm_tax_factor=[1.0] * 2 + [0.7] + [1.0] * 5 + [0.0])
    k = estimate.taxable_share_today(p)
    # mixed block: 80 % housing at the QPV factor 0.7 → 1 − 0.3 × 0.8
    assert k.tolist() == pytest.approx([1, 1, 0.76, 1, 1, 1, 1, 1, 0])
    assert (estimate.taxable_share_today(p.drop(columns="hlm_tax_factor")) == 1).all()


def test_pipeline_writes_the_three_steps_and_each_holds_the_levy(tmp_path):
    import run_pipeline as rp
    from test_farmland import _world
    parcels, buildings, dvf = _world()
    levy = 2_000_000.0
    out = rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path), make_report=False)
    side = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv")
    for col in ("revalued_tax", "new_tax_kept"):
        assert side[col].sum() == pytest.approx(levy) and (side[col] >= 0).all()
    # no social housing in this world: keeping its exemptions changes nothing
    assert np.allclose(side["new_tax_kept"], out["new_tax"])
    rec = json.loads((tmp_path / f"{rp.slug_of(rp.CFG)}.baseline.json").read_text())
    assert rec["revaluation"]["rent_price_elasticity"] == rp.REVALUATION["rent_price_elasticity"]
    # social housing exempt today: zero after the first two steps, taxed after
    p2 = parcels.assign(hlm_tax_factor=np.where(np.arange(len(parcels)) % 7 == 0, 0.0, 1.0))
    out2 = rp.run(p2, buildings, dvf, levy, out_dir=str(tmp_path / "s"), make_report=False)
    side2 = pd.read_csv(tmp_path / "s" / f"{rp.slug_of(rp.CFG)}.households.csv")
    social = (p2["hlm_tax_factor"] == 0).to_numpy() & (out2["current_tax"] == 0).to_numpy()
    built = (parcels["category_fr"] != "terrain_nu").to_numpy()
    sb = social & built & ~parcels["is_exempt_public"].to_numpy()
    assert sb.any()
    assert (side2.loc[sb, "revalued_tax"] == 0).all() and (side2.loc[sb, "new_tax_kept"] == 0).all()
    assert (out2.loc[sb, "new_tax"] > 0).all()


def test_export_publishes_the_steps_and_guards_them(tmp_path):
    import export_web as ew
    import run_pipeline as rp
    from config import COMMUNES
    from test_farmland import _world
    key = next(k for k, c in COMMUNES.items() if rp.slug_of(c) == rp.slug_of(rp.CFG))
    parcels, buildings, dvf = _world()
    rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False)
    df = ew.load_parcels(key, str(tmp_path))
    assert set(ew.STEP_TAX_COLS) <= set(df.columns)
    rows = ew.build_by_category(df)
    shown = [r for r in rows if r["total_change_pct"] is not None]
    assert shown
    for r in rows:
        vals = [r[k] for k in ew.STEP_KEYS]
        if r["step_revaluation_pct"] is not None:
            assert abs(sum(vals) - r["total_change_pct"]) <= 0.3
    ew._check_steps({"by_category": rows})
    # guards: partial steps, steps that do not add up, non-numbers
    good = {"parcels": 50, "total_change_pct": 5.0, "step_revaluation_pct": 2.0,
            "step_land_pct": 3.0, "step_exemptions_pct": 0.0}
    for bad in ({"by_category": [{**good, "total_change_pct": None}]},
                {"by_category": [{**good, "step_land_pct": 9.0}]},
                {"by_income_quintile": [{**good, "step_land_pct": "3"}]},
                {"by_income_quintile": [{**good, "step_land_pct": float("inf")}]}):
        with pytest.raises(AssertionError):
            ew._check_steps(bad)
    # a sidecar whose step bills do not hold the levy is refused
    side = tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv"
    s = pd.read_csv(side)
    s["revalued_tax"] = s["revalued_tax"] * 1.1
    s.to_csv(side, index=False)
    with pytest.raises(ValueError):
        ew.load_parcels(key, str(tmp_path))
