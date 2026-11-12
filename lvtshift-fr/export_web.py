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
    "Condominium": "Petit immeuble (2–4 logements)",
    "Large Multi-Family (5+ units)": "Immeuble collectif (5+ logements)",
    "Commercial": "Commerce",
    "Industrial": "Industriel",
    "Vacant Land": "Terrain nu / non bâti",
    "Social Housing": "Logement social (bailleurs)",
    "Other": "Autre bâtiment",
    "other": "Autre bâtiment",
}
# Social Housing (run_pipeline.SOCIAL_CATEGORY) is not residential here: its
# change falls on the landlord, so it stays out of every household figure.
FR_RESIDENTIAL = {
    "Single Family Residential", "Condominium", "Large Multi-Family (5+ units)",
}
SOCIAL_CATEGORY = "Social Housing"
# The Social Housing category, and the social housing counts in the
# provenance, are published only where at least this many landlords hold its
# parcels and none carries more than MAX_LANDLORD_SHARE of its tax, today or
# under the reform: otherwise a figure would describe one or two named
# businesses (RPLS diffusion rules: no statistic identifying a landlord; the
# two rules are those of French business statistics' secrecy). Otherwise the
# category joins "Other".
MIN_SOCIAL_LANDLORDS = 3
MAX_LANDLORD_SHARE = 0.85


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
    # step 1 keeps the industrial and professional groups only on the
    # calibrated baseline; on the plain floor-area one everything moves, which
    # the site does not claim: no steps then (a territory member without them
    # blanks the territory's steps, _steps)
    if "revalued_tax" in df.columns and not _revaluation(commune_key, out_dir).get("groups_kept"):
        df = df.assign(revalued_tax=np.nan)
    # count only (never which parcels): disclosed in the payload provenance
    df.attrs["exempt_parcels"] = n_exempt
    # unbuilt farmland stays on today's TFPNB (run_pipeline): outside the shares
    # (exports from before the exclusion have no column: nothing was excluded)
    n_farm = 0
    if "is_farmland_excluded" in df.columns:
        farm = _strict_flag(df["is_farmland_excluded"], path.name)
        paying = [c for c in ("current_tax", "new_tax", "taxable_improvement_value")
                  + STEP_TAX_COLS if c in df.columns]
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
    # (new_tax_kept, written by runs of 2026-11-11 only, is never read: with
    # the reform's bills it gave away the tax on exempt social housing)
    for col in [c for c in STEP_TAX_COLS if c in side.columns]:
        v = side[col].to_numpy(float)
        cur = df["current_tax"].to_numpy(float)
        if not (np.isfinite(v).all() and (v >= -0.01).all()
                and abs(v.sum() - cur.sum()) <= max(1.0, 1e-6 * abs(cur.sum()))):
            raise ValueError(f"{side_path.name}: {col} is not a revenue-neutral, "
                             f"non-negative re-share of {path.name}")
        df = df.assign(**{col: np.clip(v, 0.0, None)})
    if "residual_at_cap" in side.columns:
        df = df.assign(residual_at_cap=_strict_flag(side["residual_at_cap"],
                                                    side_path.name).to_numpy())
    if "landlord_key" in side.columns:      # hashed label: for counting landlords only
        keys = side["landlord_key"].fillna("").astype(str).to_numpy()
        df = df.assign(landlord_key=keys)
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
# The share was 0.5 until November 2026: a dwelling-weighted median lands on a
# building with 45 % of the dwellings unless 91 % of the rest sit on one side,
# which would publish that building's own % and € change (security review,
# 2026-11-03). At 0.1 nothing published at the time was blanked (largest
# building: 6.4 % of a category's dwellings, 5.2 % of an income fifth's).
MIN_GROUP_PARCELS = 11
MAX_DWELLING_SHARE = 0.1
# A category's total change is published only if no parcel carries more than
# this share of the category's tax, today or under the reform: otherwise the
# total would be close to that one parcel's own change.
MAX_PARCEL_TAX_SHARE = 0.1
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
    total, steps = None, dict(NO_STEPS)
    if {"current_tax", "tax_change"} <= set(rsub.columns) and len(rsub) >= MIN_GROUP_PARCELS:
        chg = rsub["tax_change"].sum(min_count=1)
        cur = rsub["current_tax"].sum(min_count=1)
        if np.isfinite(chg) and np.isfinite(cur) and rsub["tax_change"].notna().all():
            total = _pct(float(chg), float(cur))
            dominated = any(
                float(rsub[c].astype(float).sum()) > 0
                and float(rsub[c].astype(float).max())
                > MAX_PARCEL_TAX_SHARE * float(rsub[c].astype(float).sum())
                for c in ("current_tax", "new_tax") + STEP_TAX_COLS if c in rsub.columns)
            if total is not None and not dominated:
                steps = _steps(rsub)
    hh_median, dwellings = None, None
    n = rsub["n_dwellings"] if "n_dwellings" in rsub.columns else None
    # every residential parcel must carry a count (a member commune without a
    # sidecar would otherwise drop out of the weights but not of the total)
    # parcels with no dwelling carry no weight: they must not make up the floor
    if (n is not None and n.notna().all() and n.sum() > 0
            and int((n > 0).sum()) >= MIN_GROUP_PARCELS):
        pct = rsub["tax_change_pct"].replace([np.inf, -np.inf], np.nan)
        hh = weighted_median(pct, n)
        hh_median = None if hh is None else round(hh, 1)
        dwellings = int(round(float(n.sum())))
        # one building dominating the group would make its figures that
        # building's own: publish nothing household-level then
        if float(n.max()) > MAX_DWELLING_SHARE * float(n.sum()):
            hh_median, dwellings, total = None, None, None
            steps = dict(NO_STEPS)
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
        **steps,
        "household_median_change_pct": hh_median,
        "parcels": int(len(sub)),
        "dwellings": dwellings,
    }


def _pct(num: float, den: float, ndigits: int = 1):
    return round(100.0 * num / den, ndigits) if den else None


def built_at_cap_pct(df: pd.DataFrame, cap: float = LAND_SHARE_CAP):
    """% of built parcels whose residual land share sits at the upper clip.
    When most parcels are there, the aggregate land share is set by the bound,
    not measured, and the site must say so. Runs with the households sidecar's
    `residual_at_cap` flag count the clip on the residual, which forms each
    IRIS's land total; under site value a parcel's own share is not clipped and
    may exceed the bound. Older runs fall back to the parcel's share."""
    land = df["taxable_land_value"]
    imp = df["taxable_improvement_value"]
    built = imp > 0
    # too few built parcels and the % would describe individual parcels
    if built.sum() < MIN_BUILT_FOR_CAP_PCT:
        return None
    if "residual_at_cap" in df.columns:
        return _pct(int(df.loc[built, "residual_at_cap"].sum()), int(built.sum()))
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


DWELLING_FIELDS = ("median_change_eur_per_dwelling", "household_median_change_pct",
                   "share_dwellings_paying_more_pct", "dwellings")


def _per_dwelling(sub: pd.DataFrame) -> dict:
    """A residential category's figures per dwelling rather than per parcel,
    each parcel weighted by its dwellings:
      * median_change_eur_per_dwelling: the typical household's change in euros
        (the parcel's change shared over its dwellings);
      * household_median_change_pct: the typical household's change in %;
      * share_dwellings_paying_more_pct: % of dwellings in parcels paying more;
      * dwellings: the count.
    A parcel figure counts a 200-flat block once, like a house (Lyon: +800 € per
    block against +267 € per house), so the site shows these beside it.

    Same disclosure rule as the income groups: every parcel must carry a count,
    the group must reach MIN_GROUP_PARCELS, and no parcel may hold more than
    MAX_DWELLING_SHARE of its dwellings. Otherwise every field is None.
    """
    none = dict.fromkeys(DWELLING_FIELDS)
    if "n_dwellings" not in sub.columns or len(sub) < MIN_GROUP_PARCELS:
        return none
    if not sub["property_category"].isin(FR_RESIDENTIAL).all():
        return none
    n = sub["n_dwellings"]
    if not n.notna().all() or n.sum() <= 0 or float(n.max()) > MAX_DWELLING_SHARE * float(n.sum()):
        return none
    if int((n > 0).sum()) < MIN_GROUP_PARCELS:   # empty parcels make up no floor
        return none
    per = sub["tax_change"] / n.where(n > 0)
    med = weighted_median(per, n)
    pct = weighted_median(sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan), n)
    more = float(n[sub["tax_change"] > 0].sum())
    return {
        "median_change_eur_per_dwelling": None if med is None else round(med, 0),
        "household_median_change_pct": None if pct is None else round(pct, 1),
        "share_dwellings_paying_more_pct": _pct(more, float(n.sum())),
        "dwellings": int(round(float(n.sum()))),
    }


# The decomposition's intermediate bill (run_pipeline, METHODOLOGY §3.6):
# today's tax with housing at market values. The pipeline's second one, the
# TVTN with today's social housing exemptions, is never published: between
# it and the reform every unexempt bill scales by one factor, which a row of
# houses gives away, and with the published levy that factor yields the tax
# on exempt social housing, one landlord's or one parcel's in places
# (security review, 2026-11-11). Step 2 therefore includes the end of the
# exemptions.
STEP_TAX_COLS = ("revalued_tax",)
STEP_KEYS = ("step_revaluation_pct", "step_land_pct")
NO_STEPS = dict.fromkeys(STEP_KEYS)
# With a withheld row, at least this many rows must publish steps. A withheld
# row with no housing floor has a step 1 of exactly 0, and its tax today is
# about the published unbuilt-tax amount (an industrial row's, about its
# published group share); with the published levy, two rows close the
# equations (independent review, 2026-11-12), and with three, bounds from
# non-negative taxes were still tight in 0.4 % of test groupings, none with
# four (security review, 2026-11-12).
MIN_STEP_ROWS_BESIDE_WITHHELD = 4


def _steps_disclosable(rows: list) -> bool:
    """May these category rows publish steps? Yes when no row is withheld (a
    row with neither a % nor a € total), or at least
    MIN_STEP_ROWS_BESIDE_WITHHELD rows publish them. A row in euros (untaxed
    today) has no weight in the equations and is not withheld."""
    withheld = any(r.get("total_change_pct") is None and r.get("total_change_eur") is None
                   for r in rows)
    shown = sum(r.get("step_revaluation_pct") is not None for r in rows)
    return not withheld or shown >= MIN_STEP_ROWS_BESIDE_WITHHELD
# a step beyond this (in % of today's tax) is a group almost untaxed today
STEP_MAX_PCT = 1_000_000


def _steps(sub: pd.DataFrame) -> dict:
    """A group's change split into two steps, each in % of the group's tax
    today, so they add up to its total change (to rounding): housing brought
    to market values, then the move to the TVTN (end of the social housing
    exemptions included). Group totals, not medians, because only totals add
    up. Empty for an older run, a member without the column, a group untaxed
    today, or a step out of bounds."""
    cols = ("current_tax",) + STEP_TAX_COLS + ("new_tax",)
    if not set(cols) <= set(sub.columns):
        return dict(NO_STEPS)
    v = sub[list(cols)].astype(float)
    # a territory member from an older run has blanks, which sums would skip
    if not np.isfinite(v.to_numpy()).all():
        return dict(NO_STEPS)
    tot = v.sum().tolist()
    if not tot[0] > 0:
        return dict(NO_STEPS)
    out = {k: _pct(tot[i + 1] - tot[i], tot[0]) for i, k in enumerate(STEP_KEYS)}
    if any(x is None or not abs(x) < STEP_MAX_PCT for x in out.values()):
        return dict(NO_STEPS)
    return out


def _category_total(sub: pd.DataFrame) -> dict:
    """A category's total change: the sum of its parcels' changes, in % of
    today's tax, or in euros (rounded to the thousand) only where today's tax
    is 0 (vacant land) and a % is undefined. The median shows the typical
    parcel; the total shows where the levy goes (La Rochelle: houses −5.4 % at
    the median, +14.7 % in total, because a minority on large plots pay much
    more).

    Never both: the reform is revenue-neutral, so euro totals of every
    category sum to zero and a withheld one would be the others' sum, negated
    (security review, 2026-11-04). A % alone gives nothing to subtract, since
    no category's tax today is published.

    Withheld (None) for a group below MIN_GROUP_PARCELS or when one parcel
    carries more than MAX_PARCEL_TAX_SHARE of the category's tax today or
    under the reform.
    """
    none = {"total_change_pct": None, "total_change_eur": None, **NO_STEPS}
    if _small(len(sub)) or not {"current_tax", "new_tax", "tax_change"} <= set(sub.columns):
        return none
    cur, new = sub["current_tax"].astype(float), sub["new_tax"].astype(float)
    if not (np.isfinite(cur).all() and np.isfinite(new).all()):
        return none
    # one parcel dominating any of the bills would make the figures its own
    for col in [cur, new] + [sub[c].astype(float) for c in STEP_TAX_COLS if c in sub.columns]:
        tot = float(col.sum())
        if tot > 0 and float(col.max()) > MAX_PARCEL_TAX_SHARE * tot:
            return none
    chg = float(new.sum() - cur.sum())
    if cur.sum() > 0:
        return {"total_change_pct": _pct(chg, float(cur.sum())), "total_change_eur": None,
                **_steps(sub)}
    return {"total_change_pct": None, "total_change_eur": round(chg, -3), **NO_STEPS}


def social_landlords(df: pd.DataFrame) -> int:
    """Distinct landlords behind the Social Housing parcels (0 without keys)."""
    if "landlord_key" not in df.columns:
        return 0
    keys = df.loc[df["property_category"] == SOCIAL_CATEGORY, "landlord_key"]
    return int(keys[keys.fillna("").astype(str) != ""].nunique())


# Every tax the dominance test reads: today's under both baselines (in a
# baseline leg, current_tax is the variant and current_tax_central the
# central one) and the reform's, so every leg takes the same decision.
DOMINANCE_TAX_COLS = ("current_tax", "current_tax_low", "current_tax_central", "new_tax",
                      "revalued_tax")


def social_disclosable(df: pd.DataFrame) -> bool:
    """May the Social Housing figures be published? At least
    MIN_SOCIAL_LANDLORDS landlords, none holding more than MAX_LANDLORD_SHARE
    of the category's tax today (under either baseline) or under the reform
    (parcels of unknown landlord count in the total, never as a landlord)."""
    if social_landlords(df) < MIN_SOCIAL_LANDLORDS:
        return False
    sub = df[df["property_category"] == SOCIAL_CATEGORY]
    key = sub["landlord_key"].fillna("").astype(str)
    for col in DOMINANCE_TAX_COLS:
        if col not in sub.columns:
            continue
        tax = sub[col].astype(float)
        tot = float(tax.sum())
        if tot > 0 and float(tax[key != ""].groupby(key[key != ""]).sum().max()) \
                > MAX_LANDLORD_SHARE * tot:
            return False
    return True


def _median_change_pct(sub: pd.DataFrame):
    """Median % change, a parcel that pays nothing today counting as a rise
    (or a fall) of unbounded size rather than being left out: social housing
    exempt today all goes from 0 € to a land tax. None when the median itself
    falls on such a parcel (vacant land) or nothing is defined."""
    pct = sub["tax_change_pct"].replace([np.inf, -np.inf], np.nan).astype(float)
    if {"current_tax", "tax_change"} <= set(sub.columns):
        zero = sub["current_tax"].astype(float) <= 0
        chg = sub["tax_change"].astype(float)
        pct = pct.mask(zero & (chg > 0), np.inf).mask(zero & (chg < 0), -np.inf) \
                 .mask(zero & (chg == 0), 0.0)
    pct = pct.dropna()
    if not len(pct):
        return None
    med = float(np.median(pct.to_numpy()))
    return round(med, 1) if math.isfinite(med) else None


def build_by_category(df: pd.DataFrame) -> list:
    n = len(df)
    # Social Housing that would describe one or two landlords: into "Other"
    if (df["property_category"] == SOCIAL_CATEGORY).any() and not social_disclosable(df):
        df = df.assign(property_category=df["property_category"].replace(
            SOCIAL_CATEGORY, "Other"))
    # categories too small to publish join "Other" (blanking alone would leave
    # their counts recoverable from the commune totals)
    sizes = df["property_category"].value_counts()
    tiny = [c for c, k in sizes.items() if _small(int(k)) and c != "Other"]
    if tiny:
        df = df.assign(property_category=df["property_category"].where(
            ~df["property_category"].isin(tiny), "Other"))
    out = []
    for cat, sub in df.groupby("property_category"):
        small = _small(len(sub))
        med_pct = _median_change_pct(sub)
        out.append({
            "category": cat,
            "label_fr": CATEGORY_LABELS_FR.get(cat, str(cat)),
            "parcels": int(len(sub)),
            "share_of_parcels_pct": _pct(len(sub), n),
            "median_change_pct": None if small else med_pct,
            "median_change_eur": None if small else round(float(sub["tax_change"].median()), 0),
            "count_paying_more": None if small else int((sub["tax_change"] > 0).sum()),
            "share_paying_more_pct": (None if small else
                                      _pct(int((sub["tax_change"] > 0).sum()), len(sub))),
            **_category_total(sub),
            # residential only; None for other categories and older runs
            **_per_dwelling(sub),
        })
    # a withheld row whose step 1 is known to be 0 (no housing floor: vacant
    # land) next to a single published one would be recoverable from the
    # revenue-neutral equation: with a withheld row, at least two must publish
    # (security review, 2026-11-12)
    if not _steps_disclosable(out):
        for r in out:
            r.update(NO_STEPS)
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
                 "household_median_change_pct", "parcels", "dwellings", *STEP_KEYS}
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


LOW_SOURCES = ("th2017", "cfe_raw")


def build_baseline_sensitivity(df: pd.DataFrame, within: bool = False,
                               low_source: str = "cfe_raw") -> dict | None:
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
    # the central baseline rides along, so the leg folds what the central rows fold
    low = df.assign(current_tax=df["current_tax_low"], current_tax_central=df["current_tax"])
    return {
        "pro_scale_central": M["pro_undercount_scale"],
        "pro_scale_low": M["pro_undercount_scale_low"],
        # what the second column is: the local 2017 taxe d'habitation share
        # ("th2017"), the raw CFE proxy ("cfe_raw"), or both across members
        "low_source": low_source,
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
FORBIDDEN_TOKENS = ("std_geoid", "minority_pct", "black_pct", "_usd", "$", "landlord_key")


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
                    "share_paying_more_pct", "median_change_eur_per_dwelling",
                    "household_median_change_pct", "share_dwellings_paying_more_pct",
                    "total_change_pct", "total_change_eur", "dwellings") + STEP_KEYS,
    "by_income_quintile": ("median_change_pct", "median_change_pct_residential",
                           "total_change_pct", "household_median_change_pct",
                           "dwellings") + STEP_KEYS,
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
    # euro totals sum to zero across categories: one hidden would be recoverable
    for r in payload.get("by_category") or []:
        assert r.get("total_change_pct") is None or r.get("total_change_eur") is None, \
            f"by_category: {r.get('category')} publishes its total in both % and €"


SOCIAL_PROVENANCE_KEYS = {"modelled", "tax_year", "category", "rpls_dwellings",
                          "exempt_dwellings_pct", "qpv_abated_dwellings_pct"}
SOCIAL_COUNT_FIELDS = ("rpls_dwellings", "exempt_dwellings_pct", "qpv_abated_dwellings_pct")
# the landlord key is 12 hex characters: no string of that shape may appear
_LANDLORD_KEY_SHAPE = re.compile(r'"[0-9a-f]{12}"')


def _check_social(payload: dict) -> None:
    """Social housing guard: the provenance block holds known scalar keys only,
    its counts only where the Social Housing category is shown, and no
    sensitivity leg shows a category the central rows do not."""
    soc = (payload.get("provenance") or {}).get("social_housing")
    central = {r.get("category") for r in payload.get("by_category") or []}
    if soc is not None:
        assert isinstance(soc, dict) and set(soc) <= SOCIAL_PROVENANCE_KEYS, \
            f"unexpected social_housing keys: {set(soc) - SOCIAL_PROVENANCE_KEYS if isinstance(soc, dict) else soc}"
        assert all(v is None or isinstance(v, (bool, str, int, float)) for v in soc.values()), \
            "non-scalar value in social_housing"
        assert soc.get("category") in (None, "shown", "folded", "none"), \
            f"unknown social_housing category {soc.get('category')!r}"
        if soc.get("category") != "shown" or SOCIAL_CATEGORY not in central:
            filled = [k for k in SOCIAL_COUNT_FIELDS if soc.get(k) is not None]
            assert not filled, f"social_housing publishes {filled} without a published category"
    if payload.get("by_category") is None:      # a partial payload (tests): no rows to match
        return
    legs = [(payload.get("headline_sensitivity") or {}).get(x) for x in ("base", "low", "high")]
    legs += [(payload.get("baseline_sensitivity") or {}).get(x) for x in ("central", "low")]
    for leg in legs:
        extra = {r.get("category") for r in (leg or {}).get("by_category") or []} - central
        assert not extra, f"sensitivity leg shows categories the central rows do not: {extra}"


def _check_steps(payload: dict) -> None:
    """Decomposition guard: steps are bounded numbers published only beside
    their group's total and add up to it (to rounding).

    Each step is revenue-neutral across categories, one equation per step.
    Weighted by the categories' taxes today, which are never published, the
    equations cannot recover a withheld row (the protection the totals rely
    on, security review of 2026-11-04) as long as at least two other rows
    publish, which build_by_category enforces."""
    for key in ("by_category", "by_income_quintile", "by_income_quintile_within"):
        rows = payload.get(key) or []
        for r in rows:
            vals = [r.get(k) for k in STEP_KEYS]
            if all(v is None for v in vals):
                continue
            assert all(isinstance(v, (int, float)) and not isinstance(v, bool)
                       and math.isfinite(v) and abs(v) < STEP_MAX_PCT for v in vals), (
                f"{key}: steps must all be finite numbers, got {vals}")
            tot = r.get("total_change_pct")
            assert (isinstance(tot, (int, float)) and not isinstance(tot, bool)
                    and math.isfinite(tot) and abs(sum(vals) - tot) <= 0.3), (
                f"{key}: steps {vals} do not add up to the total {tot}")
        if key == "by_category" and any(r.get("step_revaluation_pct") is not None for r in rows):
            assert _steps_disclosable(rows), \
                "by_category: steps beside a withheld row with too few published"


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
            set(bs) <= {"pro_scale_central", "pro_scale_low", "low_source", "central", "low"}, \
            f"unexpected baseline_sensitivity keys: {set(bs) if isinstance(bs, dict) else bs}"
        for k in ("pro_scale_central", "pro_scale_low"):
            v = bs.get(k)
            assert isinstance(v, (int, float)) and not isinstance(v, bool), f"{k} must be a number"
        assert bs.get("low_source", "cfe_raw") in LOW_SOURCES + ("mixed",), \
            f"unknown low_source {bs.get('low_source')!r}"
        for leg in ("central", "low"):
            _check_leg(bs.get(leg) or {}, "baseline")
    sens = payload.get("headline_sensitivity") or {}
    assert set(sens) <= {"delta_pt", "base", "low", "high"},         f"unexpected sensitivity keys: {set(sens) - {'delta_pt', 'base', 'low', 'high'}}"
    for leg in ("base", "low", "high"):
        _check_leg(sens.get(leg) or {}, "band")
    _check_small_groups(payload)
    _check_social(payload)
    _check_unbuilt(payload)
    _check_steps(payload)
    blob = json.dumps(payload, ensure_ascii=False)
    for tok in FORBIDDEN_TOKENS:
        assert tok not in blob, f"forbidden token {tok!r} leaked into payload"
    assert not _LANDLORD_KEY_SHAPE.search(blob), "a landlord-key-shaped string leaked into payload"
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
    # the published alternative (§9.5): local 2017 taxe d'habitation share, or
    # the raw CFE proxy in older runs and where the 2017 line is missing
    targets = rec.get("targets") if isinstance(rec.get("targets"), dict) else {}
    src = targets.get("low_source")
    out["low_source"] = src if src in LOW_SOURCES else "cfe_raw"
    out["target_professional_low_share"] = share(targets, "professional_low")
    # where industrial m² would pay less than professional m² the two groups
    # are one (warehouses taxed as professional premises): only their combined
    # share is meaningful, so report it as professional and say so
    merged = "industrial merged into professional" in str(rec.get("note", ""))
    out["industrial_merged_into_professional"] = merged
    # the decomposition's first step (METHODOLOGY §3.6), where the run has it
    rv = _revaluation(commune_key, out_dir)
    if rv:
        out["rent_price_elasticity"] = rv["rent_price_elasticity"]
    if merged:
        for kind in ("target", "achieved"):
            i, p = out[f"{kind}_industrial_share"], out[f"{kind}_professional_share"]
            out[f"{kind}_professional_share"] = (round(i + p, 4)
                                                 if i is not None and p is not None else None)
            out[f"{kind}_industrial_share"] = None
    return out


def _revaluation(commune_key: str, out_dir: str = "output") -> dict:
    """The decomposition's first step as run (baseline sidecar): the
    rent-to-price elasticity and whether the tax groups were kept. Empty for
    runs before it existed."""
    from config import COMMUNES
    path = Path(out_dir) / f"{_slug(COMMUNES[commune_key])}.baseline.json"
    rec = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    r = rec.get("revaluation") if isinstance(rec, dict) else None
    if not isinstance(r, dict):
        return {}
    e, g = r.get("rent_price_elasticity"), r.get("groups_kept")
    if isinstance(e, bool) or not isinstance(e, (int, float)) or not 0 <= e <= 1 \
            or not isinstance(g, bool):
        raise ValueError(f"{path}: invalid revaluation record {r!r}")
    return {"rent_price_elasticity": float(e), "groups_kept": g}


def load_land_method(commune_key: str, out_dir: str = "output") -> dict:
    """How the run valued built land (households sidecar meta): site value with
    its parameters, or the residual at the existing density ("current"; also
    every run from before the field existed). Scalars only, validated."""
    from config import COMMUNES, SITE_VALUE
    path = Path(out_dir) / f"{_slug(COMMUNES[commune_key])}.households.meta.json"
    rec = json.loads(path.read_text("utf-8")) if path.exists() else {}
    land = rec.get("land_value") if isinstance(rec, dict) else None
    if land is None:
        return {"concept": "current"}
    if not isinstance(land, dict) or land.get("concept") not in ("site", "current"):
        raise ValueError(f"{path}: invalid land_value record {land!r}")
    if land["concept"] == "current":
        return {"concept": "current"}
    out = {"concept": "site"}
    for k in sorted(SITE_VALUE):
        v = land.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError(f"{path}: land_value.{k} must be a finite number, got {v!r}")
        out[k] = float(v)
    return out


SOCIAL_COUNTS = ("rpls_dwellings", "exempt_dwellings", "qpv_abated_dwellings")


def load_social_counts(commune_key: str, out_dir: str = "output") -> dict | None:
    """The run's commune-level social housing counts (households meta), or
    None for a run that did not model social housing. Integers only."""
    from config import COMMUNES
    path = Path(out_dir) / f"{_slug(COMMUNES[commune_key])}.households.meta.json"
    rec = json.loads(path.read_text("utf-8")) if path.exists() else {}
    soc = rec.get("social_housing") if isinstance(rec, dict) else None
    if soc is None:
        return None
    if not isinstance(soc, dict):
        raise ValueError(f"{path}: invalid social_housing record")
    out = {}
    for k in SOCIAL_COUNTS + ("tax_year",):
        v = soc.get(k)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ValueError(f"{path}: social_housing.{k} must be a count, got {v!r}")
        out[k] = v
    if out["exempt_dwellings"] + out["qpv_abated_dwellings"] > out["rpls_dwellings"]:
        raise ValueError(f"{path}: social_housing counts do not add up")
    return out


def social_provenance(counts: list, df: pd.DataFrame, by_category: list) -> dict:
    """Published social housing summary: modelled or not; whether the Social
    Housing category is shown, folded into "Other" (too few landlords, one
    dominant, or too few parcels) or absent; and where it is shown, the RPLS
    dwellings and the shares exempt and QPV-abated today (whole communes)."""
    if not counts or any(c is None for c in counts):
        return {"modelled": False}
    tot = {k: sum(c[k] for c in counts) for k in SOCIAL_COUNTS}
    years = {c["tax_year"] for c in counts}
    shown = any(r.get("category") == SOCIAL_CATEGORY for r in by_category)
    present = bool((df["property_category"] == SOCIAL_CATEGORY).any())
    out = {"modelled": True, "tax_year": years.pop() if len(years) == 1 else None,
           "category": "shown" if shown else "folded" if present else "none",
           "rpls_dwellings": None,
           "exempt_dwellings_pct": None, "qpv_abated_dwellings_pct": None}
    if shown and social_disclosable(df) and tot["rpls_dwellings"] > 0:
        out["rpls_dwellings"] = tot["rpls_dwellings"]
        out["exempt_dwellings_pct"] = _pct(tot["exempt_dwellings"], tot["rpls_dwellings"])
        out["qpv_abated_dwellings_pct"] = _pct(tot["qpv_abated_dwellings"], tot["rpls_dwellings"])
    return out


def _territory_land_method(present: list, out_dir: str) -> dict:
    """The members' common land method, else 'mixed' (parameters dropped)."""
    recs = [load_land_method(k, out_dir) for k in present]
    first = recs[0] if recs else {"concept": "current"}
    return first if all(r == first for r in recs) else {"concept": "mixed"}


UNBUILT_KEYS = {"replaced", "amount_eur", "non_agricultural_share", "garden_share"}


def load_unbuilt(commune_key: str, out_dir: str = "output") -> dict:
    """The unbuilt-land tax the run replaced (baseline sidecar): whether the
    TFPNB and TAFNB on non-agricultural unbuilt land joined the levy, the
    amount (public REI figures), the non-agricultural share of the commune's
    TFPNB and the part shared over houses' large gardens. Older runs, and
    runs without it, report replaced: False. Scalars only, validated."""
    from config import COMMUNES
    path = Path(out_dir) / f"{_slug(COMMUNES[commune_key])}.baseline.json"
    rec = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    un = rec.get("unbuilt") if isinstance(rec, dict) else None
    if un is None:
        return {"replaced": False}
    if not isinstance(un, dict) or not isinstance(un.get("replaced"), bool):
        raise ValueError(f"{path}: invalid unbuilt record")
    if not un["replaced"]:
        return {"replaced": False}
    amount = un.get("amount_eur")
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) \
            or not math.isfinite(amount) or amount <= 0:
        raise ValueError(f"{path}: unbuilt.amount_eur must be a positive amount, got {amount!r}")
    out = {"replaced": True, "amount_eur": round(float(amount), 0)}
    for k in ("non_agricultural_share", "garden_share"):
        v = un.get(k)
        if isinstance(v, bool) or not isinstance(v, (int, float)) \
                or not math.isfinite(v) or not 0 <= v <= 1:
            raise ValueError(f"{path}: unbuilt.{k} must lie in [0, 1], got {v!r}")
        out[k] = round(float(v), 3)
    return out


def _territory_unbuilt(present: list, out_dir: str) -> dict:
    """Sum of the members' replaced amounts; replaced only if every modelled
    member replaced it (a territory mixing both would mix two levies)."""
    recs = [load_unbuilt(k, out_dir) for k in present]
    if not recs or not all(r["replaced"] for r in recs):
        return {"replaced": False}
    amount = sum(r["amount_eur"] for r in recs)
    return {"replaced": True, "amount_eur": round(amount, 0),
            "garden_share": round(sum(r["garden_share"] * r["amount_eur"] for r in recs) / amount, 3)}


def _check_unbuilt(payload: dict) -> None:
    """Guard for the provenance block on the unbuilt-land tax replaced."""
    un = (payload.get("provenance") or {}).get("unbuilt_tax")
    if un is None:
        return
    assert isinstance(un, dict) and set(un) <= UNBUILT_KEYS, \
        f"unexpected unbuilt_tax keys: {set(un) - UNBUILT_KEYS if isinstance(un, dict) else un}"
    assert isinstance(un.get("replaced"), bool), "unbuilt_tax.replaced must be a boolean"
    if not un["replaced"]:
        assert set(un) == {"replaced"}, "unbuilt_tax carries figures but replaced is false"
        return
    amount = un.get("amount_eur")
    assert isinstance(amount, (int, float)) and not isinstance(amount, bool) \
        and math.isfinite(amount) and 0 < amount < 1e10 and float(amount).is_integer(), \
        f"unbuilt_tax.amount_eur must be a whole positive amount, got {amount!r}"
    for k in ("non_agricultural_share", "garden_share"):
        if k in un:
            v = un[k]
            assert isinstance(v, (int, float)) and not isinstance(v, bool) \
                and math.isfinite(v) and 0 <= v <= 1, f"unbuilt_tax.{k} must lie in [0, 1], got {v!r}"


def _territory_baseline(present: list, out_dir: str) -> dict:
    """'calibrated' only if every modelled member is; else 'mixed' or 'floor_area'.
    The alternative's source is the members' common one, else 'mixed'."""
    recs = [load_baseline(k, out_dir) for k in present]
    n = sum(r["method"] == "calibrated" for r in recs)
    method = ("calibrated" if n == len(present) else "floor_area" if n == 0 else "mixed")
    srcs = {r.get("low_source", "cfe_raw") for r in recs}
    out = {"method": method, "members_calibrated": n,
           "low_source": srcs.pop() if len(srcs) == 1 else "mixed"}
    els = {r.get("rent_price_elasticity") for r in recs}
    if len(els) == 1 and None not in els:
        out["rent_price_elasticity"] = els.pop()
    return out


def build_commune_payload(commune_key: str, out_dir: str = "output") -> dict:
    from config import COMMUNES
    cfg = COMMUNES[commune_key]
    df = load_parcels(commune_key, out_dir)
    baseline = load_baseline(commune_key, out_dir)
    by_category = build_by_category(df)
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
        "by_category": by_category,
        "by_income_quintile": build_by_income_quintile(df),
        "by_improvement_ratio": build_buckets(df),
        "baseline_sensitivity": build_baseline_sensitivity(
            df, low_source=baseline.get("low_source", "cfe_raw")),
        "provenance": {
            "construction_cost_eur_m2": cfg.construction_cost_eur_m2,
            "house_cost_eur_m2": getattr(cfg, "house_cost_eur_m2", None),
            "activity_land_ratio": getattr(cfg, "activity_land_ratio", None),
            "current_tax_baseline": baseline,
            "unbuilt_tax": load_unbuilt(commune_key, out_dir),
            "land_value": load_land_method(commune_key, out_dir),
            "social_housing": social_provenance(
                [load_social_counts(commune_key, out_dir)], df, by_category),
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
    tb = _territory_baseline(present, out_dir)
    by_category = build_by_category(df)
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
        "by_category": by_category,
        # metro-wide quintiles: IRIS incomes ranked across the whole ring
        "by_income_quintile": build_by_income_quintile(df),
        # same, ranked inside each commune (isolates within-jurisdiction incidence)
        "by_income_quintile_within": within,
        "by_income_quintile_within_coverage_pct": within_cov,
        "by_improvement_ratio": build_buckets(df),
        "baseline_sensitivity": build_baseline_sensitivity(df, within=True,
                                                           low_source=tb["low_source"]),
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
            "current_tax_baseline": tb,
            "unbuilt_tax": _territory_unbuilt(present, out_dir),
            "land_value": _territory_land_method(present, out_dir),
            "social_housing": social_provenance(
                [load_social_counts(k, out_dir) for k in present], df, by_category),
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
