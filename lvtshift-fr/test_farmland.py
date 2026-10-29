"""Offline tests for leaving unbuilt farmland out of the reform.

Unbuilt agricultural and natural land (PLU zones A and N) keeps today's TFPNB,
so it takes no share of the land tax and is left out of the published shares.

Run: python -m pytest -q test_farmland.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import run_pipeline as rp  # noqa: E402


def test_only_unbuilt_agricultural_and_natural_land_is_excluded():
    p = pd.DataFrame({"land_type": ["agricultural", "natural", "built", "constructible",
                                    "constructible_deferred", "unknown", None]})
    assert list(rp.farmland_excluded(p)) == [True, True, False, False, False, False, False]
    # frames without a land classification (synthetic runs) exclude nothing
    assert not rp.farmland_excluded(pd.DataFrame({"x": [1, 2]})).any()


def _world(n=600, seed=7):
    rng = np.random.default_rng(seed)
    cat = rng.choice(["appartement", "maison", "terrain_nu"], n, p=[0.5, 0.3, 0.2])
    vacant = cat == "terrain_nu"
    land_type = np.where(~vacant, "built",
                         rng.choice(["constructible", "agricultural", "natural"], n))
    area = rng.lognormal(6.5, 0.5, n).round()
    parcels = pd.DataFrame({
        "idpar": [f"99001000A{i:04d}" for i in range(n)],
        "parcel_area_m2": area,
        "cell": rng.choice(["a", "b"], n),
        "type_local": np.where(cat == "maison", "Maison", "Appartement"),
        "category_fr": cat,
        "land_type": land_type,
        "zone_typ": np.select([land_type == "agricultural", land_type == "natural"],
                              ["A", "N"], "U"),
        "constructible_eur_m2": 200.0,
        "ag_eur_m2": 0.6,
        "is_exempt_public": [i < 10 for i in range(n)],
    })
    built = ~vacant
    levels = np.where(cat == "maison", 2, 5)[built].astype(float)
    buildings = pd.DataFrame({
        "idpar": parcels.idpar[built],
        "footprint_m2": (area[built] * 0.4).round(),
        "n_levels": levels, "height_m": levels * 3.0,
        "year_built": 1980.0, "usage": cat[built],
    })
    sales = rng.choice(np.where(built)[0], 300)
    fa = area[sales] * 0.4 * np.where(cat[sales] == "maison", 2, 5)
    dvf = pd.DataFrame({
        "price": fa * 3000 * rng.lognormal(0, 0.15, 300), "floor_area_m2": fa,
        "type_local": np.where(cat[sales] == "maison", "Maison", "Appartement"),
        "year": 2024, "cell": parcels["cell"].values[sales],
    })
    return parcels, buildings, dvf


def test_pipeline_keeps_farmland_out_of_the_levy_and_stays_neutral(tmp_path):
    parcels, buildings, dvf = _world()
    levy = 2_000_000.0
    out = rp.run(parcels, buildings, dvf, levy, out_dir=str(tmp_path), make_report=False)
    farm = parcels["land_type"].isin(["agricultural", "natural"]).values
    assert abs(out["new_tax"].sum() / levy - 1) < 0.01
    assert (out.loc[farm, "new_tax"] == 0).all() and (out.loc[farm, "current_tax"] == 0).all()
    assert (out.loc[farm, "taxable_land_value"] == 0).all()
    # unbuilt building land still pays: that is the point of the reform
    con = (parcels["land_type"] == "constructible").values
    assert (out.loc[con & ~parcels["is_exempt_public"].values, "new_tax"] > 0).all()
    # the flags stay separate: public property is not counted as farmland
    assert list(out["is_farmland_excluded"]) == list(farm)
    assert out["is_fully_exempt"].sum() == 10
    # the CSV on disk carries the flag export_web reads
    disk = pd.read_csv(tmp_path / f"{rp.slug_of(rp.CFG)}.csv")
    assert disk["is_farmland_excluded"].sum() == farm.sum()


def test_export_counts_excluded_farmland_without_listing_it(tmp_path, monkeypatch):
    import config
    import export_web as ew
    monkeypatch.setitem(config.COMMUNES, "zz", config.CommuneConfig("99001", "ZZ", "99", key="zz"))
    pd.DataFrame({"taxable_land_value": [1.0, 0.0, 0.0, 3.0],
                  "is_fully_exempt": [False, True, False, False],
                  "is_farmland_excluded": [False, False, True, False]}
                 ).to_csv(tmp_path / "zz.csv", index=False)
    df = ew.load_parcels("zz", out_dir=str(tmp_path))
    assert len(df) == 2
    assert df.attrs["exempt_parcels"] == 1 and df.attrs["farmland_excluded_parcels"] == 1
    # older exports without the column load unchanged
    pd.DataFrame({"taxable_land_value": [1.0], "is_fully_exempt": [False]}
                 ).to_csv(tmp_path / "zz.csv", index=False)
    assert ew.load_parcels("zz", out_dir=str(tmp_path)).attrs["farmland_excluded_parcels"] == 0


def test_income_fifths_need_two_iris_incomes_per_fifth():
    # Leaving farmland out can let qcut form five bins from a handful of IRIS
    # (Cahors: 9); the breakdown stays unpublished below MIN_IRIS_INCOMES.
    import export_web as ew
    n = 400
    incomes = np.repeat(np.linspace(18_000, 24_000, ew.MIN_IRIS_INCOMES - 1), n // 9 + 1)[:n]
    df = pd.DataFrame({"median_income": incomes, "property_category": "Condominium",
                       "tax_change_pct": 1.0, "tax_change": 1.0, "current_tax": 100.0})
    assert ew.build_by_income_quintile(df) is None
    rows, cov = ew.build_by_income_quintile_within(df.assign(_commune="a"))
    assert rows is None and cov == 0.0
    more = df.assign(median_income=np.repeat(
        np.linspace(18_000, 24_000, ew.MIN_IRIS_INCOMES), n // 10)[:n])
    assert ew.build_by_income_quintile(more) is not None
