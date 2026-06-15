"""
Ingest: downloads and prepares the open-data inputs for one commune.

Run from a machine with normal internet access (data.gouv.fr, IGN,
ADEME, INSEE). Each function returns a DataFrame shaped for estimate.py.
Heavier geo steps (parcel-building spatial join) need geopandas.

NOTE: endpoints verified June 2026; they occasionally move. Each
function prints the URL it hits so failures are easy to diagnose.
"""

import gzip
import io
import json
import urllib.parse
import urllib.request
import zipfile

import pandas as pd

from config import DATA_SOURCES as SRC

# Projected CRS for all metric work (areas, spatial joins): RGF93 / Lambert-93,
# the French national grid. DVF/cadastre arrive in WGS84 (EPSG:4326).
CRS_METRIC = 2154
CRS_WGS84 = 4326


def _get(url: str, timeout: int = 180) -> bytes:
    print(f"  GET {url[:120]}{'...' if len(url) > 120 else ''}")
    req = urllib.request.Request(url, headers={"User-Agent": "lvtshift-fr/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ------------------------------------------------------------------ #
def fetch_dvf(cfg) -> pd.DataFrame:
    """Etalab geolocated DVF, per-commune CSVs pooled over cfg.dvf_years.

    Cleaning applied (document every drop in the methods note):
      - keep nature_mutation == 'Vente'
      - drop multi-disposition mutations (same id_mutation, several rows
        with conflicting locals) unless surfaces can be summed coherently
      - keep type_local in (Maison, Appartement); TAB kept separately
      - drop price or surface nulls; trim 1st/99th pctile of €/m²
    """
    frames = []
    for y in cfg.dvf_years:
        url = SRC["dvf"].format(year=y, dep=cfg.departement, insee=cfg.insee_code)
        try:
            frames.append(pd.read_csv(io.BytesIO(_get(url))))
        except Exception as e:  # year may not exist yet
            print(f"  [skip {y}] {e}")
    d = pd.concat(frames, ignore_index=True)

    d = d[d["nature_mutation"] == "Vente"].copy()
    # one row per (mutation, local); aggregate to mutation level
    keep = d["type_local"].isin(["Maison", "Appartement"])
    sales = (d[keep]
             .groupby("id_mutation")
             .agg(price=("valeur_fonciere", "first"),
                  floor_area_m2=("surface_reelle_bati", "sum"),
                  type_local=("type_local", lambda s: s.mode().iat[0]),
                  year=("date_mutation", lambda s: pd.to_datetime(s.iloc[0]).year),
                  lat=("latitude", "mean"), lon=("longitude", "mean"))
             .reset_index())
    ppm2 = sales.price / sales.floor_area_m2
    lo, hi = ppm2.quantile([0.01, 0.99])
    sales = sales[(ppm2 > lo) & (ppm2 < hi)]

    # terrains à bâtir / vacant land sales kept for the land-price floor
    tab = d[d["type_local"].isna() & (d["nature_culture"].notna())]
    return sales, tab


# ------------------------------------------------------------------ #
def fetch_parcels(cfg) -> pd.DataFrame:
    """Etalab cadastre parcel polygons (geojson.gz) -> idpar, area, geometry."""
    url = SRC["cadastre_parcelles"].format(dep=cfg.departement, insee=cfg.insee_code)
    raw = gzip.decompress(_get(url))
    gj = json.loads(raw)
    rows = [{
        "idpar": f["properties"]["id"],
        "parcel_area_m2": f["properties"].get("contenance"),
        "geometry": f["geometry"],          # keep raw; geopandas later
    } for f in gj["features"]]
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
def parcels_to_gdf(parcels: pd.DataFrame):
    """Raw cadastre frame (idpar, parcel_area_m2, geometry-as-geojson-dict)
    -> GeoDataFrame in Lambert-93 (metres). Etalab cadastre is WGS84."""
    import geopandas as gpd
    from shapely.geometry import shape

    geoms = [shape(g) for g in parcels["geometry"]]
    g = gpd.GeoDataFrame(
        parcels.drop(columns=["geometry"]).copy(),
        geometry=geoms, crs=CRS_WGS84)
    return g.to_crs(CRS_METRIC)


def _wfs_features(typename: str, bbox_2154, page: int = 5000) -> list:
    """All features of a Géoplateforme WFS layer intersecting a Lambert-93 bbox.

    Paginates the WFS (server caps a page at 5000). Geometry is requested
    directly in EPSG:2154 so areas/joins are metric with no reprojection.
    Used for both BD TOPO buildings and GPU zoning. Returns GeoJSON features.
    """
    minx, miny, maxx, maxy = bbox_2154
    feats, start = [], 0
    while True:
        params = {
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
            "TYPENAMES": typename,
            "OUTPUTFORMAT": "application/json",
            "SRSNAME": "EPSG:2154",
            "BBOX": f"{minx},{miny},{maxx},{maxy},urn:ogc:def:crs:EPSG::2154",
            "COUNT": page,
        }
        # STARTINDEX forces a sort the server can only do on a keyed layer
        # (zone_urba has no PK). Single-page layers therefore omit it; layers
        # that need a 2nd page (batiment, keyed) only paginate from page 2.
        if start:
            params["STARTINDEX"] = start
        batch = json.loads(_get(f"{SRC['bdtopo_wfs']}?{urllib.parse.urlencode(params)}")
                           ).get("features", [])
        feats.extend(batch)
        if len(batch) < page:
            break
        start += page
    return feats


def fetch_buildings(cfg, parcels: pd.DataFrame) -> pd.DataFrame:
    """BD TOPO V3 'batiment' for the commune, joined to cadastre parcels.

    Replaces the old BDNB path: the IGN Géoplateforme WFS exposes the same
    MAJIC-derived attributes per building with no bulk download. Each building
    is assigned to the parcel its centroid falls in (the cadastre we already
    fetched), then mapped to the schema estimate.improvement_value expects:

        idpar, footprint_m2, n_levels, height_m, year_built, usage
        (+ n_dwellings, ff_match — carried for category derivation & QA)

    The WFS bbox spans the whole commune (and a sliver of neighbours); the
    spatial join to this commune's parcels drops anything off-commune.
    """
    import geopandas as gpd

    pg = parcels_to_gdf(parcels)[["idpar", "geometry"]]
    feats = _wfs_features("BDTOPO_V3:batiment", pg.total_bounds)
    if not feats:
        raise RuntimeError(
            f"BD TOPO returned no buildings for {cfg.name} "
            f"({cfg.insee_code}); check the WFS endpoint / bbox.")

    keep = ["geometry", "nombre_d_etages", "hauteur", "date_d_apparition",
            "usage_1", "nombre_de_logements", "appariement_fichiers_fonciers"]
    bg = gpd.GeoDataFrame.from_features(feats, crs=CRS_METRIC)
    bg = bg[[c for c in keep if c in bg.columns]].copy()
    bg["bld_footprint_m2"] = bg.geometry.area

    # Area-weighted intersection join (not centroid): a building straddling a
    # parcel boundary contributes its *overlapping* footprint to EACH parcel,
    # so improvement value follows the land. Drops sliver overlaps from
    # imperfect cadastre/BD-TOPO alignment (<5 m²).
    inter = gpd.overlay(bg, pg, how="intersection", keep_geom_type=True)
    inter["footprint_m2"] = inter.geometry.area
    inter = inter[inter["footprint_m2"] >= 5.0].copy()
    share = (inter["footprint_m2"] / inter["bld_footprint_m2"]).clip(upper=1.0)

    year = pd.to_datetime(inter.get("date_d_apparition"), errors="coerce",
                          utc=True, format="ISO8601")
    out = pd.DataFrame({
        "idpar": inter["idpar"].values,
        "footprint_m2": inter["footprint_m2"].values,
        "n_levels": pd.to_numeric(inter.get("nombre_d_etages"), errors="coerce").values,
        "height_m": pd.to_numeric(inter.get("hauteur"), errors="coerce").values,
        "year_built": year.dt.year.values,
        "usage": inter.get("usage_1").values,
        # dwellings area-weighted so a shared building isn't double-counted
        "n_dwellings": (pd.to_numeric(inter.get("nombre_de_logements"),
                                      errors="coerce") * share).values,
        "ff_match": inter.get("appariement_fichiers_fonciers").values,
    })
    print(f"  [{cfg.name}] {len(bg)} BD TOPO buildings -> {len(out)} parcel "
          f"pieces on {out['idpar'].nunique()} parcels (area-weighted join)")
    return out


# ------------------------------------------------------------------ #
def fetch_parcel_zoning(cfg, parcels: pd.DataFrame) -> pd.DataFrame:
    """GPU (Géoportail de l'Urbanisme) zoning per parcel -> idpar, zone_typ.

    Classifies building-less parcels' legal constructibility. Spatial-joins each
    parcel to the PLU/PLUi `zone_urba` polygons (dominant overlap area) and
    returns its `typezone` (U / AUc / AUs / AU / A / N) plus the detailed
    `libelle`. Parcels with no zoning coverage (RNU communes, slivers) come back
    with zone_typ=None so the caller can fall back.
    """
    import geopandas as gpd

    pg = parcels_to_gdf(parcels)[["idpar", "geometry"]]
    feats = _wfs_features(SRC["gpu_zone_urba_layer"], pg.total_bounds)
    if not feats:
        print(f"  [{cfg.name}] no GPU zoning (likely RNU commune); fallback used")
        return pd.DataFrame({"idpar": pg["idpar"], "zone_typ": None,
                             "zone_libelle": None})

    keep = ["geometry", "typezone", "libelle"]
    zg = gpd.GeoDataFrame.from_features(feats, crs=CRS_METRIC)
    zg = zg[[c for c in keep if c in zg.columns]].copy()

    inter = gpd.overlay(pg, zg, how="intersection", keep_geom_type=True)
    inter["ov_area"] = inter.geometry.area
    # dominant zone per parcel = largest overlap
    dom = (inter.sort_values("ov_area")
                .groupby("idpar").tail(1)[["idpar", "typezone", "libelle"]])
    out = pg[["idpar"]].merge(
        dom.rename(columns={"typezone": "zone_typ", "libelle": "zone_libelle"}),
        on="idpar", how="left")
    cov = out["zone_typ"].notna().mean()
    print(f"  [{cfg.name}] GPU zoning: {cov:.0%} of parcels covered "
          f"({out['zone_typ'].value_counts().to_dict()})")
    return out


def tab_comparables(cfg, tab: pd.DataFrame) -> pd.DataFrame:
    """Clean terrain-à-bâtir €/m² comparables from DVF land sales.

    DVF `valeur_fonciere / surface_terrain` is contaminated for most cultures
    (mutations bundle buildings + several parcels), so we trust ONLY rows coded
    `terrains a bâtir`, aggregate to the mutation, trim outliers, and return one
    cleaned row per sale: idmut, eur_m2_land, lat, lon. The caller assigns grid
    cells and computes cell/commune medians with shrinkage.
    """
    t = tab[tab["nature_culture"].astype(str).str.contains("bâtir", na=False)].copy()
    if t.empty:
        return pd.DataFrame(columns=["eur_m2_land", "lat", "lon"])
    g = (t.groupby("id_mutation")
          .agg(price=("valeur_fonciere", "first"),
               surface=("surface_terrain", "sum"),
               lat=("latitude", "mean"), lon=("longitude", "mean"))
          .reset_index())
    g = g[(g["surface"] > 0) & (g["price"] > 0)]
    g["eur_m2_land"] = g["price"] / g["surface"]
    lo, hi = g["eur_m2_land"].quantile([0.05, 0.95])
    g = g[(g["eur_m2_land"] >= lo) & (g["eur_m2_land"] <= hi)]
    print(f"  [{cfg.name}] {len(g)} clean terrain-à-bâtir comparables "
          f"(median €{g['eur_m2_land'].median():,.0f}/m²)")
    return g[["eur_m2_land", "lat", "lon"]]


# ------------------------------------------------------------------ #
def fetch_rei_tfpb_produit(cfg, layers=("Commune", "GFP"),
                           year: int | None = None) -> float:
    """REI foncier bâti (FB) 'montant réel' for the commune, via OFGL.

    Revenue-neutrality target = the FB produit actually levied. OFGL's
    Opendatasoft REI is long-format; we pull the FB 'MONTANT RÉEL' line for
    each beneficiary layer in `layers` and sum. Default layers = Commune +
    intercommunalité (GFP): the local foncier-bâti envelope being redistributed.

    POLICY CHOICE (one of LVTShift's 5 upfront questions): which layers'
    revenue is held neutral. Pass layers=("Commune",) for the commune share
    only, or add TSE/GEMAPI dispositifs if they are in scope.

    Uses the latest REI millésime available if `year` (default cfg.reference_year)
    has no data yet — OFGL typically lags the reference year by ~1.
    """
    where = f'idcom="{cfg.insee_code}" and dispositif_fiscal="FB" and varlib like "MONTANT"'
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "where": where, "limit": 100, "offset": offset,
            "select": "annee,destinataire,varlib,valeur",
        })
        page = json.loads(_get(f"{SRC['ofgl_rei']}?{q}")).get("results", [])
        rows.extend(page)
        if len(page) < 100:
            break
        offset += 100

    # keep only the "MONTANT RÉEL" lines (exclude lissage / coeff-correcteur)
    real = [r for r in rows
            if r.get("valeur") is not None
            and "MONTANT R" in (r.get("varlib") or "").upper()
            and r.get("destinataire") in layers]
    if not real:
        raise RuntimeError(
            f"No FB 'MONTANT RÉEL' found for {cfg.name} ({cfg.insee_code}) "
            f"in layers {layers}; inspect OFGL REI for this commune.")

    years = sorted({r["annee"] for r in real})
    want = str(year or cfg.reference_year)
    use = want if want in years else years[-1]
    total = sum(r["valeur"] for r in real if r["annee"] == use)
    print(f"  [{cfg.name}] REI FB produit {use}: €{total:,.0f} "
          f"(layers {'+'.join(layers)})"
          + ("" if use == want else f"  [{want} unavailable, used {use}]"))
    return float(total)


# ------------------------------------------------------------------ #
def fetch_parcel_iris(cfg, parcels: pd.DataFrame) -> pd.DataFrame:
    """IRIS code per parcel -> idpar, iris (9-digit code_iris).

    Spatial-joins each parcel to the IGN IRIS contours (dominant overlap area),
    giving the join key for Filosofi income. IRIS tile the whole commune, so
    every parcel gets one. Same WFS/overlay pattern as fetch_parcel_zoning.
    """
    import geopandas as gpd

    pg = parcels_to_gdf(parcels)[["idpar", "geometry"]]
    feats = _wfs_features(SRC["iris_contours_layer"], pg.total_bounds)
    if not feats:
        return pd.DataFrame({"idpar": pg["idpar"], "iris": None})

    ig = gpd.GeoDataFrame.from_features(feats, crs=CRS_METRIC)[["geometry", "code_iris"]]
    inter = gpd.overlay(pg, ig, how="intersection", keep_geom_type=True)
    inter["ov_area"] = inter.geometry.area
    dom = (inter.sort_values("ov_area").groupby("idpar").tail(1)[["idpar", "code_iris"]])
    out = pg[["idpar"]].merge(dom, on="idpar", how="left").rename(
        columns={"code_iris": "iris"})
    print(f"  [{cfg.name}] IRIS join: {out['iris'].nunique()} IRIS, "
          f"{out['iris'].notna().mean():.0%} of parcels matched")
    return out


def fetch_filosofi_iris(cfg) -> pd.DataFrame:
    """INSEE Filosofi (2021) median disposable income per IRIS -> iris,
    median_income_eur.

    2021 is the last produced vintage (2022 not published). The CSV is keyed on
    the 9-digit IRIS code; median disposable income per consumption unit is
    DISP_MED21. We keep this commune's IRIS (code starts with cfg.insee_code).

    Caveat: Filosofi IRIS exists only for communes >= 5 000 inhabitants, and some
    IRIS are statistically suppressed (blank) — those come back NaN and simply
    drop out of the income quintiles. Income drives only the distributional
    charts; run_pipeline.run still works with iris_income=None.
    """
    raw = _get(SRC["filosofi_iris_csv"])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        name = next(n for n in z.namelist()
                    if n.upper().endswith(".CSV") and not n.lower().startswith("meta"))
        with z.open(name) as fh:
            df = pd.read_csv(fh, sep=";", dtype={"IRIS": str})

    df = df[df["IRIS"].str.startswith(cfg.insee_code)].copy()
    df["median_income_eur"] = pd.to_numeric(df["DISP_MED21"], errors="coerce")
    out = (df[["IRIS", "median_income_eur"]]
           .rename(columns={"IRIS": "iris"})
           .dropna(subset=["median_income_eur"]))
    print(f"  [{cfg.name}] Filosofi: {len(out)} IRIS with income "
          f"(median €{out['median_income_eur'].median():,.0f})")
    return out
