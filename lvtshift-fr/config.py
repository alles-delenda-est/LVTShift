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

    # Géoportail de l'Urbanisme (GPU) zoning, same Géoplateforme WFS as BD TOPO.
    # Layer 'wfs_du:zone_urba' carries typezone U/AU/A/N — the legal
    # constructibility signal used to classify building-less parcels (priced as
    # development land vs agricultural/natural land). Queried by commune bbox.
    "gpu_zone_urba_layer": "wfs_du:zone_urba",

    # DPE logements existants (ADEME, depuis juillet 2021): data-fair API,
    # filter by code_insee_ban. We use `periode_construction` (era band) +
    # `_geopoint` to anchor depreciation per parcel — far better than BD TOPO's
    # date_d_apparition, which is the database first-appearance date (often
    # null: 100 % of Cahors buildings) not a true construction year.
    # Caveat: residential only, and covers diagnosed dwellings (sale/rental/
    # renovation), so it under-covers never-traded and non-residential stock —
    # used where present, with a documented fallback.
    "dpe_lines": (
        "https://data.ademe.fr/data-fair/api/v1/datasets/"
        "meg-83tjwtg8dyz4vv7h1dqe/lines"
    ),

    # REI (DGFiP), territorialised at commune level by OFGL on an Opendatasoft
    # API. Long format: one row per commune × dispositif_fiscal × variable,
    # keyed on `idcom` (INSEE code). Foncier bâti is dispositif_fiscal="FB";
    # the revenue target is the "MONTANT RÉEL" line per beneficiary layer
    # (destinataire Commune / GFP). See ingest.fetch_rei_tfpb_produit.
    "ofgl_rei": "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/rei/records",

    # Filosofi (INSEE): IRIS-level income. 2021 is the last produced vintage
    # (2022 not published). CSV zip -> BASE_TD_FILO_IRIS_2021_DISP.csv (sep ';'),
    # keyed on IRIS (9-digit code_iris), median = DISP_MED21. Covers communes
    # >= 5 000 inhabitants only.
    "filosofi_iris_csv": "https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip",

    # IRIS contours, same Géoplateforme WFS. Layer attribute code_iris is the
    # 9-digit IRIS code that joins to Filosofi. Queried by commune bbox.
    "iris_contours_layer": "STATISTICALUNITS.IRIS:contours_iris",
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


# ------------------------------------------------------------------ #
# Land-valuation benchmarks (classify-then-price; see THEORY.md)
# ------------------------------------------------------------------ #
# Building-less parcels are classified by GPU zoning (U/AU -> constructible,
# A/N -> agricultural/natural) and priced against the right open benchmark.
# These tables are *pilot* anchors — refine from the primary sources before
# publication. Crucially, agricultural land is ~2-3 orders of magnitude cheaper
# than building land, so getting the *class* right matters far more than the
# exact €/m²: a ±50 % error on a 0.6 €/m² farm rate is immaterial to the levy.

# SAFER "Le prix des terres" 2024, €/m² (= €/ha ÷ 10 000), terres & prés libres.
# National default 0.64; a few pilot départements nudged on the SAFER gradient.
# Natural/forest (N zones) priced slightly below cropland.
AG_EUR_M2_BY_DEP = {           # (agricultural A, natural/forest N)
    "_default": (0.64, 0.49),
    "46": (0.45, 0.35),        # Lot — Sud-Ouest, cheaper upland
    "93": (1.00, 0.60),        # Seine-St-Denis — rich Plaine-de-France cropland
    "59": (0.85, 0.50),        # Nord — productive cropland
    "69": (0.70, 0.50),        # Rhône
    "74": (0.75, 0.55),        # Haute-Savoie
    "38": (0.60, 0.45),        # Isère
}

# EPTB (SDES) building-plot €/m² fallback when a commune has too few DVF
# terrain-à-bâtir sales for a reliable local median. National métropole ~99 €/m²
# (2023); kept as a single conservative national anchor (the commune DVF median
# is always preferred when available).
EPTB_EUR_M2_FALLBACK = 99.0

# Land-model parameters.
LAND_MODEL = {
    # AU (à urbaniser) discount vs fully-serviced U / AUc land. AU "fermée/
    # stricte" is development-deferred; pricing it at full U value overstates it
    # (Gemini review's main flag). AUc (open) ≈ U; AU/AUs (strict) discounted.
    "au_open_factor": 1.0,
    "au_strict_factor": 0.55,
    # Minimum clean terrain-à-bâtir sales for a *cell*-level constructible €/m²;
    # below this we shrink toward / fall back to the commune median.
    "min_tab_sales_cell": 8,
    "min_tab_sales_commune": 5,
    # Fallback buffer (m) around buildings to call a parcel constructible where
    # GPU has no coverage (RNU communes / uncovered slivers).
    "rnu_building_buffer_m": 25.0,
}

# Current-tax (FB baseline) VLC-proxy sensitivity weights — OFF by default.
# The published baseline distributes the FB produit by floor area only (size is
# the dominant VLC driver). These relative per-m² weights are a *labelled
# sensitivity* to show how a category-differentiated baseline (professionnel m²
# carry more VLC than housing m², esp. post-2017 revision) would shift the
# winners/losers — pass to estimate.current_tax(category_weights=...). NOT a
# measurement: the levels are illustrative, not grounded in per-commune VLC.
# Do NOT tilt toward market value (would erase the 1970 base's real regressivity).
CATEGORY_VLC_WEIGHTS_SENSITIVITY = {
    "maison": 1.0, "appartement": 1.0, "immeuble_collectif": 1.0,
    "commerce": 1.8, "industriel": 1.4, "dependance": 0.5, "terrain_nu": 0.0,
}
