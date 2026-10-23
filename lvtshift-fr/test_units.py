"""Fast offline unit tests for the LVTShift-FR pure logic.

No network, no upstream solver — just the deterministic estimation/classification
functions. Complements test_synthetic.py (the end-to-end integration test).

Run:  python test_units.py        (plain runner, exits non-zero on failure)
      pytest test_units.py        (also works if pytest is installed)

Style matches test_synthetic.py: plain asserts, no test framework required.
"""

import sys

import numpy as np
import pandas as pd

import estimate
import ingest
from config import CAHORS as CFG   # construction 1650 €/m², dep 80y/0.25, bounds [.15,.85]


def _assert_raises(exc_type, fn, *args, **kwargs):
    """Framework-free stand-in for pytest.raises."""
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


# ------------------------------------------------------------------ #
# current_tax: built-only, no land-area term
# ------------------------------------------------------------------ #

def test_current_tax_is_built_only():
    p = pd.DataFrame({
        "floor_area_m2": [100.0, 300.0, 0.0],   # two built, one vacant
        "parcel_area_m2": [200.0, 400.0, 5000.0],
        "category_fr": ["maison", "appartement", "terrain_nu"],
    })
    out = estimate.current_tax(p, 1000.0)
    assert out["current_tax"].iloc[2] == 0.0, "vacant land must bear zero FB"
    assert abs(out["current_tax"].sum() - 1000.0) < 1e-6, "produit must be conserved"
    assert abs(out["current_tax"].iloc[0] - 250.0) < 1e-6  # 100/400 * 1000
    assert abs(out["current_tax"].iloc[1] - 750.0) < 1e-6


def test_current_tax_category_weights_sensitivity():
    p = pd.DataFrame({
        "floor_area_m2": [100.0, 100.0],
        "category_fr": ["maison", "commerce"],
    })
    out = estimate.current_tax(p, 1000.0,
                               category_weights={"maison": 1.0, "commerce": 3.0})
    assert abs(out["current_tax"].iloc[0] - 250.0) < 1e-6   # weight 1 vs 3
    assert abs(out["current_tax"].iloc[1] - 750.0) < 1e-6


# ------------------------------------------------------------------ #
# _land_value_classified: classify-then-price
# ------------------------------------------------------------------ #

def _classified_frame(rows):
    cols = ["land_type", "parcel_area_m2", "ag_eur_m2", "constructible_eur_m2",
            "market_value", "improvement_value", "floor_area_m2"]
    return pd.DataFrame(rows, columns=cols)


def test_land_built_residual():
    df = _classified_frame([["built", 200.0, 0.5, 100.0, 300000.0, 200000.0, 120.0]])
    out = estimate._land_value_classified(df, CFG)
    assert abs(out["land_value"].iloc[0] - 100000.0) < 1e-6   # market − improvement
    assert out["lv_flag"].iloc[0] == "built_residual"
    assert abs(out["improvement_value"].iloc[0] - 200000.0) < 1e-6


def test_land_built_clipped_high():
    # residual share 0.95 > 0.85 ceiling -> clipped, flagged
    df = _classified_frame([["built", 100.0, 0.5, 100.0, 100000.0, 5000.0, 80.0]])
    out = estimate._land_value_classified(df, CFG)
    assert abs(out["land_value"].iloc[0] - 85000.0) < 1e-6    # 0.85 * market
    assert out["lv_flag"].iloc[0] == "built_clipped_high"


def test_land_constructible_vacant_priced_at_dev_rate():
    df = _classified_frame([["constructible", 500.0, 0.5, 120.0, 0.0, 0.0, 0.0]])
    out = estimate._land_value_classified(df, CFG)
    assert abs(out["land_value"].iloc[0] - 60000.0) < 1e-6    # 500 m² × 120 €/m²
    assert out["improvement_value"].iloc[0] == 0.0
    assert abs(out["market_value"].iloc[0] - 60000.0) < 1e-6


def test_land_agricultural_vacant_priced_cheap():
    df = _classified_frame([["agricultural", 10000.0, 0.45, 120.0, 0.0, 0.0, 0.0]])
    out = estimate._land_value_classified(df, CFG)
    assert abs(out["land_value"].iloc[0] - 4500.0) < 1e-6     # 10000 m² × 0.45
    # a big field is worth orders of magnitude less than the same area of
    # building land (here ~0.4 %), which is the whole point of the fix
    assert out["land_value"].iloc[0] < 0.01 * (10000.0 * 120.0)


def test_land_built_clipped_low_and_dirt_floor():
    # share 0.05 < 0.15 floor -> clipped up to 0.15 of market, flagged low
    df = _classified_frame([
        ["built", 100.0, 0.5, 100.0, 100000.0, 95000.0, 80.0],
        # improvement above market: residual floored at dirt value (2000 m² × 0.5
        # = 1000 €), then the 15 % share floor (1500 €) still binds
        ["built", 2000.0, 0.5, 100.0, 10000.0, 20000.0, 80.0],
    ])
    out = estimate._land_value_classified(df, CFG)
    assert abs(out["land_value"].iloc[0] - 15000.0) < 1e-6
    assert out["lv_flag"].iloc[0] == "built_clipped_low"
    assert abs(out["land_value"].iloc[1] - 1500.0) < 1e-6
    assert out["lv_flag"].iloc[1] == "built_clipped_low"
    assert (out["land_value"] >= 0).all()


def test_land_deferred_au_and_unknown_vacant():
    df = _classified_frame([
        ["constructible_deferred", 400.0, 0.5, 30.0, 0.0, 0.0, 0.0],
        ["unknown", 1000.0, 0.5, 120.0, 0.0, 0.0, 0.0],
        ["natural", 1000.0, 0.5, 120.0, 0.0, 0.0, 0.0],
    ])
    out = estimate._land_value_classified(df, CFG)
    # deferred AU priced at its (already discounted) development rate
    assert abs(out["land_value"].iloc[0] - 12000.0) < 1e-6
    # unknown zoning priced conservatively as dirt, and flagged as such
    assert abs(out["land_value"].iloc[1] - 500.0) < 1e-6
    assert out["lv_flag"].iloc[1] == "vacant_unknown_ag"
    assert out["lv_flag"].iloc[2] == "natural"
    assert (out["improvement_value"] == 0.0).all()


# ------------------------------------------------------------------ #
# improvement_value: depreciated replacement cost
# ------------------------------------------------------------------ #

def _bld(**kw):
    base = dict(idpar="P", footprint_m2=100.0, n_levels=2.0, height_m=6.0,
                year_built=2025.0, usage="Résidentiel", n_dwellings=1.0,
                ff_match="A 1.0")
    base.update(kw)
    return base


def test_improvement_value_new_building():
    b = pd.DataFrame([_bld(year_built=2025.0)])   # age 0 -> no depreciation
    out = estimate.improvement_value(b, CFG)
    assert abs(out["floor_area_m2"].iloc[0] - 200.0) < 1e-6      # 100 × 2 levels
    assert abs(out["improvement_value"].iloc[0] - 200 * 1650 * 1.0) < 1e-3


def test_improvement_value_depreciation_floor():
    b = pd.DataFrame([_bld(year_built=1900.0)])   # age 125 > 80 -> floored at 0.25
    out = estimate.improvement_value(b, CFG)
    assert abs(out["improvement_value"].iloc[0] - 200 * 1650 * CFG.dep_floor) < 1e-3


def test_improvement_value_imputes_missing_levels():
    b = pd.DataFrame([_bld(n_levels=np.nan, height_m=9.0)])   # -> round(9/3)=3
    out = estimate.improvement_value(b, CFG)
    assert abs(out["floor_area_m2"].iloc[0] - 300.0) < 1e-6
    assert out["imp_quality"].iloc[0] == "imputed_levels"


def test_missing_levels_by_building_type():
    iac = "Industriel, agricole ou commercial"
    rows = [  # (usage, nature, light, height) -> expected levels
        (("Industriel", iac, False, 14.0), 1.0),            # warehouse: not 5 storeys
        (("Commercial et services", iac, False, 16.0), 1.0),  # exhibition hall
        (("Agricole", "Serre", False, 4.0), 1.0),
        (("Résidentiel", "Indifférenciée", True, 6.0), 1.0),  # light structure
        (("Sportif", "Indifférenciée", False, 9.0), 1.0),
        (("Annexe", "Indifférenciée", False, 3.0), 1.0),
        (("Commercial et services", "Indifférenciée", False, 5.5), 1.0),   # shop
        (("Commercial et services", "Indifférenciée", False, 21.0), 6.0),  # offices
        (("Résidentiel", "Indifférenciée", False, 15.0), 5.0),             # housing
        (("Résidentiel", "Indifférenciée", False, np.nan), 1.0),
        (("Résidentiel", "Indifférenciée", False, 0.0), 1.0),               # 0 = unknown
    ]
    b = pd.DataFrame([dict(usage=u, nature=n, construction_legere=l, height_m=h)
                      for (u, n, l, h), _ in rows])
    assert list(estimate.impute_levels(b)) == [e for _, e in rows]
    # known counts are kept, and a zero count is treated as missing
    known = pd.DataFrame([_bld(n_levels=3.0, height_m=14.0, usage="Industriel", nature=iac),
                          _bld(idpar="Q", n_levels=0.0, height_m=14.0, usage="Industriel",
                               nature=iac)])
    out = estimate.improvement_value(known, CFG).set_index("idpar")
    assert out.loc["P", "floor_area_m2"] == 300.0 and out.loc["Q", "floor_area_m2"] == 100.0
    # frames without the new columns fall back to height ÷ 3 m
    s = pd.DataFrame({"usage": ["Résidentiel"] * 3, "height_m": [9.0] * 3,
                      "construction_legere": ["false", "true", None]})
    assert list(estimate.impute_levels(s)) == [3.0, 1.0, 3.0]   # "false" is not True
    huge = pd.DataFrame({"usage": ["Commercial et services", "Résidentiel", "Résidentiel"],
                         "height_m": [1e9, float("inf"), 330.0]})
    assert list(estimate.impute_levels(huge)) == [1.0, 1.0, 100.0]   # corrupt -> unknown; cap
    txt = estimate.improvement_value(pd.DataFrame([_bld(n_levels="2")]), CFG)
    assert txt["floor_area_m2"].iloc[0] == 200.0
    legacy = pd.DataFrame({"height_m": [9.0, np.nan]})
    assert list(estimate.impute_levels(legacy)) == [3.0, 1.0]


def test_newer_building_depreciates_less():
    # the construction-year fix matters because year drives building value,
    # which drives the residual land value
    old = estimate.improvement_value(pd.DataFrame([_bld(year_built=1961.0)]), CFG)
    new = estimate.improvement_value(pd.DataFrame([_bld(year_built=2017.0)]), CFG)
    assert new["improvement_value"].iloc[0] > old["improvement_value"].iloc[0]


def test_maintained_stock_effective_age():
    # w = 1: a 125-year-old building is valued as if 30 years old;
    # w = 0.5: halfway between that and its real age; w = 0: unchanged
    b = pd.DataFrame([_bld(year_built=1900.0)])
    cap = CFG.dep_maintained_age_cap
    full = 1 - (1 - CFG.dep_floor) * cap / CFG.dep_years
    for w, age in ((1.0, cap), (0.5, (cap + 125) / 2), (0.0, 125)):
        out = estimate.improvement_value(b, CFG, maint_weight=pd.Series({"P": w}))
        factor = max(CFG.dep_floor, 1 - (1 - CFG.dep_floor) * age / CFG.dep_years)
        assert abs(out["improvement_value"].iloc[0] - 200 * 1650 * factor) < 1e-3
    assert full > CFG.dep_floor


def test_maintenance_weight_ramps_on_area_price_ratio():
    lo, hi = CFG.dep_q_ramp
    # q = habitable price ÷ gross cost, the basis dep_q_ramp was calibrated on
    cost = CFG.construction_cost_eur_m2
    surface = pd.DataFrame({"cell": ["a", "b", "c"], "type_local": ["Appartement"] * 3,
                            "eur_m2": [cost * lo, cost * (lo + hi) / 2, cost * hi * 2]})
    parcels = pd.DataFrame({"idpar": ["1", "2", "3", "4"], "cell": ["a", "b", "c", "c"],
                            "type_local": ["Appartement"] * 4,
                            "iris": ["I1", "I2", "I3", None]})
    w = estimate.maintenance_weight(parcels, surface, CFG)
    assert w["1"] == 0.0 and abs(w["2"] - 0.5) < 1e-9 and w["3"] == 1.0
    # no IRIS -> commune median price (between cells b and c) -> above the ramp
    assert w["4"] == 1.0


# ------------------------------------------------------------------ #
# DPE construction-period -> year mapping
# ------------------------------------------------------------------ #

def test_dpe_period_year_mapping_complete_and_monotonic():
    m = ingest.DPE_PERIODE_TO_YEAR
    bands = ["avant 1948", "1948-1974", "1975-1977", "1978-1982", "1983-1988",
             "1989-2000", "2001-2005", "2006-2012", "2013-2021", "après 2021"]
    assert set(bands) <= set(m), "all standard DPE eras must be mapped"
    years = [m[b] for b in bands]
    assert years == sorted(years), "midpoint years must increase with the era"
    assert all(1900 <= y <= 2026 for y in years)


# ------------------------------------------------------------------ #
# tab_comparables: trust only terrains-à-bâtir, trim outliers
# ------------------------------------------------------------------ #

def test_tab_comparables_filters_non_building_plots():
    eur = list(range(30, 51))                       # 21 TAB plots, 30..50 €/m²
    rows = [{"id_mutation": f"m{i}", "valeur_fonciere": e * 1000.0,
             "surface_terrain": 1000.0, "nature_culture": "terrains a bâtir",
             "latitude": 44.4, "longitude": 1.4} for i, e in enumerate(eur)]
    # contaminated non-TAB rows (a house sold as "sols" at 2000 €/m²) must be dropped
    rows += [{"id_mutation": f"s{i}", "valeur_fonciere": 2_000_000.0,
              "surface_terrain": 1000.0, "nature_culture": "sols",
              "latitude": 44.4, "longitude": 1.4} for i in range(3)]
    out = ingest.tab_comparables(CFG, pd.DataFrame(rows))
    assert len(out) >= 15, "should keep most TAB comparables"
    assert out["eur_m2_land"].max() <= 50.0, "non-building-plot rows must be excluded"
    assert 38.0 <= out["eur_m2_land"].median() <= 42.0


# ------------------------------------------------------------------ #
# run_commune classification helpers
# ------------------------------------------------------------------ #

def test_residential_category_by_dwellings():
    import run_commune as rc
    assert rc._residential_cat(1, 2) == "maison"
    assert rc._residential_cat(3, 2) == "appartement"
    assert rc._residential_cat(8, 2) == "immeuble_collectif"
    assert rc._residential_cat(np.nan, 4) == "appartement"   # no count -> storeys
    assert rc._residential_cat(np.nan, 1) == "maison"


def test_derive_parcel_category_dominant_building():
    import run_commune as rc
    b = pd.DataFrame([
        dict(idpar="P1", footprint_m2=100.0, n_levels=1.0, usage="Résidentiel", n_dwellings=1.0),
        dict(idpar="P2", footprint_m2=100.0, n_levels=1.0, usage="Commercial et services", n_dwellings=0.0),
        dict(idpar="P3", footprint_m2=20.0, n_levels=1.0, usage="Résidentiel", n_dwellings=1.0),
        dict(idpar="P3", footprint_m2=200.0, n_levels=1.0, usage="Industriel", n_dwellings=0.0),
    ])
    cat = rc.derive_parcel_category(b)
    assert cat["P1"] == "maison"
    assert cat["P2"] == "commerce"
    assert cat["P3"] == "industriel"     # dominant (largest-floor) building wins


def test_grid_cell_deterministic():
    import run_commune as rc
    assert rc._grid_cell([800.0], [1200.0]) == ["2_3"]        # floor(x/400), floor(y/400)
    assert rc._grid_cell([0.0], [399.0]) == ["0_0"]


# ------------------------------------------------------------------ #
# hedonic market value
# ------------------------------------------------------------------ #

def test_market_value_scales_with_floor_area():
    dvf = pd.DataFrame({
        "price": [200000.0] * 4,
        "floor_area_m2": [100.0] * 4,            # all 2000 €/m²
        "type_local": ["Maison"] * 4,
        "year": [2024] * 4,
        "cell": ["A"] * 4,
    })
    surface, _ = estimate.fit_hedonic(dvf)
    parcels = pd.DataFrame({
        "cell": ["A", "A"], "type_local": ["Maison", "Maison"],
        "floor_area_m2": [50.0, 100.0],
    })
    out = estimate.market_value(parcels, surface)
    assert abs(out["market_value"].iloc[0] - 100000.0) < 1.0   # 2000 × 50
    assert abs(out["market_value"].iloc[1] - 200000.0) < 1.0   # doubles with area


def test_market_value_converts_gross_to_habitable_area():
    # DVF prices habitable m²; BD TOPO area is gross -> scale by type's ratio
    surface = pd.DataFrame({"cell": ["A", "A"], "type_local": ["Maison", "Appartement"],
                            "eur_m2": [2000.0, 3000.0]})
    parcels = pd.DataFrame({"cell": ["A", "A", "A"],
                            "type_local": ["Maison", "Appartement", "Local"],
                            "floor_area_m2": [100.0, 100.0, 100.0]})
    ntg = {"Appartement": 0.7, "Maison": 0.8}
    mv = estimate.market_value(parcels, surface, ntg)["market_value"]
    assert abs(mv.iloc[0] - 2000 * 0.8 * 100) < 1e-6
    assert abs(mv.iloc[1] - 3000 * 0.7 * 100) < 1e-6
    # an unlisted type (cell mean price) takes the flat ratio
    assert abs(mv.iloc[2] - 2500 * 0.7 * 100) < 1e-6
    for bad in ({"Maison": 0.8}, {"Appartement": 0.7, "Maison": 0.0},
                {"Appartement": 1.3, "Maison": 0.8}, {"Appartement": float("nan"), "Maison": 0.8},
                {"Appartement": 0.7, "maison": 0.8},                    # misspelt key
                {"Appartement": 0.7, "Maison": 0.8, "Local": 0.9},      # unknown key
                {"Appartement": 1e-9, "Maison": 0.8}):                  # implausible
        _assert_raises(ValueError, estimate.market_value, parcels, surface, bad)
    for bad in ({"Appartement": True, "Maison": 0.8}, {"Appartement": "0.6", "Maison": 0.8}):
        _assert_raises(TypeError, estimate.market_value, parcels, surface, bad)
    # configs validate at construction and freeze their maps
    import dataclasses
    _assert_raises(ValueError, dataclasses.replace, CFG,
                   net_to_gross={"Appartement": 0.64, "maison": 0.61})
    try:
        CFG.net_to_gross["Appartement"] = 0.1
    except TypeError:
        pass
    else:
        raise AssertionError("config ratio maps must be read-only")
    # every configured commune carries valid ratio maps
    from config import COMMUNES
    for c in COMMUNES.values():
        estimate._check_net_to_gross(c.net_to_gross)
        estimate._check_net_to_gross(c.cost_net_to_gross)


def test_habitable_basis_makes_land_share_independent_of_measured_ratio():
    import dataclasses
    p = pd.DataFrame({"type_local": ["Appartement", "Maison", "Local"],
                      "floor_area_m2": [1000.0, 150.0, 400.0],
                      "improvement_value": [1000.0 * 1650, 150.0 * 1650, 400.0 * 1650]})
    surface = pd.DataFrame({"cell": ["A", "A"], "type_local": ["Appartement", "Maison"],
                            "eur_m2": [4000.0, 3000.0]})
    p["cell"] = "A"
    shares = []
    for r in (0.5, 0.64, 0.9):
        cfg = dataclasses.replace(CFG, net_to_gross={"Appartement": r, "Maison": r})
        h = estimate.habitable_basis(p, cfg)
        m = estimate.market_value(h, surface, cfg.net_to_gross)
        shares.append(list(1 - m["improvement_value"] / m["market_value"]))
        # building value = cost per habitable m² × habitable area
        c = CFG.cost_net_to_gross
        assert abs(h["improvement_value"].iloc[0]
                   - 1650 / c["Appartement"] * r * 1000) < 1e-6
        assert abs(h["habitable_area_m2"].iloc[1] - r * 150) < 1e-9
    assert np.allclose(shares[0], shares[1]) and np.allclose(shares[1], shares[2])
    # flats: 1 − (1650 / 0.74) / 4000
    assert abs(shares[1][0] - (1 - 1650 / CFG.cost_net_to_gross["Appartement"] / 4000)) < 1e-9


def test_house_cost_applies_to_houses_only():
    import dataclasses
    p = pd.DataFrame({"type_local": ["Appartement", "Maison", "Local"],
                      "floor_area_m2": [1000.0, 150.0, 400.0],
                      "improvement_value": [1000.0 * 1650, 150.0 * 1650, 400.0 * 1650]})
    base = estimate.habitable_basis(p, CFG)
    assert CFG.house_cost_eur_m2 is None and CFG.house_cost == 1650.0
    cheap = dataclasses.replace(CFG, house_cost_eur_m2=1320.0)
    h = estimate.habitable_basis(p, cheap)
    assert abs(h["improvement_value"].iloc[1] - 0.8 * base["improvement_value"].iloc[1]) < 1e-6
    assert np.allclose(h["improvement_value"].iloc[[0, 2]], base["improvement_value"].iloc[[0, 2]])
    assert np.allclose(h["habitable_area_m2"], base["habitable_area_m2"])
    # the maintained-stock rule keeps its calibrated basis (the commune cost)
    surface = pd.DataFrame({"cell": ["a"], "type_local": ["Maison"], "eur_m2": [3300.0]})
    parcels = pd.DataFrame({"idpar": ["P"], "cell": ["a"], "type_local": ["Maison"]})
    assert np.allclose(estimate.maintenance_weight(parcels, surface, CFG),
                       estimate.maintenance_weight(parcels, surface, cheap))
    assert type(dataclasses.replace(CFG, house_cost_eur_m2=np.int64(1500)).house_cost_eur_m2) is float
    s = p.assign(type_local=pd.Series(["Appartement", "Maison", pd.NA], dtype="string"))
    assert np.isfinite(estimate.habitable_basis(s, cheap)["improvement_value"]).all()
    for bad in (0.0, -1.0, float("nan"), float("inf"), True, "1500", 1e308):
        _assert_raises(ValueError, dataclasses.replace, CFG, house_cost_eur_m2=bad)
    _assert_raises(ValueError, dataclasses.replace, CFG, construction_cost_eur_m2=0.0)


# ------------------------------------------------------------------ #
# commune slate completion
# ------------------------------------------------------------------ #

def test_commune_slate_is_complete():
    from config import COMMUNES, SITE_COMMUNES, AG_EUR_M2_BY_DEP
    expected = {
        "roubaix": ("59512", "59"), "montreuil": ("93048", "93"),
        "villeurbanne": ("69266", "69"), "grenoble": ("38185", "38"),
        "annemasse": ("74012", "74"), "cahors": ("46042", "46"),
        "figeac": ("46102", "46"), "sete": ("34301", "34"),
        "larochelle": ("17300", "17"), "mulhouse": ("68224", "68"),
        "paris": ("75056", "75"), "lyon": ("69123", "69"),
    }
    assert set(SITE_COMMUNES) == set(expected),         "site slate must be the 10 pilot communes + Paris + Lyon"
    for key, (insee, dep) in expected.items():
        assert COMMUNES[key].insee_code == insee
        assert COMMUNES[key].departement == dep
    for dep in ("34", "17", "68"):
        assert dep in AG_EUR_M2_BY_DEP, f"missing agricultural rate for dep {dep}"


def test_maintained_rule_rejects_bad_config():
    import dataclasses
    b = pd.DataFrame([_bld(year_built=1900.0)])
    w = pd.Series({"P": 1.0})
    _assert_raises(ValueError, estimate.improvement_value, b,
                   dataclasses.replace(CFG, dep_maintained_age_cap=-50), maint_weight=w)
    # an out-of-range weight is clamped, never inflates value above new
    out = estimate.improvement_value(b, CFG, maint_weight=pd.Series({"P": 5.0}))
    assert out["improvement_value"].iloc[0] <= 200 * 1650 + 1e-6
    surface = pd.DataFrame({"cell": ["a"], "type_local": ["Appartement"], "eur_m2": [3000.0]})
    parcels = pd.DataFrame({"idpar": ["P"], "cell": ["a"], "type_local": ["Appartement"]})
    for ramp in ((2.0, 1.0), (1.0,), (float("nan"), 2.0)):
        _assert_raises(ValueError, estimate.maintenance_weight, parcels, surface,
                       dataclasses.replace(CFG, dep_q_ramp=ramp))


def test_maintenance_weight_ignores_unbuilt_parcels():
    # vacant plots carry a placeholder type_local; they must not set the area price
    cost = CFG.construction_cost_eur_m2
    surface = pd.DataFrame({"cell": ["a", "a"], "type_local": ["Maison", "Appartement"],
                            "eur_m2": [cost * 4.0, cost * 1.0]})
    parcels = pd.DataFrame({
        "idpar": ["H1", "H2", "V1", "V2", "V3"], "cell": ["a"] * 5,
        "type_local": ["Maison", "Maison", "Appartement", "Appartement", "Appartement"],
        "category_fr": ["maison", "maison", "terrain_nu", "terrain_nu", "terrain_nu"],
        "iris": ["I1"] * 5,
    })
    w = estimate.maintenance_weight(parcels, surface, CFG)
    # houses set the price (q = 4, above the ramp); vacant plots inherit it
    assert (w == 1.0).all(), w.to_dict()
    # an IRIS with no built parcel falls back to the commune's built median
    parcels.loc[parcels["idpar"].isin(["V1", "V2", "V3"]), "iris"] = "I2"
    w = estimate.maintenance_weight(parcels, surface, CFG)
    assert (w == 1.0).all(), w.to_dict()
    # no built parcel anywhere: fall back to every parcel rather than fail
    w = estimate.maintenance_weight(parcels.iloc[2:], surface, CFG)
    assert (w == 0.0).all(), w.to_dict()


def test_dwellings_per_parcel_counts_homes_not_plots():
    from run_pipeline import dwellings_per_parcel, GROSS_M2_PER_DWELLING
    p = pd.DataFrame({"idpar": ["H", "B", "Bx", "Hx", "S", "V"],
                      "category_fr": ["maison", "immeuble_collectif", "immeuble_collectif",
                                      "maison", "commerce", "terrain_nu"],
                      "floor_area_m2": [120.0, 5000.0, 10 * GROSS_M2_PER_DWELLING,
                                        90.0, 800.0, 0.0]})
    b = pd.DataFrame({"idpar": ["H", "B", "B", "S"],
                      "n_dwellings": [1.0, 40.0, 19.5, 3.0]})
    out = dwellings_per_parcel(p, b)
    # measured counts summed over a parcel's buildings; missing ones imputed
    # (house 1, flats from floor area); non-residential parcels count 0
    assert list(out["n_dwellings"]) == [1.0, 59.5, 10.0, 1.0, 0.0, 0.0]
    assert list(out["dwellings_imputed"]) == [False, False, True, True, False, False]
def test_price_index_parses_full_years_only():
    def series(obs, idbank="010567012", freq="T"):
        return (f'<x><Series IDBANK="{idbank}" FREQ="{freq}">' + obs
                + "</Series></x>").encode()
    full = "".join(f'<Obs TIME_PERIOD="2024-Q{q}" OBS_VALUE="{100 + q}" OBS_STATUS="A"/>'
                   for q in (1, 2, 3, 4))
    xml = series(full + '<Obs OBS_VALUE="130" TIME_PERIOD="2025-Q1"/>')  # order varies
    orig = ingest._get
    try:
        ingest._get = lambda url, *a, **k: xml
        avg = ingest.fetch_price_index_annual("010567012")
        _assert_raises(ValueError, ingest.fetch_price_index_annual, "0105670&x")
        for bad in (b"<message:Error>no data</message:Error>",            # error body
                    series(full, idbank="010567058"),                      # wrong series
                    series(full, freq="A"),                                # not quarterly
                    series(full + '<Obs TIME_PERIOD="2024-Q1" OBS_VALUE="1"/>'),  # dup
                    series('<Obs TIME_PERIOD="2024-Q1" OBS_VALUE="0"/>'),  # non-positive
                    b"<Obs " * 20_000):                                    # hostile
            ingest._get = lambda url, *a, _b=bad, **k: _b
            _assert_raises(ValueError, ingest.fetch_price_index_annual, "010567012")
    finally:
        ingest._get = orig
    assert avg == {2024: 102.5}, avg          # 2025 has one quarter: excluded


def test_deflator_factors_and_application():
    import dataclasses
    from config import COMMUNES, price_index_geography
    cfg = dataclasses.replace(COMMUNES["paris"], dvf_years=(2022, 2024),
                              reference_year=2025)
    seen = []

    def fake(idbank, start):
        seen.append(idbank)
        return {2022: 110.0, 2024: 100.0, 2025: 99.0}
    f = estimate.deflator_factors(cfg, fetch=fake)
    assert abs(f["Appartement"][2022] - 0.9) < 1e-12 and abs(f["Maison"][2024] - 0.99) < 1e-12
    assert seen == ["010567012"]       # Paris: one flats series serves both types
    # a missing year must fail loudly, never deflate some years only
    _assert_raises(ValueError, estimate.deflator_factors, cfg,
                   fetch=lambda i, start: {2022: 1.0, 2025: 1.0})
    _assert_raises(ValueError, estimate.deflator_factors, cfg,      # implausible
                   fetch=lambda i, start: {2022: 400.0, 2024: 100.0, 2025: 99.0})
    # geography: most local series first
    assert price_index_geography(COMMUNES["montreuil"]) == "d93"
    assert price_index_geography(COMMUNES["villeurbanne"]) == "agglo_lyon"
    assert price_index_geography(COMMUNES["saint-priest"]) == "agglo_lyon"
    # keyed on the INSEE code, so a copy without its registry key still matches
    import dataclasses
    assert price_index_geography(
        dataclasses.replace(COMMUNES["saint-priest"], key="")) == "agglo_lyon"
    assert price_index_geography(COMMUNES["grenoble"]) == "auvergne_rhone_alpes"
    assert price_index_geography(COMMUNES["roubaix"]) == "agglo_lille"
    assert price_index_geography(COMMUNES["cahors"]) == "province"
    # by type and year in the hedonic; unknown year untouched
    dvf = pd.DataFrame({"price": [100_000.0] * 3, "floor_area_m2": [50.0] * 3,
                        "type_local": ["Appartement", "Maison", "Maison"],
                        "year": [2022, 2024, 2019], "cell": ["A"] * 3})
    _s, d = estimate.fit_hedonic(dvf, deflator=f)
    assert list(d["price"].round(6)) == [90_000.0, 99_000.0, 100_000.0]
    _s, d = estimate.fit_hedonic(dvf, deflator={2022: 0.5})   # legacy flat form
    assert list(d["price"]) == [50_000.0, 100_000.0, 100_000.0]


def test_tab_comparables_deflated_with_house_index():
    rows = [{"id_mutation": f"m{i}", "valeur_fonciere": 40_000.0,
             "surface_terrain": 1000.0, "nature_culture": "terrains a bâtir",
             "latitude": 44.4, "longitude": 1.4,
             "date_mutation": "2022-06-01"} for i in range(21)]
    out = ingest.tab_comparables(CFG, pd.DataFrame(rows),
                                 deflator={"Maison": {2022: 0.9}, "Appartement": {2022: 0.5}})
    assert abs(out["eur_m2_land"].median() - 36.0) < 1e-9
    flat = ingest.tab_comparables(CFG, pd.DataFrame(rows), deflator={2022: 0.5})
    assert abs(flat["eur_m2_land"].median() - 20.0) < 1e-9


def test_building_type_from_usage_and_nature():
    iac = "Industriel, agricole ou commercial"
    b = pd.DataFrame({
        "usage": ["Résidentiel", "Industriel", "Industriel", "Commercial et services",
                  "Commercial et services", "Agricole", "Commercial et services",
                  "Sportif", "Annexe", "Religieux", "Indifférencié", None],
        "nature": ["Indifférenciée", iac, "Indifférenciée", iac, "Indifférenciée",
                   "Indifférenciée", "Serre", "Indifférenciée", "Indifférenciée",
                   "Eglise", iac, None]})
    assert list(estimate.building_type(b)) == [
        "residential", "shed", "workshop", "retail_box", "office", "agri_shed",
        "greenhouse", "sports", "annex", "religious", "shed", "residential"]
    from config import BUILDING_TYPES
    for t, (ratio, life, floor, valuation, land) in BUILDING_TYPES.items():
        assert 0 < ratio <= 1.5 and valuation in ("residual", "drc")
        assert (life is None) == (floor is None) and (life is None or (life > 0 and 0 < floor < 1))
        assert (valuation == "drc") == (land in ("activity", "residential"))


def test_nonresidential_cost_life_and_mid_life_age():
    from config import BUILDING_TYPES
    iac = "Industriel, agricole ou commercial"
    ratio, life, floor = BUILDING_TYPES["shed"][:3]
    # a new shed: its own cost ratio, one level
    new = estimate.improvement_value(pd.DataFrame([_bld(
        usage="Industriel", nature=iac, n_levels=np.nan, height_m=14.0,
        year_built=2025.0)]), CFG)
    assert abs(new["improvement_value"].iloc[0] - 100 * 1650 * ratio) < 1e-6
    assert new["valuation"].iloc[0] == "drc" and new["drc_land"].iloc[0] == "activity"
    # unknown year: mid-life, not the dwellings' median age
    b = pd.DataFrame([_bld(idpar="H", year_built=1900.0),
                      _bld(idpar="S", usage="Industriel", nature=iac, n_levels=1.0,
                           year_built=np.nan)])
    out = estimate.improvement_value(b, CFG).set_index("idpar")
    dep = 1 - (1 - floor) * 0.5
    assert abs(out.loc["S", "improvement_value"] - 100 * 1650 * ratio * dep) < 1e-6
    # the maintained-stock rule is for housing only
    w = pd.Series({"H": 1.0, "S": 1.0})
    old = pd.DataFrame([_bld(idpar="S", usage="Industriel", nature=iac, n_levels=1.0,
                             year_built=1960.0)])
    a = estimate.improvement_value(old, CFG)["improvement_value"].iloc[0]
    m = estimate.improvement_value(old, CFG, maint_weight=w)["improvement_value"].iloc[0]
    assert a == m == 100 * 1650 * ratio * floor
    # the dominant building (by floor area) sets the parcel's valuation
    mixed = pd.DataFrame([_bld(idpar="M", footprint_m2=50.0),
                          _bld(idpar="M", usage="Industriel", nature=iac, footprint_m2=400.0,
                               n_levels=1.0)])
    assert estimate.improvement_value(mixed, CFG)["valuation"].iloc[0] == "drc"


def test_drc_parcels_value_land_at_local_price_not_residual():
    p = pd.DataFrame({
        "idpar": ["R", "S", "G"],
        "land_type": ["built"] * 3,
        "parcel_area_m2": [1000.0, 1000.0, 1000.0],
        "floor_area_m2": [500.0, 500.0, 50.0],
        "market_value": [2_000_000.0, 2_000_000.0, 2_000_000.0],   # flat price, unused for DRC
        "improvement_value": [800_000.0, 300_000.0, 20_000.0],
        "constructible_eur_m2": [600.0, 600.0, 600.0],
        "ag_eur_m2": [1.0, 1.0, 1.0],
        "valuation": ["residual", "drc", "drc"],
        "drc_land": [None, "activity", "residential"],
    })
    out = estimate.land_value_residual(p, CFG).set_index("idpar")
    assert out.loc["R", "land_value"] == 1_200_000.0 and out.loc["R", "lv_flag"] == "built_residual"
    land = 600.0 * CFG.activity_land_ratio * 1000
    assert abs(out.loc["S", "land_value"] - land) < 1e-6
    assert out.loc["S", "improvement_value"] == 300_000.0
    assert abs(out.loc["S", "market_value"] - (land + 300_000.0)) < 1e-6
    assert out.loc["S", "lv_flag"] == "built_drc"
    assert out.loc["G", "land_value"] == 600_000.0           # garage plot: residential land
    # never below the dirt value
    p2 = p.assign(constructible_eur_m2=0.0, ag_eur_m2=5.0)
    assert estimate.land_value_residual(p2, CFG).set_index("idpar").loc["S", "land_value"] == 5000.0
    # DRC buildings skip the habitable-area restatement
    h = estimate.habitable_basis(p.assign(type_local="Appartement"), CFG).set_index("idpar")
    assert h.loc["S", "improvement_value"] == 300_000.0
    assert h.loc["R", "improvement_value"] != 800_000.0
    import dataclasses
    # a shed on a 10 ha farmland parcel: only its yard is building land
    farm = p.assign(zone_typ=["U", "A", "U"], parcel_area_m2=[1000.0, 100_000.0, 1000.0])
    o = estimate.land_value_residual(farm, CFG).set_index("idpar")
    yard = 3.0 * 500.0
    assert abs(o.loc["S", "land_value"]
               - (600.0 * CFG.activity_land_ratio * yard + 1.0 * (100_000 - yard))) < 1e-6
    # urban zoning: the whole plot
    urban = p.assign(zone_typ="U", parcel_area_m2=[1000.0, 100_000.0, 1000.0])
    assert abs(estimate.land_value_residual(urban, CFG).set_index("idpar").loc["S", "land_value"]
               - 600.0 * CFG.activity_land_ratio * 100_000) < 1e-6
    for bad in (0.0, 0.01, 1.5, float("nan"), True, "0.4"):
        _assert_raises(ValueError, dataclasses.replace, CFG, activity_land_ratio=bad)


def test_baseline_floor_groups_and_shops_below_flats():
    iac = "Industriel, agricole ou commercial"
    b = pd.DataFrame([
        dict(idpar="F", footprint_m2=100.0, n_levels=3.0, usage="Industriel", usage_2=None, nature=iac),
        dict(idpar="O", footprint_m2=100.0, n_levels=4.0, usage="Commercial et services",
             usage_2=None, nature="Indifférenciée"),
        dict(idpar="M", footprint_m2=100.0, n_levels=5.0, usage="Résidentiel",
             usage_2="Commercial et services", nature="Indifférenciée"),
        dict(idpar="H", footprint_m2=100.0, n_levels=np.nan, height_m=6.0, usage="Résidentiel",
             usage_2=None, nature="Indifférenciée"),
    ])
    f = estimate.baseline_floor(b).set_index("idpar")
    assert f.loc["F"].tolist() == [300.0, 0.0, 0.0]
    assert f.loc["O"].tolist() == [0.0, 400.0, 0.0]
    assert f.loc["M"].tolist() == [0.0, 100.0, 400.0]     # shop on the ground floor
    assert f.loc["H"].tolist() == [0.0, 0.0, 200.0]       # storeys imputed as elsewhere


def test_calibrated_weights_hit_targets_merge_and_cap():
    floor = {"industrial": 1000.0, "professional": 1000.0, "housing": 8000.0}
    w, note = estimate.calibrated_weights(floor, {"industrial": 0.2, "professional": 0.1}, 5.0)
    tax = {k: floor[k] * w[k] for k in floor}
    tot = sum(tax.values())
    assert abs(tax["industrial"] / tot - 0.2) < 1e-12 and abs(tax["professional"] / tot - 0.1) < 1e-12
    assert note == "calibrated"
    # warehouses taxed as professional premises: industrial per m² below
    # professional -> one merged group carrying both targets
    w, note = estimate.calibrated_weights(floor, {"industrial": 0.002, "professional": 0.14}, 5.0)
    assert w["industrial"] == w["professional"] and "merged" in note
    tax = {k: floor[k] * w[k] for k in floor}
    assert abs((tax["industrial"] + tax["professional"]) / sum(tax.values()) - 0.142) < 1e-12
    # one big plant on a few m²: capped
    w, note = estimate.calibrated_weights({"industrial": 10.0, "professional": 1000.0,
                                           "housing": 8990.0},
                                          {"industrial": 0.3, "professional": 0.1}, 5.0)
    assert w["industrial"] == 5.0 and "capped" in note
    # no non-residential floor at all: everything back on housing
    w, _ = estimate.calibrated_weights({"industrial": 0.0, "professional": 0.0, "housing": 10.0},
                                       {"industrial": 0.1, "professional": 0.1}, 5.0)
    assert w == {"housing": 1.0, "industrial": 1.0, "professional": 1.0}


def test_current_tax_with_bucket_weights_is_revenue_exact():
    p = pd.DataFrame({"floor_area_m2": [100.0, 100.0, 0.0, 100.0],
                      "floor_industrial": [100.0, 0.0, 0.0, 0.0],
                      "floor_professional": [0.0, 0.0, 0.0, 100.0],
                      "floor_housing": [0.0, 100.0, 0.0, 0.0],
                      "is_exempt_public": [False, False, False, True]})
    out = estimate.current_tax(p, 3000.0, bucket_weights={"industrial": 2.0, "professional": 0.5,
                                                          "housing": 1.0})
    assert abs(out["current_tax"].sum() - 3000.0) < 1e-9
    assert out["current_tax"].tolist() == [2000.0, 1000.0, 0.0, 0.0]   # exempt and unbuilt pay 0


def test_rei_baseline_split(monkeypatch=None):
    import ingest
    rei = [{"var": "E11", "valeur": 1_000_000.0}, {"var": "WC75", "valeur": 30_000.0},
           {"var": "T29", "valeur": 500_000.0}, {"var": "X503", "valeur": 100_000.0}]
    rates = [{"destinataire": "Commune", "taux_net": 20.0},
             {"destinataire": "Département", "taux_net": 10.0}]
    orig = ingest._ofgl_records
    ingest._ofgl_records = lambda url, where, select: rei if "rei" in url else rates
    try:
        s = ingest.fetch_rei_baseline_split(CFG)
        assert abs(s["industrial"] - 0.1) < 1e-12          # 30 000 / 30 % / 1 M
        assert abs(s["professional"] - 0.2) < 1e-12        # 0.5 × (500k − 100k) / 1 M
        assert s["pro_source"] == "T29-X503"
        import dataclasses
        lyon = dataclasses.replace(CFG, departement="69")   # Rhône 2014 rate, not 10 %
        assert abs(ingest.fetch_rei_baseline_split(lyon)["industrial"]
                   - 30_000 / 0.3103 / 1e6) < 1e-12
        rei[0]["valeur"] = None
        _assert_raises(ingest.IngestUnavailable, ingest.fetch_rei_baseline_split, CFG)
    finally:
        ingest._ofgl_records = orig


# ------------------------------------------------------------------ #

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except Exception as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
