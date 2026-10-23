"""Audit the building-less land of a modelled commune (local, never published).

Usage:
    python audit_land.py paris
    python audit_land.py paris --top 15

Reads output/diagnostics/<slug>_parcels.csv (written by run_commune.py) and
answers: which zoning labels does the building-less land carry, how much
imputed land value and post-reform levy sits on it, and which large parcels
dominate. Built to catch public open space (e.g. Paris PLU zone UV — parks,
cemeteries, sports grounds — whose GPU typezone is "U") being priced as
building land. A check, not a calibration: it prints, it never edits a model.
"""

import argparse
from pathlib import Path

import pandas as pd

from config import COMMUNES, slug_of


def audit(key: str, out_dir: str = "output", top: int = 10) -> dict:
    path = Path(out_dir) / "diagnostics" / f"{slug_of(COMMUNES[key])}_parcels.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: re-run `python run_commune.py {key}`")
    d = pd.read_csv(path, dtype={"zone_libelle": str, "zone_typ": str})
    levy = float(d["new_tax"].sum())
    land = float(d["land_value"].sum())
    vac = d[d["land_type"] != "built"].copy()

    by_zone = (vac.groupby(vac["zone_libelle"].fillna("(aucune)"))
                  .agg(parcels=("idpar", "size"),
                       area_ha=("parcel_area_m2", lambda s: s.sum() / 1e4),
                       land_value_eur=("land_value", "sum"),
                       levy_eur=("new_tax", "sum"))
                  .sort_values("levy_eur", ascending=False))
    by_zone["levy_pct_of_commune"] = 100 * by_zone["levy_eur"] / levy
    by_zone["land_pct_of_commune"] = 100 * by_zone["land_value_eur"] / land

    big = vac.nlargest(top, "new_tax")[
        ["idpar", "land_type", "zone_typ", "zone_libelle", "parcel_area_m2",
         "land_value", "new_tax"]]
    return {
        "levy_eur": levy,
        "vacant_levy_pct": 100 * float(vac["new_tax"].sum()) / levy,
        "vacant_land_pct": 100 * float(vac["land_value"].sum()) / land,
        "by_zone": by_zone,
        "largest": big,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("commune", choices=sorted(COMMUNES))
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--out-dir", default="output")
    a = ap.parse_args()
    r = audit(a.commune, a.out_dir, a.top)
    pd.set_option("display.width", 160)
    print(f"levy €{r['levy_eur']:,.0f} — building-less land bears "
          f"{r['vacant_levy_pct']:.2f} % of it and {r['vacant_land_pct']:.2f} % of land value")
    print("\nby zoning label (building-less parcels):")
    print(r["by_zone"].head(25).round(2).to_string())
    print(f"\n{a.top} building-less parcels with the largest post-reform levy:")
    print(r["largest"].round(0).to_string(index=False))


if __name__ == "__main__":
    main()
