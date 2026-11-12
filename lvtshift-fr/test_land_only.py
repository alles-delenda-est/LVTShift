"""Offline tests for the land-only reform (the TVTN) and its building-cost band.

Run: python -m pytest -q test_land_only.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import run_pipeline as rp  # noqa: E402


def _frame():
    return pd.DataFrame({
        "land_value": [100_000.0, 100_000.0, 50_000.0, 80_000.0, 200_000.0],
        "improvement_value": [0.0, 900_000.0, 300_000.0, 0.0, 1_000_000.0],
        "outside_levy": [0, 0, 0, 0, 1],
    })


def test_land_only_taxes_land_alone():
    lm, im, rev, out = rp.solve_reform(_frame(), "land_value", "improvement_value",
                                       33_000.0, None, "outside_levy")
    assert im == 0.0 and rev == pytest.approx(33_000.0)
    # the same land pays the same, whatever stands on it
    assert out["new_tax"][0] == pytest.approx(out["new_tax"][1])
    assert out["new_tax"].tolist()[:4] == pytest.approx([10_000.0, 10_000.0, 5_000.0, 8_000.0])
    assert out["new_tax"][4] == 0.0
    # the bases are reported as the split-rate solver reports them
    assert out["taxable_improvement_value"].tolist() == [0.0, 900_000.0, 300_000.0, 0.0, 0.0]
    assert out["taxable_land_value"][4] == 0.0
    # a ratio still gives the split-rate model
    _lm, im4, _r, out4 = rp.solve_reform(_frame(), "land_value", "improvement_value",
                                         33_000.0, 4.0, "outside_levy")
    assert im4 > 0 and out4["new_tax"][1] > out4["new_tax"][0]


def test_pipeline_defaults_to_land_only(tmp_path):
    from test_farmland import _world
    parcels, buildings, dvf = _world()
    out = rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False)
    assert (out["model_type"] == "land_only").all()
    assert (out["improvement_millage"] == 0).all()
    inside = out["taxable_land_value"] > 0
    rate = out.loc[inside, "new_tax"] / out.loc[inside, "taxable_land_value"]
    assert np.allclose(rate, rate.iloc[0])               # one rate on land, nothing else
    assert out["new_tax"].sum() == pytest.approx(out["current_tax"].sum())
    side = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv")
    assert "iris" in side.columns and side["iris"].notna().all()


def _band_frame():
    # two IRIS; in "a" two identical built plots and a vacant one
    return pd.DataFrame({
        "taxable_land_value": [100.0, 100.0, 100.0, 300.0, 50.0],
        "taxable_improvement_value": [400.0, 400.0, 0.0, 300.0, 50.0],
        "current_tax": [10.0, 10.0, 5.0, 20.0, 5.0],
        "_iris": ["a", "a", "a", "b", "b"],
    })


def test_cost_shock_moves_built_land_by_iris():
    import export_web as ew
    d = _band_frame()
    assert np.allclose(ew._cost_shocked_land(d, 0.0), d["taxable_land_value"])
    up = ew._cost_shocked_land(d, 0.2)        # dearer buildings: less land
    # IRIS a: built land 200 − 0.2 × 800 = 40, each built plot 20, vacant unchanged;
    # IRIS b: 350 − 0.2 × 350 = 280, a factor of 0.8
    assert up.tolist() == pytest.approx([20.0, 20.0, 100.0, 240.0, 40.0])
    assert up[0] == up[1]                      # identical plots stay identical
    # never below zero, never above the parcel's whole value
    assert (ew._cost_shocked_land(d, 5.0) >= 0).all()
    dn = ew._cost_shocked_land(d, -5.0)
    assert dn[3] + dn[4] == pytest.approx(700.0)


def test_land_only_band_shifts_tax_to_vacant_land_when_buildings_cost_more():
    import export_web as ew
    d = _band_frame().assign(property_category=["Residential"] * 3 + ["Commercial"] * 2)
    rev = float(d["current_tax"].sum())
    base = ew._land_only_change(d, 0.0, rev) + d["current_tax"].to_numpy()
    low = ew._land_only_change(d, 0.2, rev) + d["current_tax"].to_numpy()
    assert low.sum() == pytest.approx(rev) and base.sum() == pytest.approx(rev)
    assert low[2] > base[2]                    # the vacant plot pays more
    assert ew._land_share_after(d, 0.2) < ew._land_share_after(d, 0.0) < ew._land_share_after(d, -0.2)
    # one IRIS of built parcels only: a uniform shock changes no bill
    mono = d.iloc[[0, 1]].assign(_iris="a")
    r2 = float(mono["current_tax"].sum())
    assert np.allclose(ew._land_only_change(mono, 0.2, r2), ew._land_only_change(mono, 0.0, r2))


def test_land_only_payload_carries_the_band_and_passes_the_guards(tmp_path):
    import export_web as ew
    from config import COMMUNES
    from test_farmland import _world
    key = next(k for k, c in COMMUNES.items() if rp.slug_of(c) == rp.slug_of(rp.CFG))
    parcels, buildings, dvf = _world()
    rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False)
    p = ew.build_commune_payload(key, str(tmp_path))
    ew.assert_aggregate_only(p)
    s = p["headline_sensitivity"]
    assert p["model_type"] == "land_only"
    assert s["kind"] == "building_cost" and s["delta_pct"] == 20
    assert s["low"]["land_share_pct"] < s["base"]["land_share_pct"] < s["high"]["land_share_pct"]
    blob = json.dumps(p)
    assert "_iris" not in blob


def test_review_fixes_model_check_blank_iris_and_zero_levy(tmp_path):
    import dataclasses
    import export_web as ew
    from config import COMMUNES
    from test_farmland import _world
    key = next(k for k, c in COMMUNES.items() if rp.slug_of(c) == rp.slug_of(rp.CFG))
    parcels, buildings, dvf = _world()
    # a run made as 4:1 is refused by an export whose config models land only
    rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False,
           cfg=dataclasses.replace(rp.CFG, split_rate_ratio=4.0))
    with pytest.raises(ValueError, match="re-run"):
        ew.load_parcels(key, str(tmp_path))
    # a blank IRIS (a territory member from an older run) is one group, not frozen
    d = _band_frame().assign(_iris=[np.nan] * 5)
    one = _band_frame().assign(_iris="x")
    assert np.allclose(ew._cost_shocked_land(d, 0.2), ew._cost_shocked_land(one, 0.2))
    assert not np.allclose(ew._cost_shocked_land(d, 0.2), d["taxable_land_value"])
    # a zero levy shares nothing, and never divides by it
    _lm, _im, rev, out = rp.solve_reform(_frame(), "land_value", "improvement_value",
                                         0.0, None, "outside_levy")
    assert rev == 0.0 and (out["new_tax"] == 0).all()
