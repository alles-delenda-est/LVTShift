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


def test_newer_building_depreciates_less():
    # the construction-year fix matters because year drives building value,
    # which drives the residual land value
    old = estimate.improvement_value(pd.DataFrame([_bld(year_built=1961.0)]), CFG)
    new = estimate.improvement_value(pd.DataFrame([_bld(year_built=2017.0)]), CFG)
    assert new["improvement_value"].iloc[0] > old["improvement_value"].iloc[0]


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
