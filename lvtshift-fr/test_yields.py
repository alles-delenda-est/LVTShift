"""Offline tests for yields.py (spec 0005: yields to replace, by scenario).

Run:  python -m pytest test_yields.py
"""

import json
from pathlib import Path

import yields as Y


def test_reference_rule_d1():
    # Cyclical taxes: mean of the last five years; others: latest year.
    dep = next(t for t in Y.YIELDS if t.key == "dmto_departements")
    assert dep.reference_years() == [2021, 2022, 2023, 2024, 2025]
    assert abs(dep.reference() - (16511 + 16776 + 13044 + 11297 + 13669) / 5) < 1e-9
    tfpb = next(t for t in Y.YIELDS if t.key == "tfpb")
    assert tfpb.reference_years() == [2025]
    assert tfpb.reference() == 42776


def test_scenarios_are_nested():
    s1 = {t.key for t in Y.lines_for("S1")}
    s2 = {t.key for t in Y.lines_for("S2")}
    s3 = {t.key for t in Y.lines_for("S3")}
    assert s1 < s2 < s3
    assert "ifi" not in s2 and "ifi" in {t.key for t in Y.lines_for("S2", True)}
    # The IFI toggle never applies to S1.
    assert {t.key for t in Y.lines_for("S1", True)} == s1
    assert Y.scenario_total("S1") < Y.scenario_total("S2") < Y.scenario_total("S3")


def test_tiers_sum_to_total():
    for sc in Y.SCENARIOS:
        for ifi in (False, True):
            assert abs(sum(Y.tier_totals(sc, ifi).values()) - Y.scenario_total(sc, ifi)) < 1e-6


def test_every_line_is_sourced():
    keys = [t.key for t in Y.YIELDS]
    assert len(keys) == len(set(keys))
    for t in Y.YIELDS:
        assert t.source and t.url.startswith("https://") and t.scope
        assert t.values and all(v > 0 for v in t.values.values())
        assert t.scenario in {"S1", "S2", "S2_IFI", "S3"}
        if t.status != "verified":
            assert t.note or t.status == "reported", t.key


def test_indicative_rate_uses_taxable_land():
    assert Y.LAND_BASE.taxable == 6_346_000 - 916_000
    r = Y.indicative_rate_pct("S1")
    assert abs(r - 100 * Y.scenario_total("S1") / Y.LAND_BASE.taxable) < 1e-9
    assert 0.5 < r < 2.0  # sanity: order of magnitude of today's property taxes


def test_export_round_trip(tmp_path: Path):
    out = tmp_path / "yields.json"
    payload = Y.export_json(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == payload
    assert len(data["variants"]) == 5  # S1, S2 ± IFI, S3 ± IFI
    for v in data["variants"]:
        assert v["total_meur"] == round(Y.scenario_total(v["scenario"], v["include_ifi"]))
        assert set(v["lines"]) <= {t["key"] for t in data["taxes"]}
