"""Split the TFPNB between agricultural/natural land and other unbuilt land (D6).

No published statistic gives this split. It is rebuilt commune by commune from
the DGFiP REI (via OFGL):

* the TAFNB (CGI art. 1519 I) is assessed on cadastral groups 7 and 10-13 only
  (quarries, building plots, amenity land, railways, sols; BOI-IF-AUT-80), so
  TAFNB base / TFPNB base is each commune's non-agricultural share; the TFPNB
  rate is the same for every group within a commune, so the share applies to
  the amount;
* the whole TAFNB amount is non-agricultural;
* syndicates (B21/B23) are split the same way but reported apart, because
  yields._TFPNB_ALL leaves them to tf_annexes.

Check printed for 2024: the base of the 20 % agricultural exemption (D21,
art. 1394 B bis, groups 1-6, 8, 9) gives the agricultural base independently.

Run: python docs/research/tfpnb_farm_split.py   (downloads ~650 000 REI rows)
Last run 2026-10-29: 1 296,3 / 1 032,9 M€ (2024) and 1 186,9 / 922,2 M€ (2025),
the constants in yields._TFPNB_ALL and _TFPNB_FARM.
"""

import collections
import json
import math
import urllib.parse
import urllib.request

API = "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei/exports/json"
VARS = ["B11", "B13", "B21", "B23", "B31", "B33", "B11TAFNB", "B13TAFNB", "B31TAFNB",
        "B33TAFNB", "B31MGPTAFNB", "B33MGPTAFNB", "D21"]


def fetch(year: int) -> dict:
    """{idcom: {var: value}} for one year."""
    where = f"annee='{int(year)}' and var in ({', '.join(repr(v) for v in VARS)})"
    url = API + "?" + urllib.parse.urlencode({"select": "idcom,var,valeur", "where": where})
    with urllib.request.urlopen(url, timeout=600) as r:
        if not r.geturl().startswith("https://data.ofgl.fr/"):
            raise RuntimeError(f"redirected to {r.geturl()}")
        rows = json.load(r)
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"no REI rows for {year}")
    out = collections.defaultdict(lambda: collections.defaultdict(float))
    for row in rows:
        if row["valeur"] is not None:
            v = float(row["valeur"])
            if not math.isfinite(v):
                raise RuntimeError(f"non-finite value in {row}")
            out[row["idcom"]][row["var"]] += v
    return out


def split(w: dict) -> dict:
    def share(c, base):   # non-agricultural share of one level's base
        taf = c["B11TAFNB"] + c["B31TAFNB"] + c["B31MGPTAFNB"]
        return min(1.0, taf / c[base]) if c[base] > 0 else 0.0
    m = 1e6
    taf_amount = sum(c["B13TAFNB"] + c["B33TAFNB"] + c["B33MGPTAFNB"] for c in w.values()) / m
    non = {"commune": sum(share(c, "B11") * c["B13"] for c in w.values()) / m,
           "gfp": sum(share(c, "B31") * c["B33"] for c in w.values()) / m,
           "syndicats": sum(share(c, "B21") * c["B23"] for c in w.values()) / m,
           "tafnb": taf_amount}
    total = {"commune": sum(c["B13"] for c in w.values()) / m,
             "gfp": sum(c["B33"] for c in w.values()) / m,
             "syndicats": sum(c["B23"] for c in w.values()) / m,
             "tafnb": taf_amount}
    excl_synd = sum(total.values()) - total["syndicats"]
    farm_excl_synd = excl_synd - (sum(non.values()) - non["syndicats"])
    return {"total_excl_syndicats": excl_synd, "farm_excl_syndicats": farm_excl_synd,
            "farm_share": farm_excl_synd / excl_synd,
            "agri_base_by_exemption": sum(c["D21"] for c in w.values()) / m / 0.2 * 0.8,
            "agri_base_by_tafnb": sum(max(0.0, c["B11"] - c["B11TAFNB"] - c["B31TAFNB"]
                                          - c["B31MGPTAFNB"]) for c in w.values()) / m}


if __name__ == "__main__":
    for y in (2024, 2025):
        r = split(fetch(y))
        print(y, {k: round(v, 3 if k == "farm_share" else 1) for k, v in r.items()})
