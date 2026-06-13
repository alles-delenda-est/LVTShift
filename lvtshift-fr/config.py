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

    # Buildings: BD TOPO V3 'batiment' via IGN Géoplateforme WFS (chosen over
    # the multi-GB BDNB departmental packages). The layer carries everything we
    # need per-commune, no bulk download: footprint geometry, hauteur,
    # nombre_d_etages, nombre_de_logements, usage_1, date_d_apparition, plus
    # appariement_fichiers_fonciers (the FF-match quality flag — same content
    # BDNB exposes, since both inherit the CEREMA MAJIC match). Queried by
    # commune bbox in EPSG:2154, paginated (5000/req). See ingest.fetch_buildings.
    "bdtopo_wfs": "https://data.geopf.fr/wfs/ows",

    # BDNB kept only as documentation/fallback if a richer building match is
    # ever needed (departmental download from data.gouv.fr 'bdnb').
    "bdnb_info": "https://www.data.gouv.fr/fr/datasets/base-de-donnees-nationale-des-batiments/",

    # DPE logements (ADEME): queryable API, filter by code INSEE.
    # Covariates only (surface, periode construction) - NOT representative
    # of the stock (sale/rental/new-build selection bias).
    "dpe_api": (
        "https://data.ademe.fr/data-fair/api/v1/datasets/"
        "dpe-v2-logements-existants/lines"
    ),

    # REI (DGFiP), territorialised at commune level by OFGL on an Opendatasoft
    # API. Long format: one row per commune × dispositif_fiscal × variable,
    # keyed on `idcom` (INSEE code). Foncier bâti is dispositif_fiscal="FB";
    # the revenue target is the "MONTANT RÉEL" line per beneficiary layer
    # (destinataire Commune / GFP). See ingest.fetch_rei_tfpb_produit.
    "ofgl_rei": "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei/records",

    # Filosofi (INSEE): IRIS-level income (median, deciles, poverty).
    "filosofi_info": "https://www.insee.fr/fr/statistiques/7233950",  # check latest millesime

    # IRIS contours (IGN/INSEE)
    "iris_contours": "https://www.data.gouv.fr/fr/datasets/contours-iris/",
}

# ------------------------------------------------------------------ #
# Communes
# ------------------------------------------------------------------ #
# construction_cost_eur_m2 is the turnkey replacement cost (gros + second
# oeuvre, hors foncier, €/m² of floor area). These are *pilot* values on a
# coarse regional gradient — Île-de-France > big metros > rural — anchored on
# FFB / Index BT01 orders of magnitude. They MUST be recalibrated against a
# regional FFB cost series before publication; a ±15 % move here flows linearly
# into improvement value, so it is a first-order sensitivity, not a detail.
# (Reported alongside the land-share band, per the README's Limites connues.)

# Pre-existing (Alpes / Haute-Savoie)
GRENOBLE = CommuneConfig("38185", "Grenoble", "38", construction_cost_eur_m2=1900.0)
ANNEMASSE = CommuneConfig("74012", "Annemasse", "74", construction_cost_eur_m2=1900.0)

# Representative pilot set (geographically + typologically diverse).
# NB: inner Lyon uses Villeurbanne, not a Lyon arrondissement — Paris/Lyon/
# Marseille arrondissements have INSEE codes for cadastre/DVF/buildings but no
# separate taxe foncière (the city + métropole levy it), so OFGL's REI carries
# no per-arrondissement FB produit. Villeurbanne is the dense, fiscally
# autonomous inner-ring commune of the Lyon core.
VILLEURBANNE = CommuneConfig(       # dense inner-Lyon-core commune (Rhône)
    "69266", "Villeurbanne", "69", construction_cost_eur_m2=1950.0)
ROUBAIX = CommuneConfig(            # post-industrial Nord metro, high vacancy
    "59512", "Roubaix", "59", construction_cost_eur_m2=1750.0)
CAHORS = CommuneConfig(             # le Lot préfecture, small rural town
    "46042", "Cahors", "46", construction_cost_eur_m2=1650.0)
MONTREUIL = CommuneConfig(          # Île-de-France inner suburb (Seine-St-Denis)
    "93048", "Montreuil", "93", construction_cost_eur_m2=2150.0)
FIGEAC = CommuneConfig(             # second town of le Lot, deep-rural contrast
    "46102", "Figeac", "46", construction_cost_eur_m2=1600.0)

# Registry for the CLI / run_commune driver (--commune <key>)
COMMUNES = {
    "grenoble": GRENOBLE, "annemasse": ANNEMASSE,
    "villeurbanne": VILLEURBANNE, "roubaix": ROUBAIX, "cahors": CAHORS,
    "montreuil": MONTREUIL, "figeac": FIGEAC,
}
