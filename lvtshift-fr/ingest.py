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
import urllib.request

import pandas as pd

from config import DATA_SOURCES as SRC


def _get(url: str) -> bytes:
    print(f"  GET {url}")
    with urllib.request.urlopen(url, timeout=120) as r:
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
def fetch_buildings_bdnb(cfg) -> pd.DataFrame:
    """BDNB extract for the commune.

    Recommended: download the departement BDNB package once from
    data.gouv.fr ('Base de Données Nationale des Bâtiments'), open the
    batiment_groupe + rel_batiment_groupe_parcelle tables, filter on
    code_commune_insee, and map to:
        idpar, footprint_m2, n_levels, height_m, year_built, usage
    Fields of interest: bdnb carries fichiers-fonciers-matched usage and
    construction year + BD TOPO height — with a matching-quality flag
    (keep it: it feeds imp_quality).
    """
    raise NotImplementedError(
        "Download the departement BDNB from data.gouv.fr and adapt the "
        "column mapping here; see docstring. ~10 lines once the file is local.")


# ------------------------------------------------------------------ #
def fetch_rei_tfpb_produit(cfg) -> float:
    """REI: the commune's actual TFPB produit (exact revenue target).

    Download the latest REI from data.economie.gouv.fr, filter on the
    INSEE code, sum the TFPB produit across beneficiary layers you are
    modeling (commune + EPCI [+ TSE/GEMAPI if included in scope]).
    The 5 upfront LVTShift policy questions apply identically here:
    which layers' revenue is being made revenue-neutral?
    """
    raise NotImplementedError("Filter the REI csv on cfg.insee_code; see docstring.")


# ------------------------------------------------------------------ #
def fetch_filosofi_iris(cfg) -> pd.DataFrame:
    """INSEE Filosofi at IRIS level -> iris, median_income_eur.

    Download the latest 'Revenus localisés (Filosofi) - IRIS' file from
    insee.fr, keep DISP_MED (median disposable income) per IRIS for the
    commune. Join key: assign each parcel to its IRIS via the
    'Contours IRIS' polygons (spatial join on parcel centroid — same
    centroid pattern LVTShift uses for Census block groups).
    """
    raise NotImplementedError("Download Filosofi IRIS millésime; see docstring.")
