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

`vacant_use` combines them: open space if either reading says so (the land
cannot be built on), business land if either says business, housing land
otherwise. `cross_check` tabulates where the two readings agree, for the run
log and the methodology.
"""
from __future__ import annotations

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
HOUSING_WORDS = (
    "habitat", "logement", "residenti", "tissu", "centre-ville", "centres-villes",
    "centre ancien", "centre-bourg", "bourg", "village", "hameau", "pavillon",
    "individuel", "faubourg",
)
OPEN_SPACE_WORDS = (
    "parc urbain", "parcs urbains", "urbaine verte", "zone verte", "espace vert",
    "espaces verts", "jardin", "square", "cimetiere", "naturel", "paysager",
    "coulee verte", "loisirs de plein air",
)
ACTIVITY_WORDS = (
    "activite", "economique", "industri", "artisan", "commerc", "tertiaire",
    "technolog", "logisti", "portuaire", "port ", "bureaux", "ferroviaire",
    "voie ferree", "grands services urbains", "infrastructure", "aeroport",
    "aerodrome", "autoroute", "zone d equipement", "secteur d equipement",
    "equipements d interet collectif", "equipements collectifs", "equipements publics",
    "services publics", "hospital", "universit", "militaire",
)


def _label_use(label: str, allow_open: bool) -> str | None:
    """Class of the keyword appearing earliest in a normalised label."""
    best, pos = None, None
    for use, words in ((HOUSING, HOUSING_WORDS), (OPEN_SPACE, OPEN_SPACE_WORDS),
                       (ACTIVITY, ACTIVITY_WORDS)):
        if use == OPEN_SPACE and not allow_open:
            continue
        hits = [i for i in (label.find(w) for w in words) if i >= 0]
        if hits and (pos is None or min(hits) < pos):
            best, pos = use, min(hits)
    return best


def _norm(text) -> str:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(s.lower().replace("'", " ").split())


def zone_use(zone_typ: pd.Series, destdomi: pd.Series | None = None,
             libelong: pd.Series | None = None) -> pd.Series:
    """The plan's stated use of each parcel's zone: housing, activity,
    open_space, or None where the plan says nothing usable.

    Only urban and to-be-urbanised zones (U, AU…) are read; A and N zones are
    open space by type. A U zone with no usable code or label stays None and is
    treated as housing land, the model's default for type U."""
    idx = zone_typ.index
    typ = zone_typ.astype("object")
    code = (destdomi.astype("object").map(lambda v: _norm(v).zfill(2) if _norm(v) else "")
            if destdomi is not None else pd.Series("", index=idx))
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
ZAI_ACTIVITY_CATEGORIES = {
    "industriel et commercial", "transport", "enseignement", "sante",
    "administratif ou militaire", "science", "gestion des eaux",
}


def bdtopo_feature_use(layer: str, props: dict) -> str | None:
    """open_space, activity or None for one BD TOPO feature."""
    layer = layer.split(":")[-1]
    if layer in ("cimetiere", "terrain_de_sport", "surface_hydrographique"):
        return OPEN_SPACE
    if layer == "equipement_de_transport":
        return ACTIVITY
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

    open_space where the plan says open space or BD TOPO covers at least
    `threshold` of the parcel with open space; else activity where either
    reading says business land; else housing. Returns columns vacant_use and
    vacant_use_source ("plan", "bdtopo", "both" or "default")."""
    if not 0.0 < threshold <= 1.0:
        raise ValueError(f"threshold must be in (0, 1], got {threshold}")
    plan = plan_use.astype("object")
    bt_open = pd.to_numeric(open_share, errors="coerce").fillna(0.0) >= threshold
    bt_act = pd.to_numeric(activity_share, errors="coerce").fillna(0.0) >= threshold
    p_open, p_act = plan.eq(OPEN_SPACE), plan.eq(ACTIVITY)

    use = np.select([p_open | bt_open, p_act | bt_act], [OPEN_SPACE, ACTIVITY], HOUSING)
    src = np.select(
        [p_open & bt_open, p_open, bt_open,
         p_act & bt_act, p_act, bt_act],
        ["both", "plan", "bdtopo", "both", "plan", "bdtopo"], "default")
    return pd.DataFrame({"vacant_use": use, "vacant_use_source": src}, index=plan.index)


def cross_check(plan_use: pd.Series, open_share: pd.Series, activity_share: pd.Series,
                weight: pd.Series | None = None, threshold: float = 0.5) -> pd.DataFrame:
    """Agreement table between the plan's use and BD TOPO's, for the run log:
    rows = plan reading, columns = BD TOPO reading, cells = parcel count (or
    the sum of `weight`, e.g. area)."""
    plan = plan_use.astype("object").fillna("unstated")
    bt = np.select(
        [pd.to_numeric(open_share, errors="coerce").fillna(0) >= threshold,
         pd.to_numeric(activity_share, errors="coerce").fillna(0) >= threshold],
        [OPEN_SPACE, ACTIVITY], "nothing")
    w = (pd.to_numeric(weight, errors="coerce").fillna(0.0) if weight is not None
         else pd.Series(1.0, index=plan.index))
    return pd.crosstab(plan, pd.Series(bt, index=plan.index, name="bdtopo"),
                       values=w, aggfunc="sum").fillna(0.0)
