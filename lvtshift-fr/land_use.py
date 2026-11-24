"""
What building-less land inside an urban zone can be used for.

A PLU zone of type U is not all housing land. Plans also carve out "dedicated"
urban zones: parks (Grenoble and Paris "UV", La Rochelle "UV"), business and
port estates (La Rochelle "UX"/"UP", Grenoble "UE"), rail yards and utilities
(Paris "UGSU"). The model used to price every building-less U parcel at the
commune's median building-plot sale, so a private park or an 11-hectare port
plot was valued as housing land.

Two independent readings decide the use of each building-less parcel:

* the plan itself (`zone_use`): the CNIG "vocation dominante" code
  (`destdomi`) and, where it is missing or "sans objet" (most plans: 2 % of
  the zones in the published territories carry it), keywords in the zone's
  long label (`libelong`, filled for 98 %). Short labels (UV, UX, UE…) mean
  different things in different plans and are never read on their own;
* BD TOPO (`bdtopo_use_shares`): the share of the parcel covered by public
  open space (parks, squares, gardens), cemeteries, sports grounds and water,
  or by business, transport and public-facility sites.

`vacant_use` combines them: the plan decides where it states a use (the tax
is on land at its permitted use; BD TOPO maps current use); BD TOPO fills in
where the plan is silent. Open space stays inside the reform, valued as
natural land. `cross_check` tabulates where the two readings agree, for the run
log and the methodology.
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

HOUSING, ACTIVITY, OPEN_SPACE = "housing", "activity", "open_space"

# CNIG standard PLU, attribute DESTDOMI ("vocation dominante de la zone").
DESTDOMI_USE = {
    "01": HOUSING,      # habitat
    "03": HOUSING,      # mixte habitat / activité
    "02": ACTIVITY,     # activité
    "04": ACTIVITY,     # loisirs et tourisme (hotels, campsites: not housing plots)
    "05": ACTIVITY,     # équipement
    "10": ACTIVITY,     # carrière
    "07": OPEN_SPACE,   # activité agricole
    "08": OPEN_SPACE,   # espace naturel
    "09": OPEN_SPACE,   # espace remarquable (littoral, montagne)
}
# "00" (sans objet), "99" (autre) and blanks fall through to the long label.

# Keywords in the zone's long label, accents and case removed. A label often
# names its main use first and then what else it allows ("Habitat collectif en
# R+5 avec bureaux autorisés", "Parc d'activités … comprenant du logement"), so
# the class whose keyword appears EARLIEST in the label wins. Open-space words
# count in U zones only: an AU zone "naturel ou agricole destiné à recevoir une
# urbanisation à long terme" is future building land, which the AU discount
# already prices.
# Words are matched as substrings, so each must not occur inside a compound
# of another class ("cités-jardins" are housing estates, "zone urbaine
# paysagère" is housing with landscape rules): open-space words are specific
# phrases, never bare "jardin", "paysager" or "naturel". At equal position the
# longer keyword wins ("tissu d'activités" over "tissu", "village
# d'entreprises" over "village").
HOUSING_WORDS = (
    "habitat", "logement", "residenti", "tissu urbain", "tissus urbains", "tissu",
    "centre-ville", "centres-villes", "centre ancien", "centre-bourg", "bourg",
    "village", "hameau", "pavillon", "individuel", "faubourg", "maison",
    "cite jardin", "cites jardins", "cite-jardin", "cites-jardins",
)
OPEN_SPACE_WORDS = (
    "parc urbain", "parcs urbains", "urbaine verte", "zone verte", "espace vert",
    "espaces verts", "jardins familiaux", "jardins partages", "jardin public",
    "jardins publics", "square", "cimetiere", "coulee verte", "loisirs de plein air",
)
ACTIVITY_WORDS = (
    "tissu d activite", "tissus d activite", "village d entreprise",
    "activite", "economique", "industri", "artisan", "commerc", "tertiaire",
    "technolog", "logisti", "portuaire", r"\bports?\b", "bureaux", "ferroviaire",
    "voie ferree", "grands services urbains", "infrastructure", "aeroport",
    "aerodrome", "autoroute", "zone d equipement", "secteur d equipement",
    "equipements d interet collectif", "equipements collectifs", "equipements publics",
    "services publics", "hospital", "hopital", "du chu", "universit", "militaire",
    "defense nationale", "penitentiaire", "plaisance", "nautique",
    "touristi",
)
# Words introducing what a zone is for: the first keyword after the earliest of
# them decides ("secteur situé en frange de tissus résidentiels et dédié aux
# activités économiques" is business land). "emplacements réservés" and
# "réserve foncière" are secondary planning overlays, not the zone's purpose.
PURPOSE_WORDS = ("dedie", "vocation", "destine", "dominante", "devolu", "reserve")
_NON_PURPOSE_RE = re.compile(r"\b(?:emplacements?\s+reserves?|reserves?\s+foncieres?)\b")


def _label_use(label: str, allow_open: bool) -> str | None:
    """Class of the keyword appearing earliest in a normalised label, read
    from its statement of purpose when it has one (PURPOSE_WORDS)."""
    probe = _NON_PURPOSE_RE.sub(lambda m: " " * len(m.group(0)), label)
    anchors = [i for i in (probe.find(w) for w in PURPOSE_WORDS) if i >= 0]
    if anchors:
        hit = _earliest(label[min(anchors):], allow_open)
        if hit is not None:
            return hit
    return _earliest(label, allow_open)


def _find_word(label: str, word: str) -> int:
    if word.startswith(r"\b"):
        m = re.search(word, label)
        return m.start() if m else -1
    return label.find(word)


def _earliest(label: str, allow_open: bool) -> str | None:
    best, key = None, None
    for use, words in ((HOUSING, HOUSING_WORDS), (OPEN_SPACE, OPEN_SPACE_WORDS),
                       (ACTIVITY, ACTIVITY_WORDS)):
        if use == OPEN_SPACE and not allow_open:
            continue
        for w in words:
            i = _find_word(label, w)
            if i >= 0 and (key is None or (i, -len(w)) < key):
                best, key = use, (i, -len(w))
    return best


def _norm(text) -> str:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""
    # Replace curly and straight apostrophes BEFORE ASCII stripping so
    # "d’activités" becomes "d activites" rather than "dactivites".
    raw = str(text)
    for ch in ("'", "\u2019", "\u2018", "\u02bc"):
        raw = raw.replace(ch, " ")
    s = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


def _code(v) -> str:
    """A destdomi value as its two-digit code ("1", 1, 1.0 -> "01")."""
    s = _norm(v)
    if not s:
        return ""
    try:
        return f"{int(float(s)):02d}"
    except ValueError:
        return s


def zone_use(zone_typ: pd.Series, destdomi: pd.Series | None = None,
             libelong: pd.Series | None = None) -> pd.Series:
    """The plan's stated use of each parcel's zone: housing, activity,
    open_space, or None where the plan says nothing usable.

    Only urban and to-be-urbanised zones (U, AU…) are read; A and N zones are
    open space by type. A U zone with no usable code or label stays None and is
    treated as housing land, the model's default for type U."""
    idx = zone_typ.index
    typ = zone_typ.astype("object")
    code = (destdomi.astype("object").map(_code) if destdomi is not None
            else pd.Series("", index=idx))
    label = (libelong.map(_norm) if libelong is not None else pd.Series("", index=idx))

    out = pd.Series(None, index=idx, dtype="object")
    by_code = code.map(DESTDOMI_USE)
    out = out.where(by_code.isna(), by_code)
    urban = typ.astype(str).str.startswith("U")
    by_label = pd.Series([_label_use(lab, bool(u)) for lab, u in zip(label, urban)],
                         index=idx, dtype="object")
    out = out.where(out.notna(), by_label)
    out = out.mask(typ.isin(["A", "N"]), OPEN_SPACE)
    return out


# BD TOPO V3 layers read for the cross-check (IGN Géoplateforme WFS), and the
# use each feature stands for. zone_d_activite_ou_d_interet is split by its
# nature/categorie attributes in `bdtopo_feature_use`.
BDTOPO_LAND_USE_LAYERS = (
    "BDTOPO_V3:zone_d_activite_ou_d_interet",
    "BDTOPO_V3:cimetiere",
    "BDTOPO_V3:terrain_de_sport",
    "BDTOPO_V3:equipement_de_transport",
    "BDTOPO_V3:surface_hydrographique",
)
ZAI_OPEN_NATURES = {"espace public", "parc de loisirs", "jardin public"}
ZAI_OPEN_CATEGORIES = {"sport"}
# Values checked live on the WFS (Grenoble, 2026-11-24): categorie
# "Culture et loisirs" with nature "Espace public" (parks, squares); schools
# and research share one category, "Science et enseignement".
ZAI_ACTIVITY_CATEGORIES = {
    "industriel et commercial", "transport", "science et enseignement", "sante",
    "administratif ou militaire", "gestion des eaux",
}
# equipement_de_transport natures that are road space or under-used land,
# not business land
TRANSPORT_NOT_ACTIVITY = ("parking", "carrefour")


def bdtopo_feature_use(layer: str, props: dict) -> str | None:
    """open_space, activity or None for one BD TOPO feature."""
    layer = layer.split(":")[-1]
    if layer in ("cimetiere", "terrain_de_sport", "surface_hydrographique"):
        return OPEN_SPACE
    if layer == "equipement_de_transport":
        # a surface car park is under-used land, not business land
        nature = _norm(props.get("nature"))
        return None if any(w in nature for w in TRANSPORT_NOT_ACTIVITY) else ACTIVITY
    if layer == "zone_d_activite_ou_d_interet":
        nature = _norm(props.get("nature"))
        cat = _norm(props.get("categorie"))
        if nature in ZAI_OPEN_NATURES or cat in ZAI_OPEN_CATEGORIES:
            return OPEN_SPACE
        if cat in ZAI_ACTIVITY_CATEGORIES:
            return ACTIVITY
    return None


def bdtopo_use_shares(parcels_gdf, features_gdf) -> pd.DataFrame:
    """Share of each parcel's area covered by BD TOPO open space and by
    business/transport/facility sites (each use's features dissolved first,
    so overlapping features are not counted twice).

    parcels_gdf: idpar + geometry (metric CRS). features_gdf: geometry + use.
    Returns idpar, bdtopo_open_share, bdtopo_activity_share (0 where none)."""
    import geopandas as gpd

    out = pd.DataFrame({"idpar": parcels_gdf["idpar"].values,
                        "bdtopo_open_share": 0.0, "bdtopo_activity_share": 0.0})
    if features_gdf is None or not len(features_gdf):
        return out
    area = parcels_gdf.geometry.area.to_numpy()
    for use, col in ((OPEN_SPACE, "bdtopo_open_share"), (ACTIVITY, "bdtopo_activity_share")):
        f = features_gdf[features_gdf["use"].eq(use)]
        f = f[f.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        if not len(f):
            continue
        u = gpd.GeoDataFrame(geometry=[f.geometry.union_all()], crs=features_gdf.crs)
        inter = gpd.overlay(parcels_gdf[["idpar", "geometry"]], u, how="intersection",
                            keep_geom_type=True)
        cov = inter.assign(a=inter.geometry.area).groupby("idpar")["a"].sum()
        covered = out["idpar"].map(cov).fillna(0.0).to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            out[col] = np.clip(np.where(area > 0, covered / area, 0.0), 0.0, 1.0)
    return out


def vacant_use(plan_use: pd.Series, open_share: pd.Series, activity_share: pd.Series,
               threshold: float = 0.5) -> pd.DataFrame:
    """Use of each building-less parcel from the two readings.

    The plan decides where it states a use: the tax is on land at its
    permitted use, and BD TOPO maps current use (a car park or a private
    sports ground in a housing zone stays housing land). Where the plan is
    silent, BD TOPO fills in: open space where it covers at least `threshold`
    of the parcel with open space, else business land at the same cover, else
    housing land. Returns columns vacant_use and vacant_use_source ("plan",
    "both" where BD TOPO agrees, "bdtopo" where it filled a silent plan, or
    "default")."""
    if not 0.0 < threshold <= 1.0:
        raise ValueError(f"threshold must be in (0, 1], got {threshold}")
    plan = plan_use.astype("object")
    bt_open = pd.to_numeric(open_share, errors="coerce").fillna(0.0) >= threshold
    bt_act = pd.to_numeric(activity_share, errors="coerce").fillna(0.0) >= threshold
    p_open, p_act = plan.eq(OPEN_SPACE), plan.eq(ACTIVITY)

    p_house, silent = plan.eq(HOUSING), plan.isna()
    use = np.select([p_open, p_act, p_house, silent & bt_open, silent & bt_act],
                    [OPEN_SPACE, ACTIVITY, HOUSING, OPEN_SPACE, ACTIVITY], HOUSING)
    src = np.select(
        [p_open & bt_open, p_act & bt_act, p_house & ~bt_open & ~bt_act,
         p_open | p_act | p_house, silent & (bt_open | bt_act)],
        ["both", "both", "both", "plan", "bdtopo"], "default")
    return pd.DataFrame({"vacant_use": use, "vacant_use_source": src}, index=plan.index)


def cross_check(plan_use: pd.Series, open_share: pd.Series, activity_share: pd.Series,
                weight: pd.Series | None = None, threshold: float = 0.5) -> pd.DataFrame:
    """Agreement table between the plan's use and BD TOPO's, for the run log:
    rows = plan reading, columns = BD TOPO reading, cells = parcel count (or
    the sum of `weight`, e.g. area)."""
    plan = plan_use.astype("object").fillna("unstated").rename("plan")
    bt = np.select(
        [pd.to_numeric(open_share, errors="coerce").fillna(0) >= threshold,
         pd.to_numeric(activity_share, errors="coerce").fillna(0) >= threshold],
        [OPEN_SPACE, ACTIVITY], "nothing")
    w = (pd.to_numeric(weight, errors="coerce").fillna(0.0) if weight is not None
         else pd.Series(1.0, index=plan.index))
    return pd.crosstab(plan, pd.Series(bt, index=plan.index, name="bdtopo"),
                       values=w, aggfunc="sum").fillna(0.0)
