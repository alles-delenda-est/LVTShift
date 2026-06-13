"""Real-commune driver: open-data ingest -> LVTShift solver -> CSV + charts.

Usage:
    python run_commune.py cahors
    python run_commune.py lyon3 --layers Commune        # commune share only

This is the real-data analogue of test_synthetic.py: it fetches the four open
sources (cadastre, DVF, BD TOPO buildings, REI), shapes them into the contract
estimate.py/run_pipeline.run expect, then calls the *real* LVTShift solver.

Income (Filosofi) is deliberately deferred (ingest.fetch_filosofi_iris), so
the distributional quintile charts are skipped; category impact, the +/-10 %
share, the tax-change distribution, and revenue-neutrality all run.

Honest caveats baked in here (see README 'Limites connues'):
  * `cell` is a 400 m grid square, a transparent spatial fixed effect for the
    hedonic — NOT an administrative geography. Swap to IRIS when income lands.
  * Non-residential parcels borrow the residential EUR/m2 surface (flagged);
    professionnels need a separate strata before publication.
  * Rural communes carry large vacant/agricultural parcels: vacant land is
    valued off the commune's median built land density, which can be coarse on
    big fields. Inspect the Vacant Land category before quoting it.
"""

import argparse

import geopandas as gpd
import numpy as np
import pandas as pd

import ingest
import run_pipeline as rp
from config import COMMUNES
from ingest import CRS_METRIC, CRS_WGS84

GRID_M = 400  # spatial fixed-effect cell size (metres) for the hedonic

# BD TOPO usage_1 -> French property category (non-residential cases).
# Résidentiel / Indifférencié are split by dwelling count in _residential_cat.
USAGE_MAP = {
    "Commercial et services": "commerce",
    "Industriel": "industriel",
    "Agricole": "dependance",
    "Annexe": "dependance",
    "Religieux": "dependance",
    "Sportif": "dependance",
}


def _residential_cat(n_dwellings, n_levels) -> str:
    """maison / appartement / immeuble_collectif from dwelling count, with a
    storey-count fallback when BD TOPO has no nombre_de_logements."""
    if pd.notna(n_dwellings):
        if n_dwellings <= 1:
            return "maison"
        if n_dwellings <= 4:
            return "appartement"
        return "immeuble_collectif"
    return "appartement" if (pd.notna(n_levels) and n_levels >= 3) else "maison"


def derive_parcel_category(buildings: pd.DataFrame) -> pd.Series:
    """One category_fr per parcel, from its dominant (largest-floor) building."""
    b = buildings.copy()
    b["floor"] = b["footprint_m2"] * b["n_levels"].fillna(1).clip(lower=1)
    dom = b.sort_values("floor").groupby("idpar").tail(1).set_index("idpar")
    dwellings = b.groupby("idpar")["n_dwellings"].sum()

    cats = {}
    for idpar, row in dom.iterrows():
        u = row["usage"]
        if pd.isna(u) or u in ("Résidentiel", "Indifférencié"):
            cats[idpar] = _residential_cat(dwellings.get(idpar), row["n_levels"])
        else:
            cats[idpar] = USAGE_MAP.get(u, "dependance")
    return pd.Series(cats, name="category_fr")


def _grid_cell(xs, ys) -> list:
    return [f"{int(x // GRID_M)}_{int(y // GRID_M)}" for x, y in zip(xs, ys)]


def prepare(cfg, layers):
    """Fetch + shape all inputs for one commune."""
    parcels = ingest.fetch_parcels(cfg)
    sales, _tab = ingest.fetch_dvf(cfg)
    buildings = ingest.fetch_buildings(cfg, parcels)
    tfpb = ingest.fetch_rei_tfpb_produit(cfg, layers=layers)

    # Parcels: official area (fallback to geometry), centroid -> grid cell
    pg = ingest.parcels_to_gdf(parcels)
    cent = pg.geometry.centroid
    parcels = parcels.copy()
    parcels["parcel_area_m2"] = pd.to_numeric(
        parcels["parcel_area_m2"], errors="coerce").astype(float)
    geo_area = pd.Series(pg.geometry.area.values, index=parcels.index)
    bad = parcels["parcel_area_m2"].isna() | (parcels["parcel_area_m2"] <= 0)
    parcels.loc[bad, "parcel_area_m2"] = geo_area[bad]
    parcels["cell"] = _grid_cell(cent.x.values, cent.y.values)

    # Category + type_local from buildings; building-less parcels are vacant
    cat = derive_parcel_category(buildings)
    parcels = parcels.merge(cat, left_on="idpar", right_index=True, how="left")
    parcels["category_fr"] = parcels["category_fr"].fillna("terrain_nu")
    parcels["type_local"] = np.where(
        parcels["category_fr"] == "maison", "Maison", "Appartement")

    # DVF: lat/lon -> same grid cell
    sales = sales.dropna(subset=["lat", "lon"]).copy()
    pts = gpd.GeoSeries(
        gpd.points_from_xy(sales["lon"], sales["lat"]), crs=CRS_WGS84
    ).to_crs(CRS_METRIC)
    sales["cell"] = _grid_cell(pts.x.values, pts.y.values)

    n_vac = (parcels["category_fr"] == "terrain_nu").sum()
    print(f"  [{cfg.name}] {len(parcels)} parcels "
          f"({n_vac} vacant / no building), {len(sales)} usable DVF sales, "
          f"{parcels['cell'].nunique()} grid cells")
    return parcels, buildings, sales, tfpb


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("commune", choices=sorted(COMMUNES),
                    help="commune key (see config.COMMUNES)")
    ap.add_argument("--layers", nargs="+", default=["Commune", "GFP"],
                    help="REI beneficiary layers held revenue-neutral "
                         "(default: Commune GFP)")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--no-report", action="store_true",
                    help="CSV only, skip the PNG charts")
    args = ap.parse_args()

    cfg = COMMUNES[args.commune]
    print(f"=== {cfg.name} ({cfg.insee_code}, dep {cfg.departement}) ===")
    parcels, buildings, sales, tfpb = prepare(cfg, tuple(args.layers))

    out = rp.run(parcels, buildings, sales, tfpb, iris_income=None,
                 out_dir=args.out_dir, make_report=not args.no_report, cfg=cfg)

    print("\n--- sanity checks -------------------------------------")
    print(f"rows exported: {len(out)}")
    rev_ok = abs(out["new_tax"].sum() / tfpb - 1) < 0.01
    print(f"revenue neutrality within 1%: {rev_ok}")
    chg = out.groupby("property_category")["tax_change_pct"].median().round(1)
    print("median tax change % by category:\n", chg.to_string())
    share = (out["property_category"].value_counts(normalize=True) * 100).round(1)
    print("parcel mix by category (%):\n", share.to_string())


if __name__ == "__main__":
    main()
