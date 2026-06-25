"""Aggregate-only JSON exporter for the « Pour une terre productive » site.

Reads the authoritative per-parcel standard export (output/<slug>.csv) and emits
aggregates by category, income quintile and improvement-ratio bucket, plus a
±10 pt land-share sensitivity band re-solved through the unmodified upstream
solver. Never emits per-parcel rows. See docs/superpowers/specs/
2026-06-24-advocacy-site-design.md §5.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Upstream `lvt` lives at the repo root (parent of lvtshift-fr/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard-category -> French display label (mirrors run_pipeline.CATEGORY_MAP).
CATEGORY_LABELS_FR = {
    "Single Family Residential": "Maison individuelle",
    "Condominium": "Appartement (copropriété)",
    "Large Multi-Family (5+ units)": "Immeuble collectif (5+ logements)",
    "Commercial": "Commerce",
    "Industrial": "Industriel",
    "Vacant Land": "Terrain nu / non bâti",
    "Other": "Autre / dépendance",
    "other": "Autre / dépendance",
}
FR_RESIDENTIAL = {
    "Single Family Residential", "Condominium", "Large Multi-Family (5+ units)",
}


def load_parcels(commune_key: str, out_dir: str = "output") -> pd.DataFrame:
    """Read the per-parcel standard export for one commune (modeled parcels only)."""
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    slug = cfg.name.lower().replace(" ", "")
    path = Path(out_dir) / f"{slug}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"No model output for {commune_key} at {path}; "
            f"run `python run_commune.py {commune_key}` first.")
    df = pd.read_csv(path)
    if "is_fully_exempt" in df.columns:
        df = df[~df["is_fully_exempt"].fillna(False).astype(bool)].copy()
    return df


def _pct(num: float, den: float, ndigits: int = 1):
    return round(100.0 * num / den, ndigits) if den else None


def build_headline(df: pd.DataFrame) -> dict:
    land = float(df["taxable_land_value"].sum())
    imp = float(df["taxable_improvement_value"].sum())
    base = land + imp
    levy = float(df["new_tax"].sum())
    gross = float(df["tax_change"].abs().sum())
    net = float(df.loc[df["tax_change"] > 0, "tax_change"].sum())
    return {
        "parcels_modeled": int(len(df)),
        "tax_base_eur": base,
        "land_base_eur": land,
        "improvement_base_eur": imp,
        "land_share_pct": _pct(land, base),
        "neutral_levy_eur": levy,
        "gross_shifted_eur": gross,
        "net_shifted_eur": net,
        "gross_pct_of_levy": _pct(gross, levy),
        "net_pct_of_levy": _pct(net, levy),
        "gross_bps_of_base": round(10000.0 * gross / base, 1) if base else None,
        "currency": "EUR",
    }


def build_buckets(df: pd.DataFrame) -> list:
    base_series = df["taxable_land_value"] + df["taxable_improvement_value"]
    total_base = float(base_series.sum())
    total_gross = float(df["tax_change"].abs().sum())
    ratio = (df["taxable_improvement_value"] / base_series.replace(0, np.nan)).fillna(0.0)
    specs = [
        ("vacant", "Terrain nu (0 %)", ratio == 0),
        ("lt10", "Très sous-bâti (<10 %)", (ratio > 0) & (ratio < 0.10)),
        ("r10_25", "Sous-bâti (10–25 %)", (ratio >= 0.10) & (ratio < 0.25)),
        ("r25_50", "Sous-bâti (25–50 %)", (ratio >= 0.25) & (ratio < 0.50)),
        ("ge50", "Bâti (≥50 %)", ratio >= 0.50),
    ]
    out = []
    for key, label, mask in specs:
        sub = df[mask]
        val = float((sub["taxable_land_value"] + sub["taxable_improvement_value"]).sum())
        gross = float(sub["tax_change"].abs().sum())
        out.append({
            "bucket": key, "label": label, "parcels": int(mask.sum()),
            "value_eur": val,
            "value_pct_of_base": _pct(val, total_base),
            "share_of_gross_change_pct": _pct(gross, total_gross),
        })
    return out


def build_by_category(df: pd.DataFrame) -> list:
    n = len(df)
    out = []
    for cat, sub in df.groupby("property_category"):
        chg_pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        out.append({
            "category": cat,
            "label_fr": CATEGORY_LABELS_FR.get(cat, str(cat)),
            "parcels": int(len(sub)),
            "share_of_parcels_pct": _pct(len(sub), n),
            "median_change_pct": round(float(chg_pct.median()), 1) if len(chg_pct) else None,
            "median_change_eur": round(float(sub["tax_change"].median()), 0),
            "count_paying_more": int((sub["tax_change"] > 0).sum()),
            "share_paying_more_pct": _pct(int((sub["tax_change"] > 0).sum()), len(sub)),
        })
    out.sort(key=lambda r: r["parcels"], reverse=True)
    return out


def build_by_income_quintile(df: pd.DataFrame):
    if "median_income" not in df.columns or df["median_income"].notna().sum() == 0:
        return None
    d = df[df["median_income"].notna()].copy()
    try:
        d["_q"] = pd.qcut(d["median_income"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    except ValueError:
        return None
    if d["_q"].nunique() < 5:
        return None
    res = d[d["property_category"].isin(FR_RESIDENTIAL)]
    out = []
    for q in [1, 2, 3, 4, 5]:
        sub = d[d["_q"] == q]
        rsub = res[res["_q"] == q]
        sub_pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        res_pct = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        out.append({
            "quintile": int(q),
            "median_income_eur": round(float(sub["median_income"].median()), 0),
            "median_change_pct": round(float(sub_pct.median()), 1) if len(sub_pct) else None,
            "median_change_pct_residential": round(float(res_pct.median()), 1) if len(res_pct) else None,
            "parcels": int(len(sub)),
        })
    return out
