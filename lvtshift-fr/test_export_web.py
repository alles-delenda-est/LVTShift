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
    # each toy parcel 11 times, so no group falls under MIN_GROUP_PARCELS
    buckets = ew.build_buckets(pd.concat([_toy_df()] * 11, ignore_index=True))
    assert [b["bucket"] for b in buckets] == ["vacant", "lt10", "r10_25", "r25_50", "ge50"]
    assert sum(b["parcels"] for b in buckets) == 44
    # Vacant Land has 0 improvement -> its 11 copies in the vacant bucket
    assert next(b for b in buckets if b["bucket"] == "vacant")["parcels"] == 11
    assert abs(sum(b["value_pct_of_base"] or 0 for b in buckets) - 100.0) < 0.5


def test_by_category_win_lose_honest():
    toy = pd.concat([_toy_df()] * 11, ignore_index=True)
    cats = {c["category"]: c for c in ew.build_by_category(toy)}
    sfr = cats["Single Family Residential"]
    assert sfr["label_fr"] == "Maison individuelle"
    assert sfr["count_paying_more"] == 0          # −100 € → pays less
    assert sfr["share_paying_more_pct"] == 0.0
    vac = cats["Vacant Land"]
    assert vac["count_paying_more"] == 11         # +350 € → pays more
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


def test_aggregate_guard_rejects_per_parcel_and_forbidden_tokens():
    good = {
        "commune_key": "x", "insee": "1", "name": "X", "departement": "1",
        "reference_year": 2025, "model_type": "split_rate:4.0",
        "headline": {"currency": "EUR"}, "headline_sensitivity": {},
        "by_category": [], "by_income_quintile": None,
        "by_improvement_ratio": [], "provenance": {}, "currency": "EUR",
    }
    ew.assert_aggregate_only(good)                 # no raise

    with pytest.raises(AssertionError):
        bad = dict(good); bad["parcels_detail"] = [{"id": 1}]   # stray per-parcel array
        ew.assert_aggregate_only(bad)

    with pytest.raises(AssertionError):
        leak = dict(good); leak["provenance"] = {"note": "std_geoid leaked"}
        ew.assert_aggregate_only(leak)

    with pytest.raises(AssertionError):
        oversized = dict(good)
        oversized["by_category"] = [{"category": str(i)} for i in range(11)]  # 11 > 10
        ew.assert_aggregate_only(oversized)


def test_payload_assembles_for_toy(monkeypatch, tmp_path):
    # write a toy commune CSV and point load_parcels at it via a fake config
    import config
    df = _toy_df()
    (tmp_path / "x.csv").write_text(df.to_csv(index=False), encoding="utf-8")

    class _Cfg:
        insee_code, name, departement, reference_year, split_rate_ratio = \
            "00000", "X", "00", 2025, 4.0
        construction_cost_eur_m2 = 1900.0
        land_share_bounds = (0.15, 0.85)
    monkeypatch.setitem(config.COMMUNES, "x", _Cfg())

    payload = ew.build_commune_payload("x", out_dir=str(tmp_path))
    ew.assert_aggregate_only(payload)
    assert payload["headline"]["parcels_modeled"] == 4
    assert payload["by_income_quintile"] is None   # only 2 distinct incomes
    blob = json.dumps(payload, ensure_ascii=False)
    for bad in ("$", "_usd", "minority_pct", "black_pct", "std_geoid"):
        assert bad not in blob


def _solved_frame(n=400, seed=7):
    """A commune-like frame solved centrally with the real upstream solver."""
    from lvt.lvt_utils import model_split_rate_tax
    rng = np.random.default_rng(seed)
    cats = rng.choice(["Single Family Residential", "Condominium", "Commercial",
                       "Vacant Land"], n, p=[0.4, 0.35, 0.15, 0.1])
    land = rng.uniform(40_000, 300_000, n)
    imp = np.where(cats == "Vacant Land", 0.0, rng.uniform(50_000, 400_000, n))
    cur = np.where(cats == "Vacant Land", 0.0, rng.uniform(500, 3000, n))
    df = pd.DataFrame({
        "property_category": cats, "taxable_land_value": land,
        "taxable_improvement_value": imp, "current_tax": cur,
        "median_income": rng.choice([15e3, 17e3, 20e3, 22e3, 25e3, 27e3, 30e3, 35e3,
                                     40e3, 47e3, 55e3, 60e3], n),
    })
    _lm, _im, _rev, solved = model_split_rate_tax(
        df=df.copy(), land_value_col="taxable_land_value",
        improvement_value_col="taxable_improvement_value",
        current_revenue=float(cur.sum()), land_improvement_ratio=4.0)
    df["new_tax"] = solved["new_tax"].to_numpy(dtype=float)
    df["tax_change"] = df["new_tax"] - df["current_tax"]
    with np.errstate(divide="ignore", invalid="ignore"):
        df["tax_change_pct"] = 100.0 * df["tax_change"] / df["current_tax"]
    return df


def test_band_base_leg_reproduces_central_groups():
    df = _solved_frame()
    s = ew.build_headline_sensitivity(df, ratio=4.0)
    cat = {r["category"]: r for r in ew.build_by_category(df)}
    for r in s["base"]["by_category"]:
        c = cat[r["category"]]
        assert r["median_change_pct"] == c["median_change_pct"]
        assert r["share_paying_more_pct"] == c["share_paying_more_pct"]
        assert abs(r["median_change_eur"] - c["median_change_eur"]) <= 1
    q = ew.build_by_income_quintile(df)
    assert [r["median_change_pct_residential"] for r in s["base"]["by_income_quintile"]] \
        == [r["median_change_pct_residential"] for r in q]


def test_band_groups_move_with_land_share():
    df = _solved_frame()
    s = ew.build_headline_sensitivity(df, ratio=4.0)
    vac = {leg: next(r for r in s[leg]["by_category"] if r["category"] == "Vacant Land")
           for leg in ("low", "base", "high")}
    # more weight on land -> vacant land's median € change rises monotonically
    assert vac["low"]["median_change_eur"] <= vac["base"]["median_change_eur"] \
        <= vac["high"]["median_change_eur"]
    for leg in ("low", "high"):
        assert len(s[leg]["by_income_quintile"]) == 5
        assert set(s[leg]["by_category"][0]) == set(ew.BAND_CATEGORY_KEYS)


def test_guard_checks_nested_band_rows():
    df = _solved_frame()
    payload = {"commune_key": "x", "headline_sensitivity":
               ew.build_headline_sensitivity(df, ratio=4.0)}
    ew.assert_aggregate_only(payload)
    payload["headline_sensitivity"]["low"]["by_category"][0]["parcel_ids"] = ["x"]
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(payload)
    payload["headline_sensitivity"]["low"]["by_category"][0].pop("parcel_ids")
    payload["headline_sensitivity"]["low"]["by_category"][0]["category"] = ["a", "b"]
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(payload)
    payload["headline_sensitivity"]["low"]["by_category"][0]["category"] = "Condominium"
    payload["headline_sensitivity"]["extra"] = {}
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(payload)


def test_weighted_median():
    assert ew.weighted_median([1.0, 2.0, 3.0], [1, 1, 1]) == 2.0
    # one heavy value dominates: a 200-flat block outweighs three houses
    assert ew.weighted_median([5.0, 5.0, 5.0, -10.0], [1, 1, 1, 200]) == -10.0
    assert ew.weighted_median([np.nan, 4.0], [10, 1]) == 4.0
    assert ew.weighted_median([1.0], [0]) is None


def test_quintile_totals_and_households_tell_the_group_story():
    # each group: twelve houses at +10 %, three 10-flat blocks at −20 % -> the
    # median parcel pays more, but the group and the typical household pay less
    houses = dict(property_category="Single Family Residential", current_tax=1000.0,
                  tax_change=100.0, tax_change_pct=10.0, n_dwellings=1.0)
    block = dict(property_category="Large Multi-Family (5+ units)", current_tax=20000.0,
                 tax_change=-4000.0, tax_change_pct=-20.0, n_dwellings=10.0)
    shop = dict(property_category="Commercial", current_tax=5000.0,
                tax_change=-2500.0, tax_change_pct=-50.0, n_dwellings=0.0)
    rows = []
    for q in range(5):   # two IRIS incomes per group (MIN_IRIS_INCOMES)
        for i, r in enumerate([houses] * 12 + [block] * 3 + [shop]):
            rows.append({**r, "median_income": 20000.0 + 1000 * q + 500 * (i % 2)})
    q1 = ew.build_by_income_quintile(pd.DataFrame(rows))[0]
    assert q1["median_change_pct_residential"] == 10.0
    assert q1["total_change_pct"] == round(100 * (1200 - 12000) / 72000, 1)  # shop excluded
    assert q1["household_median_change_pct"] == -20.0
    assert q1["dwellings"] == 42
    # older runs without dwelling counts: household figure unset, not guessed
    q1 = ew.build_by_income_quintile(pd.DataFrame(rows).drop(columns="n_dwellings"))[0]
    assert q1["household_median_change_pct"] is None and q1["total_change_pct"] is not None


def test_households_sidecar_must_match_its_run(tmp_path, monkeypatch):
    import config
    df = _toy_df()
    df.to_csv(tmp_path / "x.csv", index=False)

    class _Cfg:
        insee_code, name, departement = "00000", "X", "00"
    monkeypatch.setitem(config.COMMUNES, "x", _Cfg())
    side = pd.DataFrame({"new_tax": df["new_tax"], "n_dwellings": [1.0, 0.0, 0.0, 12.0],
                         "dwellings_imputed": False})
    side.to_csv(tmp_path / "x.households.csv", index=False)
    import hashlib
    sha = hashlib.sha256((tmp_path / "x.csv").read_bytes()).hexdigest()
    (tmp_path / "x.households.meta.json").write_text(json.dumps({"export_sha256": sha}))
    out = ew.load_parcels("x", out_dir=str(tmp_path))
    assert list(out["n_dwellings"]) == [1.0, 0.0, 0.0, 12.0]
    side.assign(new_tax=side["new_tax"] + 5).to_csv(tmp_path / "x.households.csv", index=False)
    with pytest.raises(ValueError):
        ew.load_parcels("x", out_dir=str(tmp_path))
    # a re-run export no longer matches the recorded hash
    side.to_csv(tmp_path / "x.households.csv", index=False)
    df.assign(new_tax=df["new_tax"] + 0).to_csv(tmp_path / "x.csv", index=False, float_format="%.3f")
    with pytest.raises(ValueError):
        ew.load_parcels("x", out_dir=str(tmp_path))


def test_quintile_group_figures_withheld_for_small_or_dominated_groups():
    def rows(n_houses, block_flats, nan_count=False):
        out = []
        for q in range(5):
            for i in range(n_houses):
                out.append(dict(property_category="Single Family Residential",
                                current_tax=1000.0, tax_change=50.0, tax_change_pct=5.0,
                                n_dwellings=np.nan if (nan_count and i == 0) else 1.0,
                                median_income=20000.0 + 10 * q + 5 * (i % 2)))
            out.append(dict(property_category="Large Multi-Family (5+ units)",
                            current_tax=9000.0, tax_change=-900.0, tax_change_pct=-10.0,
                            n_dwellings=block_flats, median_income=20000.0 + 10 * q + 5))
        return pd.DataFrame(out)
    ok = ew.build_by_income_quintile(rows(20, 10.0))[0]
    assert ok["household_median_change_pct"] == 5.0 and ok["total_change_pct"] is not None
    small = ew.build_by_income_quintile(rows(5, 10.0))[0]           # 6 parcels
    assert small["total_change_pct"] is None and small["dwellings"] is None
    dominated = ew.build_by_income_quintile(rows(20, 50.0))[0]       # block = 50/70
    assert dominated["household_median_change_pct"] is None
    assert dominated["dwellings"] is None and dominated["total_change_pct"] is None
    partial = ew.build_by_income_quintile(rows(20, 10.0, nan_count=True))[0]
    assert partial["household_median_change_pct"] is None
    assert partial["total_change_pct"] is not None


def test_guard_rejects_nested_values_in_quintile_rows():
    payload = {"by_income_quintile": [{"quintile": 1, "dwellings": [1, 2, 3]}]}
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(payload)


def test_baseline_sensitivity_changes_only_todays_tax():
    df = _toy_df()
    assert ew.build_baseline_sensitivity(df) is None          # no lower bound in the run
    # lower bound: less professional tax today, same total (revenue-neutral)
    low = df.assign(current_tax_low=[1200.0, 50.0, 1600.0, 1000.0])
    b = ew.build_baseline_sensitivity(low)
    assert b["pro_scale_central"] > b["pro_scale_low"]
    central = ew._sensitivity_summary(df, (df.new_tax - df.current_tax).to_numpy(), 0.0, 3850.0)
    assert b["central"]["share_paying_more_pct"] == central["share_paying_more_pct"]
    # lower professional tax today: the commercial parcel now pays more
    # (1 600 -> 1 900), the house gains more (1 200 -> 900)
    assert b["low"]["share_paying_more_pct"] == 50.0           # vacant + commercial
    payload = {"baseline_sensitivity": b}
    ew.assert_aggregate_only(payload)
    json.dumps(payload, allow_nan=False)
    bad = {"baseline_sensitivity": {**b, "parcels": [1, 2]}}
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(bad)
    leak = {"baseline_sensitivity": {**b, "low": {**b["low"], "idpar": "x"}}}
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only(leak)
    row = (b["low"]["by_category"] or [{}])[0]
    for smuggle in ({**b["low"], "by_category": [{**row, "median_change_eur": list(range(60))}]},
                    {**b["low"], "gross_pct_of_levy": [1, 2, 3]},
                    {**b["low"], "share_paying_more_pct": {"x": 1}}):
        with pytest.raises(AssertionError):
            ew.assert_aggregate_only({"baseline_sensitivity": {**b, "low": smuggle}})
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only({"baseline_sensitivity": {**b, "pro_scale_low": "1"}})
    # the second column names its source; anything else is refused
    assert b["low_source"] == "cfe_raw"
    assert ew.build_baseline_sensitivity(low, low_source="th2017")["low_source"] == "th2017"
    with pytest.raises(AssertionError):
        ew.assert_aggregate_only({"baseline_sensitivity": {**b, "low_source": "<x>"}})
    # no real lower bound: nothing published
    assert ew.build_baseline_sensitivity(df.assign(current_tax_low=df["current_tax"])) is None
    # a territory member without the figures: a clear error naming it
    mixed = low.assign(_commune=["a", "a", "b", "b"],
                       current_tax_low=[1200.0, 50.0, None, None])
    with pytest.raises(ValueError, match="b"):
        ew.build_baseline_sensitivity(mixed)


def test_lower_bound_sidecar_must_be_revenue_neutral(tmp_path, monkeypatch):
    import config
    import hashlib
    df = _toy_df()
    df.to_csv(tmp_path / "x.csv", index=False)

    class _Cfg:
        insee_code, name, departement = "00000", "X", "00"
    monkeypatch.setitem(config.COMMUNES, "x", _Cfg())
    sha = hashlib.sha256((tmp_path / "x.csv").read_bytes()).hexdigest()
    (tmp_path / "x.households.meta.json").write_text(json.dumps({"export_sha256": sha}))
    side = pd.DataFrame({"new_tax": df["new_tax"], "n_dwellings": [1.0, 0.0, 0.0, 12.0],
                         "current_tax_low": [1200.0, 50.0, 1600.0, 1000.0]})
    side.to_csv(tmp_path / "x.households.csv", index=False)
    out = ew.load_parcels("x", out_dir=str(tmp_path))
    assert list(out["current_tax_low"]) == [1200.0, 50.0, 1600.0, 1000.0]
    for bad in ([1200.0, 50.0, 1600.0, 9000.0],      # total off
                [2900.0, 50.0, -100.0, 1000.0],      # negative, same total
                [1250.0, 0.0, 1600.0, 1000.0]):      # untaxed parcel moved
        side.assign(current_tax_low=bad).to_csv(tmp_path / "x.households.csv", index=False)
        with pytest.raises(ValueError):
            ew.load_parcels("x", out_dir=str(tmp_path))


def test_small_groups_are_merged_not_left_to_subtraction():
    # nine parcels under 10 % building value, as in Cahors: merged with a
    # neighbour, so no total minus the others reveals them
    n = 200
    df = pd.DataFrame({
        "taxable_land_value": [100.0] * n, "taxable_improvement_value": [300.0] * n,
        "tax_change": [5.0] * n, "tax_change_pct": [1.0] * n,
        "property_category": ["Condominium"] * (n - 3) + ["Industrial"] * 3,
    })
    df.loc[:8, "taxable_improvement_value"] = 5.0             # < 10 %, 9 parcels
    df.loc[9:29, "taxable_improvement_value"] = 20.0          # 10-25 %, 21 parcels
    df.loc[30:39, "taxable_improvement_value"] = 0.0          # vacant, 10 parcels
    b = {r["bucket"]: r for r in ew.build_buckets(df)}
    assert all(r["parcels"] == 0 or r["parcels"] >= ew.MIN_GROUP_PARCELS for r in b.values())
    assert sum(r["parcels"] for r in b.values()) == n
    assert b["vacant+lt10"]["label"].startswith("Nu ou sous-bâti")
    assert b["ge50"]["value_eur"] == round(b["ge50"]["value_eur"], -3)
    # small categories join "Other": three industrial parcels are not shown apart
    c = {r["category"]: r for r in ew.build_by_category(df)}
    assert "Industrial" not in c and c["Other"]["parcels"] == 3
    assert all(c["Other"][k] is None for k in ew.SMALL_GROUP_BLANK["by_category"])
    # a commune too small for any group publishes counts only
    assert all(r["value_eur"] is None for r in ew.build_buckets(df.head(8)))


def test_small_group_guard():
    ew._check_small_groups({"by_improvement_ratio": [
        {"bucket": "ge50", "parcels": 500, "value_eur": 1000.0}]})
    with pytest.raises(AssertionError):
        ew._check_small_groups({"by_improvement_ratio": [
            {"bucket": "lt10", "parcels": 9, "value_eur": 563_000.0}]})
    with pytest.raises(AssertionError):          # a row must carry its count
        ew._check_small_groups({"by_improvement_ratio": [{"bucket": "x", "value_eur": 1.0}]})
    cat = {"category": "Other", "parcels": 3, "median_change_pct": None, "median_change_eur": None,
           "count_paying_more": None, "share_paying_more_pct": None}
    leg = {"by_category": [{"category": "Other", "median_change_pct": 2.0}]}
    with pytest.raises(AssertionError):
        ew._check_small_groups({"by_category": [cat], "headline_sensitivity": {"low": leg}})
    q = {"quintile": 1, "parcels": 5, "median_change_pct": None,
         "median_change_pct_residential": 3.0}
    with pytest.raises(AssertionError):
        ew._check_small_groups({"by_income_quintile": [q]})
    q["median_change_pct_residential"] = None
    qleg = {"by_income_quintile": [{"quintile": 1, "total_change_pct": -4.0}]}
    with pytest.raises(AssertionError):
        ew._check_small_groups({"by_income_quintile": [q], "baseline_sensitivity": {"low": qleg}})


def test_every_published_payload_passes_the_guards():
    # the committed site data, not just fresh exports: a hand edit or a stale
    # file must not reach the site with a small group's figures
    from pathlib import Path
    skip = {"index.json", "yields.json", "ingestion_register.json"}
    files = [f for f in (Path(__file__).parent / "site/public/data").glob("*.json")
             if f.name not in skip and not f.name.endswith(".validation.json")]
    assert files
    for f in files:
        ew.assert_aggregate_only(json.loads(f.read_text(encoding="utf-8")))
