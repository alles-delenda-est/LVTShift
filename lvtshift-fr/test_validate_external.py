import json
import pandas as pd
import pytest
import validate_external as ve


def test_land_share_band_check():
    inside = ve.land_share_band_check(50.0, band=(40.0, 65.0))
    assert inside["within_band"] is True
    assert inside["independence"] == "independent"
    outside = ve.land_share_band_check(80.0, band=(40.0, 65.0))
    assert outside["within_band"] is False


def test_building_agreement_rate_on_fixture():
    from shapely.geometry import Polygon
    import geopandas as gpd
    # three unit-square parcels; buildings overlap parcels 0 and 1 only
    parcels = gpd.GeoDataFrame(geometry=[
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(2, 0), (3, 0), (3, 1), (2, 1)]),
        Polygon([(4, 0), (5, 0), (5, 1), (4, 1)]),
    ], crs="EPSG:2154")
    buildings = gpd.GeoDataFrame(geometry=[
        Polygon([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]),
        Polygon([(2.2, 0.2), (2.8, 0.2), (2.8, 0.8), (2.2, 0.8)]),
    ], crs="EPSG:2154")
    r = ve.building_agreement_rate(parcels, buildings)
    assert r["n_parcels"] == 3 and r["n_buildings"] == 2
    assert abs(r["cadastre_built_share_pct"] - 66.7) < 0.2


def test_validate_commune_degrades_gracefully(tmp_path):
    df = pd.DataFrame({
        "property_category": ["Vacant Land", "Single Family Residential"],
        "current_tax": [50.0, 1000.0], "new_tax": [200.0, 850.0],
        "tax_change": [150.0, -150.0], "tax_change_pct": [300.0, -15.0],
        "taxable_land_value": [80000.0, 50000.0],
        "taxable_improvement_value": [0.0, 150000.0],
    })

    class _Cfg:
        insee_code, name, departement = "00000", "X", "00"

    # both network inputs unavailable -> reported "non disponible", no raise
    out = ve.validate_commune("x", df, _Cfg(), cache_dir=str(tmp_path),
                              data_dir=str(tmp_path), insee_vacancy=None, cadastre=None)
    statuses = {c["benchmark"]: c["status"] for c in out["checks"]}
    assert any(s == "non disponible" for s in statuses.values())
    # land-share band is computable offline -> always present
    assert any(c["independence"] == "independent" and c["status"] != "non disponible"
               for c in out["checks"])
    assert (tmp_path / "x.validation.json").exists()
