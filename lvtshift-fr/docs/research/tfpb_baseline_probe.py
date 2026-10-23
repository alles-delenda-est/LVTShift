"""Probe: split each commune's TFPB base into industrial / professional / residual
(housing + other) using open REI aggregates only.

Usage:
    python tfpb_baseline_probe.py OUT_DIR [--codes 93078,94070,69199,75056] [--year 2025]

Public data only (no owner names, SIREN or MAJIC ids):
  * OFGL `rei` (Opendatasoft API), REI millésime --year, long format.
  * OFGL `base-fiscale-simplifiee`, 2020 TFPB rates (commune + département).

Method (see tfpb-baseline-calibration.md):
  EI base  = WC75 / (t_commune_2020 + t_departement_2020)      [LFI 2021 art. 29 III A 2]
             (Métropole de Lyon communes: département rate = Rhône 2014 rate, 11.03 %)
  Pro base ~ k x 0.5 x CFE gross base of non-industrial premises
             = 0.5 x T29_1 where published, else 0.5 x (T29 - X503)
  Residual = E11 - EI - Pro   (housing, annexes, public/other premises)
Writes OUT_DIR/tfpb_split_<year>.csv and OUT_DIR/tfpb_split_<year>_raw.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

OFGL = "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets"
REI_VARS = ["E11", "E12", "E13", "E14", "E16", "E16NB", "WC75", "WE75",
            "T29", "T29_1", "T29_2", "T29_3", "X503", "ZX3"]
RHONE_2014_FB_RATE = 11.03  # applies to Métropole de Lyon communes (art. 29 III A 2)
DEFAULT_CODES = "93078,94070,69199,75056"


def _get_json(url: str, params: Dict[str, str], retries: int = 3) -> dict:
    """GET an Opendatasoft endpoint with simple retry; raises on final failure."""
    full = f"{url}?{urllib.parse.urlencode(params)}"
    last: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "LVTShift-FR probe"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # network / HTTP / JSON errors
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed after {retries} tries: {full} ({last})")


def fetch_rei(code: str, year: int) -> Dict[str, Optional[float]]:
    """Return {var: valeur} for the REI variables of interest (one commune, one year)."""
    vars_sql = ",".join(f'"{v}"' for v in REI_VARS)
    data = _get_json(f"{OFGL}/rei/records", {
        "where": f'idcom="{code}" and annee="{year}" and var in ({vars_sql})',
        "select": "var,valeur,libcom,dep", "limit": "100"})
    out: Dict[str, Optional[float]] = {v: None for v in REI_VARS}
    for r in data.get("results", []):
        out[r["var"]] = r["valeur"]
        out["libcom"], out["dep"] = r.get("libcom"), r.get("dep")
    return out


def fetch_rates_2020(code: str) -> Dict[str, Optional[float]]:
    """2020 TFPB net rates (percent) for the commune and its département."""
    data = _get_json(f"{OFGL}/base-fiscale-simplifiee/records", {
        "where": f'idcom="{code}" and exer="2020" and dispositif_fiscal="TFPB"',
        "select": "destinataire,taux_net", "limit": "20"})
    rates: Dict[str, Optional[float]] = {"t_com_2020": None, "t_dep_2020": None}
    for r in data.get("results", []):
        if r["destinataire"] == "Commune":
            rates["t_com_2020"] = r["taux_net"]
        elif r["destinataire"] == "Département":
            rates["t_dep_2020"] = r["taux_net"]
    return rates


def split(code: str, year: int, pro_scale: float = 1.0) -> Dict[str, object]:
    """Compute the industrial / professional / residual split for one commune."""
    rei = fetch_rei(code, year)
    rates = fetch_rates_2020(code)
    row: Dict[str, object] = {"idcom": code, **rei, **rates}
    t_dep = rates["t_dep_2020"]
    if code.startswith("69"):
        # Métropole communes: the law uses the Rhône 2014 rate. OFGL's simplified base
        # reports 11.58 (Métropole 2020) for them; REI 2020 E42 shows 11.03 for dep 69.
        t_dep = RHONE_2014_FB_RATE
        row["t_dep_note"] = "Rhône 2014 rate (art. 29 III A 2)"
    e11 = rei.get("E11") or 0.0
    t_sum = (rates["t_com_2020"] or 0.0) + (t_dep or 0.0)
    ei = (rei.get("WC75") or 0.0) / (t_sum / 100) if t_sum else None
    if rei.get("T29_1") not in (None, 0):
        cfe_pro, src = rei["T29_1"], "T29_1"
    elif rei.get("T29") is not None:
        cfe_pro, src = (rei["T29"] or 0.0) - (rei.get("X503") or 0.0), "T29-X503"
    else:
        cfe_pro, src = None, "none"
    # pro_scale (k): 1.0 = raw CFE proxy (lower bound); 2.5 = central national calibration
    # to Cour des comptes 2023 (pro = 22 % of TFPB receipts vs 8.6 % raw proxy). See note §9.4.
    pro = pro_scale * 0.5 * cfe_pro if cfe_pro is not None else None
    if pro is not None and e11:
        pro = min(pro, max(0.0, 0.9 * e11 - (ei or 0.0)))  # guard: pro + EI <= 90 % of base
    resid = e11 - (ei or 0.0) - (pro or 0.0) if e11 else None
    row.update({
        "t_dep_used": t_dep, "base_EI": ei, "base_pro_proxy": pro, "pro_source": src,
        "base_residual": resid,
        "share_EI": ei / e11 if e11 and ei is not None else None,
        "share_pro": pro / e11 if e11 and pro is not None else None,
        "share_residual": resid / e11 if e11 and resid is not None else None,
        # Cross-check: CFE EI base (X503) vs TFPB-implied VL x 2 x 0.7 (CFE 30 % EI reduction)
        "check_X503_over_implied": ((rei.get("X503") or 0) / (ei * 2 * 0.7)) if ei else None,
    })
    return row


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--codes", default=DEFAULT_CODES, help="comma-separated INSEE codes")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--pro-scale", type=float, default=1.0,
                    help="k multiplier on the CFE professional proxy (1.0 low, 2.5 central)")
    a = ap.parse_args(argv)
    codes = [c.strip() for c in a.codes.split(",") if c.strip().isdigit() and len(c.strip()) == 5]
    if not 0 < a.pro_scale <= 5:
        ap.error("--pro-scale must be in (0, 5]")
    if not codes:
        ap.error("no valid 5-digit INSEE codes")
    a.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for c in codes:
        try:
            rows.append(split(c, a.year, a.pro_scale))
        except RuntimeError as exc:
            print(f"[skip] {c}: {exc}", file=sys.stderr)
    (a.out_dir / f"tfpb_split_{a.year}_raw.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    cols = ["idcom", "libcom", "E11", "E13", "WC75", "t_com_2020", "t_dep_used",
            "base_EI", "share_EI", "pro_source", "base_pro_proxy", "share_pro",
            "share_residual", "E16NB", "ZX3", "check_X503_over_implied"]
    with open(a.out_dir / f"tfpb_split_{a.year}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        fmt = lambda x: "n/a" if x is None else f"{x:.1%}"
        print(f"{r['idcom']} {r.get('libcom')}: EI {fmt(r['share_EI'])}, "
              f"pro~ {fmt(r['share_pro'])} ({r['pro_source']}), rest {fmt(r['share_residual'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
