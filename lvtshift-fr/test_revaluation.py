"""Offline tests for the decomposition of the reform in two steps: housing at
market values, then the move to the TVTN (METHODOLOGY §3.6).

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


def _as_calibrated(tmp_path, rp):
    """The synthetic world has no REI split (plain floor-area baseline), where
    the export publishes no steps; mark the run calibrated to test them."""
    side = tmp_path / f"{rp.slug_of(rp.CFG)}.baseline.json"
    rec = json.loads(side.read_text())
    rec["revaluation"]["groups_kept"] = True
    side.write_text(json.dumps(rec))


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
    # nothing taxable: a loud failure, as for today's tax
    with pytest.raises(ValueError):
        estimate.revalued_tax(p.assign(hlm_tax_factor=0.0, is_exempt_public=True), 1e6, 0.5)
    g = _parcels()
    for bad_w in ({**W, "housing": -1.0}, {"housing": 1.0}):
        with pytest.raises(ValueError):
            estimate.revalued_tax(g, 1e6, 0.5, bucket_weights=bad_w)
    with pytest.raises(ValueError):
        estimate.revalued_tax(g.assign(floor_professional=-1.0), 1e6, 0.5, bucket_weights=W)


def test_price_index_uses_the_hedonic_price_not_value_over_floor():
    # a 1 m² shed on a large plot: market value ÷ floor is huge, but its
    # location's hedonic price is ordinary, so it stays a small payer
    p = pd.DataFrame({
        "floor_area_m2": [100.0, 1.0],
        "floor_housing": [100.0, 1.0],
        "floor_professional": [0.0, 0.0],
        "floor_industrial": [0.0, 0.0],
        "market_value": [400_000.0, 500_000.0],
        "eur_m2": [4_000.0, 4_000.0],
    })
    rev = estimate.revalued_tax(p, 1_000.0, 0.8, bucket_weights=W)
    assert rev.tolist() == pytest.approx([1_000.0 * 100 / 101, 1_000.0 / 101])
    # a parcel without a hedonic price takes the housing median
    q = p.assign(eur_m2=[4_000.0, np.nan])
    assert estimate.revalued_tax(q, 1_000.0, 0.8, bucket_weights=W).tolist() == \
        pytest.approx(rev.tolist())


def test_pipeline_writes_step_one_and_it_holds_the_levy(tmp_path):
    import run_pipeline as rp
    from test_farmland import _world
    parcels, buildings, dvf = _world()
    levy = 2_000_000.0
    rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path), make_report=False)
    side = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv")
    assert side["revalued_tax"].sum() == pytest.approx(levy) and (side["revalued_tax"] >= 0).all()
    # the kept-exemptions bill is gone: it revealed exempt landlords' tax
    assert "new_tax_kept" not in side.columns
    rec = json.loads((tmp_path / f"{rp.slug_of(rp.CFG)}.baseline.json").read_text())
    assert rec["revaluation"] == {
        "rent_price_elasticity": rp.REVALUATION["rent_price_elasticity"], "groups_kept": False}
    # social housing exempt today stays untaxed at step 1, and is taxed after
    p2 = parcels.assign(hlm_tax_factor=np.where(np.arange(len(parcels)) % 7 == 0, 0.0, 1.0))
    out2 = rp.run(p2, buildings, dvf, levy, out_dir=str(tmp_path / "s"), make_report=False)
    side2 = pd.read_csv(tmp_path / "s" / f"{rp.slug_of(rp.CFG)}.households.csv")
    social = (p2["hlm_tax_factor"] == 0).to_numpy() & (out2["current_tax"] == 0).to_numpy()
    built = (parcels["category_fr"] != "terrain_nu").to_numpy()
    sb = social & built & ~parcels["is_exempt_public"].to_numpy()
    assert sb.any()
    assert (side2.loc[sb, "revalued_tax"] == 0).all()
    assert (out2.loc[sb, "new_tax"] > 0).all()


def test_export_publishes_the_steps_and_guards_them(tmp_path):
    import export_web as ew
    import run_pipeline as rp
    from config import COMMUNES
    from test_farmland import _world
    key = next(k for k, c in COMMUNES.items() if rp.slug_of(c) == rp.slug_of(rp.CFG))
    parcels, buildings, dvf = _world()
    rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False)
    plain = ew.load_parcels(key, str(tmp_path))
    assert plain["revalued_tax"].isna().all()          # plain baseline: no steps
    _as_calibrated(tmp_path, rp)
    df = ew.load_parcels(key, str(tmp_path))
    assert df["revalued_tax"].notna().all()
    assert set(ew.STEP_TAX_COLS) <= set(df.columns)
    rows = ew.build_by_category(df)
    shown = [r for r in rows if r["total_change_pct"] is not None]
    assert shown and any(r["step_revaluation_pct"] is not None for r in rows)
    for r in rows:
        vals = [r[k] for k in ew.STEP_KEYS]
        if r["step_revaluation_pct"] is not None:
            assert abs(sum(vals) - r["total_change_pct"]) <= 0.3
    ew._check_steps({"by_category": rows})
    # guards: partial steps, steps that do not add up, non-numbers
    good = {"parcels": 50, "total_change_pct": 5.0, "step_revaluation_pct": 2.0,
            "step_land_pct": 3.0}
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


def test_the_kept_exemptions_bill_is_never_read_and_steps_are_robust(tmp_path):
    import export_web as ew
    import run_pipeline as rp
    from config import COMMUNES
    from test_farmland import _world
    key = next(k for k, c in COMMUNES.items() if rp.slug_of(c) == rp.slug_of(rp.CFG))
    parcels, buildings, dvf = _world()
    rp.run(parcels, buildings, dvf, 2_000_000.0, out_dir=str(tmp_path), make_report=False)
    plain = ew.load_parcels(key, str(tmp_path))
    assert plain["revalued_tax"].isna().all()          # plain baseline: no steps
    _as_calibrated(tmp_path, rp)
    df = ew.load_parcels(key, str(tmp_path))
    assert df["revalued_tax"].notna().all()
    # the TVTN-with-exemptions bill gives away the tax on exempt social
    # housing: it never leaves the sidecar
    assert "new_tax_kept" not in df.columns
    assert ew.STEP_KEYS == ("step_revaluation_pct", "step_land_pct")
    assert "new_tax_kept" not in ew.DOMINANCE_TAX_COLS
    # a member without the column (older run) blanks the steps, never skews them
    mixed = df.assign(revalued_tax=df["revalued_tax"].where(df.index % 2 == 0))
    assert ew._steps(mixed) == ew.NO_STEPS
    # a group almost untaxed today: no steps rather than a crash
    tiny = df.assign(current_tax=1e-12, revalued_tax=1e-12, new_tax=df["new_tax"] + 1e6)
    assert ew._steps(tiny) == ew.NO_STEPS
    # a withheld row beside a single published one: no steps at all
    two = pd.concat([df.assign(property_category="Single Family Residential"),
                     df.head(3).assign(property_category="Vacant Land")], ignore_index=True)
    rows = ew.build_by_category(two)
    assert all(r["step_revaluation_pct"] is None for r in rows)
    # booleans and non-finite totals are refused
    good = {"parcels": 50, "step_revaluation_pct": 2.0, "step_land_pct": 3.0}
    for tot in (True, float("nan")):
        with pytest.raises(AssertionError):
            ew._check_steps({"by_category": [{**good, "total_change_pct": tot}]})


def test_steps_disclosable_counts_withheld_rows_only():
    import export_web as ew
    pub = {"total_change_pct": 5.0, "total_change_eur": None, "step_revaluation_pct": 1.0}
    eur = {"total_change_pct": None, "total_change_eur": 12_000.0, "step_revaluation_pct": None}
    hid = {"total_change_pct": None, "total_change_eur": None, "step_revaluation_pct": None}
    assert ew._steps_disclosable([pub, eur])               # a row in euros is not withheld
    assert not ew._steps_disclosable([pub, pub, pub, hid])  # three beside a withheld row
    assert ew._steps_disclosable([pub, pub, pub, pub, hid])
    with pytest.raises(AssertionError):
        ew._check_steps({"by_category": [
            {**pub, "parcels": 50, "step_land_pct": 4.0}, {**hid, "parcels": 50}]})
