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
    floats = lu.zone_use(pd.Series(["U", "U"]), pd.Series([1.0, 2.0]), None)
    assert list(floats) == [lu.HOUSING, lu.ACTIVITY]


def test_zone_use_falls_back_to_the_long_label_and_never_to_the_short_one():
    typ = pd.Series(["U"] * 6)
    code = pd.Series(["00", "99", None, "", "00", "00"])
    label = pd.Series(["Parcs urbains", "Zone économique tertiaire et technologique",
                       "Parc d'activités de la Pallice", "Zone de grands services urbains",
                       "Centre ancien", None])
    out = lu.zone_use(typ, code, label)
    assert list(out[:4]) == [lu.OPEN_SPACE, lu.ACTIVITY, lu.ACTIVITY, lu.ACTIVITY]
    assert out[4] == lu.HOUSING and pd.isna(out[5])   # housing word; silent plan


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
    assert lu.bdtopo_feature_use("BDTOPO_V3:equipement_de_transport", {"nature": "Parking"}) is None
    assert lu.bdtopo_feature_use("BDTOPO_V3:equipement_de_transport", {"nature": "Gare"}) == lu.ACTIVITY
    assert lu.bdtopo_feature_use("BDTOPO_V3:equipement_de_transport", {"nature": "Carrefour"}) is None
    # live values (Grenoble WFS, 2026-11-24)
    assert lu.bdtopo_feature_use(zai, {"nature": "Lycée", "categorie": "Science et enseignement"}) == lu.ACTIVITY
    assert lu.bdtopo_feature_use(zai, {"nature": "Culte chrétien", "categorie": "Religieux"}) is None


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


def test_vacant_use_plan_decides_and_bdtopo_fills_silence():
    plan = pd.Series([lu.OPEN_SPACE, None, lu.ACTIVITY, None, lu.HOUSING, lu.HOUSING, None])
    open_sh = pd.Series([0.0, 0.8, 0.0, 0.0, 0.2, 0.9, 0.1])
    act_sh = pd.Series([0.0, 0.0, 0.7, 0.6, 0.0, 0.0, 0.1])
    out = lu.vacant_use(plan, open_sh, act_sh, 0.5)
    # a housing zone stays housing land whatever BD TOPO shows (current use)
    assert list(out["vacant_use"]) == [lu.OPEN_SPACE, lu.OPEN_SPACE, lu.ACTIVITY,
                                       lu.ACTIVITY, lu.HOUSING, lu.HOUSING, lu.HOUSING]
    assert list(out["vacant_use_source"]) == ["plan", "bdtopo", "both", "bdtopo",
                                              "both", "plan", "default"]
    with pytest.raises(ValueError):
        lu.vacant_use(plan, open_sh, act_sh, 0.0)


def test_cross_check_tabulates_agreement():
    t = lu.cross_check(pd.Series([lu.OPEN_SPACE, lu.OPEN_SPACE, None]),
                       pd.Series([0.9, 0.0, 0.0]), pd.Series([0.0, 0.0, 0.0]),
                       pd.Series([2.0, 3.0, 5.0]))
    assert t.loc[lu.OPEN_SPACE, lu.OPEN_SPACE] == 2.0
    assert t.loc[lu.OPEN_SPACE, "nothing"] == 3.0
    assert t.loc["unstated", "nothing"] == 5.0
    assert t.index.name == "plan"


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

def test_open_space_becomes_natural_land_inside_the_reform(monkeypatch):
    import run_commune
    import run_pipeline
    from config import AG_EUR_M2_BY_DEP, COMMUNES

    cfg = next(iter(COMMUNES.values()))
    _a_rate, n_rate = AG_EUR_M2_BY_DEP.get(cfg.departement, AG_EUR_M2_BY_DEP["_default"])
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
    assert out.loc["park", "land_type"] == "open_space"
    assert out.loc["park", "vacant_use_source"] == "both"
    assert out.loc["park", "ag_eur_m2"] == n_rate
    assert out.loc["biz", "land_type"] == "constructible"
    assert abs(out.loc["biz", "vacant_price_factor"] - cfg.activity_land_ratio) < 1e-12
    assert out.loc["home", "vacant_price_factor"] == 1.0
    assert out.loc["house", "land_type"] == "built" and pd.isna(out.loc["house", "vacant_use"])
    # open space stays inside the reform: it carries its share of the
    # replaced tax on unbuilt land
    excluded = run_pipeline.farmland_excluded(out.reset_index())
    assert list(excluded) == [False, False, False, False]


def test_zone_label_earliest_keyword_wins_and_au_is_never_open_space():
    typ = pd.Series(["U", "U", "U", "AU", "U", "U", "AU"])
    label = pd.Series([
        "Habitat collectif en R+5 avec bureaux autorisés sans limitation de surface",
        "parc d'activités « Bas Carbone » Atlantech: mixité fonctionnelle comprenant du logement",
        "Tissus urbains hétérogènes du coeur métropolitain avec bureaux autorisés",
        "espaces naturels ou agricoles destinés à recevoir une urbanisation à long terme",
        "Zone urbaine verte",
        "Zone d'équipements",
        "Zone à urbaniser ; opération réalisée au fur et à mesure de la réalisation des équipements",
    ])
    out = lu.zone_use(typ, None, label)
    assert list(out[:3]) == [lu.HOUSING, lu.ACTIVITY, lu.HOUSING]
    assert pd.isna(out[3])                       # AU: priced by the AU discount
    assert out[4] == lu.OPEN_SPACE and out[5] == lu.ACTIVITY
    assert pd.isna(out[6])


def test_zone_label_statement_of_purpose_overrides_word_order():
    typ = pd.Series(["U", "AU", "U", "U", "U"])
    label = pd.Series([
        "secteur urbain situé en frange de tissus résidentiels et dédié aux activités économiques",
        "espaces naturels ou agricoles destinés à recevoir une urbanisation à long terme : principalement de l'habitat.",
        "espaces dévolus aux jardins familiaux ou partagés situés en zone urbaine",
        "espaces spécifiques des ports de plaisance",
        "Défense nationale et administration pénitentiaire",
    ])
    out = lu.zone_use(typ, None, label)
    assert list(out) == [lu.ACTIVITY, lu.HOUSING, lu.OPEN_SPACE, lu.ACTIVITY, lu.ACTIVITY]


def test_compound_terms_do_not_misclassify():
    typ = pd.Series(["U"] * 8)
    label = pd.Series([
        "Zone de cités-jardins",
        "Zone urbaine paysagère",
        "Zone urbaine de transition avec les espaces naturels, habitat pavillonnaire",
        "Tissu d'activités économiques",
        "Village d'entreprises",
        "secteur en frange de tissus résidentiels, réservée aux activités",
        "Pavillonnaire en évolution modérée avec secteurs réservés aux gens du voyage",
        "espaces dévolus aux jardins familiaux",
    ])
    out = lu.zone_use(typ, None, label)
    assert list(out[:3]) == [lu.HOUSING, None, lu.HOUSING] or (
        out[0] == lu.HOUSING and pd.isna(out[1]) and out[2] == lu.HOUSING)
    assert list(out[3:]) == [lu.ACTIVITY, lu.ACTIVITY, lu.ACTIVITY, lu.HOUSING, lu.OPEN_SPACE]


def test_curly_apostrophes_port_word_and_emplacements_reserves():
    typ = pd.Series(["U"] * 6)
    label = pd.Series([
        "Tissu d\u2019activités économiques",
        "Village d\u2019entreprises",
        "Zone d\u2019équipements",
        "Zone du port",
        "Quartiers comportant des immeubles de logement",
        "Zone d'habitat collectif, emplacements réservés pour équipements publics",
    ])
    out = lu.zone_use(typ, None, label)
    assert list(out) == [
        lu.ACTIVITY, lu.ACTIVITY, lu.ACTIVITY, lu.ACTIVITY, lu.HOUSING, lu.HOUSING
    ]


def test_vacant_land_takes_its_own_iris_rate_not_the_communes():
    p = _frame()
    # a second IRIS with dearer built land, holding V
    extra = p[p["idpar"].isin(["B1", "B2", "B3"])].copy()
    extra["idpar"] = ["C1", "C2", "C3"]
    extra["iris"] = "I3"
    extra["land_value"] = extra["land_value"] * 2
    p = pd.concat([p, extra], ignore_index=True)
    p.loc[p["idpar"].eq("V"), "iris"] = "I3"
    out = estimate.vacant_site_value(estimate.site_value_land(p, PRM), PRM).set_index("idpar")
    assert abs(out.loc["V", "land_value"] - 1_600_000.0) < 1e-6      # I3's rate
    assert abs(out.loc["W", "land_value"] - 1_200_000.0) < 1e-6      # commune's rate


def test_large_plot_rule_garden_band_then_subdivision_site():
    """PR #85: in a house-scale zone extra area counts at the garden weight up
    to subdivision_threshold_m2, then at development_net_share; in a dense zone
    the whole plot counts."""
    for far in (0.5, 2.0):                                         # house scale, dense
        p = _frame()
        p["floor_area_m2"] = p["floor_area_m2"].where(p["floor_area_m2"] == 0, 500.0 * far)
        prm = {"min_zone_parcels": 2, "plot_cap_quantile": 1.0,
               "development_net_share": 0.75, "subdivision_threshold_m2": 5000.0}
        for size, house in ((1000.0, 1000.0), (3000.0, 1500.0), (5000.0, 2000.0),
                            (20_000.0, 2000.0 + 0.75 * 15_000)):
            p.loc[p["idpar"].eq("V"), "parcel_area_m2"] = size
            out = estimate.vacant_site_value(estimate.site_value_land(p, prm), prm).set_index("idpar")
            b = out.loc["B2"]
            rate = b["land_value"] / (500.0 if far < 1.0 else b["parcel_area_m2"])
            want = house if far < 1.0 else size
            assert abs(out.loc["V", "land_value"] - rate * want) < 1e-6, (far, size)


def test_building_on_a_plot_never_changes_its_land_value():
    """Built and vacant plots of one IRIS, zone and size get the same land (the
    review of PR #85 found a vacant 3 000 m² plot worth 1.67 × a built one)."""
    for size in (3000.0, 8000.0, 20_000.0):
        rows = _fabric("H", "I1", "UC", HAB, [0.5] * 5)
        big = _fabric("BIG", "I1", "UC", HAB, [0.0001], area=size)
        rows += big + [_vacant("V", "I1", "U", "UC", HAB, size)]
        prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0}
        out = estimate.vacant_site_value(estimate.site_value_land(_finish(rows), prm), prm).set_index("idpar")
        assert out.loc["BIG0", "lv_flag"] == "built_site_value"
        assert abs(out.loc["V", "land_value"] / out.loc["BIG0", "land_value"] - 1.0) < 1e-9, size


def test_house_scale_area_is_continuous_and_legacy_rule_is_the_garden_weight():
    plot = pd.Series([999.0, 1000.0, 1001.0, 4999.0, 5000.0, 5001.0, 50_000.0])
    typ = pd.Series(500.0, index=plot.index)
    eff = estimate._house_scale_area(plot, typ, 2.0, 0.25, 0.75, 5000.0)
    assert (eff.diff().dropna() > 0).all()                         # rises with size
    assert abs(eff[2] - eff[1] - 0.25) < 1e-9 and abs(eff[5] - eff[4] - 0.75) < 1e-9
    old = estimate._house_scale_area(plot, typ, 2.0, 0.25, 0.75, None)
    assert abs(old.iloc[-1] - (1000 + 0.25 * 49_000)) < 1e-9
    with pytest.raises(ValueError):
        estimate._large_plot_params({"development_net_share": 0.75, "subdivision_threshold_m2": 0})

def test_au_and_business_factors_multiply(monkeypatch):
    import run_commune
    from config import COMMUNES, LAND_MODEL
    cfg = next(iter(COMMUNES.values()))
    monkeypatch.setattr(run_commune.ingest, "tab_comparables",
                        lambda cfg, tab, deflator=None: pd.DataFrame(
                            columns=["eur_m2_land", "lon", "lat"]))
    parcels = pd.DataFrame({
        "idpar": ["au_biz", "au_home"], "zone_typ": ["AU", "AU"],
        "zone_libelle": ["2AUX", "2AU"], "zone_destdomi": ["02", "01"],
        "zone_libelong": ["", ""], "cell": ["c", "c"], "parcel_area_m2": [1000.0, 1000.0]})
    out = run_commune.classify_and_price_land(cfg, parcels, pd.DataFrame({"idpar": []}),
                                              tab=None).set_index("idpar")
    f = LAND_MODEL["au_strict_factor"]
    assert abs(out.loc["au_biz", "vacant_price_factor"] - f * cfg.activity_land_ratio) < 1e-12
    assert abs(out.loc["au_home", "vacant_price_factor"] - f) < 1e-12


def test_band_commune_factor_sums_clipped_iris_totals_and_tolerates_nan_flags():
    df = pd.DataFrame({
        "taxable_land_value": [100.0, 100.0, 40.0, 60.0],
        "taxable_improvement_value": [100.0, 300.0, 0.0, 0.0],
        "_residual_land": [True, True, False, False],
        "_site_vacant": [False, False, True, np.nan],   # NaN: older territory member
        "_iris": ["I1", "I2", "I3", "I3"],
    })
    land = export_web._cost_shocked_land(df, 0.5)
    # I1 → 50, I2 → clipped at 0: commune factor (50 + 0) / 200 = 0.25
    assert np.allclose(land, [50.0, 0.0, 10.0, 60.0])


def test_wfs_json_evicts_and_retries_a_non_json_reply(monkeypatch, tmp_path):
    import ingest
    replies = iter([b"# HELP jmx_exporter_build_info metrics", b'{"features": []}'])
    evicted = []
    monkeypatch.setattr(ingest, "_get", lambda url: next(replies))
    monkeypatch.setattr(ingest, "_evict_cache", lambda url: evicted.append(url))
    monkeypatch.setattr(ingest.time, "sleep", lambda s: None)
    assert ingest._wfs_json("https://example.org/wfs") == {"features": []}
    assert evicted == ["https://example.org/wfs"]
    assert not ingest._cacheable(b"# HELP jmx_exporter_build_info A metric")


def test_transport_zone_is_business_land_without_matching_inside_words():
    out = lu.zone_use(pd.Series(["U", "U"]),
                      None, pd.Series(["Ut : Zone à usage de transport collectif",
                                       "Habitat collectif desservi par les transports en commun"]))
    assert list(out) == [lu.ACTIVITY, lu.HOUSING]


# ------------------------------------------------- AU (to-be-urbanised) land

def _au_frame():
    """One IRIS: three built parcels in a housing zone UA (FAR 2), three in a
    business zone UX (FAR 0.5), and building-less parcels in AU zones."""
    rows = []
    for i in range(3):
        rows.append(dict(idpar=f"H{i}", zone_typ="U", zone_libelle="UA",
                         zone_libelong="Habitat collectif", floor_area_m2=1000.0,
                         parcel_area_m2=500.0, land_value=800_000.0))
        rows.append(dict(idpar=f"X{i}", zone_typ="U", zone_libelle="UX",
                         zone_libelong="Zone d'activités économiques", floor_area_m2=250.0,
                         parcel_area_m2=500.0, land_value=400_000.0))
    for k, (typ, lab, long_, area) in {
        "AUh": ("AUc", "1AUH", "Zone à urbaniser à vocation d'habitat", 20_000.0),
        "AUx": ("AUc", "1AUX", "Zone à urbaniser à vocation d'activités", 20_000.0),
        "AUs": ("AU", "2AU", "", 400.0),
    }.items():
        rows.append(dict(idpar=k, zone_typ=typ, zone_libelle=lab, zone_libelong=long_,
                         floor_area_m2=0.0, parcel_area_m2=area, land_value=9e9))
    p = pd.DataFrame(rows)
    built = p["floor_area_m2"] > 0
    p["iris"] = "I1"
    p["building_cost"] = np.where(built, 1_000_000.0, 0.0)
    p["improvement_value"] = p["building_cost"]
    p["market_value"] = p["land_value"] + p["building_cost"]
    p["land_share"] = p["land_value"] / p["market_value"]
    p["land_share_raw"] = p["land_share"]
    p["lv_flag"] = np.where(built, "built_residual", "constructible")
    p["is_exempt_public"] = False
    return p


def test_au_land_takes_the_density_of_same_use_urban_zones_net_of_roads():
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0, "development_net_share": 0.75}
    out = estimate.vacant_site_value(estimate.site_value_land(_au_frame(), prm), prm).set_index("idpar")
    assert out.loc["AUh", "site_density"] == 2.0       # the housing zone's, not the commune's
    assert out.loc["AUx", "site_density"] == 0.5       # the business zone's
    # same IRIS rate as the built plots: land per m² of net area × density^0.5
    rate = out.loc["H0", "land_value"] / (500.0 * 2.0 ** 0.5)
    assert abs(out.loc["AUh", "land_value"] - rate * 20_000 * 0.75 * 2.0 ** 0.5) < 1e-3
    assert bool(out.loc["AUs", "vacant_au"]) and not bool(out.loc["H0", "vacant_au"])
    assert abs(out.loc["AUs", "land_value"] - rate * 400 * 0.75 * 2.0 ** 0.5) < 1e-3


def test_au_land_takes_the_density_of_its_own_iris_before_the_commune():
    p = _au_frame()
    edge = p[p["idpar"].str.startswith("H")].copy()
    edge["idpar"] = ["E0", "E1", "E2"]
    edge["iris"], edge["zone_libelle"] = "I2", "UC"
    edge["floor_area_m2"] = 200.0                       # low-density fabric, FAR 0.4
    au = p[p["idpar"].eq("AUh")].copy()
    au["idpar"], au["iris"] = "AUedge", "I2"
    p = pd.concat([p, edge, au], ignore_index=True)
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0}
    out = estimate.vacant_site_value(estimate.site_value_land(p, prm), prm).set_index("idpar")
    assert abs(out.loc["AUedge", "site_density"] - 0.4) < 1e-9   # its IRIS's, not the town's
    assert out.loc["AUh", "site_density"] == 2.0


def test_au_label_with_enough_built_parcels_keeps_its_own_density():
    p = _au_frame()
    extra = p[p["idpar"].str.startswith("H")].copy()
    extra["idpar"] = ["A0", "A1", "A2"]
    extra["zone_typ"], extra["zone_libelle"] = "AUc", "1AUH"
    extra["floor_area_m2"] = 500.0                      # FAR 1 inside the AU zone
    p = pd.concat([p, extra], ignore_index=True)
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0}
    out = estimate.vacant_site_value(estimate.site_value_land(p, prm), prm).set_index("idpar")
    assert out.loc["AUh", "site_density"] == 1.0
    with pytest.raises(ValueError):
        estimate.vacant_site_value(estimate.site_value_land(p, prm), {**prm, "development_net_share": 0.0})


def _fabric(prefix, iris, label, long_, fars, area=500.0):
    return [dict(idpar=f"{prefix}{i}", iris=iris, zone_typ="U", zone_libelle=label,
                 zone_libelong=long_, floor_area_m2=far * area, parcel_area_m2=area,
                 land_value=600_000.0) for i, far in enumerate(fars)]


def _finish(rows):
    p = pd.DataFrame(rows)
    built = p["floor_area_m2"] > 0
    p["building_cost"] = np.where(built, 1_000_000.0, 0.0)
    p["improvement_value"] = p["building_cost"]
    p["market_value"] = p["land_value"] + p["building_cost"]
    p["land_share"] = p["land_value"] / p["market_value"]
    p["land_share_raw"] = p["land_share"]
    p["lv_flag"] = np.where(built, "built_residual", "constructible")
    p["is_exempt_public"] = False
    return p


def _vacant(idpar, iris, typ, label, long_, area):
    return dict(idpar=idpar, iris=iris, zone_typ=typ, zone_libelle=label, zone_libelong=long_,
                floor_area_m2=0.0, parcel_area_m2=area, land_value=9e9)


HAB, ACT = "Habitat", "Zone d'activités économiques"


def test_au_density_steps_use_reference_densities_on_one_scale():
    """Step 2 (the IRIS's U fabric) takes the median of the parcels' own label
    references, so it lands on the same level as step 3 (the commune's labels)
    instead of the lower realised median."""
    rows = (_fabric("A", "I1", "UA", HAB, [0.5, 1.0, 4.0])      # ref p75 = 2.5
            + _fabric("B", "I2", "UB", HAB, [0.2, 0.2, 0.4])    # ref p75 = 0.3
            + _fabric("X", "I3", "UX", ACT, [0.3, 0.3, 0.3]))
    rows += [_vacant("AU1", "I1", "AUc", "1AU", "Zone à urbaniser à vocation d'habitat", 5000.0),
             _vacant("AU3", "I3", "AUc", "1AU", "Zone à urbaniser à vocation d'habitat", 5000.0)]
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0}
    p = _finish(rows)
    out = estimate.vacant_site_value(estimate.site_value_land(p, prm), prm).set_index("idpar")
    assert abs(out.loc["AU1", "site_density"] - 2.5) < 1e-9     # step 2: UA's reference, not 1.0
    # I3 has no housing fabric: step 3, median of the commune's housing labels (2.5, 0.3)
    assert abs(out.loc["AU3", "site_density"] - 1.4) < 1e-9


def test_au_land_is_valued_as_u_land_of_the_same_density_net_of_roads():
    """Same IRIS, use, density and size: AU = U × development_net_share, garden and strip rules
    included (fresh-context review of PR #84: a 2 ha AU site must not come out
    dearer than a 2 ha U site)."""
    rows = _fabric("H", "I1", "UC", HAB, [0.5] * 4)
    rows += [_vacant("U2ha", "I1", "U", "UC", HAB, 20_000.0),
             _vacant("AU2ha", "I1", "AUc", "1AU", "Zone à urbaniser à vocation d'habitat", 20_000.0)]
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0, "development_net_share": 0.75}
    out = estimate.vacant_site_value(estimate.site_value_land(_finish(rows), prm), prm).set_index("idpar")
    assert out.loc["AU2ha", "site_density"] == out.loc["U2ha", "site_density"] == 0.5
    # AU = 0.75 × the U value of the same density and size
    assert abs(out.loc["AU2ha", "land_value"] - 0.75 * out.loc["U2ha", "land_value"]) < 1e-6
    # an AU strip is a strip: same sliver rule as in U
    rows += [_vacant("AUstrip", "I1", "AUc", "1AU", "Zone à urbaniser à vocation d'habitat", 50.0),
             _vacant("Ustrip", "I1", "U", "UC", HAB, 50.0)]
    out = estimate.vacant_site_value(estimate.site_value_land(_finish(rows), prm), prm).set_index("idpar")
    assert bool(out.loc["AUstrip", "vacant_sliver"])
    assert abs(out.loc["AUstrip", "land_value"] - 0.75 * out.loc["Ustrip", "land_value"]) < 1e-6


def test_au_density_ignores_parcels_without_iris_and_needs_no_optional_columns():
    rows = _fabric("H", "I1", "UA", HAB, [2.0] * 3) + _fabric("N", None, "UB", HAB, [0.2] * 3)
    rows.append(_vacant("AUn", None, "AUc", "1AU", "Zone à urbaniser à vocation d'habitat", 5000.0))
    prm = {"min_zone_parcels": 3, "plot_cap_quantile": 1.0}
    p = _finish(rows)
    out = estimate.vacant_site_value(estimate.site_value_land(p, prm), prm).set_index("idpar")
    # no IRIS: never pooled with other IRIS-less parcels; commune labels' median (2.0, 0.2)
    assert abs(out.loc["AUn", "site_density"] - 1.1) < 1e-9
    bare = p.drop(columns=["zone_libelong"])
    estimate.vacant_site_value(estimate.site_value_land(bare, prm), prm)   # runs
    with pytest.raises(ValueError):
        estimate.vacant_site_value(estimate.site_value_land(p, prm), {**prm, "development_net_share": 1.5})
