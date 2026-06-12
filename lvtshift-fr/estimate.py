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
    """
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
                vlc_proxy_cols=("floor_area_m2",)) -> pd.DataFrame:
    """
    THE honestly-flagged weak link (replaced by FF parcel VLC when access lands).

    Proxy: VLC ~ floor area x category weight (1970 tarifs were per-m²
    by category; without the category we default to pure floor area).
    The commune's actual TFPB produit (REI, exact) is distributed
    proportionally to the proxy -> aggregate is right by construction,
    distribution is approximate.
    """
    out = p.copy()
    w = out[list(vlc_proxy_cols)].prod(axis=1).fillna(0)
    # non-bâti gets a small weight via land area (TFPNB is tiny in cities)
    w = w + 0.002 * out["parcel_area_m2"].fillna(0) * (w == 0)
    out["current_tax"] = commune_tfpb_produit * w / w.sum()
    return out
