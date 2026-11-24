"""Offline tests for building-less urban land: its use (plan × BD TOPO) and its
value at site value (land_use.py, estimate.vacant_site_value,
run_commune.classify_and_price_land, the band's treatment of it).

Run: python -m pytest -q test_land_use.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import estimate  # noqa: E402
import export_web  # noqa: E402
import land_use as lu  # noqa: E402


# ---------------------------------------------------------------- plan's use

def test_zone_use_reads_the_cnig_code_first():
    typ = pd.Series(["U"] * 6)
    code = pd.Series(["01", "03", "02", "05", "08", "1"])
    out = lu.zone_use(typ, code, pd.Series([""] * 6))
    assert list(out) == [lu.HOUSING, lu.HOUSING, lu.ACTIVITY, lu.ACTIVITY,
                         lu.OPEN_SPACE, lu.HOUSING]       # "1" read as "01"


def test_zone_use_falls_back_to_the_long_label_and_never_to_the_short_one():
    typ = pd.Series(["U"] * 6)
    code = pd.Series(["00", "99", None, "", "00", "00"])
    label = pd.Series(["Parcs urbains", "Zone économique tertiaire et technologique",
                       "Parc d'activités de la Pallice", "Zone de grands services urbains",
                       "Centre ancien", None])
    out = lu.zone_use(typ, code, label)
    assert list(out[:4]) == [lu.OPEN_SPACE, lu.ACTIVITY, lu.ACTIVITY, lu.ACTIVITY]
    assert pd.isna(out[4]) and pd.isna(out[5])       # silent plan: model default


def test_zone_use_treats_a_and_n_as_open_space():
    out = lu.zone_use(pd.Series(["A", "N", "AU"]), pd.Series(["01", "", ""]), None)
    assert list(out[:2]) == [lu.OPEN_SPACE, lu.OPEN_SPACE] and pd.isna(out[2])


def test_bdtopo_feature_use():
    zai = "BDTOPO_V3:zone_d_activite_ou_d_interet"
    assert lu.bdtopo_feature_use(zai, {"nature": "Espace public", "categorie": "Culture et loisirs"}) == lu.OPEN_SPACE
    assert lu.bdtopo_feature_use(zai, {"nature": "Stade", "categorie": "Sport"}) == lu.OPEN_SPACE
    assert lu.bdtopo_feature_use(zai, {"nature": "Zone industrielle",
                                       "categorie": "Industriel et commercial"}) == lu.ACTIVITY
    assert lu.bdtopo_feature_use(zai, {"nature": "Musée", "categorie": "Culture et loisirs"}) is None
    assert lu.bdtopo_feature_use("BDTOPO_V3:cimetiere", {}) == lu.OPEN_SPACE
    assert lu.bdtopo_feature_use("BDTOPO_V3:equipement_de_transport", {"nature": "Parking"}) == lu.ACTIVITY


def test_bdtopo_use_shares_dissolves_overlaps():
    gpd = pytest.importorskip("geopandas")
    from shapely.geometry import box
    parcels = gpd.GeoDataFrame({"idpar": ["P", "Q"]},
                               geometry=[box(0, 0, 10, 10), box(20, 0, 30, 10)], crs=2154)
    feats = gpd.GeoDataFrame({"use": [lu.OPEN_SPACE, lu.OPEN_SPACE, lu.ACTIVITY]},
                             geometry=[box(0, 0, 6, 10), box(0, 0, 6, 10), box(25, 0, 40, 10)],
                             crs=2154)
    out = lu.bdtopo_use_shares(parcels, feats).set_index("idpar")
    assert abs(out.loc["P", "bdtopo_open_share"] - 0.6) < 1e-9     # not 1.2
    assert out.loc["P", "bdtopo_activity_share"] == 0.0
    assert abs(out.loc["Q", "bdtopo_activity_share"] - 0.5) < 1e-9


def test_vacant_use_combines_the_two_readings():
    plan = pd.Series([lu.OPEN_SPACE, None, lu.ACTIVITY, None, lu.HOUSING, lu.ACTIVITY])
    open_sh = pd.Series([0.0, 0.8, 0.0, 0.0, 0.2, 0.9])
    act_sh = pd.Series([0.0, 0.0, 0.7, 0.6, 0.0, 0.0])
    out = lu.vacant_use(plan, open_sh, act_sh, 0.5)
    assert list(out["vacant_use"]) == [lu.OPEN_SPACE, lu.OPEN_SPACE, lu.ACTIVITY,
                                       lu.ACTIVITY, lu.HOUSING, lu.OPEN_SPACE]
    assert list(out["vacant_use_source"]) == ["plan", "bdtopo", "both", "bdtopo",
                                              "default", "bdtopo"]
    with pytest.raises(ValueError):
        lu.vacant_use(plan, open_sh, act_sh, 0.0)


def test_cross_check_tabulates_agreement():
    t = lu.cross_check(pd.Series([lu.OPEN_SPACE, lu.OPEN_SPACE, None]),
                       pd.Series([0.9, 0.0, 0.0]), pd.Series([0.0, 0.0, 0.0]),
                       pd.Series([2.0, 3.0, 5.0]))
    assert t.loc[lu.OPEN_SPACE, lu.OPEN_SPACE] == 2.0
    assert t.loc[lu.OPEN_SPACE, "nothing"] == 3.0
    assert t.loc["unstated", "nothing"] == 5.0


# ----------------------------------------------------------- value at site

def _frame():
    """One IRIS, one zone: three built parcels and building-less ones."""
    built = pd.DataFrame({
        "idpar": ["B1", "B2", "B3"],
        "parcel_area_m2": [500.0, 500.0, 500.0],
        "floor_area_m2": [1000.0, 1000.0, 1000.0],          # FAR 2 everywhere
        "building_cost": [1_000_000.0] * 3,
        "land_value": [600_000.0, 800_000.0, 1_000_000.0],
        "improvement_value": [1_000_000.0] * 3,
        "market_value": [1_600_000.0, 1_800_000.0, 2_000_000.0],
        "land_share": [0.4] * 3, "land_share_raw": [0.4] * 3,
        "lv_flag": ["built_residual"] * 3,
    })
    vac = pd.DataFrame({
        "idpar": ["V", "A", "S", "E", "W"],
        "parcel_area_m2": [500.0, 500.0, 40.0, 500.0, 500.0],
        "floor_area_m2": [0.0] * 5,
        "building_cost": [0.0] * 5,
        "land_value": [9e9] * 5,             # the plot-sale price, to be replaced
        "improvement_value": [0.0] * 5,
        "market_value": [9e9] * 5,
        "land_share": [1.0] * 5, "land_share_raw": [1.0] * 5,
        "lv_flag": ["constructible", "constructible", "constructible", "constructible",
                    "constructible"],
        "vacant_price_factor": [1.0, 0.45, 1.0, 1.0, 1.0],
    })
    p = pd.concat([built, vac], ignore_index=True)
    p["iris"] = ["I1"] * 7 + ["I2"]          # W alone in an IRIS without built land
    p["zone_typ"] = "U"
    p["zone_libelle"] = "UA"
    p["is_exempt_public"] = [False] * 6 + [True, False]      # E is exempt
    return p


PRM = {"min_zone_parcels": 1, "plot_cap_quantile": 1.0}


def test_vacant_land_is_valued_like_the_built_land_of_its_iris_and_zone():
    p = estimate.site_value_land(_frame(), PRM)
    out = estimate.vacant_site_value(p, PRM).set_index("idpar")
    # same plot, same zone: the building-less plot gets the built plots' land
    assert abs(out.loc["V", "land_value"] - 800_000.0) < 1e-6
    assert out.loc["V", "lv_flag"] == "vacant_site_value"
    assert out.loc["V", "land_value_current"] == 9e9             # old price kept
    # business land at the business-land ratio
    assert abs(out.loc["A", "land_value"] - 0.45 * 800_000.0) < 1e-6
    # a sliver (40 m² against a 500 m² typical plot) counts as garden ground
    assert bool(out.loc["S", "vacant_sliver"])
    assert abs(out.loc["S", "land_value"] - 0.25 * 40 / 500 * 800_000.0) < 1e-6
    # exempt land untouched; an IRIS without built land takes the commune's rate
    assert out.loc["E", "land_value"] == 9e9
    assert abs(out.loc["W", "land_value"] - 800_000.0) < 1e-6
    # built land unchanged by the vacant step
    assert abs(out.loc[["B1", "B2", "B3"], "land_value"].sum() - 2_400_000.0) < 1e-6


def test_vacant_site_value_follows_zone_density():
    p = _frame()
    p.loc[p["idpar"].eq("V"), "zone_libelle"] = "UB"     # a zone of its own...
    p = pd.concat([p, pd.DataFrame({
        "idpar": ["L1"], "parcel_area_m2": [500.0], "floor_area_m2": [250.0],   # ...at FAR 0.5
        "building_cost": [300_000.0], "land_value": [100_000.0],
        "improvement_value": [300_000.0], "market_value": [400_000.0],
        "land_share": [0.25], "land_share_raw": [0.25], "lv_flag": ["built_residual"],
        "iris": ["I1"], "zone_typ": ["U"], "zone_libelle": ["UB"],
        "is_exempt_public": [False]})], ignore_index=True)
    out = estimate.vacant_site_value(estimate.site_value_land(p, PRM), PRM).set_index("idpar")
    # V is weighed at its zone's density, as L1 on the same plot is
    assert abs(out.loc["V", "land_value"] - out.loc["L1", "land_value"]) < 1e-6
    assert out.loc["V", "land_value"] < out.loc["B1", "land_value"]


def test_vacant_site_value_without_built_land_changes_nothing():
    p = _frame()
    p["lv_flag"] = "constructible"
    p["floor_area_m2"] = 0.0
    out = estimate.vacant_site_value(p, PRM)
    assert (out["land_value"] == p["land_value"]).all()
    with pytest.raises(ValueError):
        estimate.vacant_site_value(estimate.site_value_land(_frame(), PRM),
                                   {**PRM, "vacant_sliver_fraction": 1.5})


def test_band_moves_vacant_land_with_its_iris_without_adding_to_it():
    df = pd.DataFrame({
        "taxable_land_value": [100.0, 100.0, 50.0, 80.0],
        "taxable_improvement_value": [100.0, 100.0, 0.0, 0.0],
        "_residual_land": [True, True, False, False],
        "_site_vacant": [False, False, True, False],
        "_iris": ["I1", "I1", "I1", "I1"],
    })
    land = export_web._cost_shocked_land(df, 0.2)
    # built: L 200 − 0.2 × B 200 = 160, factor 0.8; vacant site land too; the
    # plot-sale-priced parcel does not move
    assert np.allclose(land, [80.0, 80.0, 40.0, 80.0])
    # without the flag (older sidecars) vacant land stays put
    assert np.allclose(export_web._cost_shocked_land(df.drop(columns="_site_vacant"), 0.2),
                       [80.0, 80.0, 50.0, 80.0])


# ------------------------------------------------- classification in a run

def test_open_space_becomes_natural_land_outside_the_reform(monkeypatch):
    import run_commune
    import run_pipeline
    from config import COMMUNES

    cfg = next(iter(COMMUNES.values()))
    monkeypatch.setattr(run_commune.ingest, "tab_comparables",
                        lambda cfg, tab, deflator=None: pd.DataFrame(
                            columns=["eur_m2_land", "lon", "lat"]))
    parcels = pd.DataFrame({
        "idpar": ["park", "biz", "home", "house"],
        "zone_typ": ["U", "U", "U", "U"],
        "zone_libelle": ["UV", "UX", "UA", "UA"],
        "zone_destdomi": ["00", "02", "01", "01"],
        "zone_libelong": ["Parcs urbains", "", "", ""],
        "cell": ["c"] * 4,
        "parcel_area_m2": [5000.0, 5000.0, 500.0, 500.0],
    })
    buildings = pd.DataFrame({"idpar": ["house"]})
    shares = pd.DataFrame({"idpar": ["park", "biz", "home", "house"],
                           "bdtopo_open_share": [0.9, 0.0, 0.0, 0.0],
                           "bdtopo_activity_share": [0.0, 0.0, 0.0, 0.0]})
    out = run_commune.classify_and_price_land(cfg, parcels, buildings, tab=None,
                                              land_use_shares=shares).set_index("idpar")
    assert out.loc["park", "land_type"] == "natural"
    assert out.loc["park", "vacant_use_source"] == "both"
    assert out.loc["biz", "land_type"] == "constructible"
    assert abs(out.loc["biz", "vacant_price_factor"] - cfg.activity_land_ratio) < 1e-12
    assert out.loc["home", "vacant_price_factor"] == 1.0
    assert out.loc["house", "land_type"] == "built" and pd.isna(out.loc["house", "vacant_use"])
    excluded = run_pipeline.farmland_excluded(out.reset_index())
    assert list(excluded) == [True, False, False, False]
