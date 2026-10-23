"""Open-DVF probe: activity-land vs residential-land prices, and business-premises
sales quality, for 93, 94 (MOS 2021 classes) and Métropole de Lyon (ZAE polygons).

Usage: python -I dvf_nonres.py <data_dir>
"""
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

D = Path(sys.argv[1])
LOC_IND = "Local industriel. commercial ou assimilé"

ACT = {37: "grandes emprises indus", 38: "ZAE", 39: "entreposage air libre",
       40: "entrepôts logistiques", 42: "grandes surfaces comm."}
RES = {28: "habitat individuel", 29: "hab. indiv. identique", 31: "habitat continu bas",
       32: "collectif continu haut", 33: "collectif discontinu"}


def load(dep):
    frames = [pd.read_csv(D / f"dvf_{y}_{dep}.csv.gz", dtype=str, low_memory=False)
              for y in (2023, 2024)]
    df = pd.concat(frames, ignore_index=True)
    for c in ("valeur_fonciere", "surface_terrain", "surface_reelle_bati",
              "longitude", "latitude", "lot1_numero"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[df.nature_mutation == "Vente"]


def land_only(df):
    g = df.groupby("id_mutation")
    has_local = g.type_local.apply(lambda s: s.notna().any())
    m = g.agg(val=("valeur_fonciere", "first"), area=("surface_terrain", "sum"),
              npar=("id_parcelle", "nunique"), lon=("longitude", "first"),
              lat=("latitude", "first"), com=("code_commune", "first"),
              tab=("nature_culture", lambda s: (s == "terrains a bâtir").any()))
    m = m[~has_local.reindex(m.index).values]
    m = m[(m.area >= 200) & (m.val >= 10_000) & (m.npar <= 3) & m.lon.notna()]
    m["ppm2"] = m.val / m.area
    return m


def premises(df):
    g = df.groupby("id_mutation")
    types = g.type_local.apply(lambda s: set(s.dropna()))
    only_ind = types.apply(lambda t: t == {LOC_IND} or t == {LOC_IND, "Dépendance"})
    sub = df[df.id_mutation.isin(only_ind[only_ind].index)]
    sub = sub[sub.type_local == LOC_IND]
    m = sub.groupby("id_mutation").agg(val=("valeur_fonciere", "first"),
                                       n_loc=("type_local", "size"),
                                       surf=("surface_reelle_bati", "sum"),
                                       surf_na=("surface_reelle_bati", lambda s: s.isna().all()),
                                       land=("surface_terrain", "max"))
    return m


def classify(points, polys, col):
    gp = gpd.GeoDataFrame(points, geometry=gpd.points_from_xy(points.lon, points.lat),
                          crs=4326)
    j = gpd.sjoin(gp, polys[[col, "geometry"]], how="left", predicate="within")
    return j[~j.index.duplicated()]


def q(s):
    s = s.dropna()
    if len(s) == 0:
        return "n=0"
    return (f"n={len(s):4d}  p25={s.quantile(.25):6.0f}  median={s.median():6.0f}  "
            f"p75={s.quantile(.75):6.0f}")


if __name__ == "__main__":
    mos = gpd.read_file(D / "mos_9394.geojson")
    mos["mos2021"] = mos["mos2021"].astype(int)
    for dep in ("93", "94"):
        df = load(dep)
        print(f"\n== Dept {dep}: land-only sales 2023-24 (€/m² land), MOS 2021 class at point")
        lo = classify(land_only(df), mos, "mos2021")
        lo["grp"] = np.where(lo.mos2021.isin(ACT), "ACTIVITY",
                             np.where(lo.mos2021.isin(RES), "RESIDENTIAL", "other/none"))
        for grp in ("ACTIVITY", "RESIDENTIAL", "other/none"):
            print(f"  {grp:12s} {q(lo[lo.grp == grp].ppm2)}")
        for k, v in ACT.items():
            s = lo[lo.mos2021 == k].ppm2
            if len(s):
                print(f"     {k} {v:24s} {q(s)}")
        pm = premises(df)
        n = len(pm)
        print(f"  business premises mutations (only '{LOC_IND}'): {n}")
        print(f"    surface missing: {pm.surf_na.mean():.0%}; multi-local (>1 local): "
              f"{(pm.n_loc > 1).mean():.0%}")
        ok = pm[(~pm.surf_na) & (pm.n_loc == 1) & (pm.surf >= 20)]
        print(f"    single-local with surface: {len(ok)}; €/m² bâti {q(ok.val / ok.surf)}")
        big = ok[ok.surf >= 1000]
        print(f"    of which >=1000 m²: {q(big.val / big.surf)}")

    print("\n== Rhône 69, Métropole de Lyon ZAE polygons")
    zae = gpd.read_file(D / "zae_lyon.geojson").to_crs(4326)
    zae["in_zae"] = 1
    df = load("69")
    lo = classify(land_only(df), zae, "in_zae")
    zcom = set(lo[lo.in_zae == 1].com)
    lo = lo[lo.com.isin(zcom)]
    print(f"  communes with a ZAE land sale: {len(zcom)}")
    print(f"  inside ZAE   {q(lo[lo.in_zae == 1].ppm2)}")
    print(f"  outside ZAE  {q(lo[lo.in_zae != 1].ppm2)}")
    print(f"  outside ZAE, 'terrains a bâtir' {q(lo[(lo.in_zae != 1) & lo.tab].ppm2)}")
    pm = premises(df[df.code_commune.isin(zcom)])
    print(f"  business premises mutations: {len(pm)}; surface missing {pm.surf_na.mean():.0%};"
          f" multi-local {(pm.n_loc > 1).mean():.0%}")
    ok = pm[(~pm.surf_na) & (pm.n_loc == 1) & (pm.surf >= 20)]
    print(f"    single-local €/m² bâti {q(ok.val / ok.surf)}")
    big = ok[ok.surf >= 1000]
    print(f"    of which >=1000 m²: {q(big.val / big.surf)}")
