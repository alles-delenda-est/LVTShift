"""
Core estimation steps for LVTShift-FR.

Pipeline:  parcels + buildings -> improvement value
           DVF sales           -> hedonic market value surface
           residual            -> land value (with anchors & sensitivity)
           REI + VLC proxy     -> current tax per parcel

Every function takes/returns plain DataFrames so the output plugs
directly into LVTShift's model_split_rate_tax / save_standard_export.
"""

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ #
# 1. Improvement (building) values
# ------------------------------------------------------------------ #

def improvement_value(buildings: pd.DataFrame, cfg) -> pd.DataFrame:
    """
    Depreciated replacement cost per parcel.

    buildings: one row per building, columns
        idpar          parcel id (BDNB/BD TOPO joined to cadastre)
        footprint_m2   ground footprint
        n_levels       storeys (BDNB nb_niveaux, else height/3m)
        year_built     construction year (BDNB / DPE periode; NaN ok)
        usage          residential / commercial / etc. (BDNB usage_principal)

    Returns parcel-level frame: idpar, improvement_value, floor_area_m2,
    mean_age, imp_quality ('measured' | 'imputed_age' | 'imputed_levels').
    """
    b = buildings.copy()
    quality = pd.Series("measured", index=b.index)

    missing_lvl = b["n_levels"].isna()
    b.loc[missing_lvl, "n_levels"] = (b.loc[missing_lvl, "height_m"] / 3.0).clip(lower=1).round()
    quality[missing_lvl] = "imputed_levels"
    b["n_levels"] = b["n_levels"].fillna(1)

    b["floor_area"] = b["footprint_m2"] * b["n_levels"]

    ref_year = float(getattr(cfg, "reference_year", 2025))
    age = (ref_year - b["year_built"]).clip(lower=0)
    missing_age = age.isna()
    # neighbourhood median age would be better; commune median as fallback
    age = age.fillna(age.median())
    quality[missing_age & (quality == "measured")] = "imputed_age"

    dep = (1.0 - (1.0 - cfg.dep_floor) * (age / cfg.dep_years)).clip(lower=cfg.dep_floor)
    b["imp_value"] = b["floor_area"] * cfg.construction_cost_eur_m2 * dep
    b["imp_quality"] = quality

    out = b.groupby("idpar").agg(
        improvement_value=("imp_value", "sum"),
        floor_area_m2=("floor_area", "sum"),
        mean_age=("year_built", lambda s: ref_year - s.mean()),
        imp_quality=("imp_quality", lambda s: s.mode().iat[0] if len(s) else "none"),
    ).reset_index()
    return out


# ------------------------------------------------------------------ #
# 2. Hedonic market value surface from DVF
# ------------------------------------------------------------------ #

def fit_hedonic(dvf: pd.DataFrame, deflator: dict | None = None):
    """
    Log-linear hedonic on DVF mutations -> predicted €/m² of floor area
    by location cell and property type.

    dvf columns: price, floor_area_m2, type_local ('Maison'/'Appartement'),
                 year, cell (spatial cell id: IRIS, or 200m grid id).

    Deliberately simple (cell fixed effects + type + log area). The point
    is a *transparent, criticisable* baseline; upgrade to GAM / spatial
    smoothing once the demo lands. Multi-parcel and outlier mutations
    must be filtered upstream (see ingest notes).
    """
    d = dvf.dropna(subset=["price", "floor_area_m2", "cell"]).copy()
    d = d[(d.floor_area_m2 > 9) & (d.price > 1_000)]
    if deflator:
        d["price"] = d.apply(lambda r: r["price"] * deflator.get(r["year"], 1.0), axis=1)
    d["log_ppm2"] = np.log(d.price / d.floor_area_m2)

    # cell x type median with shrinkage toward commune-wide type median
    g = d.groupby(["cell", "type_local"])["log_ppm2"].agg(["median", "count"])
    prior = d.groupby("type_local")["log_ppm2"].median()
    k = 8.0  # shrinkage strength (pseudo-observations)
    g["shrunk"] = (g["median"] * g["count"] + prior.reindex(
        g.index.get_level_values(1)).values * k) / (g["count"] + k)
    surface = np.exp(g["shrunk"]).rename("eur_m2").reset_index()
    return surface, d


def market_value(parcels: pd.DataFrame, surface: pd.DataFrame) -> pd.DataFrame:
    """Predicted market value = hedonic €/m² (by cell & dominant type) × floor area."""
    p = parcels.merge(surface, on=["cell", "type_local"], how="left")
    # fall back to cell-level mean across types, then commune mean
    cell_mean = surface.groupby("cell")["eur_m2"].mean()
    p["eur_m2"] = p["eur_m2"].fillna(p["cell"].map(cell_mean))
    p["eur_m2"] = p["eur_m2"].fillna(surface["eur_m2"].mean())
    p["market_value"] = p["eur_m2"] * p["floor_area_m2"]
    return p


# ------------------------------------------------------------------ #
# 3. Residual land value, anchored
# ------------------------------------------------------------------ #

def _land_value_classified(out: pd.DataFrame, cfg) -> pd.DataFrame:
    """Classify-then-price land value (see THEORY.md). Used when parcels carry a
    `land_type` column (real French runs); the legacy residual path below is
    kept for the synthetic test.

    Expects per-parcel columns set upstream (run_commune):
        land_type   built | constructible | constructible_deferred
                    | agricultural | natural | unknown
        market_value, improvement_value, parcel_area_m2, floor_area_m2,
        constructible_eur_m2  (AU-discounted development €/m², from DVF TAB),
        ag_eur_m2             (agricultural/natural €/m², from SAFER by dépt).

    Pricing:
      * built (floor_area>0): residual = market − improvement, floored at the
        dirt (agricultural) value, land-share clipped to cfg.land_share_bounds.
      * constructible vacant: land = development €/m² × parcel area.
      * agricultural/natural vacant: land = ag €/m² × parcel area.
      * unknown vacant: priced as agricultural (conservative).
    """
    lo, hi = cfg.land_share_bounds
    area = pd.to_numeric(out["parcel_area_m2"], errors="coerce").fillna(0.0)
    ag = pd.to_numeric(out.get("ag_eur_m2"), errors="coerce").fillna(0.0)
    con = pd.to_numeric(out.get("constructible_eur_m2"), errors="coerce").fillna(0.0)
    mv = pd.to_numeric(out["market_value"], errors="coerce").fillna(0.0)
    imp = pd.to_numeric(out["improvement_value"], errors="coerce").fillna(0.0)
    built = pd.to_numeric(out["floor_area_m2"], errors="coerce").fillna(0.0) > 0

    land = pd.Series(0.0, index=out.index)
    flag = out["land_type"].astype("object").copy()

    # built: residual, floored at dirt value, then land-share clipped
    resid = (mv - imp).clip(lower=0)
    resid = resid.where(resid >= ag * area, ag * area)
    share = resid / mv.replace(0, np.nan)
    hi_clip = built & (share > hi)
    lo_clip = built & (share < lo)
    resid = resid.mask(hi_clip, hi * mv).mask(lo_clip, lo * mv)
    land = land.mask(built, resid)
    flag = flag.mask(built, "built_residual")
    flag = flag.mask(hi_clip, "built_clipped_high").mask(lo_clip, "built_clipped_low")

    # vacant: price by class
    is_con = ~built & out["land_type"].isin(["constructible", "constructible_deferred"])
    is_un = ~built & ~is_con & ~out["land_type"].isin(["agricultural", "natural"])
    land = land.mask(is_con, con * area)
    land = land.mask(~built & ~is_con, ag * area)   # ag/natural/unknown -> dirt
    flag = flag.mask(is_un, "vacant_unknown_ag")

    out["land_value"] = land
    out["improvement_value"] = (mv - land).clip(lower=0).where(built, 0.0)
    out["market_value"] = mv.where(built, land)
    out["land_share"] = out["land_value"] / out["market_value"].replace(0, np.nan)
    out["lv_flag"] = flag
    return out


def land_value_residual(p: pd.DataFrame, cfg,
                        tab_prices: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    land = market_value - improvement_value, with:
      * floor at vacant-land comparables (tab_prices: cell, eur_m2_land)
        interpolated from terrains-à-bâtir sales in the wider aire urbaine;
      * land share clipped to cfg.land_share_bounds, clip events flagged;
      * vacant parcels valued directly at land comparables.

    Adds: land_value, land_share, lv_flag
          ('residual'|'clipped_low'|'clipped_high'|'vacant_comparable')

    Real French runs supply a `land_type` column and are routed to the
    classify-then-price model (`_land_value_classified`); the body below is the
    legacy single-density path retained for the synthetic test.
    """
    if "land_type" in p.columns:
        return _land_value_classified(p.copy(), cfg)

    out = p.copy()
    out["land_value"] = out["market_value"] - out["improvement_value"]
    out["lv_flag"] = "residual"

    if tab_prices is not None:
        floor = out["cell"].map(tab_prices.set_index("cell")["eur_m2_land"])
        floor_val = (floor * out["parcel_area_m2"]).fillna(0)
        low = out["land_value"] < floor_val
        out.loc[low, "land_value"] = floor_val[low]
        out.loc[low, "lv_flag"] = "clipped_low"

    vacant = out["floor_area_m2"].fillna(0) <= 0
    if tab_prices is not None:
        comp = out.loc[vacant, "cell"].map(tab_prices.set_index("cell")["eur_m2_land"])
        out.loc[vacant, "land_value"] = (comp * out.loc[vacant, "parcel_area_m2"]).fillna(0)
    else:
        # no TAB comparables supplied: value vacant land off the commune's
        # built land-value density (€ land per m² parcel), zone-blind fallback
        dens = (out.loc[~vacant, "land_value"] /
                out.loc[~vacant, "parcel_area_m2"]).median()
        out.loc[vacant, "land_value"] = dens * out.loc[vacant, "parcel_area_m2"]
    out.loc[vacant, "improvement_value"] = 0.0
    out.loc[vacant, "market_value"] = out.loc[vacant, "land_value"]
    out.loc[vacant, "lv_flag"] = "vacant_comparable"

    lo, hi = cfg.land_share_bounds
    share = out["land_value"] / out["market_value"].replace(0, np.nan)
    high = share > hi
    lowc = (share < lo) & ~vacant
    out.loc[high, "land_value"] = hi * out.loc[high, "market_value"]
    out.loc[lowc, "land_value"] = lo * out.loc[lowc, "market_value"]
    out.loc[high, "lv_flag"] = "clipped_high"
    out.loc[lowc, "lv_flag"] = "clipped_low"

    out["improvement_value"] = (out["market_value"] - out["land_value"]).clip(lower=0)
    out["land_share"] = out["land_value"] / out["market_value"].replace(0, np.nan)
    return out


def sensitivity_band(p: pd.DataFrame, cfg, shifts=(-0.10, 0.0, +0.10)):
    """Re-split market value at land_share +/- shift -> dict of variants
    for the published sensitivity band."""
    variants = {}
    for s in shifts:
        v = p.copy()
        v["land_value"] = (v["land_share"].clip(0.05, 0.95) + s).clip(0.05, 0.95) * v["market_value"]
        v["improvement_value"] = v["market_value"] - v["land_value"]
        variants[f"land_share{s:+.0%}"] = v
    return variants


# ------------------------------------------------------------------ #
# 4. Current tax: REI total distributed via VLC proxy
# ------------------------------------------------------------------ #

def current_tax(p: pd.DataFrame, commune_tfpb_produit: float,
                vlc_proxy_cols=("floor_area_m2",),
                category_weights: dict | None = None,
                category_col: str = "category_fr") -> pd.DataFrame:
    """Distribute the commune's foncier-bâti (FB) produit across parcels.

    THE honestly-flagged weak link (replaced by Fichiers-Fonciers parcel VLC when
    access lands). The exact REI produit is shared out by a VLC proxy, so the
    aggregate is right by construction and only the distribution is approximate.

    Two deliberate design choices (France-context reviewed):

    * **Built parcels only.** TFPB is a tax on *built* property; unbuilt land pays
      the separate, much smaller TFPNB, which is **not** in our FB target. So
      parcels with no building footprint bear **zero** current tax — they go from
      ~0 today to a positive LVT bill (the under-used-land incentive made literal).
      (The old code mistakenly gave them a ``0.002 × parcel_area`` share, which
      manufactured a baseline over-charge on rural land.)

    * **Proxy = floor area, no market-value tilt.** Size is the dominant VLC
      driver. We do *not* tilt toward the hedonic market value: the 1970 VLC is
      famously regressive vs market (central old stock under-assessed, peripheral
      over-assessed), so a value tilt would *worsen* fidelity to the current
      system. ``category_weights`` (e.g. weighting professionnel m² above housing
      m², post-2017 revision) is offered only as a labelled **sensitivity**, off
      by default — never as the published baseline.
    """
    out = p.copy()
    w = out[list(vlc_proxy_cols)].prod(axis=1).fillna(0.0).clip(lower=0)
    if "floor_area_m2" in out.columns:        # enforce built-only
        w = w.where(out["floor_area_m2"].fillna(0) > 0, 0.0)
    if category_weights and category_col in out.columns:   # sensitivity only
        w = w * out[category_col].map(category_weights).fillna(1.0)
    total = w.sum()
    out["current_tax"] = (commune_tfpb_produit * w / total) if total > 0 else 0.0
    return out
