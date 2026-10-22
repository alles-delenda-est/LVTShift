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

def maintenance_weight(parcels: pd.DataFrame, surface: pd.DataFrame, cfg,
                       area_col: str = "iris") -> pd.Series:
    """
    Per-parcel weight w in [0, 1] of the maintained-stock effective-age rule.

    q = median hedonic €/m² (habitable) of the parcel's area (IRIS when
    known, else the whole commune) ÷ cfg.construction_cost_eur_m2 (per gross
    m²). The mixed basis is deliberate: dep_q_ramp was calibrated on it, and
    restating q per habitable m² would silently retune the rule; w ramps linearly from 0 at
    cfg.dep_q_ramp[0] to 1 at cfg.dep_q_ramp[1]. Taking q at area level, not
    per parcel, keeps a local land-price rise from being read as a newer
    building, and the ramp avoids a cliff between neighbouring parcels.

    Returns a Series indexed by idpar.
    """
    ramp = tuple(cfg.dep_q_ramp)
    if len(ramp) != 2:
        raise ValueError(f"dep_q_ramp must be (low, high), got {cfg.dep_q_ramp!r}")
    lo, hi = float(ramp[0]), float(ramp[1])
    if not (np.isfinite(lo) and np.isfinite(hi) and lo < hi):
        raise ValueError(f"dep_q_ramp must be finite and increasing, got {cfg.dep_q_ramp!r}")
    cost = float(cfg.construction_cost_eur_m2)
    if not (np.isfinite(cost) and cost > 0):
        raise ValueError("construction_cost_eur_m2 must be finite and positive")
    extra = [c for c in (area_col, "category_fr") if c in parcels.columns]
    p = market_value(parcels[["idpar", "cell", "type_local"] + extra]
                     .assign(floor_area_m2=1.0), surface)
    # The area price is read from built parcels only: vacant plots carry a
    # placeholder type_local and would otherwise drag the median towards the
    # flat price in house-dominated areas. Vacant plots inherit their area's
    # weight (it is unused for them, having no building to depreciate).
    built = (p["category_fr"].notna() & (p["category_fr"] != "terrain_nu")) \
        if "category_fr" in p.columns else pd.Series(True, index=p.index)
    ref = p[built] if built.any() else p
    commune_median = ref["market_value"].median()
    if area_col in p.columns:
        area_median = ref.groupby(area_col, observed=True)["market_value"].median()
        price = p[area_col].map(area_median).astype(float).fillna(commune_median)
    else:
        price = pd.Series(commune_median, index=p.index)
    q = price / cost
    w = ((q - lo) / (hi - lo)).clip(0.0, 1.0).fillna(0.0)
    out = pd.Series(w.values, index=p["idpar"].values, name="maint_weight")
    # one weight per parcel even if the surface ever carried duplicate keys
    return out[~out.index.duplicated()]


def habitable_basis(p: pd.DataFrame, cfg) -> pd.DataFrame:
    """
    Restate improvement_value on habitable area, the basis DVF prices use.

    improvement_value arrives as cost per gross m² × the model's floor area.
    The model's floor area overstates true gross area (BD TOPO counts
    non-habitable levels), so it is converted to habitable area with the
    measured cfg.net_to_gross and priced at the cost per habitable m²
    (cost ÷ cfg.cost_net_to_gross): improvement × net_to_gross ÷
    cost_net_to_gross, by type_local (unlisted types use 'Appartement').
    Houses are priced at cfg.house_cost instead of the commune cost
    (improvement_value is linear in cost, so the ratio rescales it).
    Adds habitable_area_m2; floor_area_m2 is left as is.
    """
    ntg = _check_net_to_gross(cfg.net_to_gross)
    cntg = _check_net_to_gross(cfg.cost_net_to_gross)
    t = p["type_local"]
    r = t.map(ntg).fillna(ntg["Appartement"]).astype(float)
    rc = t.map(cntg).fillna(cntg["Appartement"]).astype(float)
    house = float(getattr(cfg, "house_cost", cfg.construction_cost_eur_m2))
    cost = float(cfg.construction_cost_eur_m2)
    if not (np.isfinite(house) and house > 0 and np.isfinite(cost) and cost > 0):
        raise ValueError("construction costs must be finite and positive")
    is_house = t.eq("Maison").fillna(False).to_numpy(dtype=bool)
    k = np.where(is_house, house / cost, 1.0)
    out = p.copy()
    out["improvement_value"] = out["improvement_value"] * r / rc * k
    out["habitable_area_m2"] = out["floor_area_m2"] * r
    return out


# Storey imputation when BD TOPO has no nombre_d_etages (never filled for
# annexes, light structures or buildings unmatched to the fichiers fonciers).
# Height ÷ 3 m suits housing (measured 2.65 m per storey) but turns a 14 m
# single-storey warehouse into five storeys; ~90 % of shed area with a known
# count has one level (docs/research/nonres-valuation-2025.md §1).
ONE_LEVEL_NATURES = frozenset({"Industriel, agricole ou commercial", "Serre", "Silo"})
ONE_LEVEL_USAGES = frozenset({"Annexe", "Agricole", "Industriel", "Sportif", "Religieux"})
COMMERCIAL_USAGE = "Commercial et services"
COMMERCIAL_ONE_LEVEL_BELOW_M = 7.0     # shop / hall below this height
COMMERCIAL_M_PER_LEVEL = 3.5           # offices above it
RESIDENTIAL_M_PER_LEVEL = 3.0
MAX_HEIGHT_M = 350.0                   # taller than any French building: corrupt
MAX_LEVELS = 100.0


def impute_levels(b: pd.DataFrame) -> pd.Series:
    """
    Storey count for buildings whose BD TOPO nombre_d_etages is missing.

    b: building rows with height_m and, when available, usage, nature and
    construction_legere (older frames without them fall back to height ÷ 3 m).

      * shed natures (Industriel/agricole/commercial, Serre, Silo), light
        structures, and usages Annexe/Agricole/Industriel/Sportif/Religieux
        -> 1 level, whatever the height;
      * other Commercial et services -> 1 level below 7 m, else height ÷ 3.5 m;
      * everything else (housing) -> height ÷ 3 m.
    Unknown, zero or implausible (> 350 m) height -> 1 level; at most 100
    levels. Returns a float Series aligned with b.
    """
    h = (pd.to_numeric(b["height_m"], errors="coerce") if "height_m" in b.columns
         else pd.Series(np.nan, index=b.index))
    h = h.where((h > 0) & (h <= MAX_HEIGHT_M))
    usage = b["usage"] if "usage" in b.columns else pd.Series(None, index=b.index)
    nature = b["nature"] if "nature" in b.columns else pd.Series(None, index=b.index)
    # explicit parse: astype(bool) would read the string "false" as True
    light = (b["construction_legere"].map(
                 lambda v: v is True or v is np.True_
                 or (isinstance(v, str) and v.strip().lower() in ("true", "1", "oui")))
             if "construction_legere" in b.columns
             else pd.Series(False, index=b.index))
    one = nature.isin(ONE_LEVEL_NATURES) | usage.isin(ONE_LEVEL_USAGES) | light
    commercial = ~one & usage.eq(COMMERCIAL_USAGE)
    lv = (h / RESIDENTIAL_M_PER_LEVEL).round()
    lv = lv.mask(commercial, np.where(h < COMMERCIAL_ONE_LEVEL_BELOW_M, 1.0,
                                      (h / COMMERCIAL_M_PER_LEVEL).round()))
    lv = lv.mask(one, 1.0)
    return lv.fillna(1.0).clip(lower=1.0, upper=MAX_LEVELS).astype(float)


def improvement_value(buildings: pd.DataFrame, cfg,
                      maint_weight: pd.Series | None = None) -> pd.DataFrame:
    """
    Depreciated replacement cost per parcel.

    maint_weight: optional per-idpar weight from `maintenance_weight`; when
    given (and cfg.dep_maintained_age_cap is set) age is replaced by the
    effective age w·min(age, cap) + (1−w)·age before depreciating.

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

    b["n_levels"] = pd.to_numeric(b["n_levels"], errors="coerce")
    missing_lvl = b["n_levels"].isna() | (b["n_levels"] <= 0)
    b.loc[missing_lvl, "n_levels"] = impute_levels(b.loc[missing_lvl])
    quality[missing_lvl] = "imputed_levels"
    b["n_levels"] = b["n_levels"].fillna(1)

    b["floor_area"] = b["footprint_m2"] * b["n_levels"]

    ref_year = float(getattr(cfg, "reference_year", 2025))
    age = (ref_year - b["year_built"]).clip(lower=0)
    missing_age = age.isna()
    # neighbourhood median age would be better; commune median as fallback
    age = age.fillna(age.median())
    quality[missing_age & (quality == "measured")] = "imputed_age"

    cap = getattr(cfg, "dep_maintained_age_cap", None)
    if cap is not None and maint_weight is not None:
        if not (isinstance(cap, (int, np.integer)) and cap >= 1):
            raise ValueError(f"dep_maintained_age_cap must be an integer >= 1, got {cap!r}")
        if not maint_weight.index.is_unique:
            raise ValueError("maint_weight must have one entry per idpar")
        w = b["idpar"].map(maint_weight).fillna(0.0).astype(float).clip(0.0, 1.0)
        age = w * age.clip(upper=cap) + (1.0 - w) * age

    dep = (1.0 - (1.0 - cfg.dep_floor) * (age / cfg.dep_years)).clip(
        lower=cfg.dep_floor, upper=1.0)
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

def deflator_factors(cfg, fetch=None) -> dict:
    """{type_local: {year: factor}} bringing each DVF year to reference-year €.

    factor(Y) = annual mean of the area's Notaires-INSEE index in
    cfg.reference_year ÷ its annual mean in Y (config.PRICE_INDEX_IDBANKS).
    Fails loudly if the reference year or any DVF year is missing: deflating
    some years and not others would bias the pooled prices.
    """
    from config import PRICE_INDEX_IDBANKS, price_index_geography
    if fetch is None:
        from ingest import fetch_price_index_annual as fetch
    ref = int(cfg.reference_year)
    apt, house = PRICE_INDEX_IDBANKS[price_index_geography(cfg)]
    out, fetched = {}, {}
    for typ, idbank in (("Appartement", apt), ("Maison", house)):
        if idbank not in fetched:          # one series often serves both types
            fetched[idbank] = fetch(idbank, start=min(cfg.dvf_years))
        avg = fetched[idbank]
        need = sorted({ref, *cfg.dvf_years})
        missing = [y for y in need if y not in avg]
        if missing:
            raise ValueError(f"price index {idbank} lacks full years {missing}")
        out[typ] = {int(y): avg[ref] / avg[y] for y in cfg.dvf_years}
        bad = {y: f for y, f in out[typ].items() if not 0.5 < f < 2.0}
        if bad:      # a few years of house prices never halve or double
            raise ValueError(f"implausible deflator factors from {idbank}: {bad}")
    return out


def _deflator_column(d: pd.DataFrame, deflator: dict) -> pd.Series:
    """Per-sale factor: by type_local and year when the deflator is nested
    ({type: {year: f}}), by year alone for a flat {year: f}; 1.0 if unknown."""
    nested = all(isinstance(v, dict) for v in deflator.values())
    if not nested:
        return d["year"].map(deflator).fillna(1.0)
    f = pd.Series(1.0, index=d.index)
    for typ, by_year in deflator.items():
        m = d["type_local"] == typ
        f[m] = d.loc[m, "year"].map(by_year).fillna(1.0)
    return f


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
        d["price"] = d["price"] * _deflator_column(d, deflator)
    d["log_ppm2"] = np.log(d.price / d.floor_area_m2)

    # cell x type median with shrinkage toward commune-wide type median
    g = d.groupby(["cell", "type_local"])["log_ppm2"].agg(["median", "count"])
    prior = d.groupby("type_local")["log_ppm2"].median()
    k = 8.0  # shrinkage strength (pseudo-observations)
    g["shrunk"] = (g["median"] * g["count"] + prior.reindex(
        g.index.get_level_values(1)).values * k) / (g["count"] + k)
    surface = np.exp(g["shrunk"]).rename("eur_m2").reset_index()
    return surface, d


def _check_net_to_gross(net_to_gross) -> dict:
    """Validate a {type_local: ratio} map (config.check_area_ratios).

    Used for both cfg.net_to_gross and cfg.cost_net_to_gross.
    """
    from config import check_area_ratios
    return dict(check_area_ratios(net_to_gross))


def market_value(parcels: pd.DataFrame, surface: pd.DataFrame,
                 net_to_gross: dict | None = None) -> pd.DataFrame:
    """
    Predicted market value = hedonic €/m² × habitable floor area.

    The hedonic surface is priced per m² of DVF `surface_reelle_bati`
    (habitable area), while floor_area_m2 is BD TOPO footprint × storeys (gross
    external area, walls, stairwells and corridors included). net_to_gross
    ({type_local: habitable ÷ gross}) converts the latter to the former; types
    it does not list use the 'Appartement' ratio (non-residential parcels are
    priced as flats). None keeps the unconverted gross area (tests, legacy).
    """
    p = parcels.merge(surface, on=["cell", "type_local"], how="left")
    # fall back to cell-level mean across types, then commune mean
    cell_mean = surface.groupby("cell")["eur_m2"].mean()
    p["eur_m2"] = p["eur_m2"].fillna(p["cell"].map(cell_mean))
    p["eur_m2"] = p["eur_m2"].fillna(surface["eur_m2"].mean())
    if net_to_gross is None:
        ratio = 1.0
    else:
        ntg = _check_net_to_gross(net_to_gross)
        ratio = p["type_local"].map(ntg).fillna(ntg["Appartement"]).astype(float)
    p["market_value"] = p["eur_m2"] * ratio * p["floor_area_m2"]
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
                category_col: str = "category_fr",
                exempt_col: str | None = "is_exempt_public") -> pd.DataFrame:
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
    if exempt_col and exempt_col in out.columns:   # exempt today: bears no FB
        w = w.where(~out[exempt_col].fillna(False).astype(bool), 0.0)
    if category_weights and category_col in out.columns:   # sensitivity only
        w = w * out[category_col].map(category_weights).fillna(1.0)
    total = w.sum()
    out["current_tax"] = (commune_tfpb_produit * w / total) if total > 0 else 0.0
    return out
