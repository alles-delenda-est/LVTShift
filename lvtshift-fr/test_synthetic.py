"""
End-to-end test on synthetic Grenoble-like data, through LVTShift's
REAL solver and export. Proves the integration before any download.

Synthetic world: 5,000 parcels, 3 zones (centre / mid / periphery)
with a land price gradient, mixed housing/commercial/vacant.
"""

import numpy as np
import pandas as pd

import run_pipeline as rp

rng = np.random.default_rng(42)
N = 5_000

zones = rng.choice(["centre", "mid", "peri"], N, p=[0.25, 0.45, 0.30])
zone_ppm2 = {"centre": 4200, "mid": 3100, "peri": 2300}      # €/m² floor
zone_land = {"centre": 1500, "mid": 700, "peri": 250}        # €/m² land

cat = rng.choice(
    ["appartement", "maison", "commerce", "terrain_nu"], N,
    p=[0.55, 0.30, 0.10, 0.05])

parcel_area = np.where(cat == "maison", rng.lognormal(6.2, 0.4, N),
                       rng.lognormal(6.8, 0.6, N)).round()

parcels = pd.DataFrame({
    "idpar": [f"38185000A{i:04d}" for i in range(N)],
    "parcel_area_m2": parcel_area,
    "cell": zones,
    "type_local": np.where(cat == "maison", "Maison", "Appartement"),
    "category_fr": cat,
})

built = cat != "terrain_nu"
n_levels = np.select(
    [cat == "maison", cat == "appartement", cat == "commerce"],
    [rng.integers(1, 3, N), rng.integers(3, 9, N), rng.integers(1, 4, N)], 1)
buildings = pd.DataFrame({
    "idpar": parcels.idpar[built],
    "footprint_m2": (parcel_area[built] * rng.uniform(0.3, 0.7, built.sum())).round(),
    "n_levels": n_levels[built].astype(float),
    "height_m": n_levels[built] * 3.0,
    "year_built": rng.integers(1900, 2024, built.sum()).astype(float),
    "usage": cat[built],
})
# degrade 15% to test imputation paths
mask = rng.random(len(buildings)) < 0.15
buildings.loc[mask, "n_levels"] = np.nan
buildings.loc[rng.random(len(buildings)) < 0.20, "year_built"] = np.nan

# synthetic DVF: 1,200 sales priced off the zone gradient + noise
sale_idx = rng.choice(np.where(built)[0], 1200)
fa = (parcel_area[sale_idx] * 0.5 * n_levels[sale_idx])
dvf = pd.DataFrame({
    "price": fa * np.vectorize(zone_ppm2.get)(zones[sale_idx])
             * rng.lognormal(0, 0.18, 1200),
    "floor_area_m2": fa,
    "type_local": np.where(cat[sale_idx] == "maison", "Maison", "Appartement"),
    "year": rng.choice([2022, 2023, 2024], 1200),
    "cell": zones[sale_idx],
})

iris_income = pd.DataFrame({
    "iris": ["centre", "mid", "peri"],
    "median_income_eur": [26_000, 23_500, 21_000],
})

# Grenoble TFPB produit, ballpark for the test (real value: read from REI)
TFPB = 95_000_000.0

out = rp.run(parcels, buildings, dvf, TFPB, iris_income, out_dir="output")

print("\n--- sanity checks -------------------------------------")
print(f"rows exported: {len(out)}")
chg = out.groupby("property_category")["tax_change_pct"].median().round(1)
print("median tax change % by category:\n", chg.to_string())
rev_ok = abs(out["new_tax"].sum() / TFPB - 1) < 0.01
print(f"revenue neutrality within 1%: {rev_ok}")
assert rev_ok
# FB is a built-only tax: vacant land pays ~0 today, then a positive LVT bill.
vac = out["property_category"] == "Vacant Land"
assert out.loc[vac, "current_tax"].sum() == 0, "vacant land is not in the FB base"
assert (out.loc[vac, "new_tax"] > 0).mean() > 0.9, "vacant land should pay LVT"
print("ALL CHECKS PASSED ✅")
