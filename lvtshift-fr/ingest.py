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


def _wfs_batiment(bbox_2154, page: int = 5000) -> list:
    """All BD TOPO V3 'batiment' features intersecting a Lambert-93 bbox.

    Paginates the Géoplateforme WFS (server caps a page at 5000). Geometry is
    requested directly in EPSG:2154 so footprint areas are metric with no
    reprojection. Returns a list of GeoJSON features.
    """
    minx, miny, maxx, maxy = bbox_2154
    feats, start = [], 0
    while True:
        q = urllib.parse.urlencode({
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
            "TYPENAMES": "BDTOPO_V3:batiment",
            "OUTPUTFORMAT": "application/json",
            "SRSNAME": "EPSG:2154",
            "BBOX": f"{minx},{miny},{maxx},{maxy},urn:ogc:def:crs:EPSG::2154",
            "COUNT": page, "STARTINDEX": start,
        })
        batch = json.loads(_get(f"{SRC['bdtopo_wfs']}?{q}")).get("features", [])
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
    feats = _wfs_batiment(pg.total_bounds)
    if not feats:
        raise RuntimeError(
            f"BD TOPO returned no buildings for {cfg.name} "
            f"({cfg.insee_code}); check the WFS endpoint / bbox.")

    bg = gpd.GeoDataFrame.from_features(feats, crs=CRS_METRIC)
    bg["footprint_m2"] = bg.geometry.area
    # join on centroid-in-parcel (same pattern LVTShift uses for block groups)
    cent = bg.copy()
    cent["geometry"] = bg.geometry.centroid
    j = gpd.sjoin(cent, pg, how="inner", predicate="within")

    year = pd.to_datetime(j.get("date_d_apparition"), errors="coerce",
                          utc=True, format="ISO8601")
    out = pd.DataFrame({
        "idpar": j["idpar"].values,
        "footprint_m2": j["footprint_m2"].values,
        "n_levels": pd.to_numeric(j.get("nombre_d_etages"), errors="coerce"),
        "height_m": pd.to_numeric(j.get("hauteur"), errors="coerce"),
        "year_built": year.dt.year.values,
        "usage": j.get("usage_1").values,
        "n_dwellings": pd.to_numeric(j.get("nombre_de_logements"), errors="coerce"),
        "ff_match": j.get("appariement_fichiers_fonciers").values,
    })
    print(f"  [{cfg.name}] {len(out)} buildings joined to "
          f"{out['idpar'].nunique()} parcels "
          f"(of {len(feats)} BD TOPO features in bbox)")
    return out


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
def fetch_filosofi_iris(cfg) -> pd.DataFrame:
    """INSEE Filosofi at IRIS level -> iris, median_income_eur (DISP_MED).

    NOT on the critical path for a revenue-neutral LVT result: income only
    drives the distributional (quintile) charts, and run_pipeline.run accepts
    iris_income=None (those charts then auto-skip). Wired as a follow-up so the
    headline result lands first.

    When enabled: download the latest 'Revenus, pauvreté et niveau de vie
    (Filosofi) — IRIS' file (2021 is the last produced vintage; 2022 was not),
    keep DISP_MED per IRIS, filter to IRIS whose code starts with cfg.insee_code.
    Caveat: Filosofi IRIS exists only for communes >=5 000 inhabitants — small
    communes (e.g. Figeac, rural Lot) will have no IRIS income and fall back to
    no distributional charts.
    """
    raise NotImplementedError(
        "Filosofi IRIS income is the documented next step (distributional "
        "charts only); the headline pipeline runs without it via "
        "iris_income=None. See docstring for the INSEE 2021 IRIS file.")
