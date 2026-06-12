"""
Configuration for LVTShift-FR: French commune LVT simulation on open data.

All URLs documented as of June 2026 — verify before first run, these
endpoints occasionally move. Network access required for ingest only.
"""

from dataclasses import dataclass, field


@dataclass
class CommuneConfig:
    insee_code: str          # e.g. "38185" Grenoble, "74012" Annemasse
    name: str
    departement: str         # "38", "74"
    # DVF years to pool for the hedonic model (more years = more obs,
    # but deflate to a common year with the INSEE/Notaires index)
    dvf_years: tuple = (2021, 2022, 2023, 2024, 2025)
    reference_year: int = 2025
    # Construction cost (€/m² SHON, gros oeuvre + second oeuvre, hors foncier).
    # Calibrate from the Index BT01 / CSTB references for the region.
    construction_cost_eur_m2: float = 1900.0
    # Depreciation: straight-line floor model. A building loses
    # (1 - floor) of replacement value linearly over `dep_years`, never
    # below `dep_floor` (structures retain site-prep / shell value).
    dep_years: int = 80
    dep_floor: float = 0.25
    # Land share sanity anchors (INSEE comptes de patrimoine: terrains bâtis
    # ~45-50% of household real estate nationally; dense cores higher,
    # periphery lower). Used to clip/flag, not to impose.
    land_share_bounds: tuple = (0.15, 0.85)
    # Split-rate ratio for the headline scenario (LVTShift convention)
    split_rate_ratio: float = 4.0


# ------------------------------------------------------------------ #
# Open data endpoints (verify at runtime; all Licence Ouverte / Etalab)
# ------------------------------------------------------------------ #

DATA_SOURCES = {
    # DVF géolocalisé (Etalab): per-commune CSV, 5 rolling years
    # pattern: {year}, {dep}, {insee}
    "dvf": "https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/communes/{dep}/{insee}.csv",

    # Cadastre Etalab: parcel polygons (geojson.gz), per commune
    "cadastre_parcelles": (
        "https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/"
        "geojson/communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz"
    ),

    # BDNB (CSTB, open data): building-level database merging BD TOPO
    # geometry+height, DPE, and fichiers-fonciers-matched attributes.
    # Download by departement from data.gouv.fr ("bdnb" dataset) or the
    # CSTB API. THE key open source for improvement values.
    "bdnb_info": "https://www.data.gouv.fr/fr/datasets/base-de-donnees-nationale-des-batiments/",

    # Fallback if BDNB join is poor: BD TOPO batiment via IGN Géoplateforme WFS
    # (layer BDTOPO_V3:batiment, bbox query, returns HAUTEUR + NB_ETAGES
    # + fichiers-fonciers-matched usage fields).
    "bdtopo_wfs": "https://data.geopf.fr/wfs/ows",

    # DPE logements (ADEME): queryable API, filter by code INSEE.
    # Covariates only (surface, periode construction) - NOT representative
    # of the stock (sale/rental/new-build selection bias).
    "dpe_api": (
        "https://data.ademe.fr/data-fair/api/v1/datasets/"
        "dpe-v2-logements-existants/lines"
    ),

    # REI (DGFiP): communal tax bases, rates and produits, all taxes.
    # Gives the EXACT revenue-neutrality target.
    "rei": "https://www.data.gouv.fr/fr/datasets/r/{resource_id}",  # resolve on data.gouv.fr 'REI'

    # Filosofi (INSEE): IRIS-level income (median, deciles, poverty).
    "filosofi_info": "https://www.insee.fr/fr/statistiques/7233950",  # check latest millesime

    # IRIS contours (IGN/INSEE)
    "iris_contours": "https://www.data.gouv.fr/fr/datasets/contours-iris/",
}

GRENOBLE = CommuneConfig("38185", "Grenoble", "38")
ANNEMASSE = CommuneConfig("74012", "Annemasse", "74")
