"""BD TOPO probe: nombre_d_etages coverage and implied storey height (hauteur ÷
étages) by nature × usage_1, for a few non-residential-heavy communes.

Usage: python -I bdtopo_probe.py <out_dir> INSEE [INSEE ...]
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import geopandas as gpd
import pandas as pd

OUT = Path(sys.argv[1])
WFS = "https://data.geopf.fr/wfs/ows"


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def commune(insee):
    js = json.loads(get(f"https://geo.api.gouv.fr/communes/{insee}?format=geojson&geometry=contour"))
    return gpd.GeoDataFrame.from_features([js], crs=4326)


def buildings(poly):
    xmin, ymin, xmax, ymax = poly.total_bounds
    feats, start = [], 0
    while True:
        p = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
             "TYPENAMES": "BDTOPO_V3:batiment", "OUTPUTFORMAT": "application/json",
             "SRSNAME": "EPSG:4326", "COUNT": 5000, "STARTINDEX": start,
             "BBOX": f"{ymin},{xmin},{ymax},{xmax},urn:ogc:def:crs:EPSG::4326"}
        js = json.loads(get(f"{WFS}?{urllib.parse.urlencode(p)}"))
        feats += js["features"]
        if len(js["features"]) < 5000:
            break
        start += 5000
    g = gpd.GeoDataFrame.from_features(feats, crs=4326)
    g = g[g.representative_point().within(poly.geometry.iloc[0])]
    return g.to_crs(2154)


if __name__ == "__main__":
    frames = []
    for insee in sys.argv[2:]:
        c = commune(insee)
        b = buildings(c)
        b["insee"] = insee
        b["commune"] = c["nom"].iloc[0]
        frames.append(b)
        print(insee, c["nom"].iloc[0], len(b), "buildings")
    b = pd.concat(frames)
    b["area"] = b.geometry.area
    b["h"] = pd.to_numeric(b.hauteur, errors="coerce").where(lambda s: s > 0)
    b["lv"] = pd.to_numeric(b.nombre_d_etages, errors="coerce")
    b["h_per_lv"] = b.h / b.lv
    b["is_light"] = b.construction_legere.astype(str).str.lower().isin(["true", "1"])
    grp = b.groupby(["nature", "usage_1"])
    t = pd.DataFrame({
        "n": grp.size(),
        "footprint_m2": grp.area.sum().round(-2),
        "share_area": (grp.area.sum() / b.area.sum()).round(3),
        "lv_null": grp.lv.apply(lambda s: s.isna().mean()).round(2),
        "h_null": grp.h.apply(lambda s: s.isna().mean()).round(2),
        "h_med": grp.h.median().round(1),
        "h_p90": grp.h.quantile(.9).round(1),
        "lv_med": grp.lv.median(),
        "h_per_lv_med": grp.h_per_lv.median().round(2),
        "light": grp.is_light.mean().round(2),
    }).sort_values("footprint_m2", ascending=False)
    pd.set_option("display.width", 220)
    print(t[t.n >= 5].to_string())
    big = b[(b.nature == "Industriel, agricole ou commercial") & b.lv.notna()]
    print("\nIAC nature with known storeys: lv distribution (area-weighted share)")
    print((big.groupby("lv").area.sum() / big.area.sum()).round(3).head(8).to_string())
    print("\nIAC nature, h/lv by lv:")
    print(big.groupby("lv").h_per_lv.median().round(2).head(6).to_string())
    nonres = b[b.usage_1.isin(["Commercial et services", "Industriel"]) & (b.nature == "Indifférenciée") & b.lv.notna()]
    print("\nIndifférenciée + commercial/industriel: h/lv median by lv")
    print(nonres.groupby("lv").h_per_lv.median().round(2).head(8).to_string())
    res = b[(b.usage_1 == "Résidentiel") & b.lv.notna() & (b.lv >= 2)]
    print("\nRésidentiel lv>=2: h/lv median", round(res.h_per_lv.median(), 2))
    b.drop(columns="geometry").to_csv(OUT / "bdtopo_probe.csv", index=False)
