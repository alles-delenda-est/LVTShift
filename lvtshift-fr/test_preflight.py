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
                            out_dir="/nonexistent", probe=probe)
    assert r["modellable"] is False
    assert r["verdict"] == pf.FAIL
    assert r["n_fail"] >= 1
