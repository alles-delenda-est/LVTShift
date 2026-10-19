"""Aggregate-only JSON exporter for the « Pour une terre productive » site.

Reads the authoritative per-parcel standard export (output/<slug>.csv) and emits
aggregates by category, income quintile and improvement-ratio bucket, plus a
±10 pt land-share sensitivity band re-solved through the unmodified upstream
solver. Never emits per-parcel rows. See docs/superpowers/specs/
2026-06-24-advocacy-site-design.md §5.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Upstream `lvt` lives at the repo root (parent of lvtshift-fr/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Upper land-share clip shared by every commune (config.CommuneConfig default).
LAND_SHARE_CAP = 0.85
MIN_BUILT_FOR_CAP_PCT = 30

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
    from config import slug_of
    return slug_of(cfg)


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
    n_exempt = 0
    if "is_fully_exempt" in df.columns:
        exempt = df["is_fully_exempt"].fillna(False).astype(bool)
        n_exempt = int(exempt.sum())
        df = df[~exempt].copy()
    # count only (never which parcels): disclosed in the payload provenance
    df.attrs["exempt_parcels"] = n_exempt
    return df


def _pct(num: float, den: float, ndigits: int = 1):
    return round(100.0 * num / den, ndigits) if den else None


def built_at_cap_pct(df: pd.DataFrame, cap: float = LAND_SHARE_CAP):
    """% of built parcels whose land share sits at the upper clip. When most
    parcels are there, the aggregate land share is set by the bound, not
    measured, and the site must say so."""
    land = df["taxable_land_value"]
    imp = df["taxable_improvement_value"]
    built = imp > 0
    # too few built parcels and the % would describe individual parcels
    if built.sum() < MIN_BUILT_FOR_CAP_PCT:
        return None
    share = land[built] / (land[built] + imp[built])
    return _pct(int((share >= cap - 0.001).sum()), int(built.sum()))


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
        "built_at_cap_pct": built_at_cap_pct(df),
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


def _tilted_change(df: pd.DataFrame, target_share: float, ratio: float,
                   current_revenue: float) -> np.ndarray:
    """Per-parcel tax change after re-solving with the aggregate land share of
    `df` tilted to `target_share` (total base and revenue held fixed)."""
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
    return solved["new_tax"].to_numpy(dtype=float) - current


def _sensitivity_summary(df: pd.DataFrame, chg: np.ndarray, target_share: float,
                         current_revenue: float) -> dict:
    current = df["current_tax"].to_numpy(dtype=float)
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


def _resolve_at_land_share(df: pd.DataFrame, target_share: float,
                           ratio: float, current_revenue: float) -> dict:
    """Re-solve the split-rate model with the aggregate land share tilted to
    `target_share`, holding total base and revenue fixed. Uniform per-parcel
    scaling preserves the relative structure of land vs improvement values."""
    chg = _tilted_change(df, target_share, ratio, current_revenue)
    return _sensitivity_summary(df, chg, target_share, current_revenue)


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
    "kind", "members", "coverage",
    "by_income_quintile_within", "by_income_quintile_within_coverage_pct",
}
HEADLINE_KEYS = {
    "parcels_modeled", "tax_base_eur", "land_base_eur", "improvement_base_eur",
    "land_share_pct", "built_at_cap_pct", "neutral_levy_eur", "gross_shifted_eur",
    "net_shifted_eur", "gross_pct_of_levy", "net_pct_of_levy", "gross_bps_of_base",
    "currency",
}
MEMBER_KEYS = {
    "commune_key", "name", "insee", "parcels_modeled", "neutral_levy_eur",
    "land_share_pct", "gross_pct_of_levy", "share_paying_more_pct",
}
PARCEL_ID_RE = re.compile(r"\b\d[\dAB]\d{3}[0-9]{3}[0-9A-Z]{2}\d{4}\b")
IRIS_CODE_RE = re.compile(r'"\d[\dAB]\d{7}"')
FORBIDDEN_TOKENS = ("std_geoid", "minority_pct", "black_pct", "_usd", "$")


def assert_aggregate_only(payload: dict) -> None:
    """Shape guard: only aggregate keys, bounded lists, no US/per-parcel leakage."""
    extra = set(payload) - ALLOWED_TOP_KEYS
    assert not extra, f"unexpected top-level keys (possible per-parcel leak): {extra}"
    extra_h = set(payload.get("headline") or {}) - HEADLINE_KEYS
    assert not extra_h, f"unexpected headline keys: {extra_h}"
    assert len(payload.get("by_improvement_ratio") or []) <= 5
    assert len(payload.get("by_category") or []) <= 10
    # territory member rows are per-COMMUNE aggregates (never per-parcel)
    for m in payload.get("members") or []:
        assert set(m) <= MEMBER_KEYS, f"unexpected member keys: {set(m) - MEMBER_KEYS}"
    for k in ("by_income_quintile", "by_income_quintile_within"):
        if payload.get(k) is not None:
            assert len(payload[k]) <= 5
    blob = json.dumps(payload, ensure_ascii=False)
    for tok in FORBIDDEN_TOKENS:
        assert tok not in blob, f"forbidden token {tok!r} leaked into payload"
    # value-level guard: no cadastral parcel id (14 chars, e.g. 75101000AB0002)
    # or 9-digit IRIS code may appear anywhere, whatever the key is called
    assert not PARCEL_ID_RE.search(blob), "a parcel id leaked into payload"
    assert not IRIS_CODE_RE.search(blob), "an IRIS code leaked into payload"


def build_commune_payload(commune_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    df = load_parcels(commune_key, out_dir)
    return {
        "commune_key": commune_key,
        "kind": "commune",
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
            "exempt_public_parcels": df.attrs.get("exempt_parcels", 0),
            "note": ("Agrégats uniquement — imputations honnêtes au niveau "
                     "catégorie/quintile, jamais à la parcelle."),
        },
        "currency": "EUR",
    }


def load_territory(territory_key: str, out_dir: str = "output"):
    """Stack the member communes' standard exports for a territory.

    Returns (frame, members_present, members_missing). Each row keeps its
    commune key in `_commune` so per-commune re-solves stay possible. A member
    with no output is reported as missing — never imputed.
    """
    from config import TERRITORIES
    frames, present, missing, n_exempt = [], [], [], 0
    for key in TERRITORIES[territory_key]["members"]:
        try:
            df = load_parcels(key, out_dir)
        except FileNotFoundError:
            missing.append(key)
            continue
        frames.append(df.assign(_commune=key))
        present.append(key)
        n_exempt += df.attrs.get("exempt_parcels", 0)
    if not frames:
        raise FileNotFoundError(f"no member outputs for territory {territory_key}")
    out = pd.concat(frames, ignore_index=True)
    out.attrs["exempt_parcels"] = n_exempt
    return out, present, missing


def build_territory_sensitivity(df: pd.DataFrame, ratio: float,
                                delta_pt: float = 10.0) -> dict:
    """±10 pt band for a territory, honouring per-commune revenue neutrality.

    Each member commune keeps its own levy, so the tilt is applied and re-solved
    commune by commune (each tilted by ±delta around its own land share), then
    the per-parcel changes are pooled for the summary. A single pooled solve
    would silently model a metropolitan tax instead.
    """
    d = delta_pt / 100.0
    legs = {"base": [], "low": [], "high": []}
    tilted_land = {"base": 0.0, "low": 0.0, "high": 0.0}
    kept = []
    for _key, sub in df.groupby("_commune", sort=False):
        land = float(sub["taxable_land_value"].sum())
        base = land + float(sub["taxable_improvement_value"].sum())
        s = land / base if base else 0.0
        if not 0.0 < s < 1.0:
            continue          # degenerate member (all-land / all-building): skipped
        rev = float(sub["current_tax"].sum())
        for leg, tgt in (("base", s), ("low", min(0.99, max(0.01, s - d))),
                         ("high", min(0.99, max(0.01, s + d)))):
            legs[leg].append(_tilted_change(sub, tgt, ratio, rev))
            tilted_land[leg] += tgt * base
        kept.append(sub)
    if not kept:
        raise ValueError("no member commune has a non-degenerate land share")
    pooled = pd.concat(kept, ignore_index=True)
    rev = float(pooled["current_tax"].sum())
    total_base = float((pooled["taxable_land_value"]
                        + pooled["taxable_improvement_value"]).sum())
    # the territory's actual tilted land share (exact even if a member clamps)
    targets = {leg: v / total_base for leg, v in tilted_land.items()}
    return {
        "delta_pt": delta_pt,
        **{leg: _sensitivity_summary(pooled, np.concatenate(v), targets[leg], rev)
           for leg, v in legs.items()},
    }


def _member_row(key: str, sub: pd.DataFrame) -> dict:
    from config import COMMUNES
    cfg = COMMUNES[key]
    h = build_headline(sub)
    return {
        "commune_key": key, "name": cfg.name, "insee": cfg.insee_code,
        "parcels_modeled": h["parcels_modeled"],
        "neutral_levy_eur": h["neutral_levy_eur"],
        "land_share_pct": h["land_share_pct"],
        "gross_pct_of_levy": h["gross_pct_of_levy"],
        "share_paying_more_pct": _pct(int((sub["tax_change"] > 0).sum()), len(sub)),
    }


def build_by_income_quintile_within(df: pd.DataFrame):
    """Income quintiles ranked WITHIN each member commune, then pooled.

    The ring-wide ranking (build_by_income_quintile) mixes the reform's effect
    with differences BETWEEN communes — each keeps its own levy, so a poor
    commune next to a rich one can make the pooled gradient look regressive
    when it is progressive inside every commune (Lyon extra-muros does exactly
    this). This variant isolates the within-jurisdiction incidence. Communes
    whose IRIS incomes cannot form 5 bins are excluded and the share of parcels
    covered is reported. Returns (rows, coverage_pct) or (None, coverage_pct).
    """
    if "median_income" not in df.columns:
        return None, 0.0
    parts = []
    for _key, sub in df[df["median_income"].notna()].groupby("_commune"):
        try:
            q = pd.qcut(sub["median_income"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
        except ValueError:
            continue
        if q.nunique() == 5:
            parts.append(sub.assign(_q=q))
    coverage = _pct(sum(len(p) for p in parts), len(df)) or 0.0
    if not parts:
        return None, coverage
    d = pd.concat(parts, ignore_index=True)
    out = []
    for q in [1, 2, 3, 4, 5]:
        sub = d[d["_q"] == q]
        rsub = sub[sub["property_category"].isin(FR_RESIDENTIAL)]
        sp = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        rp = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        out.append({
            "quintile": q,
            "median_income_eur": round(float(sub["median_income"].median()), 0),
            "median_change_pct": round(float(sp.median()), 1) if len(sp) else None,
            "median_change_pct_residential": round(float(rp.median()), 1) if len(rp) else None,
            "parcels": int(len(sub)),
        })
    return out, coverage


def build_territory_payload(territory_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES, TERRITORIES, TERRITORY_COST_EUR_M2
    t = TERRITORIES[territory_key]
    df, present, missing = load_territory(territory_key, out_dir)
    ratios = {COMMUNES[k].split_rate_ratio for k in present}
    if len(ratios) != 1:
        raise ValueError(f"{territory_key}: members use different split ratios {ratios}")
    ratio = ratios.pop()
    members = [_member_row(k, sub) for k, sub in df.groupby("_commune", sort=False)]
    members.sort(key=lambda m: m["neutral_levy_eur"], reverse=True)
    within, within_cov = build_by_income_quintile_within(df)
    return {
        "commune_key": territory_key,
        "kind": "territory",
        "insee": None,
        "name": t["name"],
        "departement": t["departement"],
        "reference_year": COMMUNES[present[0]].reference_year,
        "model_type": f"split_rate:{ratio}",
        "headline": build_headline(df),
        "headline_sensitivity": build_territory_sensitivity(df, ratio),
        "by_category": build_by_category(df),
        # metro-wide quintiles: IRIS incomes ranked across the whole ring
        "by_income_quintile": build_by_income_quintile(df),
        # same, ranked inside each commune (isolates within-jurisdiction incidence)
        "by_income_quintile_within": within,
        "by_income_quintile_within_coverage_pct": within_cov,
        "by_improvement_ratio": build_buckets(df),
        "members": members,
        "coverage": {
            "members_total": len(t["members"]),
            "members_modeled": len(present),
            "members_missing": missing,
        },
        "provenance": {
            "construction_cost_eur_m2": TERRITORY_COST_EUR_M2.get(territory_key),
            "exempt_public_parcels": df.attrs.get("exempt_parcels", 0),
            "land_share_bounds": list(COMMUNES[present[0]].land_share_bounds),
            "note": ("Agrégat de communes modélisées chacune à recettes "
                     "constantes sur son propre produit de TFPB (pas de taux "
                     "métropolitain unique). Agrégats uniquement."),
        },
        "currency": "EUR",
    }


def export_territory(territory_key: str, out_dir: str = "output",
                     data_dir: str = "site/public/data") -> Path:
    return _write_commune_json(build_territory_payload(territory_key, out_dir), data_dir)


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
    # De-duplicated contribution to the site-wide totals: a territory's members
    # that are also published on their own (Montreuil, Villeurbanne) are
    # counted once, via their own entry.
    if payload.get("kind") == "territory":
        from config import SITE_COMMUNES
        uniq = [m for m in payload["members"] if m["commune_key"] not in SITE_COMMUNES]
        n_unique, parcels_unique = len(uniq), sum(m["parcels_modeled"] for m in uniq)
    else:
        n_unique, parcels_unique = 1, h["parcels_modeled"]
    return {
        "n_communes_unique": n_unique, "parcels_unique": parcels_unique,
        "commune_key": payload["commune_key"], "name": payload["name"],
        "kind": payload.get("kind", "commune"),
        "insee": payload["insee"], "departement": payload["departement"],
        "parcels_modeled": h["parcels_modeled"],
        "land_share_pct": h["land_share_pct"],
        "gross_pct_of_levy": h["gross_pct_of_levy"],
    }


def export_commune(commune_key: str, out_dir: str = "output",
                   data_dir: str = "site/public/data") -> Path:
    return _write_commune_json(build_commune_payload(commune_key, out_dir), data_dir)


def rebuild_index(data_dir: str = "site/public/data") -> dict:
    """Rebuild index.json from the payload JSONs already in data_dir.

    Lets new communes/territories be exported one by one without regenerating
    — and so silently changing — already-published payloads (whose source
    data may have moved on since they were modelled). Order: site communes,
    then territories, as configured.
    """
    from config import SITE_COMMUNES, TERRITORIES
    index = []
    for key in list(SITE_COMMUNES) + list(TERRITORIES):
        path = Path(data_dir) / f"{key}.json"
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert_aggregate_only(payload)
        index.append(_index_entry(payload))
    (Path(data_dir) / "index.json").write_text(
        json.dumps({"communes": index, "currency": "EUR"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return {"indexed": [c["commune_key"] for c in index]}


def export_all(out_dir: str = "output", data_dir: str = "site/public/data") -> dict:
    from config import COMMUNES, SITE_COMMUNES, TERRITORIES
    index = []
    for key in SITE_COMMUNES:
        if not (Path(out_dir) / f"{_slug(COMMUNES[key])}.csv").exists():
            continue
        payload = build_commune_payload(key, out_dir)   # load the CSV exactly once
        _write_commune_json(payload, data_dir)
        index.append(_index_entry(payload))
    for key in TERRITORIES:
        try:
            payload = build_territory_payload(key, out_dir)
        except FileNotFoundError:
            continue
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
    ap.add_argument("--index-only", action="store_true",
                    help="only rebuild index.json from the payloads already in --data-dir")
    a = ap.parse_args()
    if a.index_only:
        print(rebuild_index(a.data_dir))
    elif a.commune:
        from config import TERRITORIES
        fn = export_territory if a.commune in TERRITORIES else export_commune
        print("wrote", fn(a.commune, a.out_dir, a.data_dir))
    else:
        print(export_all(a.out_dir, a.data_dir))
