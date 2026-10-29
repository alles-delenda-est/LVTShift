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
    # Farmland keeps its TFPNB (D6): the non-built parts lose its share.
    nb = 1 - Y._FARM_SHARE[2025]
    assert tf.reference() == round(0.03 * (42776 + (1188 - 922.2) + 376.6 + 20.5 * nb
                                           + 184.3 + 6.7 * nb)
                                   + 0.08 * 57.9 + 0.09 * (275.1 + 1.5 * nb))
    annexes = next(t for t in Y.YIELDS if t.key == "tf_annexes")
    assert annexes.scenario == "S1"
    assert abs(annexes.reference() - (922.6 - (1.5 + 20.5 + 6.7) * Y._FARM_SHARE[2025])) < 0.05
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


def test_constant_euros_sensitivity():
    # 2025 lines are unchanged; older years are raised by CPI; the headline stays nominal (D1).
    tfpb = next(t for t in Y.YIELDS if t.key == "tfpb")
    assert tfpb.reference_constant() == tfpb.reference()
    rents = next(t for t in Y.YIELDS if t.key == "rents_ir")
    assert abs(rents.reference_constant() - 4198 * 120.95 / 112.01) < 1e-9
    for sc in Y.SCENARIOS:
        for ifi in (False, True):
            assert Y.scenario_total_constant(sc, ifi) > Y.scenario_total(sc, ifi)
    assert set(Y.CPI) >= {y for t in Y.YIELDS for y in t.reference_years()}


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
    assert Y.LAND_BASE.taxable_built == 7_032_000 - 941_000
    # D6: farmland is outside the reform, so outside the base; unbuilt
    # building land is in it
    assert Y.LAND_BASE.taxable == Y.LAND_BASE.taxable_built + Y.UNBUILT_LAND.value
    r = Y.indicative_rate_pct("S1")
    assert abs(r - 100 * Y.scenario_total("S1") / Y.LAND_BASE.taxable) < 1e-9
    assert 0.5 < r < 2.0  # sanity: order of magnitude of today's property taxes


def test_unbuilt_building_land_estimate():
    u = Y.UNBUILT_LAND
    assert u.low < u.value < u.high
    # central AU: 185 000 ha × 20 €/m² × 85 % private; U plots stay outside
    assert abs(u.value - 185_000e4 * 20 / 1e6 * 0.85) < 1e-6
    assert abs(u.u_value - 150_000e4 * 100 / 1e6 * 0.85) < 1e-6
    # second-order: under a tenth of built land even with U plots, high case
    assert u.high + u.u_high < 0.10 * Y.LAND_BASE.taxable_built


def test_farmland_keeps_its_tfpnb():
    # only the non-agricultural part of the TFPNB is replaced: about a fifth
    tfpnb = next(t for t in Y.YIELDS if t.key == "tfpnb")
    for y, all_ in Y._TFPNB_ALL.items():
        assert abs(tfpnb.values[y] + Y._TFPNB_FARM[y] - all_) < 0.1
        assert 0.70 < Y._TFPNB_FARM[y] / all_ < 0.85
    # sensitivity: putting farmland back at SAFER prices, with its TFPNB, lowers
    # the rate, and farmland would pay more than its TFPNB today
    s = Y.farmland_sensitivity()
    assert s["rate_pct"] < Y.indicative_rate_pct("S1")
    assert s["farmland_pays_meur"] > s["farmland_tfpnb_meur"]


def test_farmland_at_safer_prices():
    # D6: price × area, vines apart; the central value sits between the bounds,
    # far below INSEE's AN.2112.
    f = Y.FARMLAND
    assert f.low < f.value < f.high
    assert abs(f.low - (25_890_657 * 5_350 + 747_976 * 87_400) / 1e6) < 1e-6
    assert 150_000 < f.value < 300_000 < Y.INSEE_FARMLAND_MEUR


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


def test_companies_shift_only_from_s2_s3_lines():
    assert Y.companies_shift("S1") == 0
    share = Y.LAND_BASE.companies_share
    assert 0.30 < share < 0.32
    added = Y.scenario_total("S3", True) - Y.scenario_total("S1")
    assert abs(Y.companies_shift("S3", True) - share * added) < 1e-6
    assert Y.companies_shift("S2") < Y.companies_shift("S3") < Y.companies_shift("S3", True)


def test_export_round_trip(tmp_path: Path):
    out = tmp_path / "yields.json"
    payload = Y.export_json(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == payload
    assert len(data["variants"]) == 5  # S1, S2 ± IFI, S3 ± IFI
    for v in data["variants"]:
        assert v["total_meur"] == round(Y.scenario_total(v["scenario"], v["include_ifi"]))
        assert set(v["lines"]) <= {t["key"] for t in data["taxes"]}


def test_committed_yields_json_links_are_https():
    # the site reads the committed file, not a fresh export: check it too
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

    committed = Path(__file__).parent / "site/public/data/yields.json"
    found = list(urls(json.loads(committed.read_text(encoding="utf-8"))))
    assert found and all(isinstance(u, str) and u.startswith("https://") for u in found)
