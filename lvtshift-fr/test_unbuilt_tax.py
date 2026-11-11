"""Offline tests for replacing the tax on non-agricultural unbuilt land.

The reform replaces the TFPNB (its non-agricultural share) and the TAFNB: the
amount joins the revenue held constant and is today's tax on vacant plots and
on houses' large gardens.

Run: python -m pytest -q test_unbuilt_tax.py
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
import ingest  # noqa: E402


class Cfg:
    insee_code, name, reference_year = "99001", "ZZ", 2025


def _rei(monkeypatch, lines: dict):
    rows = [{"var": k, "valeur": v} for k, v in lines.items()]
    monkeypatch.setattr(ingest, "_ofgl_records", lambda url, where, select, max_pages=5: rows)


def test_replaced_amount_is_the_non_agricultural_share_plus_the_tafnb(monkeypatch):
    # commune and EPCI share one base of 1,000, 600 of it non-agricultural
    _rei(monkeypatch, {"B11": 1000.0, "B13": 500.0, "B31": 1000.0, "B33": 40.0,
                       "B31TAFNB": 600.0, "B33TAFNB": 230.0})
    r = ingest.fetch_rei_unbuilt_replaced(Cfg)
    assert r["tfpnb"] == pytest.approx(0.6 * 540.0) and r["tafnb"] == 230.0
    assert r["amount"] == pytest.approx(554.0)
    assert r["non_agricultural_share"] == pytest.approx(0.6) and r["year"] == 2025
    # commune share only: the EPCI's TFPNB and its TAFNB stay out
    only = ingest.fetch_rei_unbuilt_replaced(Cfg, layers=("Commune",))
    assert only["amount"] == pytest.approx(0.6 * 500.0)


def test_replaced_amount_handles_the_grand_paris_and_caps_the_share(monkeypatch):
    # no EPCI TFPNB (petite couronne); the Métropole levies the TAFNB
    _rei(monkeypatch, {"B11": 1000.0, "B13": 350.0, "B31MGPTAFNB": 1200.0, "B33MGPTAFNB": 115.0})
    r = ingest.fetch_rei_unbuilt_replaced(Cfg)
    assert r["non_agricultural_share"] == 1.0            # capped, never above the TFPNB
    assert r["amount"] == pytest.approx(350.0 + 115.0)


def test_replaced_amount_fails_loudly_on_missing_or_bad_lines(monkeypatch):
    for lines in ({}, {"B13": 10.0}, {"B11": 100.0, "B13": -5.0},
                  {"B11": 100.0, "B13": "80000"}, {"B11": 100.0, "B13": float("nan")},
                  {"B11": 100.0, "B13": float("inf")}):
        _rei(monkeypatch, lines)
        with pytest.raises(ingest.IngestUnavailable):
            ingest.fetch_rei_unbuilt_replaced(Cfg)
    monkeypatch.setattr(ingest, "_ofgl_records", lambda *a, **k: [
        {"var": "B11", "valeur": 1.0}, {"var": "B11", "valeur": 2.0}])
    with pytest.raises(ingest.IngestUnavailable):
        ingest.fetch_rei_unbuilt_replaced(Cfg)
    # malformed rows fail as unavailable, never as a crash
    for rows in ([["B11", 1.0]], [{"var": ["B11"], "valeur": 1.0}], {"results": []},
                 [{"var": "X99", "valeur": 1.0}]):
        monkeypatch.setattr(ingest, "_ofgl_records", lambda *a, _r=rows, **k: _r)
        with pytest.raises(ingest.IngestUnavailable):
            ingest.fetch_rei_unbuilt_replaced(Cfg)
    # a null value is an absent line, read as zero
    _rei(monkeypatch, {"B11": 100.0, "B13": 50.0, "B11TAFNB": None})
    assert ingest.fetch_rei_unbuilt_replaced(Cfg)["amount"] == 0.0


def _parcels():
    return pd.DataFrame({
        "parcel_area_m2": [1000.0, 3000.0, 2000.0, 400.0, 1300.0, 5000.0, 900.0],
        "floor_area_m2": [0.0, 0.0, 0.0, 120.0, 200.0, 800.0, 150.0],
        "category_fr": ["terrain_nu", "terrain_nu", "terrain_nu", "maison", "maison",
                        "immeuble_collectif", "maison"],
        "zone_typ": ["U", "U", "U", "U", "U", "U", "N"]})


def test_unbuilt_tax_is_shared_by_area_over_vacant_plots_and_large_gardens():
    p = _parcels()
    in_reform = pd.Series([True, True, False, True, True, True, True])   # third: farmland / exempt
    footprint = pd.Series([0.0, 0.0, 0.0, 100.0, 100.0, 400.0, 100.0])
    t = estimate.unbuilt_tax(p, 4700.0, in_reform, footprint)
    # vacant plots: whole area; the house on 1,300 m²: 1,300 − 100 − 500 = 700 m²;
    # the small plot, the block and the house in an N zone: nothing
    assert list(t.round(6)) == [1000.0, 3000.0, 0.0, 0.0, 700.0, 0.0, 0.0]
    assert t.sum() == pytest.approx(4700.0)


def test_unbuilt_tax_degenerate_cases():
    p = _parcels()
    every = pd.Series(True, index=p.index)
    assert estimate.unbuilt_tax(p, 0.0, every).sum() == 0.0
    # nothing can carry it: zeros, so the caller adds nothing to the levy
    assert estimate.unbuilt_tax(p, 100.0, pd.Series(False, index=p.index)).sum() == 0.0
    # without categories (synthetic frames): vacant plots only
    plain = estimate.unbuilt_tax(p.drop(columns=["category_fr", "zone_typ"]), 600.0, every)
    assert list(plain.round(6)) == [100.0, 300.0, 200.0, 0.0, 0.0, 0.0, 0.0]
    for bad in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            estimate.unbuilt_tax(p, bad, every)
    with pytest.raises(ValueError):
        estimate.unbuilt_tax(p.assign(parcel_area_m2=[float("inf")] + [1.0] * 6), 100.0, every)


def test_pipeline_adds_the_replaced_tax_to_the_levy_and_to_todays_bills(tmp_path):
    import run_pipeline as rp
    from test_farmland import _world
    parcels, buildings, dvf = _world()
    levy, unbuilt = 2_000_000.0, {"amount": 30_000.0, "non_agricultural_share": 0.8, "year": 2025}
    plain = rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path / "plain"), make_report=False)
    out = rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path), make_report=False,
                 unbuilt_replaced=unbuilt)
    assert out["current_tax"].sum() == pytest.approx(levy + 30_000.0)
    assert out["new_tax"].sum() == pytest.approx(levy + 30_000.0, rel=1e-6)
    farm = parcels["land_type"].isin(["agricultural", "natural"]).values
    exempt = parcels["is_exempt_public"].values
    vacant = (parcels["category_fr"] == "terrain_nu").values & ~farm & ~exempt
    # farmland and exempt property stay outside; vacant building land pays today
    assert (out.loc[farm | exempt, "current_tax"] == 0).all()
    assert (out.loc[vacant, "current_tax"] > 0).all()
    assert (plain.loc[vacant, "current_tax"] == 0).all()
    # built parcels keep their share of the built tax, plus any garden share
    built = ~(parcels["category_fr"] == "terrain_nu").values & ~exempt
    assert (out.loc[built, "current_tax"] >= plain.loc[built, "current_tax"] - 1e-6).all()
    # every new bill scales with the larger levy, nothing else moves
    assert np.allclose(out["new_tax"], plain["new_tax"] * (levy + 30_000.0) / levy)
    side = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.households.csv")
    assert side["current_tax_low"].sum() == pytest.approx(levy + 30_000.0)
    rec = json.loads((tmp_path / f"{rp.slug_of(rp.CFG)}.baseline.json").read_text())["unbuilt"]
    assert rec["replaced"] and rec["amount_eur"] == 30_000.0 and 0 <= rec["garden_share"] <= 1
    off = json.loads((tmp_path / "plain" / f"{rp.slug_of(rp.CFG)}.baseline.json").read_text())
    assert off["unbuilt"]["replaced"] is False


def test_export_reports_what_was_replaced_and_guards_the_block(tmp_path, monkeypatch):
    import config
    import export_web as ew
    monkeypatch.setitem(config.COMMUNES, "zz", config.CommuneConfig("99001", "ZZ", "99", key="zz"))
    monkeypatch.setitem(config.COMMUNES, "yy", config.CommuneConfig("99002", "YY", "99", key="yy"))
    side = tmp_path / "zz.baseline.json"
    assert ew.load_unbuilt("zz", str(tmp_path)) == {"replaced": False}          # older run
    good = {"replaced": True, "amount_eur": 289146.4, "non_agricultural_share": 0.9381,
            "garden_share": 0.3584, "year": 2025}
    side.write_text(json.dumps({"method": "floor_area", "unbuilt": good}))
    assert ew.load_unbuilt("zz", str(tmp_path)) == {
        "replaced": True, "amount_eur": 289146.0, "non_agricultural_share": 0.938,
        "garden_share": 0.358}
    for bad in ({**good, "amount_eur": -1}, {**good, "garden_share": 1.5},
                {**good, "replaced": "yes"}, {**good, "non_agricultural_share": None}):
        side.write_text(json.dumps({"method": "floor_area", "unbuilt": bad}))
        with pytest.raises(ValueError):
            ew.load_unbuilt("zz", str(tmp_path))
    # a territory replaces it only if every member does
    side.write_text(json.dumps({"method": "floor_area", "unbuilt": good}))
    assert ew._territory_unbuilt(["zz", "yy"], str(tmp_path)) == {"replaced": False}
    (tmp_path / "yy.baseline.json").write_text(json.dumps({"method": "floor_area", "unbuilt": {
        **good, "amount_eur": 100000.0, "garden_share": 0.1}}))
    t = ew._territory_unbuilt(["zz", "yy"], str(tmp_path))
    assert t["replaced"] and t["amount_eur"] == 389146.0 and 0.1 < t["garden_share"] < 0.358
    ew._check_unbuilt({"provenance": {"unbuilt_tax": t}})
    ew._check_unbuilt({"provenance": {"unbuilt_tax": {"replaced": False}}})
    for bad in ({"replaced": True, "parcels": [1, 2]}, {"replaced": "yes"},
                {"replaced": True, "owner": "x"}, {**t, "garden_share": 5},
                {**t, "amount_eur": -1.0}, {**t, "amount_eur": float("nan")},
                {**t, "amount_eur": 1e15}, {**t, "amount_eur": 1234.5},
                {"replaced": False, "amount_eur": 1000.0}):
        with pytest.raises(AssertionError):
            ew._check_unbuilt({"provenance": {"unbuilt_tax": bad}})
