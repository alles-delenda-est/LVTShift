import pandas as pd
import preflight as pf


class _Cfg:
    def __init__(self, insee="00000", name="Test", dept="00", years=(2021, 2022, 2023)):
        self.insee_code, self.name, self.departement, self.dvf_years = insee, name, dept, years


def test_alsace_moselle_dvf_is_fail_without_probing():
    calls = []
    probe = lambda url, timeout=30: calls.append(url) or 200  # would say "available"
    c = pf.check_dvf(_Cfg(insee="68224", name="Mulhouse", dept="68"), probe=probe)
    assert c["severity"] == pf.FAIL
    assert c["detail"]["structural"] == "alsace_moselle_dvf_exclusion"
    assert calls == [], "must not waste a network probe on a structurally-excluded dept"


def test_dvf_none_partial_full():
    cfg = _Cfg(dept="59", years=(2021, 2022, 2023))
    none = pf.check_dvf(cfg, probe=lambda u, timeout=30: 404)
    assert none["severity"] == pf.FAIL and none["detail"]["years_available"] == 0
    only_one = {True: 0}
    def partial(u, timeout=30):
        only_one[True] += 1
        return 200 if only_one[True] == 1 else 404
    p = pf.check_dvf(cfg, probe=partial)
    assert p["severity"] == pf.WARN and p["detail"]["years_available"] == 1
    full = pf.check_dvf(cfg, probe=lambda u, timeout=30: 206)  # ranged 206 counts
    assert full["severity"] == pf.OK and full["detail"]["years_available"] == 3


def test_analyze_run_flags_thin_income_and_checks_neutrality(tmp_path):
    # neutral revenue, land share ~50%, only 2 distinct incomes -> quintiles WARN
    df = pd.DataFrame({
        "property_category": ["Single Family Residential"] * 4,
        "tax_change_pct": [10.0, -10.0, 5.0, -5.0],
        "current_tax": [1000.0, 1000.0, 1000.0, 1000.0],
        "new_tax":     [1100.0, 900.0, 1050.0, 950.0],   # sums to 4000 == current
        "taxable_land_value":        [50.0, 50.0, 50.0, 50.0],
        "taxable_improvement_value": [50.0, 50.0, 50.0, 50.0],
        "median_income": [20000.0, 20000.0, 30000.0, 30000.0],
    })
    cfg = _Cfg(name="Test")
    (tmp_path / "test.csv").write_text(df.to_csv(index=False), encoding="utf-8")
    checks = {c["check"]: c for c in pf.analyze_run(cfg, out_dir=str(tmp_path))}
    assert checks["model_ran"]["severity"] == pf.OK
    assert checks["revenue_neutrality"]["severity"] == pf.OK      # exact neutrality
    assert checks["income_quintiles"]["severity"] == pf.WARN      # 2 distinct < 5
    assert checks["land_share_band"]["severity"] == pf.OK         # 50% in band


def test_analyze_run_warns_when_not_run(tmp_path):
    checks = pf.analyze_run(_Cfg(name="Ghost"), out_dir=str(tmp_path))
    assert len(checks) == 1 and checks[0]["check"] == "model_ran"
    assert checks[0]["severity"] == pf.WARN


def test_diagnose_commune_marks_unmodellable_on_source_fail():
    # Alsace-Moselle -> DVF FAIL in 'source' category -> modellable False
    probe = lambda url, timeout=30: 200
    r = pf.diagnose_commune("mulhouse", _Cfg(insee="68224", name="Mulhouse", dept="68"),
                            out_dir="/nonexistent", probe=probe, rei_fetch=None)
    assert r["modellable"] is False
    assert r["verdict"] == pf.FAIL
    assert r["n_fail"] >= 1


def test_rei_layers_flags_material_excluded_share():
    cfg = _Cfg(insee="69029", name="Bron", dept="69")
    ok = pf.check_rei_layers(cfg, fetch=lambda c: {
        "2025": {"Commune": 95.0, "GFP": 3.0, "Syndicat": 2.0}})
    assert ok["severity"] == pf.OK
    assert ok["detail"]["excluded"] == {"Syndicat": 2}
    warn = pf.check_rei_layers(cfg, fetch=lambda c: {
        "2024": {"Commune": 1.0}, "2025": {"Commune": 80.0, "TSE": 20.0}})
    assert warn["severity"] == pf.WARN and warn["detail"]["year"] == "2025"
    assert warn["detail"]["excluded_share_pct"] == 20.0


def test_rei_layers_missing_is_fail_and_network_is_warn():
    cfg = _Cfg(insee="75101", name="Paris 1er", dept="75")
    assert pf.check_rei_layers(cfg, fetch=lambda c: {})["severity"] == pf.FAIL

    def boom(c):
        raise OSError("offline")
    assert pf.check_rei_layers(cfg, fetch=boom)["severity"] == pf.WARN


def test_dvf_year_requires_every_arrondissement():
    cfg = _Cfg(dept="75", years=(2024, 2025))
    cfg.sub_codes = ("75101", "75102")
    cfg.data_codes = ("75101", "75102")
    # 2025 missing for one arrondissement only -> that year does not count
    probe = lambda url, timeout=30: 404 if ("2025" in url and "75102" in url) else 206
    r = pf.check_dvf(cfg, probe=probe)
    assert r["severity"] == pf.WARN and r["detail"]["years"] == [2024]


def test_land_share_clip_warns_when_split_is_set_by_the_bound(tmp_path):
    import pandas as pd
    n = 10
    pinned = pd.DataFrame({
        "current_tax": [100.0] * n, "new_tax": [100.0] * n,
        "taxable_land_value": [85.0] * 8 + [50.0, 0.0],
        "taxable_improvement_value": [15.0] * 8 + [50.0, 0.0],
        "median_income": [None] * n,
    })
    pinned.to_csv(tmp_path / "test.csv", index=False)
    checks = {c["check"]: c for c in pf.analyze_run(_Cfg(name="Test"), out_dir=str(tmp_path))}
    clip = checks["land_share_clip"]
    assert clip["severity"] == pf.WARN
    assert clip["detail"]["at_cap_pct"] == round(100 * 8 / 9, 1)  # vacant row excluded
