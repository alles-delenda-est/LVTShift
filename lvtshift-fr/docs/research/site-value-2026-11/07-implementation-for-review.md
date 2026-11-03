# Review request: site value of built land and house classification (LVTShift-FR)

Context: a French civic model of a revenue-neutral 4:1 split-rate shift of the TFPB, per commune, from open data. Results are published only in aggregate. The project lead has chosen **site value** (land as if vacant at its permitted / zone-typical use) as the central concept for built parcels, and will state its limitation: it can only be checked against rare vacant land sales and hard-to-identify teardown sales.

Two changes, diff below.
1. **House classification fix.** A missing BD TOPO dwelling count used to sum to 0, which made every unmatched building a "house". Large buildings with one recorded dwelling were also counted as houses.
2. **Site value.** Within each IRIS, the residual land (market value − depreciated cost) of built parcels valued by the residual is kept as a total and re-shared in proportion to plot × max(own FAR, zone-label p75 FAR)^0.5. The building stays at depreciated cost and value = land + building, with no share cap.
   - **Sources for the form:** German Bodenrichtwert / WertR GFZ conversion coefficients (land per m² of plot ∝ GFZ^0.45–0.54), and BW / NSW / Wales practice (linear in plot area).
   - **Concavity not used:** vacant house-plot sales are concave in plot area (EPTB 0.3–0.45), but a concave plot term applied to every parcel moves land from blocks' large plots to small house plots, so it was not used. This is documented as a limitation.
   - **Pool:** residential, offices and "other" buildings valued by the residual. Excluded: depreciated-replacement-cost parcels (sheds, retail boxes, already valued as plot × business-land price), exempt public parcels, and parcels floored at farmland value.

## First results (6 communes; median change % by category, central baseline)

Columns: classification fix only → classification fix + site value.

| | Villeurbanne | Montreuil | Lyon | Roubaix | Cahors |
|---|---|---|---|---|---|
| Houses | +21.8 → +52.3 | +14.1 → +46.3 | +23.4 → +67.8 | −15.5 → −15.5 | +14.0 → +2.5 |
| Small blocks (2–4) | +4.5 → +23.4 | +0.1 → +24.8 | +3.5 → +22.4 | +11.4 → −14.7 | +3.5 → −14.5 |
| Large blocks (5+) | +8.1 → −17.2 | +8.3 → −13.5 | +9.5 → −8.1 | +6.2 → −27.2 | +10.2 → −24.8 |
| Commercial | +24.7 → +49.4 | +0.1 → +19.8 | −5.8 → +4.9 | −39.6 → −16.0 | −25.8 → −24.0 |
| Poorest fifth, total / household median | −6.2/−6.7 → −6.1/−19.2 | −15.2/−22.1 → −18.7/−41.0 | −15.6/−9.9 → −16.8/−32.5 | −25.1/−22.6 → −26.9/−38.8 | n/a |
| Richest fifth, total / household median | +9.5/+11.8 → +2.9/−13.8 | +20.0/+25.1 → +17.9/−6.2 | +19.7/+22.8 → +15.5/+2.9 | +42.2/+38.5 → +43.7/+12.1 | n/a |
| Share of levy changing payer | 11.7 → 23.7 % | 12.9 → 26.2 % | 10.5 → 22.7 % | 23.2 → 29.1 % | 15.6 → 27.4 % |

Share of re-shared parcels whose site land exceeds their old floor-based market value: 8–37 % (Roubaix 8, Cahors 13.5, Lyon 23, Villeurbanne 26, Montreuil 37).

Vacant-plot check: median land € per m² of plot under houses is close to vacant building-plot prices where those exist. In Montreuil: houses €2,183/m² under site value, against €1,936 before and vacant plots at €1,791 (n = 2,006 vacant constructible parcels priced at that). In Villeurbanne, vacant plots are priced at a commune-wide €214/m², which is uninformative.

## Questions
1. Are the formula and parameters sound and correctly implemented: θ = 0.5, reference = p75 of realised FAR by PLU zone label, linear in plot area, pooling within IRIS, offices included? Look for bugs in the code below.
2. Are the results plausible for a site-value LVT, especially: houses in Cahors falling while their land doubles elsewhere; small blocks flipping sign by city; commercial rising; household medians falling for every income fifth?
3. What are the main risks, and what guardrails or sensitivity should be published? Sensitivity runs at θ = 0.3, θ = 0.7 and reference = p50 are under way.
4. Is the wording of the limitation honest and complete? "Site value cannot be checked against sale prices of built property; the only direct evidence is rare vacant building-plot sales and teardown sales, which are hard to identify in open data."

Be concise; rank issues.

## Code diff
diff --git a/lvtshift-fr/config.py b/lvtshift-fr/config.py
index d0dddb1..5ec52c9 100644
--- a/lvtshift-fr/config.py
+++ b/lvtshift-fr/config.py
@@ -115,6 +115,9 @@ class CommuneConfig:
     # ~45-50% of household real estate nationally; dense cores higher,
     # periphery lower). Used to clip/flag, not to impose.
     land_share_bounds: tuple = (0.15, 0.85)
+    # Land of built parcels: "site" (as if vacant at the zone's typical
+    # density, SITE_VALUE) or "current" (the residual at the existing density).
+    land_concept: str = "site"
     # Split-rate ratio for the headline scenario (LVTShift convention)
     split_rate_ratio: float = 4.0
     # Paris / Lyon / Marseille: the commune levies the taxe foncière under its
@@ -146,6 +149,9 @@ class CommuneConfig:
             raise ValueError(f"activity_land_ratio must be in "
                              f"[{ACTIVITY_LAND_RATIO_MIN}, 1], got {r!r}")
         self.activity_land_ratio = float(r)
+        if self.land_concept not in ("site", "current"):
+            raise ValueError(f"land_concept must be 'site' or 'current', "
+                             f"got {self.land_concept!r}")
         for name in ("construction_cost_eur_m2", "house_cost_eur_m2"):
             v = getattr(self, name)
             if v is None and name == "house_cost_eur_m2":
@@ -568,6 +574,37 @@ LAND_MODEL = {
     "rnu_building_buffer_m": 25.0,
 }
 
+# Site value of built land (estimate.site_value_land, METHODOLOGY §3.4).
+# An LVT taxes land as if vacant at its permitted use, not at the density that
+# happens to stand on it. Within each IRIS the residual land of parcels valued
+# by the residual is pooled and shared again in proportion to
+#     plot area × density ** density_elasticity,
+#     density = max(own floor-area ratio, reference ratio of its zone),
+# a standard land value per m² of plot adjusted for the density the zone
+# typically allows (or the parcel's own, if denser: lawful existing use, as in
+# Denmark), as German Bodenrichtwerte are.
+# Land is in proportion to plot area, as Baden-Württemberg's land tax, NSW and
+# the Welsh studies price it (zone €/m² × area). Vacant house plots sell for
+# less than proportionally more as they grow (EPTB: 0.3–0.45 % per 1 %), but a
+# concave curve applied to every parcel would move land from the large plots of
+# blocks to small house plots; it would belong within house plots only, which
+# is not modelled (METHODOLOGY §6).
+SITE_VALUE = {
+    # Land per m² of plot against floor-area ratio: German residential
+    # conversion coefficients (WertR 2006 Anl. 11) imply 0.45–0.54.
+    "density_elasticity": 0.5,
+    # Reference density: this quantile of the realised floor-area ratio of the
+    # pooled parcels in the same PLU zone label (permitted density is not open
+    # data in structured form; the typical upper end of what was built stands in).
+    "ref_density_quantile": 0.75,
+    # Zone labels with fewer pooled parcels fall back to the zone type (U, AU…),
+    # then to the commune.
+    "min_zone_parcels": 20,
+    # Plot areas above this quantile of the commune's pooled parcels are capped
+    # (parks of horizontal copropriétés, estates with farmland attached).
+    "plot_cap_quantile": 0.99,
+}
+
 # Current-tax (FB baseline) VLC-proxy sensitivity weights — OFF by default.
 # The published baseline distributes the FB produit by floor area only (size is
 # the dominant VLC driver). These relative per-m² weights are a *labelled
diff --git a/lvtshift-fr/estimate.py b/lvtshift-fr/estimate.py
index 63c4446..87b8378 100644
--- a/lvtshift-fr/estimate.py
+++ b/lvtshift-fr/estimate.py
@@ -538,6 +538,100 @@ def land_value_residual(p: pd.DataFrame, cfg,
     return out
 
 
+# Built parcels whose land is the residual (clipped or not) at the existing
+# density: the ones site_value_land re-shares. Replacement-cost parcels (sheds,
+# retail boxes) and those floored at the farmland value are already priced off
+# their plot.
+SITE_POOLED_FLAGS = frozenset({"built_residual", "built_clipped_high", "built_clipped_low"})
+
+
+def site_value_land(p: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
+    """
+    Land of built parcels as site value: as if vacant, at its zone's typical
+    density, instead of in proportion to the floor area standing on it.
+
+    The residual (market value − building cost) makes land proportional to the
+    existing floor area, so a low house gets a fraction of the land of a block
+    on an identical plot. Within each IRIS (the whole commune where there is
+    none) the residual land of the pooled parcels is kept as a total and shared
+    again in proportion to
+
+        capped plot area × density ** density_elasticity,
+        density = max(own floor-area ratio, reference FAR),
+
+    the reference FAR being the ref_density_quantile of the pooled parcels'
+    floor-area ratio in the same PLU zone label (zone type, then commune, where
+    the label has fewer than min_zone_parcels). The building keeps its
+    depreciated replacement cost (`building_cost`) and market value becomes
+    land + building, so land may exceed the old floor-proportional market value:
+    no land-share clip applies to these parcels.
+
+    p: frame after land_value_residual, with building_cost (depreciated cost
+    before the residual), lv_flag, land_value, parcel_area_m2, floor_area_m2,
+    and optionally iris, zone_libelle, zone_typ, is_exempt_public (exempt
+    parcels keep their values and stay out of the pools).
+    params: SITE_VALUE keys (config.SITE_VALUE by default).
+
+    Adds land_value_current and market_value_current (before re-sharing) and
+    site_density (the density used); updates land_value, improvement_value,
+    market_value, land_share, land_share_raw and lv_flag ('built_site_value').
+    """
+    from config import SITE_VALUE
+    prm = {**SITE_VALUE, **(params or {})}
+    theta = float(prm["density_elasticity"])
+    q_ref = float(prm["ref_density_quantile"])
+    q_cap = float(prm["plot_cap_quantile"])
+    min_n = int(prm["min_zone_parcels"])
+    if not (0.0 <= theta <= 1.0 and 0.0 < q_ref < 1.0
+            and 0.5 <= q_cap <= 1.0 and min_n >= 1):
+        raise ValueError(f"invalid SITE_VALUE parameters {prm}")
+
+    out = p.copy()
+    out["land_value_current"] = out["land_value"]
+    out["market_value_current"] = out["market_value"]
+    out["site_density"] = np.nan
+    area = pd.to_numeric(out["parcel_area_m2"], errors="coerce")
+    floor = pd.to_numeric(out["floor_area_m2"], errors="coerce")
+    cost = pd.to_numeric(out["building_cost"], errors="coerce")
+    exempt = (out["is_exempt_public"].fillna(False).astype(bool)
+              if "is_exempt_public" in out.columns
+              else pd.Series(False, index=out.index))
+    pool = (out["lv_flag"].isin(SITE_POOLED_FLAGS) & ~exempt
+            & (area > 0) & (floor > 0) & cost.notna() & (cost >= 0))
+    if not pool.any():
+        return out
+
+    far = floor[pool] / area[pool]
+    plot = area[pool].clip(upper=area[pool].quantile(q_cap))
+    ref = pd.Series(far.quantile(q_ref), index=far.index)
+    for col in ("zone_typ", "zone_libelle"):          # coarse first, finest wins
+        if col not in out.columns:
+            continue
+        key = out.loc[pool, col].astype("object")
+        known = key.notna()
+        n = key[known].map(key[known].value_counts())
+        ok = n[n >= min_n].index
+        by_zone = far[ok].groupby(key[ok]).quantile(q_ref)
+        ref = ref.mask(key.index.isin(ok), key.map(by_zone))
+    density = np.maximum(far, ref)
+    weight = plot * density ** theta
+
+    group = (out.loc[pool, "iris"].astype("object").fillna("_commune")
+             if "iris" in out.columns else pd.Series("_commune", index=far.index))
+    total = out.loc[pool, "land_value"].groupby(group).transform("sum")
+    land = total * weight / weight.groupby(group).transform("sum")
+
+    out.loc[pool, "land_value"] = land
+    out.loc[pool, "improvement_value"] = cost[pool]
+    out.loc[pool, "market_value"] = land + cost[pool]
+    share = land / (land + cost[pool]).replace(0, np.nan)
+    out.loc[pool, "land_share"] = share
+    out.loc[pool, "land_share_raw"] = share
+    out.loc[pool, "lv_flag"] = "built_site_value"
+    out.loc[pool, "site_density"] = density
+    return out
+
+
 def sensitivity_band(p: pd.DataFrame, cfg, shifts=(-0.10, 0.0, +0.10)):
     """Re-split market value at land_share +/- shift -> dict of variants
     for the published sensitivity band.
diff --git a/lvtshift-fr/run_commune.py b/lvtshift-fr/run_commune.py
index c51eaab..5e04dc3 100644
--- a/lvtshift-fr/run_commune.py
+++ b/lvtshift-fr/run_commune.py
@@ -47,30 +47,64 @@ USAGE_MAP = {
 }
 
 
-def _residential_cat(n_dwellings, n_levels) -> str:
-    """maison / appartement / immeuble_collectif from dwelling count, with a
-    storey-count fallback when BD TOPO has no nombre_de_logements."""
-    if pd.notna(n_dwellings):
+# Largest parcel floor area (BD TOPO footprint × storeys, gross) still read as
+# one house: ≈ 300 m² habitable at the measured 0.61 habitable ÷ BD TOPO ratio
+# for houses. Larger buildings with one recorded dwelling or none were 20 % of
+# Paris "houses" and 80 % of the category's tax before this bound.
+MAISON_MAX_FLOOR_M2 = 500.0
+
+
+def _residential_cat(n_dwellings, n_levels, floor_m2) -> str:
+    """maison / appartement / immeuble_collectif / dependance for a parcel whose
+    dominant building is residential or of undifferentiated use.
+
+    n_dwellings: BD TOPO nombre_de_logements, area-shared across parcels (NaN
+    when the building is unmatched to the fichiers fonciers). floor_m2: the
+    parcel's gross floor area, storeys imputed where BD TOPO has none.
+      * a recorded 0: the tax files hold no dwelling in it -> dependance;
+      * no count: a building above 2 storeys or MAISON_MAX_FLOOR_M2 is flats,
+        sized at the households sidecar's m² per dwelling; otherwise a house;
+      * at most one dwelling: a house, unless the building is larger than any
+        house (-> dependance: offices, mixed use or an unreliable count);
+      * otherwise by count: 2–4 appartement, 5+ immeuble_collectif.
+    """
+    floor = float(floor_m2) if pd.notna(floor_m2) else 0.0
+    large = floor > MAISON_MAX_FLOOR_M2
+    if pd.isna(n_dwellings):
+        if not large and not (pd.notna(n_levels) and n_levels >= 3):
+            return "maison"
+        n_dwellings = max(1.0, round(floor / rp.GROSS_M2_PER_DWELLING))
         if n_dwellings <= 1:
             return "maison"
-        if n_dwellings <= 4:
-            return "appartement"
-        return "immeuble_collectif"
-    return "appartement" if (pd.notna(n_levels) and n_levels >= 3) else "maison"
+    elif n_dwellings == 0:
+        return "dependance"
+    if n_dwellings <= 1:
+        return "dependance" if large else "maison"
+    if n_dwellings <= 4:
+        return "appartement"
+    return "immeuble_collectif"
 
 
 def derive_parcel_category(buildings: pd.DataFrame) -> pd.Series:
     """One category_fr per parcel, from its dominant (largest-floor) building."""
     b = buildings.copy()
-    b["floor"] = b["footprint_m2"] * b["n_levels"].fillna(1).clip(lower=1)
+    levels = pd.to_numeric(b["n_levels"], errors="coerce")
+    missing = levels.isna() | (levels <= 0)
+    if missing.any():            # same storey rule as improvement_value
+        levels = levels.mask(missing, estimate.impute_levels(b.loc[missing]))
+    b["levels"] = levels
+    b["floor"] = pd.to_numeric(b["footprint_m2"], errors="coerce").fillna(0.0) * levels
     dom = b.sort_values("floor").groupby("idpar").tail(1).set_index("idpar")
-    dwellings = b.groupby("idpar")["n_dwellings"].sum()
+    # min_count=1: a parcel with no count stays NaN rather than summing to 0
+    dwellings = b.groupby("idpar")["n_dwellings"].sum(min_count=1)
+    floor = b.groupby("idpar")["floor"].sum()
 
     cats = {}
     for idpar, row in dom.iterrows():
         u = row["usage"]
         if pd.isna(u) or u in ("Résidentiel", "Indifférencié"):
-            cats[idpar] = _residential_cat(dwellings.get(idpar), row["n_levels"])
+            cats[idpar] = _residential_cat(dwellings.get(idpar), row["levels"],
+                                           floor.get(idpar))
         else:
             cats[idpar] = USAGE_MAP.get(u, "dependance")
     return pd.Series(cats, name="category_fr")
@@ -248,6 +282,14 @@ def main():
     ap.add_argument("--baseline", choices=("calibrated", "floor"), default="calibrated",
                     help="today's tax: calibrated to the commune's REI split by tax "
                          "group (default), or shared by plain floor area (sensitivity)")
+    ap.add_argument("--land", choices=("site", "current"), default=None,
+                    help="land of built parcels: site value at the zone's typical "
+                         "density (default, config.SITE_VALUE) or the residual at "
+                         "the existing density (sensitivity)")
+    ap.add_argument("--site-elasticity", type=float, default=None,
+                    help="override SITE_VALUE density_elasticity (sensitivity)")
+    ap.add_argument("--site-ref-quantile", type=float, default=None,
+                    help="override SITE_VALUE ref_density_quantile (sensitivity)")
     ap.add_argument("--cache-dir", default=None,
                     help="cache raw downloads here (resumable batch runs); "
                          "default: env LVTFR_CACHE_DIR, else no cache")
@@ -256,6 +298,12 @@ def main():
         ingest.CACHE_DIR = args.cache_dir
 
     cfg = COMMUNES[args.commune]
+    if args.land:
+        import dataclasses
+        cfg = dataclasses.replace(cfg, land_concept=args.land)
+    site_value = {k: v for k, v in (("density_elasticity", args.site_elasticity),
+                                    ("ref_density_quantile", args.site_ref_quantile))
+                  if v is not None} or None
     print(f"=== {cfg.name} ({cfg.insee_code}, dep {cfg.departement}) ===")
     deflator = None if args.no_deflator else estimate.deflator_factors(cfg)
     if deflator:
@@ -276,7 +324,7 @@ def main():
 
     out = rp.run(parcels, buildings, sales, tfpb, iris_income=iris_income,
                  out_dir=args.out_dir, make_report=not args.no_report, cfg=cfg,
-                 deflator=deflator, baseline_split=split)
+                 deflator=deflator, baseline_split=split, site_value=site_value)
 
     print("\n--- sanity checks -------------------------------------")
     print(f"rows exported: {len(out)}")
diff --git a/lvtshift-fr/run_pipeline.py b/lvtshift-fr/run_pipeline.py
index 50e78f5..ea6826e 100644
--- a/lvtshift-fr/run_pipeline.py
+++ b/lvtshift-fr/run_pipeline.py
@@ -92,7 +92,8 @@ def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
         commune_tfpb_produit: float, iris_income: pd.DataFrame | None = None,
         out_dir: str = "output", make_report: bool = True, cfg=CFG,
         deflator: dict | None = None,
-        baseline_split: dict | None = None) -> pd.DataFrame:
+        baseline_split: dict | None = None,
+        site_value: dict | None = None) -> pd.DataFrame:
     """parcels: idpar, parcel_area_m2, cell, type_local, category_fr
        buildings / dvf / iris_income: see estimate.py docstrings.
        cfg: CommuneConfig for the commune being modelled (construction cost,
@@ -104,7 +105,9 @@ def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
        bringing DVF prices to cfg.reference_year euros before the hedonic fit.
        baseline_split: optional {'industrial': s, 'professional': s} shares of
        the commune's TFPB base (ingest.fetch_rei_baseline_split); when given,
-       today's tax is calibrated by tax group, otherwise shared by floor area."""
+       today's tax is calibrated by tax group, otherwise shared by floor area.
+       site_value: overrides of config.SITE_VALUE (sensitivity runs); used when
+       cfg.land_concept is "site"."""
 
     # hedonic surface first: the maintained-stock depreciation rule needs the
     # neighbourhood price level before buildings are valued
@@ -122,7 +125,11 @@ def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
     # both sides of the residual on habitable area (METHODOLOGY §3.2)
     p = estimate.habitable_basis(p, cfg)
     p = estimate.market_value(p, surface, cfg.net_to_gross)
+    p["building_cost"] = p["improvement_value"]     # before the residual reshapes it
     p = estimate.land_value_residual(p, cfg)
+    if getattr(cfg, "land_concept", "site") == "site":
+        p = estimate.site_value_land(p, site_value)
+        _report_site_value(p, cfg)
     stale = Path(out_dir) / f"{slug_of(cfg)}.baseline.json"
     if stale.exists():          # never pair a new export with an old sidecar
         stale.unlink()
@@ -214,13 +221,26 @@ def run(parcels: pd.DataFrame, buildings: pd.DataFrame, dvf: pd.DataFrame,
     print(f"[{cfg.name}] land mill {land_mill:.3f} | imp mill {imp_mill:.3f} "
           f"| revenue €{revenue:,.0f} (target €{commune_tfpb_produit:,.0f})")
 
-    _write_households(p, buildings, out_dir, name)
+    _write_households(p, buildings, out_dir, name, land_method(cfg, site_value))
     _write_baseline(p, baseline, out_dir, name)
     if make_report:
         _write_report(out, out_dir, cfg)
     return out
 
 
+def _report_site_value(p: pd.DataFrame, cfg) -> None:
+    """One log line on the site-value re-sharing (commune-level figures only)."""
+    s = p["lv_flag"].eq("built_site_value")
+    if not s.any():
+        print(f"[{cfg.name}] site value: no parcel valued by the residual; nothing re-shared")
+        return
+    moved = float((p.loc[s, "land_value"] - p.loc[s, "land_value_current"]).abs().sum()) / 2
+    over = float((p.loc[s, "land_value"] > p.loc[s, "market_value_current"]).mean())
+    print(f"[{cfg.name}] site value: {int(s.sum())} parcels re-shared, "
+          f"{100 * moved / float(p.loc[s, 'land_value'].sum()):.1f}% of their land moved; "
+          f"{100 * over:.1f}% now have land above their old floor-based market value")
+
+
 def _baseline_weights(p: pd.DataFrame, buildings: pd.DataFrame,
                       split: dict | None, cfg) -> dict:
     """Per-m² weights of the current-tax groups (estimate.calibrated_weights)
@@ -326,8 +346,17 @@ def dwellings_per_parcel(p: pd.DataFrame, buildings: pd.DataFrame) -> pd.DataFra
                          "dwellings_imputed": missing.values})
 
 
+def land_method(cfg, site_value: dict | None = None) -> dict:
+    """How built land was valued in this run, for the payload provenance."""
+    from config import SITE_VALUE
+    if getattr(cfg, "land_concept", "site") != "site":
+        return {"concept": "current"}
+    prm = {**SITE_VALUE, **(site_value or {})}
+    return {"concept": "site", **{k: prm[k] for k in sorted(SITE_VALUE)}}
+
+
 def _write_households(p: pd.DataFrame, buildings: pd.DataFrame, out_dir: str,
-                      name: str) -> None:
+                      name: str, land: dict | None = None) -> None:
     """Sidecar to the standard export (whose 16 columns are fixed upstream):
     same rows in the same order, with new_tax repeated so a reader can check
     the alignment. Local only — output/ is git-ignored and never published."""
@@ -344,6 +373,8 @@ def _write_households(p: pd.DataFrame, buildings: pd.DataFrame, out_dir: str,
     export = Path(out_dir) / f"{name}.csv"
     meta = {"export_sha256": hashlib.sha256(export.read_bytes()).hexdigest(),
             "rows": int(len(side))}
+    if land is not None:            # how built land was valued (export provenance)
+        meta["land_value"] = land
     (Path(out_dir) / f"{name}.households.meta.json").write_text(
         json.dumps(meta) + "\n", encoding="utf-8")
     print(f"[{name}] dwellings: {side['n_dwellings'].sum():,.0f} "
