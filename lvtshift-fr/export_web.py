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


def _slug(cfg) -> str:
    """Output-file slug for a commune (matches run_pipeline's naming)."""
    return cfg.name.lower().replace(" ", "")


def load_parcels(commune_key: str, out_dir: str = "output") -> pd.DataFrame:
    """Read the per-parcel standard export for one commune (modeled parcels only)."""
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    path = Path(out_dir) / f"{_slug(cfg)}.csv"
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


def _resolve_at_land_share(df: pd.DataFrame, target_share: float,
                           ratio: float, current_revenue: float) -> dict:
    """Re-solve the split-rate model with the aggregate land share tilted to
    `target_share`, holding total base and revenue fixed. Uniform per-parcel
    scaling preserves the relative structure of land vs improvement values."""
    from lvt.lvt_utils import model_split_rate_tax
    land = df["taxable_land_value"].to_numpy(dtype=float)
    imp = df["taxable_improvement_value"].to_numpy(dtype=float)
    current = df["current_tax"].to_numpy(dtype=float)
    base = float((land + imp).sum())
    s = float(land.sum()) / base
    if not 0.0 < s < 1.0:
        raise ValueError(
            f"cannot tilt land share: base land share is {s:.3f} (need 0 < s < 1). "
            "The commune frame has all-land or all-improvement value, so uniform "
            "scaling is undefined.")
    f_land = target_share / s
    f_imp = (1.0 - target_share) / (1.0 - s)
    tmp = pd.DataFrame({"_land": land * f_land, "_imp": imp * f_imp})
    _lm, _im, _rev, solved = model_split_rate_tax(
        df=tmp, land_value_col="_land", improvement_value_col="_imp",
        current_revenue=current_revenue, land_improvement_ratio=ratio)
    chg = solved["new_tax"].to_numpy(dtype=float) - current
    gross = float(np.abs(chg).sum())
    net = float(chg[chg > 0].sum())
    res_mask = df["property_category"].isin(FR_RESIDENTIAL).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        res_pct = 100.0 * chg[res_mask] / current[res_mask]
    res_pct = pd.Series(res_pct).replace([np.inf, -np.inf], np.nan).dropna()
    return {
        "land_share_pct": round(100.0 * target_share, 1),
        "gross_pct_of_levy": _pct(gross, current_revenue),
        "net_pct_of_levy": _pct(net, current_revenue),
        "median_change_pct_residential": round(float(res_pct.median()), 1) if len(res_pct) else None,
        "share_paying_more_pct": _pct(int((chg > 0).sum()), len(chg)),
    }


def build_headline_sensitivity(df: pd.DataFrame, ratio: float, delta_pt: float = 10.0) -> dict:
    current_revenue = float(df["current_tax"].sum())
    land = float(df["taxable_land_value"].sum())
    base = land + float(df["taxable_improvement_value"].sum())
    s = land / base
    d = delta_pt / 100.0
    lo = min(0.99, max(0.01, s - d))
    hi = min(0.99, max(0.01, s + d))
    return {
        "delta_pt": delta_pt,
        "base": _resolve_at_land_share(df, s, ratio, current_revenue),
        "low": _resolve_at_land_share(df, lo, ratio, current_revenue),
        "high": _resolve_at_land_share(df, hi, ratio, current_revenue),
    }


ALLOWED_TOP_KEYS = {
    "commune_key", "insee", "name", "departement", "reference_year",
    "model_type", "headline", "headline_sensitivity", "by_category",
    "by_income_quintile", "by_improvement_ratio", "provenance", "currency",
}
FORBIDDEN_TOKENS = ("std_geoid", "minority_pct", "black_pct", "_usd", "$")


def assert_aggregate_only(payload: dict) -> None:
    """Shape guard: only aggregate keys, bounded lists, no US/per-parcel leakage."""
    extra = set(payload) - ALLOWED_TOP_KEYS
    assert not extra, f"unexpected top-level keys (possible per-parcel leak): {extra}"
    assert len(payload.get("by_improvement_ratio") or []) <= 5
    assert len(payload.get("by_category") or []) <= 10
    if payload.get("by_income_quintile") is not None:
        assert len(payload["by_income_quintile"]) <= 5
    blob = json.dumps(payload, ensure_ascii=False)
    for tok in FORBIDDEN_TOKENS:
        assert tok not in blob, f"forbidden token {tok!r} leaked into payload"


def build_commune_payload(commune_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    df = load_parcels(commune_key, out_dir)
    return {
        "commune_key": commune_key,
        "insee": cfg.insee_code,
        "name": cfg.name,
        "departement": cfg.departement,
        "reference_year": getattr(cfg, "reference_year", None),
        "model_type": f"split_rate:{cfg.split_rate_ratio}",
        "headline": build_headline(df),
        "headline_sensitivity": build_headline_sensitivity(df, cfg.split_rate_ratio),
        "by_category": build_by_category(df),
        "by_income_quintile": build_by_income_quintile(df),
        "by_improvement_ratio": build_buckets(df),
        "provenance": {
            "construction_cost_eur_m2": cfg.construction_cost_eur_m2,
            "land_share_bounds": list(cfg.land_share_bounds),
            "note": ("Agrégats uniquement — imputations honnêtes au niveau "
                     "catégorie/quintile, jamais à la parcelle."),
        },
        "currency": "EUR",
    }


def _write_commune_json(payload: dict, data_dir: str) -> Path:
    """Guard then write one commune payload to <data_dir>/<commune_key>.json."""
    assert_aggregate_only(payload)
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(data_dir) / f"{payload['commune_key']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _index_entry(payload: dict) -> dict:
    """Teaser fields for index.json, taken from an already-built payload."""
    h = payload["headline"]
    return {
        "commune_key": payload["commune_key"], "name": payload["name"],
        "insee": payload["insee"], "departement": payload["departement"],
        "parcels_modeled": h["parcels_modeled"],
        "land_share_pct": h["land_share_pct"],
        "gross_pct_of_levy": h["gross_pct_of_levy"],
    }


def export_commune(commune_key: str, out_dir: str = "output",
                   data_dir: str = "site/public/data") -> Path:
    return _write_commune_json(build_commune_payload(commune_key, out_dir), data_dir)


def export_all(out_dir: str = "output", data_dir: str = "site/public/data") -> dict:
    from config import COMMUNES
    index = []
    for key, cfg in COMMUNES.items():
        if not (Path(out_dir) / f"{_slug(cfg)}.csv").exists():
            continue
        payload = build_commune_payload(key, out_dir)   # load the CSV exactly once
        _write_commune_json(payload, data_dir)
        index.append(_index_entry(payload))
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / "index.json").write_text(
        json.dumps({"communes": index, "currency": "EUR"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return {"exported": [c["commune_key"] for c in index]}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Export aggregate JSON for the advocacy site.")
    ap.add_argument("commune", nargs="?", help="commune key; omit to export all available")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--data-dir", default="site/public/data")
    a = ap.parse_args()
    if a.commune:
        print("wrote", export_commune(a.commune, a.out_dir, a.data_dir))
    else:
        print(export_all(a.out_dir, a.data_dir))
