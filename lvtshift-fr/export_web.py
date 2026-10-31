"""Aggregate-only JSON exporter for the « Pour une terre productive » site.

Reads the authoritative per-parcel standard export (output/<slug>.csv) and emits
aggregates by category, income quintile and improvement-ratio bucket, plus a
±10 pt land-share sensitivity band re-solved through the unmodified upstream
solver. Never emits per-parcel rows. See docs/superpowers/specs/
2026-06-24-advocacy-site-design.md §5.
"""

import json
import math
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
    df = _attach_dwellings(df, path, commune_key)
    n_exempt = 0
    if "is_fully_exempt" in df.columns:
        exempt = df["is_fully_exempt"].fillna(False).astype(bool)
        n_exempt = int(exempt.sum())
        df = df[~exempt].copy()
    # count only (never which parcels): disclosed in the payload provenance
    df.attrs["exempt_parcels"] = n_exempt
    # unbuilt farmland stays on today's TFPNB (run_pipeline): outside the shares
    # (exports from before the exclusion have no column: nothing was excluded)
    n_farm = 0
    if "is_farmland_excluded" in df.columns:
        farm = _strict_flag(df["is_farmland_excluded"], path.name)
        paying = [c for c in ("current_tax", "new_tax", "taxable_improvement_value")
                  if c in df.columns]
        if paying and (df.loc[farm, paying].abs().sum(axis=1) > 0).any():
            raise ValueError(f"{path.name}: rows flagged as excluded farmland pay tax "
                             f"or carry a building")
        n_farm = int(farm.sum())
        df = df[~farm].copy()
    df.attrs["farmland_excluded_parcels"] = n_farm
    return df


def _strict_flag(col: pd.Series, where: str) -> pd.Series:
    """A boolean CSV column read back strictly: True/False or 1/0, nothing else
    (``astype(bool)`` would turn the string "False" into True)."""
    if col.dtype == bool:
        return col
    mapping = {True: True, False: False, 1: True, 0: False,
               "True": True, "False": False, "1": True, "0": False}
    out = col.map(mapping)          # anything unmapped, NaN included, becomes NaN
    if out.isna().any():
        raise ValueError(f"{where}: flag column {col.name!r} has values other than "
                         f"True/False: {sorted(set(map(str, col[out.isna()])))[:5]}")
    return out.astype(bool)


def _attach_dwellings(df: pd.DataFrame, path: Path, commune_key: str) -> pd.DataFrame:
    """Add n_dwellings from the run's households sidecar (run_pipeline).

    The sidecar repeats new_tax row by row; any mismatch means it belongs to a
    different run, which would silently attach dwellings to the wrong parcels,
    so it fails loudly. A missing sidecar (older run) leaves the household
    figures unset rather than guessed.
    """
    side_path = path.with_name(f"{path.stem}.households.csv")
    if not side_path.exists():
        return df
    import hashlib
    meta_path = path.with_name(f"{path.stem}.households.meta.json")
    meta = json.loads(meta_path.read_text("utf-8")) if meta_path.exists() else {}
    if meta.get("export_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError(
            f"{side_path.name} was not written with this {path.name}; "
            f"re-run `python run_commune.py {commune_key}`")
    side = pd.read_csv(side_path)
    if len(side) != len(df) or not np.allclose(
            side["new_tax"].to_numpy(float), df["new_tax"].to_numpy(float),
            rtol=1e-9, atol=0.01, equal_nan=True):
        raise ValueError(
            f"{side_path.name} does not match {path.name}; "
            f"re-run `python run_commune.py {commune_key}`")
    df = df.assign(n_dwellings=side["n_dwellings"].to_numpy(float))
    if "current_tax_low" in side.columns:
        low = side["current_tax_low"].to_numpy(float)
        cur = df["current_tax"].to_numpy(float)
        ok = (np.isfinite(low).all() and (low >= 0).all()
              # untaxed today (exempt, unbuilt) in one baseline = in both
              and ((low > 0) == (cur > 0)).all()
              and abs(low.sum() - cur.sum()) <= max(1.0, 1e-6 * abs(cur.sum())))
        if not ok:
            raise ValueError(f"{side_path.name}: lower-bound current tax is not a "
                             f"revenue-neutral, non-negative re-share of {path.name}")
        df = df.assign(current_tax_low=low)
    return df


def weighted_median(values, weights):
    """Median of values with each counted `weights` times (None if no weight).

    Non-finite values and non-positive weights are ignored; an exact 50/50
    split returns the lower value.
    """
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    ok = np.isfinite(v) & np.isfinite(w) & (w > 0)
    if not ok.any():
        return None
    v, w = v[ok], w[ok]
    order = np.argsort(v, kind="stable")
    v, w = v[order], w[order]
    cum = np.cumsum(w)
    return float(v[np.searchsorted(cum, cum[-1] / 2.0)])


# Disclosure control for the per-quintile group figures: a group must hold at
# least this many residential parcels, and no parcel more than this share of
# its dwellings, or its total and household figures are left unpublished.
MIN_GROUP_PARCELS = 11
MAX_DWELLING_SHARE = 0.5
# Income fifths are built from IRIS medians (Filosofi): with fewer than two
# distinct IRIS incomes per fifth, a "fifth" is one neighbourhood, so the
# breakdown is not published (Cahors, Figeac). Stated, not left to qcut.
MIN_IRIS_INCOMES = 10


def _small(n: int) -> bool:
    """A published group below MIN_GROUP_PARCELS keeps its count only."""
    return n < MIN_GROUP_PARCELS


def _quintile_row(q: int, sub: pd.DataFrame) -> dict:
    """One income group: the parcel medians, plus the group's total change and
    the typical household's change (residential parcels weighted by dwellings).

    A parcel median counts a 200-flat block once and a house once, so it can
    show most of a group paying more while the group as a whole pays less.
    """
    rsub = sub[sub["property_category"].isin(FR_RESIDENTIAL)]
    sp = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
    rp = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
    total = None
    if {"current_tax", "tax_change"} <= set(rsub.columns) and len(rsub) >= MIN_GROUP_PARCELS:
        chg = rsub["tax_change"].sum(min_count=1)
        cur = rsub["current_tax"].sum(min_count=1)
        if np.isfinite(chg) and np.isfinite(cur) and rsub["tax_change"].notna().all():
            total = _pct(float(chg), float(cur))
    hh_median, dwellings = None, None
    n = rsub["n_dwellings"] if "n_dwellings" in rsub.columns else None
    # every residential parcel must carry a count (a member commune without a
    # sidecar would otherwise drop out of the weights but not of the total)
    if n is not None and len(rsub) >= MIN_GROUP_PARCELS and n.notna().all() and n.sum() > 0:
        pct = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan)
        hh = weighted_median(pct, n)
        hh_median = None if hh is None else round(hh, 1)
        dwellings = int(round(float(n.sum())))
        # one building dominating the group would make its figures that
        # building's own: publish nothing household-level then
        if float(n.max()) > MAX_DWELLING_SHARE * float(n.sum()):
            hh_median, dwellings, total = None, None, None
    if _small(len(sub)):
        sp = sp.iloc[:0]
    if _small(len(rsub)):
        rp = rp.iloc[:0]
    return {
        "quintile": int(q),
        "median_income_eur": round(float(sub["median_income"].median()), 0),
        "median_change_pct": round(float(sp.median()), 1) if len(sp) else None,
        "median_change_pct_residential": round(float(rp.median()), 1) if len(rp) else None,
        "total_change_pct": total,
        "household_median_change_pct": hh_median,
        "parcels": int(len(sub)),
        "dwellings": dwellings,
    }


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


# Building-share bands: (key, label, lower, upper) on improvement / value;
# "vacant" is exactly 0. Bands too small to publish are merged with a
# neighbour (blanking alone would leave them recoverable by subtraction from
# the commune totals).
BUCKETS_SPEC = [
    ("vacant", "Terrain nu (0 %)", 0.0, 0.0),
    ("lt10", "Très sous-bâti (<10 %)", 0.0, 0.10),
    ("r10_25", "Sous-bâti (10–25 %)", 0.10, 0.25),
    ("r25_50", "Sous-bâti (25–50 %)", 0.25, 0.50),
    ("ge50", "Bâti (≥50 %)", 0.50, math.inf),
]


def _merged_label(lo: float, hi: float, has_vacant: bool) -> str:
    if math.isinf(hi):
        return f"Bâti (≥{lo * 100:.0f} %)"
    if lo == 0.0:
        return f"{'Nu ou sous-bâti' if has_vacant else 'Sous-bâti'} (<{hi * 100:.0f} %)"
    return f"Sous-bâti ({lo * 100:.0f}–{hi * 100:.0f} %)"


def _bucket_groups(ratio: pd.Series) -> list:
    """[(key, label, mask)] after merging every band under MIN_GROUP_PARCELS
    into its smaller neighbour, until none is left or one band remains."""
    groups = []
    for key, label, lo, hi in BUCKETS_SPEC:
        mask = (ratio == 0) if key == "vacant" else (ratio > 0) & (ratio >= lo) & (ratio < hi)
        groups.append({"keys": [key], "label": label, "lo": lo, "hi": hi, "mask": mask})
    while len(groups) > 1:
        sizes = [int(g["mask"].sum()) for g in groups]
        small = [i for i, n in enumerate(sizes) if 0 < n < MIN_GROUP_PARCELS]   # empty reveals nothing
        if not small:
            break
        i = min(small, key=lambda k: sizes[k])
        nbrs = [j for j in (i - 1, i + 1) if 0 <= j < len(groups)]
        j = min(nbrs, key=lambda k: sizes[k])
        a, b = sorted((i, j))
        g, h = groups[a], groups[b]
        keys = g["keys"] + h["keys"]
        groups[a:b + 1] = [{"keys": keys, "lo": g["lo"], "hi": h["hi"],
                            "mask": g["mask"] | h["mask"],
                            "label": _merged_label(g["lo"], h["hi"], "vacant" in keys)}]
    return [("+".join(g["keys"]), g["label"], g["mask"]) for g in groups]


def build_buckets(df: pd.DataFrame) -> list:
    base_series = df["taxable_land_value"] + df["taxable_improvement_value"]
    total_base = float(base_series.sum())
    total_gross = float(df["tax_change"].abs().sum())
    ratio = (df["taxable_improvement_value"] / base_series.replace(0, np.nan)).fillna(0.0)
    out = []
    for key, label, mask in _bucket_groups(ratio):
        sub = df[mask]
        n = int(mask.sum())
        val = float((sub["taxable_land_value"] + sub["taxable_improvement_value"]).sum())
        gross = float(sub["tax_change"].abs().sum())
        small = 0 < n < MIN_GROUP_PARCELS     # only if the whole commune is that small
        out.append({
            "bucket": key, "label": label, "parcels": n,
            # an imputed value, so to the thousand euros, not to the euro
            "value_eur": None if small else round(val, -3),
            "value_pct_of_base": None if small else _pct(val, total_base),
            "share_of_gross_change_pct": None if small else _pct(gross, total_gross),
        })
    return out


def build_by_category(df: pd.DataFrame) -> list:
    n = len(df)
    # categories too small to publish join "Other" (blanking alone would leave
    # their counts recoverable from the commune totals)
    sizes = df["property_category"].value_counts()
    tiny = [c for c, k in sizes.items() if _small(int(k)) and c != "Other"]
    if tiny:
        df = df.assign(property_category=df["property_category"].where(
            ~df["property_category"].isin(tiny), "Other"))
    out = []
    for cat, sub in df.groupby("property_category"):
        chg_pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        small = _small(len(sub))
        out.append({
            "category": cat,
            "label_fr": CATEGORY_LABELS_FR.get(cat, str(cat)),
            "parcels": int(len(sub)),
            "share_of_parcels_pct": _pct(len(sub), n),
            "median_change_pct": (round(float(chg_pct.median()), 1)
                                  if len(chg_pct) and not small else None),
            "median_change_eur": None if small else round(float(sub["tax_change"].median()), 0),
            "count_paying_more": None if small else int((sub["tax_change"] > 0).sum()),
            "share_paying_more_pct": (None if small else
                                      _pct(int((sub["tax_change"] > 0).sum()), len(sub))),
        })
    out.sort(key=lambda r: r["parcels"], reverse=True)
    return out


def build_by_income_quintile(df: pd.DataFrame):
    if "median_income" not in df.columns or df["median_income"].notna().sum() == 0:
        return None
    d = df[df["median_income"].notna()].copy()
    if d["median_income"].nunique() < MIN_IRIS_INCOMES:
        return None
    try:
        d["_q"] = pd.qcut(d["median_income"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    except ValueError:
        return None
    if d["_q"].nunique() < 5:
        return None
    return [_quintile_row(q, d[d["_q"] == q]) for q in [1, 2, 3, 4, 5]]


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


BAND_CATEGORY_KEYS = ("category", "median_change_pct", "median_change_eur",
                      "share_paying_more_pct")
QUINTILE_KEYS = {"quintile", "median_income_eur", "median_change_pct",
                 "median_change_pct_residential", "total_change_pct",
                 "household_median_change_pct", "parcels", "dwellings"}
BAND_QUINTILE_KEYS = ("quintile", "median_change_pct", "median_change_pct_residential",
                      "total_change_pct", "household_median_change_pct")


def _band_groups(df: pd.DataFrame, chg: np.ndarray, within: bool = False) -> dict:
    """The per-category and per-income-quintile figures of one sensitivity leg.

    Rebuilt with the same functions as the central figures (so quintile cut
    points and category sets are identical), with the leg's per-parcel change
    substituted. Only the band-relevant fields are kept, to keep payloads small.
    """
    current = df["current_tax"].to_numpy(dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = 100.0 * chg / current
    d = df.assign(tax_change=chg, tax_change_pct=pct)

    def slim(rows, keys):
        return None if rows is None else [{k: r[k] for k in keys} for r in rows]

    out = {
        "by_category": slim(build_by_category(d), BAND_CATEGORY_KEYS),
        "by_income_quintile": slim(build_by_income_quintile(d), BAND_QUINTILE_KEYS),
    }
    if within:
        rows, _cov = build_by_income_quintile_within(d)
        out["by_income_quintile_within"] = slim(rows, BAND_QUINTILE_KEYS)
    return out


def _sensitivity_summary(df: pd.DataFrame, chg: np.ndarray, target_share: float,
                         current_revenue: float, within: bool = False) -> dict:
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
        **_band_groups(df, chg, within=within),
    }


def _resolve_at_land_share(df: pd.DataFrame, target_share: float,
                           ratio: float, current_revenue: float) -> dict:
    """Re-solve the split-rate model with the aggregate land share tilted to
    `target_share`, holding total base and revenue fixed. Uniform per-parcel
    scaling preserves the relative structure of land vs improvement values."""
    chg = _tilted_change(df, target_share, ratio, current_revenue)
    return _sensitivity_summary(df, chg, target_share, current_revenue)


def build_baseline_sensitivity(df: pd.DataFrame, within: bool = False) -> dict | None:
    """Central vs lower-bound baseline (professional premises' share of today's
    tax at the raw CFE proxy). The LVT bills are identical; only today's tax,
    and so every change, differs. None when the run carries no lower bound."""
    if "current_tax_low" not in df.columns:
        return None
    missing = df["current_tax_low"].isna()
    if missing.any():
        who = sorted(set(df.loc[missing, "_commune"])) if "_commune" in df.columns else []
        raise ValueError(f"lower-bound current tax missing for {who or 'some parcels'}; "
                         f"re-run those communes")
    # no real lower bound (floor-area baseline, or identical shares): say
    # nothing rather than show two identical columns
    if np.allclose(df["current_tax_low"].to_numpy(float), df["current_tax"].to_numpy(float),
                   rtol=1e-9, atol=0.01):
        return None
    from config import BASELINE_MODEL as M
    revenue = float(df["current_tax"].sum())
    land = float(df["taxable_land_value"].sum())
    base = land + float(df["taxable_improvement_value"].sum())
    share = land / base if base else 0.0
    new = df["new_tax"].to_numpy(dtype=float)
    low = df.assign(current_tax=df["current_tax_low"])
    return {
        "pro_scale_central": M["pro_undercount_scale"],
        "pro_scale_low": M["pro_undercount_scale_low"],
        "central": _sensitivity_summary(
            df, new - df["current_tax"].to_numpy(dtype=float), share, revenue, within),
        "low": _sensitivity_summary(
            low, new - df["current_tax_low"].to_numpy(dtype=float), share, revenue, within),
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
    "kind", "members", "coverage",
    "by_income_quintile_within", "by_income_quintile_within_coverage_pct",
    "baseline_sensitivity",
}
HEADLINE_KEYS = {
    "parcels_modeled", "tax_base_eur", "land_base_eur", "improvement_base_eur",
    "land_share_pct", "built_at_cap_pct", "neutral_levy_eur", "gross_shifted_eur",
    "net_shifted_eur", "gross_pct_of_levy", "net_pct_of_levy", "gross_bps_of_base",
    "currency",
}
SENSITIVITY_LEG_KEYS = {
    "land_share_pct", "gross_pct_of_levy", "net_pct_of_levy",
    "median_change_pct_residential", "share_paying_more_pct",
    "by_category", "by_income_quintile", "by_income_quintile_within",
}
MEMBER_KEYS = {
    "commune_key", "name", "insee", "parcels_modeled", "neutral_levy_eur",
    "land_share_pct", "gross_pct_of_levy", "net_pct_of_levy", "share_paying_more_pct",
}
PARCEL_ID_RE = re.compile(r"\b\d[\dAB]\d{3}[0-9]{3}[0-9A-Z]{2}\d{4}\b")
IRIS_CODE_RE = re.compile(r'"\d[\dAB]\d{7}"')
FORBIDDEN_TOKENS = ("std_geoid", "minority_pct", "black_pct", "_usd", "$")


def _check_leg(g: dict, what: str) -> None:
    """A sensitivity leg: known keys, scalar headline fields, bounded lists of
    rows with known keys and scalar values only (a nested list or dict could
    smuggle per-parcel values)."""
    assert isinstance(g, dict), f"{what} leg must be an object"
    assert set(g) <= SENSITIVITY_LEG_KEYS, \
        f"unexpected {what} leg keys: {set(g) - SENSITIVITY_LEG_KEYS}"
    lists = {"by_category", "by_income_quintile", "by_income_quintile_within"}
    for k, v in g.items():
        if k not in lists:
            assert v is None or (isinstance(v, (int, float)) and not isinstance(v, bool)), \
                f"non-numeric {what} leg field {k}"
    assert len(g.get("by_category") or []) <= 10
    rows = [(r, BAND_CATEGORY_KEYS) for r in g.get("by_category") or []]
    for k in ("by_income_quintile", "by_income_quintile_within"):
        assert len(g.get(k) or []) <= 5
        rows += [(r, BAND_QUINTILE_KEYS) for r in g.get(k) or []]
    for r, keys in rows:
        assert isinstance(r, dict), f"{what} row must be an object"
        assert set(r) <= set(keys), f"unexpected {what} row keys: {set(r) - set(keys)}"
        assert all(v is None or isinstance(v, (str, int, float)) for v in r.values()), \
            f"non-scalar value in a {what} row"


# Fields a group below MIN_GROUP_PARCELS must leave empty (its count stays).
SMALL_GROUP_BLANK = {
    "by_improvement_ratio": ("value_eur", "value_pct_of_base", "share_of_gross_change_pct"),
    "by_category": ("median_change_pct", "median_change_eur", "count_paying_more",
                    "share_paying_more_pct"),
    "by_income_quintile": ("median_change_pct", "median_change_pct_residential",
                           "total_change_pct", "household_median_change_pct", "dwellings"),
}


def _check_small_groups(payload: dict) -> None:
    """Value guard: no figure for a published group of fewer than
    MIN_GROUP_PARCELS parcels, in the central rows or any sensitivity leg."""
    for k, blank in SMALL_GROUP_BLANK.items():
        keys = (k, "by_income_quintile_within") if k == "by_income_quintile" else (k,)
        for key in keys:
            for r in payload.get(key) or []:
                assert isinstance(r.get("parcels"), int), f"{key}: row without a parcel count"
                if r["parcels"] < MIN_GROUP_PARCELS:
                    # an empty group's zeros describe nobody
                    allowed = (None, 0) if r["parcels"] == 0 else (None,)
                    filled = [f for f in blank if r.get(f) not in allowed]
                    assert not filled, f"{key}: group of {r['parcels']} parcels publishes {filled}"
    # leg rows carry no count: match them to the central rows
    small = {r["category"] for r in payload.get("by_category") or []
             if r["parcels"] < MIN_GROUP_PARCELS}
    legs = [(payload.get("headline_sensitivity") or {}).get(x) for x in ("base", "low", "high")]
    legs += [(payload.get("baseline_sensitivity") or {}).get(x) for x in ("central", "low")]
    small_q = {k: {r["quintile"] for r in payload.get(k) or [] if r["parcels"] < MIN_GROUP_PARCELS}
               for k in ("by_income_quintile", "by_income_quintile_within")}
    for leg in legs:
        for r in (leg or {}).get("by_category") or []:
            if r.get("category") in small:
                filled = [f for f in BAND_CATEGORY_KEYS[1:] if r.get(f) is not None]
                assert not filled, f"sensitivity leg: small group {r['category']} publishes {filled}"
        for k, qs in small_q.items():
            for r in (leg or {}).get(k) or []:
                if r.get("quintile") in qs:
                    filled = [f for f in BAND_QUINTILE_KEYS[1:] if r.get(f) is not None]
                    assert not filled, f"sensitivity leg: small fifth {r['quintile']} publishes {filled}"


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
            for r in payload[k]:
                assert set(r) <= QUINTILE_KEYS, f"unexpected quintile keys: {set(r) - QUINTILE_KEYS}"
                assert all(v is None or isinstance(v, (str, int, float)) for v in r.values()), \
                    "non-scalar value in a quintile row"
    bs = payload.get("baseline_sensitivity")
    if bs is not None:
        assert isinstance(bs, dict) and \
            set(bs) <= {"pro_scale_central", "pro_scale_low", "central", "low"}, \
            f"unexpected baseline_sensitivity keys: {set(bs) if isinstance(bs, dict) else bs}"
        for k in ("pro_scale_central", "pro_scale_low"):
            v = bs.get(k)
            assert isinstance(v, (int, float)) and not isinstance(v, bool), f"{k} must be a number"
        for leg in ("central", "low"):
            _check_leg(bs.get(leg) or {}, "baseline")
    sens = payload.get("headline_sensitivity") or {}
    assert set(sens) <= {"delta_pt", "base", "low", "high"},         f"unexpected sensitivity keys: {set(sens) - {'delta_pt', 'base', 'low', 'high'}}"
    for leg in ("base", "low", "high"):
        _check_leg(sens.get(leg) or {}, "band")
    _check_small_groups(payload)
    blob = json.dumps(payload, ensure_ascii=False)
    for tok in FORBIDDEN_TOKENS:
        assert tok not in blob, f"forbidden token {tok!r} leaked into payload"
    # value-level guard: no cadastral parcel id (14 chars, e.g. 75101000AB0002)
    # or 9-digit IRIS code may appear anywhere, whatever the key is called
    assert not PARCEL_ID_RE.search(blob), "a parcel id leaked into payload"
    assert not IRIS_CODE_RE.search(blob), "an IRIS code leaked into payload"


def load_baseline(commune_key: str, out_dir: str = "output") -> dict:
    """How the run shared today's tax (run_pipeline sidecar): method, and the
    commune-level target and achieved shares by tax group. Older runs without
    the sidecar report the floor-area method. Scalars only."""
    from config import COMMUNES
    path = Path(out_dir) / f"{_slug(COMMUNES[commune_key])}.baseline.json"
    if not path.exists():
        return {"method": "floor_area"}
    rec = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rec, dict):
        raise ValueError(f"{path}: baseline sidecar must be an object")
    method = rec.get("method")
    if method not in ("calibrated", "floor_area"):
        raise ValueError(f"{path}: unknown baseline method {method!r}")

    def share(d, k):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        v = float(v)
        return round(v, 4) if math.isfinite(v) and 0 <= v <= 1 else None

    out = {"method": method}
    for k in ("industrial", "professional"):
        out[f"target_{k}_share"] = share(rec.get("targets"), k)
        out[f"achieved_{k}_share"] = share(rec.get("achieved"), k)
    # where industrial m² would pay less than professional m² the two groups
    # are one (warehouses taxed as professional premises): only their combined
    # share is meaningful, so report it as professional and say so
    merged = "industrial merged into professional" in str(rec.get("note", ""))
    out["industrial_merged_into_professional"] = merged
    if merged:
        for kind in ("target", "achieved"):
            i, p = out[f"{kind}_industrial_share"], out[f"{kind}_professional_share"]
            out[f"{kind}_professional_share"] = (round(i + p, 4)
                                                 if i is not None and p is not None else None)
            out[f"{kind}_industrial_share"] = None
    return out


def _territory_baseline(present: list, out_dir: str) -> dict:
    """'calibrated' only if every modelled member is; else 'mixed' or 'floor_area'."""
    n = sum(load_baseline(k, out_dir)["method"] == "calibrated" for k in present)
    method = ("calibrated" if n == len(present) else "floor_area" if n == 0 else "mixed")
    return {"method": method, "members_calibrated": n}


def build_commune_payload(commune_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    df = load_parcels(commune_key, out_dir)
    baseline = load_baseline(commune_key, out_dir)
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
        "baseline_sensitivity": build_baseline_sensitivity(df),
        "provenance": {
            "construction_cost_eur_m2": cfg.construction_cost_eur_m2,
            "house_cost_eur_m2": getattr(cfg, "house_cost_eur_m2", None),
            "activity_land_ratio": getattr(cfg, "activity_land_ratio", None),
            "current_tax_baseline": baseline,
            "land_share_bounds": list(cfg.land_share_bounds),
            "exempt_public_parcels": df.attrs.get("exempt_parcels", 0),
            "farmland_excluded_parcels": df.attrs.get("farmland_excluded_parcels", 0),
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
    frames, present, missing, n_exempt, n_farm = [], [], [], 0, 0
    for key in TERRITORIES[territory_key]["members"]:
        try:
            df = load_parcels(key, out_dir)
        except FileNotFoundError:
            missing.append(key)
            continue
        frames.append(df.assign(_commune=key))
        present.append(key)
        n_exempt += df.attrs.get("exempt_parcels", 0)
        n_farm += df.attrs.get("farmland_excluded_parcels", 0)
    if not frames:
        raise FileNotFoundError(f"no member outputs for territory {territory_key}")
    out = pd.concat(frames, ignore_index=True)
    out.attrs["exempt_parcels"] = n_exempt
    out.attrs["farmland_excluded_parcels"] = n_farm
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
        **{leg: _sensitivity_summary(pooled, np.concatenate(v), targets[leg], rev,
                                     within=True)
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
        "net_pct_of_levy": h["net_pct_of_levy"],
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
        if sub["median_income"].nunique() < MIN_IRIS_INCOMES:
            continue
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
    return [_quintile_row(q, d[d["_q"] == q]) for q in [1, 2, 3, 4, 5]], coverage


def build_territory_payload(territory_key: str, out_dir: str = "output") -> dict:
    from config import (COMMUNES, TERRITORIES, TERRITORY_ACTIVITY_LAND_RATIO,
                        TERRITORY_COST_EUR_M2, TERRITORY_HOUSE_COST_EUR_M2)
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
        "baseline_sensitivity": build_baseline_sensitivity(df, within=True),
        "members": members,
        "coverage": {
            "members_total": len(t["members"]),
            "members_modeled": len(present),
            "members_missing": missing,
        },
        "provenance": {
            "construction_cost_eur_m2": TERRITORY_COST_EUR_M2.get(territory_key),
            "house_cost_eur_m2": TERRITORY_HOUSE_COST_EUR_M2.get(territory_key),
            "activity_land_ratio": TERRITORY_ACTIVITY_LAND_RATIO.get(territory_key),
            "current_tax_baseline": _territory_baseline(present, out_dir),
            "exempt_public_parcels": df.attrs.get("exempt_parcels", 0),
            "farmland_excluded_parcels": df.attrs.get("farmland_excluded_parcels", 0),
            "land_share_bounds": list(COMMUNES[present[0]].land_share_bounds),
            "note": ("Agrégat de communes modélisées chacune à recettes "
                     "constantes sur son propre produit de TFPB (pas de taux "
                     "métropolitain unique). Les coûts indiqués sont ceux du "
                     "territoire ; les communes du panel qui en sont membres "
                     "(Montreuil, Villeurbanne) gardent les leurs. "
                     "Agrégats uniquement."),
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")
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
