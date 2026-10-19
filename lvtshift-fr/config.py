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
    # Maintained stock: where neighbourhood prices far exceed rebuild cost,
    # owners renovate, so age stops measuring wear (effective age, see
    # METHODOLOGY §3.1). Effective age = w·min(age, cap) + (1−w)·age, with w
    # ramping linearly from 0 to 1 as q = IRIS median price/m² ÷ construction
    # cost goes from dep_q_ramp[0] to dep_q_ramp[1]. None disables it.
    dep_maintained_age_cap: int | None = 30
    dep_q_ramp: tuple = (1.2, 2.5)
    # Land share sanity anchors (INSEE comptes de patrimoine: terrains bâtis
    # ~45-50% of household real estate nationally; dense cores higher,
    # periphery lower). Used to clip/flag, not to impose.
    land_share_bounds: tuple = (0.15, 0.85)
    # Split-rate ratio for the headline scenario (LVTShift convention)
    split_rate_ratio: float = 4.0
    # Paris / Lyon / Marseille: the commune levies the taxe foncière under its
    # own INSEE code (75056, 69123 — the code REI is keyed on), but cadastre,
    # DVF, DPE and IRIS are published per *arrondissement* (75101…75120,
    # 69381…69389). `sub_codes` lists those data codes; empty = ordinary
    # commune whose data and levy share one code.
    sub_codes: tuple = ()
    # Output-file/registry key override (ASCII); default derives from name.
    key: str = ""

    @property
    def data_codes(self) -> tuple:
        """INSEE codes under which parcel-level open data are published."""
        return tuple(self.sub_codes) or (self.insee_code,)

    @property
    def slug(self) -> str:
        """Output-file stem (output/<slug>.csv). Legacy panel communes keep
        their historical name-derived stem; new configs use the ASCII key."""
        return self.key or self.name.lower().replace(" ", "")


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

    # DGFiP « Fichiers des locaux et des parcelles des personnes morales »
    # (Licence Ouverte 2.0, annual). Catalog of yearly zip attachments; ids change
    # every vintage, so exemptions._attachments() matches them by pattern.
    "pm_catalog": ("https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
                   "fichiers-des-locaux-et-des-parcelles-des-personnes-morales/attachments"),

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
SETE = CommuneConfig(               # Méditerranée — port/tourist, second homes
    "34301", "Sète", "34", construction_cost_eur_m2=1850.0)
LA_ROCHELLE = CommuneConfig(        # Atlantique — prosperous tourist port
    "17300", "La Rochelle", "17", construction_cost_eur_m2=1850.0)
MULHOUSE = CommuneConfig(           # Est/Rhin — Alsatian post-industrial, vacant
    "68224", "Mulhouse", "68", construction_cost_eur_m2=1800.0)

# Intra-muros Paris and Lyon: one fiscal commune (REI code) whose parcel data
# live under the arrondissement codes. Construction costs: see the PARIS_LYON
# note below — pilot values pending the FFB/BT01 calibration work item.
PARIS = CommuneConfig(
    "75056", "Paris", "75", construction_cost_eur_m2=2300.0,
    sub_codes=tuple(f"751{n:02d}" for n in range(1, 21)), key="paris")
LYON = CommuneConfig(
    "69123", "Lyon", "69", construction_cost_eur_m2=1950.0,
    sub_codes=tuple(f"6938{n}" for n in range(1, 10)), key="lyon")

# Registry for the CLI / run_commune driver (--commune <key>)
COMMUNES = {
    "grenoble": GRENOBLE, "annemasse": ANNEMASSE,
    "villeurbanne": VILLEURBANNE, "roubaix": ROUBAIX, "cahors": CAHORS,
    "montreuil": MONTREUIL, "figeac": FIGEAC,
    "sete": SETE, "larochelle": LA_ROCHELLE, "mulhouse": MULHOUSE,
    "paris": PARIS, "lyon": LYON,
}


# ------------------------------------------------------------------ #
# Extra-muros territories (inner rings), modelled commune by commune
# ------------------------------------------------------------------ #
# Each member commune is run on its OWN levy and held revenue-neutral on its
# own (communes set their own TFPB rate — the legally realistic case); the
# territory figures are then aggregates of those per-commune runs, never a
# pooled metropolitan rate. Membership is frozen in territories.py.
from territories import LYON_EXTRA_MUROS, PARIS_EXTRA_MUROS  # noqa: E402

# Communes published individually on the site (the panel + Paris + Lyon).
# Territory members are published only inside their territory aggregate —
# 177 extra picker entries would swamp the explorer and its bundle.
SITE_COMMUNES = tuple(COMMUNES)

# Pilot construction cost by territory (same gradient as the existing panel:
# Île-de-France inner ring = Montreuil's 2150, Lyon ring = Villeurbanne's 1950).
TERRITORY_COST_EUR_M2 = {"paris-extra-muros": 2150.0, "lyon-extra-muros": 1950.0}


def commune_key(name: str) -> str:
    """ASCII registry/site key for a commune name: 'L'Haÿ-les-Roses' -> 'l-hay-les-roses'."""
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _territory_members(rows, territory: str) -> list:
    """Member keys for a territory, registering a config for each commune.

    Reuses an existing panel config when the INSEE code is already configured
    (Montreuil, Villeurbanne), so a commune is never modelled twice with
    different parameters.
    """
    by_insee = {c.insee_code: k for k, c in COMMUNES.items()}
    keys = []
    for insee, name, dep in rows:
        if insee in by_insee:
            keys.append(by_insee[insee])
            continue
        key = commune_key(name)
        if key in COMMUNES:
            raise ValueError(f"commune key collision: {key} ({insee})")
        COMMUNES[key] = CommuneConfig(
            insee, name, dep, key=key,
            construction_cost_eur_m2=TERRITORY_COST_EUR_M2[territory])
        keys.append(key)
    return keys


TERRITORIES = {
    "paris-extra-muros": {
        "name": "Paris extra-muros (petite couronne)",
        "departement": "92/93/94",
        "members": _territory_members(PARIS_EXTRA_MUROS, "paris-extra-muros"),
    },
    "lyon-extra-muros": {
        "name": "Lyon extra-muros (Métropole hors Lyon)",
        "departement": "69",
        "members": _territory_members(LYON_EXTRA_MUROS, "lyon-extra-muros"),
    },
}

# Keys of the Métropole de Lyon communes (price-index geography).
LYON_METROPOLE_KEYS = frozenset(TERRITORIES["lyon-extra-muros"]["members"])


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
    "34": (0.80, 0.50),        # Hérault — Méditerranée, vignoble/maraîchage
    "17": (0.75, 0.45),        # Charente-Maritime — Atlantique cropland
    "68": (0.95, 0.55),        # Haut-Rhin — rich Alsatian plain
    # Petite couronne: almost no A/N zoning survives; the few parcels are
    # parks/allotments. Priced on the Île-de-France cropland anchor (as 93).
    "75": (1.00, 0.60),
    "92": (1.00, 0.60),
    "94": (1.00, 0.60),
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


def slug_of(cfg) -> str:
    """Output stem for any config-like object (tests pass lightweight fakes)."""
    return getattr(cfg, "slug", None) or cfg.name.lower().replace(" ", "")


def data_codes_of(cfg) -> tuple:
    """Data INSEE codes for any config-like object (see CommuneConfig.data_codes)."""
    return getattr(cfg, "data_codes", None) or (cfg.insee_code,)


# INSEE codes of the Métropole de Lyon (Lyon, Villeurbanne and the 57-commune
# ring): where the Métropole's own property counts as on its territory
# (exemptions._in_territory).
LYON_METROPOLE_INSEE = frozenset(
    {"69123", "69266"} | {COMMUNES[k].insee_code for k in LYON_METROPOLE_KEYS})
