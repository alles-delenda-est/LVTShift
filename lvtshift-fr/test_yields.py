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
    assert abs(dep.reference() - (16259 + 16538 + 12882 + 11145 + 13484) / 5) < 1e-9


def test_dmto_paris_counted_once():
    # Paris's communal share leaves the departmental line (it is in dmto_communes);
    # the single authorities of Corse, Martinique and Guyane join it.
    for y in Y._DMTO_DEP:
        assert Y._DMTO_DEP[y] == Y._DMTO_DEP_OFGL[y] - Y._PARIS_COMMUNAL[y] + Y._DMTO_CTU[y]


def test_state_fees_on_both_local_taxes():
    # Counting the State's fee on DMTO but not on the taxe foncière would be inconsistent.
    keys = {t.key for t in Y.lines_for("S1")}
    assert {"dmto_etat", "tf_etat"} <= keys
    tf = next(t for t in Y.YIELDS if t.key == "tf_etat")
    # CGI art. 1641: 3 % on TF, syndicates and GEMAPI; 8 % on TASA; 9 % on TSE.
    assert tf.reference() == round(0.03 * (42776 + 1188 + 397.1 + 191.0) + 0.08 * 57.9 + 0.09 * 276.6)
    annexes = next(t for t in Y.YIELDS if t.key == "tf_annexes")
    assert annexes.scenario == "S1" and abs(annexes.reference() - 922.6) < 0.05
    tfpb = next(t for t in Y.YIELDS if t.key == "tfpb")
    assert tfpb.reference_years() == [2025]
    assert tfpb.reference() == 42776


def test_thrs_in_s1_with_surcharge_and_fee():
    # THRS counts the zone-tendue surcharge (not in H13THS) and the State's 3 % fee.
    r = {t.key: t for t in Y.lines_for("S1")}
    assert abs(r["thrs"].reference() - 2973.6) < 0.05
    assert r["thrs"].tier == "local" and r["thrs_etat"].tier == "national"
    assert r["thrs_etat"].reference() == round(0.03 * (1727.42 + 843.14 + 12.10 + 390.92))


def test_rents_include_csg():
    # CPO rapport particulier n° 1: IR, PS and CSG are separate lines that add up;
    # CRL and IS (companies) stay out (D3).
    s3_only = {t.key: t.reference() for t in Y.YIELDS if t.scenario == "S3"}
    assert s3_only == {"rents_ir": 4198, "rents_ps": 2399, "rents_csg": 1093}


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
    assert Y.LAND_BASE.taxable == 7_032_000 - 941_000
    r = Y.indicative_rate_pct("S1")
    assert abs(r - 100 * Y.scenario_total("S1") / Y.LAND_BASE.taxable) < 1e-9
    assert 0.5 < r < 2.0  # sanity: order of magnitude of today's property taxes


def test_every_exported_url_is_https(tmp_path: Path):
    # The site renders every "url" field as a link: only https may reach it.
    def urls(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "url" or k.endswith("_url"):
                    yield v
                else:
                    yield from urls(v)
        elif isinstance(node, list):
            for v in node:
                yield from urls(v)

    found = list(urls(Y.export_json(tmp_path / "yields.json")))
    assert found and all(isinstance(u, str) and u.startswith("https://") for u in found)


def test_export_round_trip(tmp_path: Path):
    out = tmp_path / "yields.json"
    payload = Y.export_json(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == payload
    assert len(data["variants"]) == 5  # S1, S2 ± IFI, S3 ± IFI
    for v in data["variants"]:
        assert v["total_meur"] == round(Y.scenario_total(v["scenario"], v["include_ifi"]))
        assert set(v["lines"]) <= {t["key"] for t in data["taxes"]}
