"""Real-commune driver: open-data ingest -> LVTShift solver -> CSV + charts.

Usage:
    python run_commune.py cahors
    python run_commune.py villeurbanne --layers Commune   # commune share only

This is the real-data analogue of test_synthetic.py: it fetches the open sources
(cadastre, DVF, BD TOPO buildings, GPU zoning, REI, IRIS contours, Filosofi),
shapes them into the contract estimate.py/run_pipeline.run expect, then calls
the *real* LVTShift solver. Output: the standard CSV plus euro charts — category
impact, the +/-10 % share, the tax-change distribution, and the income-quintile
(distributional) charts.

Honest caveats baked in here (see README 'Limites connues'):
  * `cell` is a 400 m grid square, a transparent spatial fixed effect for the
    hedonic — NOT an administrative geography (income uses the real IRIS code).
  * Non-residential parcels borrow the residential EUR/m2 surface (flagged);
    professionnels need a separate strata before publication.
  * The current-tax baseline (floor-area VLC proxy) is the load-bearing weak
    link for the *starting* bill — read the change by category/quintile.
"""

import argparse

import geopandas as gpd
import numpy as np
import pandas as pd

import ingest
import run_pipeline as rp
from config import (COMMUNES, AG_EUR_M2_BY_DEP, EPTB_EUR_M2_FALLBACK, LAND_MODEL)
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


def classify_and_price_land(cfg, parcels, buildings, tab):
    """Add land_type + per-parcel land prices (classify-then-price).

    - land_type from GPU zoning (U/AU->constructible, A->agricultural,
      N->natural) for building-less parcels; parcels with a building are 'built'.
    - constructible_eur_m2: DVF terrain-à-bâtir median by grid cell (shrunk to
      the commune median; EPTB national fallback when comparables are thin),
      discounted for AU 'fermée/stricte' zones.
    - ag_eur_m2: SAFER départemental agricultural/natural €/m².
    """
    import geopandas as gpd
    parcels = parcels.copy()

    # --- zoning -> land_type ---
    zoning = ingest.fetch_parcel_zoning(cfg, parcels)
    parcels = parcels.merge(zoning, on="idpar", how="left")
    z = parcels["zone_typ"].astype("object")
    has_bld = parcels["idpar"].isin(buildings["idpar"])
    constructible = z.isin(["U", "AUc", "AU", "AUs"])
    deferred = z.isin(["AU", "AUs"])           # AU fermée/stricte
    parcels["land_type"] = np.select(
        [has_bld, constructible & deferred, constructible, z.eq("A"), z.eq("N")],
        ["built", "constructible_deferred", "constructible", "agricultural", "natural"],
        default="unknown")  # no GPU coverage -> priced as agricultural (conservative)

    # --- agricultural €/m² (SAFER, by département, A vs N) ---
    a_rate, n_rate = AG_EUR_M2_BY_DEP.get(
        cfg.departement, AG_EUR_M2_BY_DEP["_default"])
    parcels["ag_eur_m2"] = np.where(z.eq("N"), n_rate, a_rate)

    # --- constructible €/m² from terrain-à-bâtir comparables ---
    comps = ingest.tab_comparables(cfg, tab)
    commune_med = float(comps["eur_m2_land"].median()) if len(comps) else None
    enough_cells = {}
    comps = comps.dropna(subset=["lon", "lat"]) if len(comps) else comps
    if len(comps):
        cpts = gpd.GeoSeries(
            gpd.points_from_xy(comps["lon"], comps["lat"]), crs=CRS_WGS84
        ).to_crs(CRS_METRIC)
        comps = comps.assign(cell=_grid_cell(cpts.x.values, cpts.y.values))
        cm = comps.groupby("cell")["eur_m2_land"].agg(["median", "count"])
        enough_cells = cm[cm["count"] >= LAND_MODEL["min_tab_sales_cell"]]["median"].to_dict()
    # commune base price: median if enough sales, else EPTB national fallback
    if commune_med is not None and len(comps) >= LAND_MODEL["min_tab_sales_commune"]:
        base = commune_med
    else:
        base = EPTB_EUR_M2_FALLBACK
    parcels["constructible_eur_m2"] = parcels["cell"].map(
        lambda c: enough_cells.get(c, base))
    # AU fermée/stricte discount (Gemini review: deferred development potential)
    parcels.loc[deferred.values, "constructible_eur_m2"] *= LAND_MODEL["au_strict_factor"]

    return parcels


def prepare(cfg, layers):
    """Fetch + shape all inputs for one commune."""
    parcels = ingest.fetch_parcels(cfg)
    sales, tab = ingest.fetch_dvf(cfg)
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

    # Classify-then-price land (GPU zoning + TAB comparables + SAFER)
    parcels = classify_and_price_land(cfg, parcels, buildings, tab)

    # IRIS code per parcel + Filosofi income (drives the distributional charts)
    parcels = parcels.merge(ingest.fetch_parcel_iris(cfg, parcels),
                            on="idpar", how="left")
    iris_income = ingest.fetch_filosofi_iris(cfg)

    # DVF: lat/lon -> same grid cell
    sales = sales.dropna(subset=["lat", "lon"]).copy()
    pts = gpd.GeoSeries(
        gpd.points_from_xy(sales["lon"], sales["lat"]), crs=CRS_WGS84
    ).to_crs(CRS_METRIC)
    sales["cell"] = _grid_cell(pts.x.values, pts.y.values)

    print(f"  [{cfg.name}] {len(parcels)} parcels, {len(sales)} usable DVF "
          f"sales, {parcels['cell'].nunique()} grid cells")
    print("  land_type:", parcels["land_type"].value_counts().to_dict())
    return parcels, buildings, sales, tfpb, iris_income


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
    parcels, buildings, sales, tfpb, iris_income = prepare(cfg, tuple(args.layers))

    out = rp.run(parcels, buildings, sales, tfpb, iris_income=iris_income,
                 out_dir=args.out_dir, make_report=not args.no_report, cfg=cfg)

    print("\n--- sanity checks -------------------------------------")
    print(f"rows exported: {len(out)}")
    rev_ok = abs(out["new_tax"].sum() / tfpb - 1) < 0.01
    print(f"revenue neutrality within 1%: {rev_ok}")
    chg = out.groupby("property_category")["tax_change_pct"].median().round(1)
    print("median tax change % by category:\n", chg.to_string())

    # land-class composition of the levy (validates the classify-then-price fix:
    # agricultural/natural land should bear a tiny share)
    o = out.reset_index(drop=True)
    o["land_type"] = parcels.reset_index(drop=True)["land_type"].values
    lc = o.groupby("land_type").agg(
        parcels=("new_tax", "size"),
        levy_eur=("new_tax", "sum"),
    )
    lc["levy_pct"] = (100 * lc["levy_eur"] / o["new_tax"].sum()).round(1)
    lc["levy_eur"] = lc["levy_eur"].round(0)
    print("levy borne by land class:\n", lc.sort_values("levy_eur").to_string())


if __name__ == "__main__":
    main()
