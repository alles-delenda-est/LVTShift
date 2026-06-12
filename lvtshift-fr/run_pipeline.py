"""
Orchestrator: French parcel data -> LVTShift solver -> standard export.

Usage (after ingest produced the input frames):
    python run_pipeline.py

This module lives inside a fork of LVTShift, in the lvtshift-fr/ subdirectory.
The upstream `lvt` package therefore sits one level up, at the repository root.
We call their *actual* solver and export functions and never modify upstream
files, so improvements pulled from upstream flow through automatically.
"""

import sys
from pathlib import Path

import pandas as pd

# Repository root (parent of lvtshift-fr/) holds the upstream `lvt` package.
LVTSHIFT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LVTSHIFT))

from lvt.lvt_utils import model_split_rate_tax, save_standard_export  # noqa: E402

import estimate  # noqa: E402
from config import GRENOBLE as CFG  # switch commune here  # noqa: E402

# French -> LVTShift standard property categories (exact strings from
# lvt_utils.STANDARD_PROPERTY_CATEGORIES)
CATEGORY_MAP = {
    "maison": "Single Family Residential",
    "appartement": "Condominium",
    "immeuble_collectif": "Large Multi-Family (5+ units)",
    "commerce": "Commercial",
    "industriel": "Industrial",
    "terrain_nu": "Vacant Land",
    "dependance": "Other",
}

# Residential standard-categories for the France equity charts. The upstream
# report's default "residential" set is US-specific, so we pass the French
# mapping explicitly. (The minority/black quintile charts auto-skip: those
# columns are null by design — France produces no ethnic statistics.)
FR_RESIDENTIAL_CATEGORIES = [
    "Single Family Residential",       # maison
    "Condominium",                     # appartement
    "Large Multi-Family (5+ units)",   # immeuble_collectif
]


def _write_report(out: pd.DataFrame, out_dir: str) -> None:
    """Render the France-relevant PNG charts from the standard export.

    Imported lazily so a CSV-only run never requires matplotlib. The upstream
    ``create_city_report`` saves PNGs under ``{out_dir}/reports/{commune}/`` and
    auto-skips the minority/black quintile charts when those columns are null
    (always, for France). What remains: category impact, ±10 % share,
    income-quintile (Filosofi), and the tax-change distribution.
    """
    try:
        from lvt.viz import create_city_report
    except ImportError as exc:  # matplotlib not installed
        print(f"[{CFG.name}] charts skipped (matplotlib not installed): {exc}")
        return
    report = create_city_report(
        out,
        city=CFG.name.lower(),
        output_dir=f"{out_dir}/reports",
        show=False,
        census_categories=FR_RESIDENTIAL_CATEGORIES,
    )
    print(f"[{CFG.name}] {len(report['charts_saved'])} charts -> "
          f"{out_dir}/reports/{CFG.name.lower()}/")


def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
        commune_tfpb_produit: float, iris_income: pd.DataFrame | None = None,
        out_dir: str = "output", make_report: bool = True) -> pd.DataFrame:
    """parcels: idpar, parcel_area_m2, cell, type_local, category_fr
       buildings / dvf / iris_income: see estimate.py docstrings.
       make_report: also write the PNG charts (needs matplotlib); set False
       for a CSV-only run."""

    imp = estimate.improvement_value(buildings, CFG)
    p = parcels.merge(imp, on="idpar", how="left")
    p[["improvement_value", "floor_area_m2"]] = \
        p[["improvement_value", "floor_area_m2"]].fillna(0)

    surface, _trans = estimate.fit_hedonic(dvf)
    p = estimate.market_value(p, surface)
    p = estimate.land_value_residual(p, CFG)
    p = estimate.current_tax(p, commune_tfpb_produit)

    p["PROPERTY_CATEGORY"] = p["category_fr"].map(CATEGORY_MAP).fillna("other")

    # ---- LVTShift's real revenue-neutral solver -------------------- #
    land_mill, imp_mill, revenue, p = model_split_rate_tax(
        df=p,
        land_value_col="land_value",
        improvement_value_col="improvement_value",
        current_revenue=commune_tfpb_produit,
        land_improvement_ratio=CFG.split_rate_ratio,
    )

    p["tax_change"] = p["new_tax"] - p["current_tax"]
    p["tax_change_pct"] = 100 * p["tax_change"] / p["current_tax"].replace(0, pd.NA)
    p["taxable_land_value"] = p["land_value"]
    p["taxable_improvement_value"] = p["improvement_value"]

    # demographics: IRIS code stands in for geoid; Filosofi median income;
    # minority/black left null - France produces no ethnic statistics
    # (constitutional principle), flag this in any cross-city comparison.
    if iris_income is not None:
        p = p.merge(iris_income.rename(columns={
            "iris": "std_geoid", "median_income_eur": "median_income"}),
            left_on="cell", right_on="std_geoid", how="left")

    Path(out_dir).mkdir(exist_ok=True)
    out = save_standard_export(
        df=p, city=CFG.name.lower(),
        output_path=f"{out_dir}/{CFG.name.lower()}.csv",
        model_type=f"split_rate:{CFG.split_rate_ratio}",
        land_millage=land_mill, improvement_millage=imp_mill,
    )
    print(f"[{CFG.name}] land mill {land_mill:.3f} | imp mill {imp_mill:.3f} "
          f"| revenue €{revenue:,.0f} (target €{commune_tfpb_produit:,.0f})")

    if make_report:
        _write_report(out, out_dir)
    return out


if __name__ == "__main__":
    print("Run ingest first, then call run() with the prepared frames. "
          "See test_synthetic.py for an end-to-end example.")
