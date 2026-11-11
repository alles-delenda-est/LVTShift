"""
Orchestrator: French parcel data -> LVTShift solver -> standard export.

Usage (after ingest produced the input frames):
    python run_pipeline.py

This module lives inside a fork of LVTShift, in the lvtshift-fr/ subdirectory.
The upstream `lvt` package therefore sits one level up, at the repository root.
We call their *actual* solver and export functions and never modify upstream
files, so improvements pulled from upstream flow through automatically.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Repository root (parent of lvtshift-fr/) holds the upstream `lvt` package.
LVTSHIFT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LVTSHIFT))

from lvt.lvt_utils import model_split_rate_tax, save_standard_export  # noqa: E402

import estimate  # noqa: E402
from config import GRENOBLE as CFG, slug_of  # noqa: E402
from social_housing import SOCIAL_CATEGORY_SHARE  # noqa: E402

# French -> LVTShift standard property categories (exact strings from
# lvt_utils.STANDARD_PROPERTY_CATEGORIES)
CATEGORY_MAP = {
    "maison": "Single Family Residential",
    "appartement": "Condominium",
    "immeuble_collectif": "Large Multi-Family (5+ units)",
    "commerce": "Commercial",
    "industriel": "Industrial",
    "terrain_nu": "Vacant Land",
    "dependance": "Other",
}

# Residential standard-categories for the France equity charts. The upstream
# report's default "residential" set is US-specific, so we pass the French
# mapping explicitly. (The minority/black quintile charts auto-skip: those
# columns are null by design — France produces no ethnic statistics.)
FR_RESIDENTIAL_CATEGORIES = [
    "Single Family Residential",       # maison
    "Condominium",                     # appartement
    "Large Multi-Family (5+ units)",   # immeuble_collectif
]

# Parcels held mainly by social landlords (social_housing.parcel_social): the
# TFPB is not recoverable from tenants and social rents are capped, so the
# reform's change falls on the landlord. A category of their own, outside the
# residential set and so outside every household figure. Not an upstream
# standard category (save_standard_export keeps it, with a warning).
SOCIAL_CATEGORY = "Social Housing"
SOCIAL_HOST_CATEGORIES = ("maison", "appartement", "immeuble_collectif", "dependance")


def social_landlord_parcels(p: pd.DataFrame) -> pd.Series:
    """True where social landlords hold at least SOCIAL_CATEGORY_SHARE of a
    residential (or annex) parcel's housing floor."""
    if "social_share" not in p.columns:
        return pd.Series(False, index=p.index)
    share = pd.to_numeric(p["social_share"], errors="coerce").fillna(0.0)
    return (share >= SOCIAL_CATEGORY_SHARE) & p["category_fr"].isin(SOCIAL_HOST_CATEGORIES)


# Unbuilt agricultural and natural land (PLU zones A and N, run_commune) is
# outside the reform: it keeps today's TFPNB and its exemptions, so it takes no
# share of the land tax. Parcels holding only farm buildings are unbuilt here,
# since those buildings are dropped as TFPB-exempt (CGI 1382 6°).
FARMLAND_TYPES = frozenset({"agricultural", "natural"})


def farmland_excluded(p: pd.DataFrame) -> pd.Series:
    """True for unbuilt A/N parcels, which stay on today's TFPNB."""
    if "land_type" not in p.columns:
        return pd.Series(False, index=p.index)
    return p["land_type"].isin(FARMLAND_TYPES)


def _write_report(out: pd.DataFrame, out_dir: str, cfg) -> None:
    """Render the France-relevant PNG charts from the standard export.

    Imported lazily so a CSV-only run never requires matplotlib. Charts are
    rendered in euros via charts_fr (which wraps the upstream report and swaps
    the currency); PNGs land under ``{out_dir}/reports/{commune}/``. The
    minority/black quintile charts auto-skip when those columns are null
    (always, for France). What remains: category impact, ±10 % share,
    income-quintile (Filosofi), and the tax-change distribution.
    """
    name = slug_of(cfg)
    try:
        from charts_fr import create_city_report_fr
    except ImportError as exc:  # matplotlib not installed
        print(f"[{cfg.name}] charts skipped (matplotlib not installed): {exc}")
        return
    report = create_city_report_fr(
        out,
        city=name,
        output_dir=f"{out_dir}/reports",
        show=False,
        census_categories=FR_RESIDENTIAL_CATEGORIES,
    )
    print(f"[{cfg.name}] {len(report['charts_saved'])} charts -> "
          f"{out_dir}/reports/{name}/")


def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
        commune_tfpb_produit: float, iris_income: pd.DataFrame | None = None,
        out_dir: str = "output", make_report: bool = True, cfg=CFG,
        deflator: dict | None = None,
        baseline_split: dict | None = None,
        site_value: dict | None = None,
        social_summary: dict | None = None,
        unbuilt_replaced: dict | None = None) -> pd.DataFrame:
    """parcels: idpar, parcel_area_m2, cell, type_local, category_fr
       buildings / dvf / iris_income: see estimate.py docstrings.
       cfg: CommuneConfig for the commune being modelled (construction cost,
       split ratio, name used for output paths). Defaults to the module CFG
       so the synthetic test keeps working unchanged.
       make_report: also write the PNG charts (needs matplotlib); set False
       for a CSV-only run.
       deflator: optional {type_local: {year: factor}} (estimate.deflator_factors)
       bringing DVF prices to cfg.reference_year euros before the hedonic fit.
       baseline_split: optional {'industrial': s, 'professional': s} shares of
       the commune's TFPB base (ingest.fetch_rei_baseline_split); when given,
       today's tax is calibrated by tax group, otherwise shared by floor area.
       site_value: overrides of config.SITE_VALUE (sensitivity runs); used when
       cfg.land_concept is "site".
       social_summary: commune-level counts from social_housing.parcel_social,
       recorded in the households meta (parcels then carry social_share,
       hlm_tax_factor and landlord_key).
       unbuilt_replaced: the tax on non-agricultural unbuilt land that the
       reform replaces (ingest.fetch_rei_unbuilt_replaced): its "amount" joins
       the revenue held constant and is shared, as today's tax, over the
       building-less parcels inside the reform and houses' large gardens
       (estimate.unbuilt_tax). None keeps the built tax alone."""

    # hedonic surface first: the maintained-stock depreciation rule needs the
    # neighbourhood price level before buildings are valued
    surface, _trans = estimate.fit_hedonic(dvf, deflator=deflator)
    maint_w = None
    if getattr(cfg, "dep_maintained_age_cap", None) is not None:
        maint_w = estimate.maintenance_weight(parcels, surface, cfg)
        # never let the rule switch itself off silently (e.g. empty surface)
        print(f"[{cfg.name}] maintained-stock rule: mean w {maint_w.mean():.2f}, "
              f"{100 * (maint_w > 0).mean():.0f}% of parcels with w > 0")
    imp = estimate.improvement_value(buildings, cfg, maint_weight=maint_w)
    p = parcels.merge(imp, on="idpar", how="left")
    p[["improvement_value", "floor_area_m2"]] = \
        p[["improvement_value", "floor_area_m2"]].fillna(0)
    # both sides of the residual on habitable area (METHODOLOGY §3.2)
    p = estimate.habitable_basis(p, cfg)
    p = estimate.market_value(p, surface, cfg.net_to_gross)
    p["building_cost"] = p["improvement_value"]     # before the residual reshapes it
    p = estimate.land_value_residual(p, cfg)
    if getattr(cfg, "land_concept", "site") == "site":
        p = estimate.site_value_land(p, site_value)
        _report_site_value(p, cfg)
    stale = Path(out_dir) / f"{slug_of(cfg)}.baseline.json"
    if stale.exists():          # never pair a new export with an old sidecar
        stale.unlink()
    baseline = _baseline_weights(p, buildings, baseline_split, cfg)
    if baseline["weights"]:
        p = p.merge(baseline.pop("floor"), on="idpar", how="left")
    else:
        baseline.pop("floor", None)
    p = estimate.current_tax(p, commune_tfpb_produit,
                             bucket_weights=baseline["weights"])
    # lower-bound baseline for the published sensitivity (new bills unchanged)
    w_low = baseline.get("weights_low")
    p["current_tax_low"] = (estimate.current_tax(p, commune_tfpb_produit,
                                                 bucket_weights=w_low)["current_tax"]
                            if w_low else p["current_tax"])

    p["PROPERTY_CATEGORY"] = p["category_fr"].map(CATEGORY_MAP).fillna("other")
    # after valuation: the category changes who bears the change, not the value
    p.loc[social_landlord_parcels(p), "PROPERTY_CATEGORY"] = SOCIAL_CATEGORY

    # Exempt public property (exemptions.py) pays neither tax: zero share of
    # today's tax and zero taxable value in the solve, so the levy is held
    # neutral over the taxable base only. Excluded farmland keeps today's
    # TFPNB, outside the levy, and is left out of the solve the same way.
    exempt_col = "is_exempt_public" if "is_exempt_public" in p.columns else None
    if exempt_col:
        p[exempt_col] = p[exempt_col].fillna(False).astype(int)
    p["is_farmland_excluded"] = farmland_excluded(p).astype(int)
    farm = p["is_farmland_excluded"].astype(bool)

    # The reform replaces the tax on the other unbuilt land (TFPNB and TAFNB):
    # that amount joins the revenue held constant and is today's tax on the
    # ground that pays it, shared by area (estimate.unbuilt_tax).
    in_reform = ~farm
    if exempt_col:
        in_reform &= ~p[exempt_col].astype(bool)
    footprint = (p["idpar"].map(pd.to_numeric(buildings["footprint_m2"], errors="coerce")
                                .groupby(buildings["idpar"]).sum())
                 if len(buildings) else None)
    amount = float((unbuilt_replaced or {}).get("amount") or 0.0)
    p["unbuilt_tax_today"] = estimate.unbuilt_tax(p, amount, in_reform, footprint)
    unbuilt_total = float(p["unbuilt_tax_today"].sum())
    baseline["unbuilt"] = _unbuilt_record(p, unbuilt_replaced, cfg)
    p["current_tax"] = p["current_tax"] + p["unbuilt_tax_today"]
    p["current_tax_low"] = p["current_tax_low"] + p["unbuilt_tax_today"]
    levy = commune_tfpb_produit + unbuilt_total

    # a single non-finite value would poison the solver's rates for everyone
    for col in ("market_value", "land_value", "improvement_value", "current_tax"):
        bad = ~np.isfinite(pd.to_numeric(p[col], errors="coerce"))
        if bad.any():
            raise ValueError(f"[{cfg.name}] {int(bad.sum())} non-finite {col} "
                             f"values before the solve")

    # ---- LVTShift's real revenue-neutral solver -------------------- #
    # excluded farmland must be unbuilt land outside today's levy: anything
    # else would take part of the levy out of the solve and the published shares
    bad = farm & ((p["improvement_value"] != 0) | (p["current_tax"] != 0))
    if bad.any():
        raise ValueError(f"[{cfg.name}] {int(bad.sum())} parcels flagged as excluded "
                         f"farmland carry a building or a share of today's levy")
    if exempt_col:
        p["outside_levy"] = (p[exempt_col].astype(bool)
                             | p["is_farmland_excluded"].astype(bool)).astype(int)
    else:
        p["outside_levy"] = p["is_farmland_excluded"]
    land_mill, imp_mill, revenue, p = model_split_rate_tax(
        df=p,
        land_value_col="land_value",
        improvement_value_col="improvement_value",
        current_revenue=levy,
        land_improvement_ratio=cfg.split_rate_ratio,
        exemption_flag_col="outside_levy",
    )

    p["tax_change"] = p["new_tax"] - p["current_tax"]
    p["tax_change_pct"] = 100 * p["tax_change"] / p["current_tax"].replace(0, pd.NA)
    # (taxable_land_value / taxable_improvement_value come from the solver:
    #  equal to land_value / improvement_value except on exempt parcels, 0)

    # demographics: IRIS code stands in for geoid; Filosofi median income;
    # minority/black left null - France produces no ethnic statistics
    # (constitutional principle), flag this in any cross-city comparison.
    if iris_income is not None:
        # real runs carry a true IRIS code; the synthetic test keys on `cell`
        income_key = "iris" if "iris" in p.columns else "cell"
        p = p.merge(iris_income.rename(columns={
            "iris": "std_geoid", "median_income_eur": "median_income"}),
            left_on=income_key, right_on="std_geoid", how="left")

    name = slug_of(cfg)
    Path(out_dir).mkdir(exist_ok=True)
    out = save_standard_export(
        df=p, city=name,
        output_path=f"{out_dir}/{name}.csv",
        model_type=f"split_rate:{cfg.split_rate_ratio}",
        land_millage=land_mill, improvement_millage=imp_mill,
        exempt_flag_col=exempt_col,
    )
    # the standard export has no column for it: add the flag so export_web can
    # leave these parcels out of the published shares (counted, never listed)
    out["is_farmland_excluded"] = p["is_farmland_excluded"].astype(bool).values
    csv = Path(out_dir) / f"{name}.csv"
    tmp = csv.with_suffix(".csv.part")
    out.to_csv(tmp, index=False)
    tmp.replace(csv)     # atomic: a crash never leaves the export without its flag
    print(f"[{cfg.name}] farmland outside the reform (A/N, unbuilt): "
          f"{int(out['is_farmland_excluded'].sum())} parcels")
    print(f"[{cfg.name}] land mill {land_mill:.3f} | imp mill {imp_mill:.3f} "
          f"| revenue €{revenue:,.0f} (target €{levy:,.0f}: built "
          f"€{commune_tfpb_produit:,.0f} + unbuilt replaced €{unbuilt_total:,.0f})")

    _write_households(p, buildings, out_dir, name, land_method(cfg, site_value),
                      social_summary)
    _write_baseline(p, baseline, out_dir, name)
    if make_report:
        _write_report(out, out_dir, cfg)
    return out


def _unbuilt_record(p: pd.DataFrame, replaced: dict | None, cfg) -> dict:
    """What the baseline sidecar says about the unbuilt-land tax replaced
    (commune-level figures only): the amount, the non-agricultural share of
    the commune's TFPNB, and the part shared over houses' large gardens."""
    if not replaced:
        return {"replaced": False, "note": "not requested or REI lines unavailable"}
    tax = p["unbuilt_tax_today"]
    shared = float(tax.sum())
    amount = float(replaced.get("amount") or 0.0)
    on_built = float(tax[p["floor_area_m2"] > 0].sum())
    rec = {"replaced": shared > 0, "amount_eur": round(shared, 2),
           "non_agricultural_share": round(float(replaced.get("non_agricultural_share") or 0.0), 4),
           "garden_share": round(on_built / shared, 4) if shared > 0 else None,
           "year": replaced.get("year")}
    if amount > 0 and shared <= 0:
        rec["note"] = "no unbuilt ground inside the reform"
        print(f"[{cfg.name}] unbuilt-land tax (€{amount:,.0f}) not replaced: "
              f"no unbuilt ground inside the reform to carry it")
    elif shared > 0:
        print(f"[{cfg.name}] unbuilt-land tax replaced: €{shared:,.0f}, of which "
              f"{100 * on_built / shared:.0f}% on houses' large gardens")
    return rec


def _report_site_value(p: pd.DataFrame, cfg) -> None:
    """One log line on the site-value re-sharing (commune-level figures only)."""
    s = p["lv_flag"].eq("built_site_value")
    if not s.any():
        print(f"[{cfg.name}] site value: no parcel valued by the residual; nothing re-shared")
        return
    moved = float((p.loc[s, "land_value"] - p.loc[s, "land_value_current"]).abs().sum()) / 2
    over = float((p.loc[s, "land_value"] > p.loc[s, "market_value_current"]).mean())
    print(f"[{cfg.name}] site value: {int(s.sum())} parcels re-shared, "
          f"{100 * moved / float(p.loc[s, 'land_value'].sum()):.1f}% of their land moved; "
          f"{100 * over:.1f}% now have land above their old floor-based market value")


def _baseline_weights(p: pd.DataFrame, buildings: pd.DataFrame,
                      split: dict | None, cfg) -> dict:
    """Per-m² weights of the current-tax groups (estimate.calibrated_weights)
    over taxable built parcels, or no weights (plain floor area) when the
    REI split is missing or fails the sanity bound."""
    from config import BASELINE_MODEL as M
    out = {"method": "floor_area", "weights": None, "targets": split, "note": ""}
    if split is None:
        out["note"] = "REI split unavailable"
        return out
    if not (0 <= split["industrial"] <= 1 and 0 <= split["professional"] <= 1):
        out["note"] = f"invalid split {split}"
        print(f"[{cfg.name}] baseline: {out['note']}; floor-area baseline kept")
        return out
    floor = estimate.baseline_floor(buildings)
    q = p[["idpar", "floor_area_m2"]].merge(floor, on="idpar", how="left")
    taxable = q["floor_area_m2"].fillna(0).to_numpy() > 0
    if "is_exempt_public" in p.columns:
        taxable &= ~p["is_exempt_public"].fillna(False).astype(bool).to_numpy()
    # exempt or abated social housing floor is outside the REI base
    q["floor_housing"] = q["floor_housing"].fillna(0) * _housing_factor(p).to_numpy()
    totals = {k: float(q.loc[taxable, f"floor_{k}"].fillna(0).sum())
              for k in estimate.BUCKETS}
    split, w, note = _weights_for(split, "professional", totals, M)
    out.update(method="calibrated", weights=w, note=note, floor=floor,
               floor_totals=totals, targets=split)
    # lower bound of the professional share (raw CFE proxy), published as a
    # sensitivity: same groups and rules, only the professional target differs
    if split.get("professional_low") is not None:
        _s, out["weights_low"], _n = _weights_for(split, "professional_low", totals, M)
    print(f"[{cfg.name}] baseline weights per m² vs housing: industrial "
          f"{w['industrial']:.2f}, professional {w['professional']:.2f} ({note})")
    return out


def _housing_factor(p: pd.DataFrame) -> pd.Series:
    """Today's TFPB weight of each parcel's housing floor (social_housing):
    1 outside social housing, 0 for exempt dwellings, 0.7 for QPV-abated."""
    if "hlm_tax_factor" not in p.columns:
        return pd.Series(1.0, index=p.index)
    return pd.to_numeric(p["hlm_tax_factor"], errors="coerce").fillna(1.0)


def _weights_for(split: dict, pro_key: str, totals: dict, M: dict) -> tuple:
    """Calibrated weights for one professional target (pro_key). Business-heavy
    communes (Rungis, Vaujours…) whose industrial + professional share exceeds
    the ceiling are scaled down to it. Returns (split, weights, note)."""
    target = {"industrial": split["industrial"], "professional": split[pro_key]}
    targeted = target["industrial"] + target["professional"]
    cap_note = ""
    if targeted > M["max_targeted_share"]:
        k = M["max_targeted_share"] / targeted
        target = {key: v * k for key, v in target.items()}
        cap_note = (f"industrial + professional {targeted:.0%} scaled to "
                    f"{M['max_targeted_share']:.0%}; ")
    w, note = estimate.calibrated_weights(totals, target, M["max_weight_ratio"])
    if pro_key == "professional":
        split = {**split, **target}
    return split, w, cap_note + note


def _write_baseline(p: pd.DataFrame, baseline: dict, out_dir: str, name: str) -> None:
    """Sidecar recording how today's tax was shared (commune-level figures
    only), for the payload provenance and the docs."""
    import json
    rec = {k: baseline.get(k) for k in ("method", "targets", "weights", "note", "unbuilt")}
    if baseline.get("weights"):
        # group shares are shares of the built tax, not of the whole levy
        tax = p["current_tax"] - p["unbuilt_tax_today"]
        tot = float(tax.sum())
        shares = {}
        floor = {k: p[f"floor_{k}"].fillna(0.0) for k in estimate.BUCKETS}
        floor["housing"] = floor["housing"] * _housing_factor(p)   # taxable floor
        for k in estimate.BUCKETS:
            f = floor[k]
            wf = sum(floor[j] * baseline["weights"][j] for j in estimate.BUCKETS)
            part = (tax * (f * baseline["weights"][k] / wf.where(wf > 0))).fillna(0.0)
            shares[k] = round(float(part.sum()) / tot, 4) if tot > 0 else None
        rec["achieved"] = shares
    (Path(out_dir) / f"{name}.baseline.json").write_text(
        json.dumps(rec, allow_nan=False) + "\n", encoding="utf-8")


# Gross floor area per dwelling used when BD TOPO gives a residential parcel no
# dwelling count: a ~63 m² habitable flat at the ~0.74 habitable/gross ratio.
GROSS_M2_PER_DWELLING = 85.0
RESIDENTIAL_CATEGORIES_FR = ("maison", "appartement", "immeuble_collectif")


def dwellings_per_parcel(p: pd.DataFrame, buildings: pd.DataFrame) -> pd.DataFrame:
    """
    Dwellings per parcel, so income-group figures can count households, not
    plots (a 200-flat block is one parcel but 200 homes).

    BD TOPO nombre_de_logements, already area-shared across parcels in ingest.
    Residential parcels without a count get 1 (houses) or gross floor area ÷
    GROSS_M2_PER_DWELLING (flats), at least 1, and are flagged imputed;
    non-residential parcels get 0.

    Returns a frame aligned with p: n_dwellings, dwellings_imputed.
    """
    if "n_dwellings" in buildings.columns:
        counts = (pd.to_numeric(buildings["n_dwellings"], errors="coerce")
                  .groupby(buildings["idpar"]).sum(min_count=1))
    else:                                   # no counts at all: impute every one
        counts = pd.Series(dtype=float)
    n = p["idpar"].map(counts).astype(float)
    res = p["category_fr"].isin(RESIDENTIAL_CATEGORIES_FR)
    missing = res & ~(n > 0)
    flats = (pd.to_numeric(p["floor_area_m2"], errors="coerce").fillna(0.0)
             / GROSS_M2_PER_DWELLING).round().clip(lower=1.0)
    n = n.where(~missing, np.where(p["category_fr"] == "maison", 1.0, flats))
    n = n.where(res, 0.0).fillna(0.0)
    return pd.DataFrame({"n_dwellings": n.round(2).values,
                         "dwellings_imputed": missing.values})


def land_method(cfg, site_value: dict | None = None) -> dict:
    """How built land was valued in this run, for the payload provenance."""
    from config import SITE_VALUE
    if getattr(cfg, "land_concept", "site") != "site":
        return {"concept": "current"}
    prm = {**SITE_VALUE, **(site_value or {})}
    return {"concept": "site", **{k: prm[k] for k in sorted(SITE_VALUE)}}


def _write_households(p: pd.DataFrame, buildings: pd.DataFrame, out_dir: str,
                      name: str, land: dict | None = None,
                      social: dict | None = None) -> None:
    """Sidecar to the standard export (whose 16 columns are fixed upstream):
    same rows in the same order, with new_tax repeated so a reader can check
    the alignment. Local only — output/ is git-ignored and never published.

    Social landlords' dwellings are no household's: none on a Social Housing
    parcel, and only the private share elsewhere. landlord_key (a hashed
    label, reversible from the public SIREN list: it never leaves the
    machine) lets the export count the landlords behind the category."""
    import hashlib
    import json
    side = dwellings_per_parcel(p, buildings)
    if "social_share" in p.columns:
        share = pd.to_numeric(p["social_share"], errors="coerce").fillna(0.0).clip(0, 1)
        soc = (p["PROPERTY_CATEGORY"] == SOCIAL_CATEGORY).to_numpy()
        side["n_dwellings"] = np.where(soc, 0.0, side["n_dwellings"] * (1.0 - share.to_numpy())
                                       ).round(2)
        side["social_share"] = share.round(4).values
        side["landlord_key"] = np.where(soc, p.get("landlord_key", pd.Series("", index=p.index))
                                        .fillna("").astype(str).to_numpy(), "")
    side.insert(0, "new_tax", p["new_tax"].values)
    # today's tax at the lower-bound professional share (baseline sensitivity)
    if "current_tax_low" in p.columns:
        side["current_tax_low"] = p["current_tax_low"].values
    # residual land clipped at the upper land-share bound before any site-value
    # re-sharing: the clip still shapes each IRIS's land total (export_web)
    flag = p["lv_flag_current"] if "lv_flag_current" in p.columns else p.get("lv_flag")
    if flag is not None:
        side["residual_at_cap"] = flag.eq("built_clipped_high").values
    side.to_csv(Path(out_dir) / f"{name}.households.csv", index=False)
    # tie the sidecar to the exact export it belongs to (new_tax alone repeats
    # across parcels, so it cannot prove the rows line up)
    export = Path(out_dir) / f"{name}.csv"
    meta = {"export_sha256": hashlib.sha256(export.read_bytes()).hexdigest(),
            "rows": int(len(side))}
    if land is not None:            # how built land was valued (export provenance)
        meta["land_value"] = land
    if social is not None:          # commune-level social housing counts
        meta["social_housing"] = social
    (Path(out_dir) / f"{name}.households.meta.json").write_text(
        json.dumps(meta) + "\n", encoding="utf-8")
    print(f"[{name}] dwellings: {side['n_dwellings'].sum():,.0f} "
          f"({100 * side['dwellings_imputed'].mean():.1f}% of parcels imputed)")


if __name__ == "__main__":
    print("Run ingest first, then call run() with the prepared frames. "
          "See test_synthetic.py for an end-to-end example.")
