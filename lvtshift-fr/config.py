"""
Configuration for LVTShift-FR: French commune LVT simulation on open data.

All URLs documented as of June 2026 — verify before first run, these
endpoints occasionally move. Network access required for ingest only.
"""

import math
import numbers
from dataclasses import dataclass, field
from types import MappingProxyType


# Habitable area ÷ the model's floor area (BD TOPO footprint × storeys), by DVF
# type, measured on 35 communes from DPE habitable surfaces matched to BD TOPO
# buildings by RNB id (area-weighted; flats 0.59-0.68, houses 0.58-0.66). BD
# TOPO counts attics, raised basements and technical levels as storeys, so
# this is well below a true habitable ÷ gross ratio.
NET_TO_GROSS_DEFAULT = {"Appartement": 0.64, "Maison": 0.61}
# Habitable ÷ true gross area behind the construction costs; dividing a cost by
# it gives the cost per habitable m². Flats: the cost research converted social
# housing costs per m² of surface utile with SU ÷ gross = 0.74, and SU (which
# adds half the annexes) is 1.03-1.05 × habitable area, so 0.74 ÷ 1.04 ≈ 0.71.
# Houses: habitable ÷ gross external ≈ 0.82 (desk estimate: SDP ÷ gross
# 0.85-0.90 × habitable ÷ SDP ≈ 0.93-0.95).
COST_NET_TO_GROSS_DEFAULT = {"Appartement": 0.71, "Maison": 0.82}
AREA_RATIO_TYPES = frozenset({"Appartement", "Maison"})
AREA_RATIO_BOUNDS = (0.3, 1.0)        # plausible habitable ÷ gross range


def check_area_ratios(ratios, name: str = "net_to_gross") -> MappingProxyType:
    """Validate a {type_local: habitable ÷ gross} map and return a read-only copy.

    Exactly the DVF types 'Appartement' and 'Maison' (a misspelt key would
    silently fall back to the flat ratio), each a real number (not a bool or
    a string) within AREA_RATIO_BOUNDS.
    """
    if not hasattr(ratios, "items"):
        raise TypeError(f"{name} must be a mapping, got {type(ratios).__name__}")
    keys = set(ratios)
    if keys != AREA_RATIO_TYPES:
        raise ValueError(f"{name} must have exactly the keys {sorted(AREA_RATIO_TYPES)}, "
                         f"got {sorted(map(str, keys))}")
    lo, hi = AREA_RATIO_BOUNDS
    out = {}
    for k, v in ratios.items():
        if isinstance(v, (bool, str)) or not isinstance(v, numbers.Real):
            raise TypeError(f"{name}[{k!r}] must be a number, got {v!r}")
        v = float(v)
        if not (math.isfinite(v) and lo <= v <= hi):
            raise ValueError(f"{name}[{k!r}] must be in [{lo}, {hi}], got {v!r}")
        out[k] = v
    return MappingProxyType(out)


@dataclass
class CommuneConfig:
    insee_code: str          # e.g. "38185" Grenoble, "74012" Annemasse
    name: str
    departement: str         # "38", "74"
    # DVF years to pool for the hedonic model (more years = more obs,
    # but deflate to a common year with the INSEE/Notaires index)
    dvf_years: tuple = (2021, 2022, 2023, 2024, 2025)
    reference_year: int = 2025
    # Construction cost: 2025 € per m² of GROSS floor area (BD TOPO footprint ×
    # storeys), building only (hors foncier, hors VRD), fees and 20 % VAT
    # included. See the calibration note above the commune list.
    construction_cost_eur_m2: float = 1900.0
    # Both sides of the residual are put on habitable area (METHODOLOGY §3.1):
    # habitable = net_to_gross[type] × the model's floor area; market value =
    # DVF €/m² (habitable) × habitable area; building value = cost per
    # habitable m² (construction_cost_eur_m2 ÷ cost_net_to_gross[type]) ×
    # habitable area. The land share then depends on cost_net_to_gross, not on
    # the measured net_to_gross, which only sets the euro level.
    net_to_gross: dict = field(default_factory=lambda: dict(NET_TO_GROSS_DEFAULT))
    cost_net_to_gross: dict = field(
        default_factory=lambda: dict(COST_NET_TO_GROSS_DEFAULT))
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

    def __post_init__(self):
        # validate once at construction, and freeze the maps so a later edit to
        # one config can never leak into another that shares them (copy.copy)
        self.net_to_gross = check_area_ratios(self.net_to_gross, "net_to_gross")
        self.cost_net_to_gross = check_area_ratios(self.cost_net_to_gross,
                                                   "cost_net_to_gross")

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
    # Notaires-INSEE « indice des prix des logements anciens » (IPLA), quarterly,
    # base 100 = 2015, série brute, via the INSEE BDM SDMX API (no key). One
    # series per idbank; see PRICE_INDEX_IDBANKS for the geography mapping.
    "insee_bdm_series": "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/{idbank}?startPeriod={start}",

    # Filosofi (INSEE): IRIS-level income, 2021 vintage. NB: INSEE published a
    # « Filosofi 2 » 2023 vintage with IRIS-level indicators in May 2026
    # (methodological break, not directly comparable with 2021); 2021 is
    # retained here pending evaluation — see METHODOLOGY §6. CSV zip ->
    # BASE_TD_FILO_IRIS_2021_DISP.csv (sep ';'), keyed on IRIS (9-digit
    # code_iris), median = DISP_MED21. Covers communes >= 5 000 inhabitants only.
    "filosofi_iris_csv": "https://www.insee.fr/fr/statistiques/fichier/8229323/BASE_TD_FILO_IRIS_2021_DISP_CSV.zip",

    # IRIS contours, same Géoplateforme WFS. Layer attribute code_iris is the
    # 9-digit IRIS code that joins to Filosofi. Queried by commune bbox.
    "iris_contours_layer": "STATISTICALUNITS.IRIS:contours_iris",
}

# ------------------------------------------------------------------ #
# Communes
# ------------------------------------------------------------------ #
# construction_cost_eur_m2 is the turnkey replacement cost of a modern
# equivalent building: 2025 €, per m² of gross floor area, hors foncier and hors
# VRD, architects'/engineers' fees and 20 % VAT included, developer margin
# excluded. Paris, the Paris inner ring (incl. Montreuil), Lyon (incl.
# Villeurbanne) and the Lyon ring are calibrated on the DHUP/SISAL « Bilan des
# logements aidés » 2021-22 building-only cost of new social housing, indexed
# to 2025 with INSEE BT01 and converted to gross area (METHODOLOGY §3.1):
# central values, plausible ranges Paris 2 350-3 100, inner ring 2 150-2 700,
# Lyon 1 750-2 300, Lyon ring 1 600-2 100. The other panel communes keep their
# pilot values on the SDES house-cost survey (EPTB) gradient. A ±15 % move
# flows linearly into improvement value: a first-order sensitivity, reported
# alongside the land-share band.

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
    "69266", "Villeurbanne", "69", construction_cost_eur_m2=2000.0)
ROUBAIX = CommuneConfig(            # post-industrial Nord metro, high vacancy
    "59512", "Roubaix", "59", construction_cost_eur_m2=1750.0)
CAHORS = CommuneConfig(             # le Lot préfecture, small rural town
    "46042", "Cahors", "46", construction_cost_eur_m2=1650.0)
MONTREUIL = CommuneConfig(          # Île-de-France inner suburb (Seine-St-Denis)
    "93048", "Montreuil", "93", construction_cost_eur_m2=2400.0)
FIGEAC = CommuneConfig(             # second town of le Lot, deep-rural contrast
    "46102", "Figeac", "46", construction_cost_eur_m2=1600.0)
SETE = CommuneConfig(               # Méditerranée — port/tourist, second homes
    "34301", "Sète", "34", construction_cost_eur_m2=1850.0)
LA_ROCHELLE = CommuneConfig(        # Atlantique — prosperous tourist port
    "17300", "La Rochelle", "17", construction_cost_eur_m2=1850.0)
MULHOUSE = CommuneConfig(           # Est/Rhin — Alsatian post-industrial, vacant
    "68224", "Mulhouse", "68", construction_cost_eur_m2=1800.0)

# Intra-muros Paris and Lyon: one fiscal commune (REI code) whose parcel data
# live under the arrondissement codes. Construction costs: see the
# calibration note above.
PARIS = CommuneConfig(
    "75056", "Paris", "75", construction_cost_eur_m2=2650.0,
    sub_codes=tuple(f"751{n:02d}" for n in range(1, 21)), key="paris")
LYON = CommuneConfig(
    "69123", "Lyon", "69", construction_cost_eur_m2=2000.0,
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

# Construction cost by territory (calibration note above; the Paris ring
# shares Montreuil's value).
TERRITORY_COST_EUR_M2 = {"paris-extra-muros": 2400.0, "lyon-extra-muros": 1850.0}


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

# SAFER « Le prix des terres », édition 2025 (marché 2024), €/m² (= €/ha ÷
# 10 000), terres & prés libres. The 6 400 €/ha national figure is from the
# 2025 publication covering 2024 sales — NOT the 2024 publication, which
# reported 6 200 €/ha for 2023 sales (the 2026 edition, 2025 sales, gives
# 6 460). National default 0.64; a few pilot départements nudged on the SAFER
# gradient. Natural/forest (N zones) priced slightly below cropland.
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

# Price deflator (spec 0001). DVF sales are pooled over `dvf_years`; prices rose
# to 2022 and then corrected, by very different amounts by place (Paris flats
# −10 % 2022→2025, Lyon −13.5 %, Marseille +0 %, France −4 %). Each sale is
# brought to `reference_year` euros with factor(Y) = avg(index, ref) / avg(index,
# Y), using the most local Notaires-INSEE series INSEE publishes, by dwelling
# type. Values are fetched live (ingest.fetch_price_index_annual); series
# verified 2026-10-19 against the BDM dataflow IPLA-IPLNA-2015 (raw series).
# Agglomeration series (A_69123 « Agglomération de Lyon », A_13055 Marseille,
# Lille houses) cover the urban area, not only the central commune.
PRICE_INDEX_IDBANKS = {
    # geography: (Appartement idbank, Maison idbank). A type-specific pair is
    # used only when both series exist for the same geography.
    "paris": ("010567012", "010567012"),          # Paris: flats only (no houses series)
    "d92": ("010567032", "010567036"),             # Hauts-de-Seine
    "d93": ("010567038", "010567042"),             # Seine-Saint-Denis
    "d94": ("010567044", "010567048"),             # Val-de-Marne
    # Agglomerations publish one dwelling type only; it is used for both types.
    # Mixing a local flats series with a regional houses series would move
    # houses against flats by the city-vs-region gap (Lyon: −13.5 % vs −4 %
    # 2022→2025), although within a region the two types moved alike.
    "agglo_lyon": ("010567010", "010567010"),      # Agglomération de Lyon, flats
    "agglo_marseille": ("010567006", "010567006"),  # Agglomération de Marseille, flats
    "agglo_lille": ("010567008", "010567008"),     # Agglomération de Lille, houses
    "auvergne_rhone_alpes": ("010567128", "010567132"),
    "paca": ("010567110", "010567114"),
    "nord_pas_de_calais": ("010567098", "010567102"),
    "province": ("010567062", "010567074"),        # default outside Île-de-France
}
_ARA_DEPS = {"01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"}
_PACA_DEPS = {"04", "05", "06", "13", "83", "84"}


def price_index_geography(cfg) -> str:
    """Key into PRICE_INDEX_IDBANKS for a commune (most local series first)."""
    dep = cfg.departement
    if dep == "75":
        return "paris"
    if dep in ("92", "93", "94"):
        return "d" + dep
    if cfg.insee_code in LYON_METROPOLE_INSEE:
        return "agglo_lyon"
    if cfg.insee_code == "13055":
        return "agglo_marseille"
    if cfg.insee_code in LILLE_AGGLO_INSEE:
        return "agglo_lille"
    if dep in _ARA_DEPS:
        return "auvergne_rhone_alpes"
    if dep in _PACA_DEPS:
        return "paca"
    if dep in ("59", "62"):
        return "nord_pas_de_calais"
    return "province"


# Communes of the Lille agglomeration among those modelled (Roubaix).
LILLE_AGGLO_INSEE = {"59350", "59512", "59599"}   # Lille, Roubaix, Tourcoing


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
