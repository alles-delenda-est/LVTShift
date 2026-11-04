"""Social housing (HLM) in today's TFPB, and in the reform.

Today (tax year 2025, legal_report §7 in docs/research/hlm-2026-11/):
  * CGI art. 1384 A (new builds and VEFA) and 1384 C (acquisitions) exempt
    conventioned social rental dwellings financed by PLAI, PLUS or PLS for
    15 years from the year after completion or acquisition, 25 years when the
    financing decision falls between 1 July 2004 and 31 December 2026;
  * CGI art. 1388 bis abates by 30 % the base of taxable HLM and SEM dwellings
    in a 2024 priority neighbourhood (QPV), tax years 2025 to 2030.
  The REI produit excludes exempt and abated bases, so the housing group's
  share of today's produit falls on taxable floor only: an exempt dwelling's
  floor carries weight 0 and an abated one 0.7 (estimate.current_tax).

The reform ends both, as the site states: social landlords pay the land tax
like every owner. The TFPB is not a recoverable charge (décret 82-955, annex
VIII) and social rents are capped, so the change falls on the landlord, a
business: parcels held mainly by social landlords form their own category,
outside every household figure.

Sources:
  * DGFiP « locaux et parcelles des personnes morales » (exemptions.fetch_rows):
    which parcels a social landlord holds, and whether it holds the land too;
  * SDES RPLS at 1 January 2025 (DiDo, Licence Ouverte; config DATA_SOURCES
    "rpls_rows" / "rpls_csv"): one row per social dwelling, with coordinates,
    financing, dates and QPV, but no parcel and no landlord.

RPLS diffusion rules (décret 2009-1485, restated in the SDES dictionary): no
statistic identifying a landlord, no figure on fewer than 11 dwellings below
commune level, no redistribution of the rows. The rows stay in the download
cache; the run receives parcel shares and factors only, and the payload
commune-level aggregates only (export_web.MIN_SOCIAL_LANDLORDS). Owner names
are read only to recognise public housing offices and intermediate-rent
companies; the cache keeps a hashed landlord key, for counting landlords.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

import exemptions
import ingest
from config import DATA_SOURCES as SRC, data_codes_of

TAX_YEAR = 2025              # the REI produit being shared (situation at 1 Jan)
RPLS_MILLESIME = "2025-01"   # RPLS at 1 January of the tax year

# Exemption durations (CGI 1384 A I and I ter, 1384 C I)
SHORT_YEARS, LONG_YEARS = 15, 25
LONG_WINDOW = (pd.Timestamp("2004-07-01"), pd.Timestamp("2026-12-31"))
# A financing decision from July 2004 cannot complete before 2005: earlier
# completions had the 15-year exemption, ended by 2020
FIRST_LONG_START = 2005
# Without a convention date (DATCONV), completions from 2007 are taken as
# under the 25-year rule and 2005–06 as not (legal_report §7, rule 2)
LONG_DEFAULT_FROM = 2007
# A convention can be signed months after the financing decision: for the
# 2005–06 cohort, a convention dated in the second half of 2004 may follow a
# decision taken before July 2004, so it must date from 2005 (Gemini review)
AMBIGUOUS_DATCONV_FROM = pd.Timestamp("2005-01-01")
# RPLS FINAN_CODE (initial financing) by a prêt réglementé still able to carry
# an exemption in 2025: PLA-I / LLTS, PLA-LM / PLAI, PLUS, PLS, other
# post-1977 aided financing. PLA ordinaire (12) is not: PLUS replaced it in
# 1999, so every such decision predates July 2004 and its 15 years (20 with
# the environmental bonus) ended by 2024.
ELIGIBLE_FINANCING = frozenset({"10", "11", "13", "14", "49"})
# An acquisition whose convention is older than its entry into the landlord's
# stock by more than this was social housing already (a transfer between
# landlords): no new exemption (CGI 1384 C; the convention follows the
# dwelling, CCH L. 353-4)
TRANSFER_CONV_GAP = 2
# PLI and PCL: intermediate rents, outside both the exemption and the abatement
INTERMEDIATE_FINANCING = frozenset({"16", "17"})
# Pre-1977 HLM financing (HBM, PLR/PSR, HLM/O, ILM, ILN, CFF, other): such
# dwellings had the old art. 1384 exemption, so 1388 bis covers them without
# a convention; a later dwelling needs one (no 1384 A exemption without it)
PRE_1977_FINANCING = frozenset({"50", "51", "52", "53", "54", "55", "99"})
QPV_FACTOR = 0.7             # CGI 1388 bis: 30 % off the base

# Landlords (DGFiP PM file): HLM legal forms (SA and coopératives d'HLM,
# OPHLM), SEM forms, and local EPICs named like a public housing office
HLM_FORMS = frozenset({"5546", "5646", "5547", "5647", "7371"})
SEM_FORMS = frozenset({"5515", "5615"})
OPH_FORM = "4140"
OPH_NAME = re.compile(r"OFFICE PUBLIC|\bOPH\b|\bOPAC\b|HABITAT|\bHLM\b")
# groupe-5 companies letting at intermediate, not social, rents
NOT_SOCIAL_NAME = re.compile(r"\bIN ?'?LI\b")
# rights whose holder pays the TFPB on a unit: owner, usufructuary,
# emphyteuta, building lessee, rehabilitation lessee (B, N, G, S… do not)
HOLDER_RIGHTS = frozenset({"P", "U", "E", "R", "W"})
LESSEE_RIGHTS = HOLDER_RIGHTS - {"P"}
PM_KEEP = exemptions.KEEP + ["groupe", "bat", "ent", "niv", "porte"]

# Joining RPLS address points to parcels (sources_report §4, join C): the
# nearest parcel where a social landlord holds units or land within
# JOIN_SOCIAL_M, otherwise the parcel holding the point (nearest within
# JOIN_ANY_M for points on the street)
JOIN_SOCIAL_M = 30.0
JOIN_ANY_M = 15.0
# Contiguous social parcels form an estate; exemption and QPV shares are taken
# per estate, since an address point often falls on a neighbouring parcel
CLUSTER_GAP_M = 2.0
# RPLS habitable m² per BD TOPO gross residential m² (estate medians 0.70 and
# 0.75 in Villeurbanne and Montreuil, sources_report §4)
HAB_TO_GROSS = 0.72
# A parcel whose housing floor is at least this share social is the landlord's
SOCIAL_CATEGORY_SHARE = 0.5

RPLS_COLS = ["DEPCOM", "X", "Y", "EPSG", "CONSTRUCT", "LOCAT", "PATRIMOINE",
             "ORIGINE", "FINAN_CODE", "CONV", "DATCONV", "PLG_QP24", "SURFHAB"]
SOCIAL_COLS = ["idpar", "landlord", "units", "land", "landlord_key"]
PARCEL_COLS = ["idpar", "social_share", "hlm_tax_factor", "rpls_dwellings",
               "landlord_key"]

# A company counts as HLM (or SEM) by its groupe code only if most of its rows
# carry it: the code is recorded per row, and one stray row must not turn a
# private developer into a social landlord across the département
GROUPE_MAJORITY = 0.5

RULE_VERSION = hashlib.sha256(repr((
    sorted(HLM_FORMS), sorted(SEM_FORMS), OPH_FORM, OPH_NAME.pattern,
    NOT_SOCIAL_NAME.pattern, sorted(HOLDER_RIGHTS), GROUPE_MAJORITY, 2)).encode()).hexdigest()[:10]


def _landlord_key(siren: str) -> str:
    """Per-landlord label, so the export can count landlords without names.
    A hash, not a secret: anyone with the public SIREN list could reverse it,
    so it stays in local outputs and never reaches a payload."""
    return hashlib.sha256(f"lvtshift-fr:{siren}".encode()).hexdigest()[:12]


def social_sirens(rows: pd.DataFrame) -> dict:
    """SIREN -> 'hlm' | 'sem', over a whole département's rights rows.

    HLM: most of its rows in groupe 5 (« office HLM »; real HLM bodies have
    about 95 %), an HLM legal form, or a local EPIC named like an OPH (the
    Métropole de Lyon's OPH is coded groupe 9). SEM: most rows in groupe 6
    or an SEM form, kept apart (SEMs are partly non-social; parcel_social
    needs RPLS dwellings to count one). Intermediate-rent companies are never
    social.
    """
    siren = rows["siren"].fillna("").str.strip()
    g = rows["groupe"].fillna("").str.strip().str[:1]
    forme = rows["forme"].fillna("").str.strip()
    den = rows["denomination"].fillna("").str.upper()
    known = siren != ""

    def by_group(code):
        share = (g[known] == code).groupby(siren[known]).mean()
        return set(share[share > GROUPE_MAJORITY].index)

    by_form = known & (forme.isin(HLM_FORMS) | ((forme == OPH_FORM) & den.str.contains(OPH_NAME)))
    bad = set(siren[den.str.contains(NOT_SOCIAL_NAME)])
    h = (by_group("5") | set(siren[by_form])) - bad
    s = (by_group("6") | set(siren[known & forme.isin(SEM_FORMS)])) - bad - h
    return {**{x: "sem" for x in s}, **{x: "hlm" for x in h}}


def social_parcels(rows: pd.DataFrame) -> pd.DataFrame:
    """Parcels where a social landlord is the taxable holder of at least one
    building unit, or holds the land: idpar, landlord ('hlm' | 'sem', of the
    landlord with most units), units, land (bool), landlord_key.

    A landlord holds a unit when it has a holder right on it (P, U, E, R, W),
    except full ownership (P) of a unit on which someone else holds a lessee
    right (a commune's land under an emphyteutic lease to an OPH is the
    OPH's). Rows: exemptions.fetch_rows(dep, keep=PM_KEEP).
    """
    cls = social_sirens(rows)
    r = rows.assign(siren=rows["siren"].fillna("").str.strip(),
                    droit=rows["code_droit"].fillna("").str.strip().str[:1])
    r["soc"] = r["siren"].map(cls)
    # only holder rights on parcels where a social landlord holds one matter:
    # filter before building unit keys (Paris: 1.3 M unit rows)
    b = r[(r["src"] == "B") & r["droit"].isin(HOLDER_RIGHTS)]
    b = b[b["idpar"].isin(set(b.loc[b["soc"].notna(), "idpar"]))]
    unit = (b["idpar"] + "|" + b["bat"].str.strip() + "|" + b["ent"].str.strip()
            + "|" + b["niv"].str.strip() + "|" + b["porte"].str.strip())
    b = b.assign(unit=unit)
    others = set(b.loc[b["droit"].isin(LESSEE_RIGHTS) & b["soc"].isna(), "unit"])
    held = b[b["droit"].isin(HOLDER_RIGHTS) & b["soc"].notna()]
    held = held[~((held["droit"] == "P") & held["unit"].isin(others))]
    # one holder per unit, the lessee before the owner
    held = (held.assign(_own=held["droit"] == "P")
            .sort_values(["unit", "_own"], kind="stable").drop_duplicates("unit"))
    per = held.groupby(["idpar", "siren"]).size().rename("n").reset_index()
    top = per.sort_values(["idpar", "n"], ascending=[True, False],
                          kind="stable").drop_duplicates("idpar")
    units = per.groupby("idpar")["n"].sum()
    land = r[(r["src"] == "NB") & r["droit"].isin(HOLDER_RIGHTS) & r["soc"].notna()]
    land_siren = land.drop_duplicates("idpar").set_index("idpar")["siren"]
    ids = sorted(set(units.index) | set(land_siren.index))
    if not ids:
        return pd.DataFrame(columns=SOCIAL_COLS)
    who = top.set_index("idpar")["siren"].reindex(ids).fillna(land_siren.reindex(ids))
    return pd.DataFrame({
        "idpar": ids,
        "landlord": who.map(cls).values,
        "units": units.reindex(ids).fillna(0).astype(int).values,
        "land": pd.Index(ids).isin(land_siren.index),
        "landlord_key": who.map(_landlord_key).values,
    })


def social_parcels_for_departement(dep: str, year: int = exemptions.PM_YEAR) -> pd.DataFrame:
    """social_parcels for a whole département, cached (no names, no SIREN)
    when ingest.CACHE_DIR is set, so a batch of communes reads it once."""
    dep = str(dep).strip().upper()
    cache = None
    if ingest.CACHE_DIR:
        cache = Path(ingest.CACHE_DIR) / f"pm_social_{year}_{dep}_{RULE_VERSION}.csv"
        if cache.exists():
            cached = pd.read_csv(cache, dtype={"idpar": str, "landlord": str,
                                               "landlord_key": str})
            if list(cached.columns) == SOCIAL_COLS:
                cached["land"] = cached["land"].map({True: True, False: False,
                                                     "True": True, "False": False})
                if cached["land"].notna().all():
                    return cached.astype({"land": bool})
            cache.unlink(missing_ok=True)          # unusable: recompute
    out = social_parcels(exemptions.fetch_rows(dep, year, keep=PM_KEEP))
    if cache is not None:
        tmp = cache.with_suffix(f".{os.getpid()}.part")
        out.to_csv(tmp, index=False)
        try:
            tmp.replace(cache)
        except OSError:          # another worker wrote it first
            tmp.unlink(missing_ok=True)
    return out


def fetch_rpls(cfg, millesime: str = RPLS_MILLESIME) -> pd.DataFrame:
    """RPLS dwellings of the commune (all its data codes), RPLS_COLS as text.

    The row count comes first: a code with no social dwelling makes the CSV
    endpoint answer an error, and a CSV shorter than the count is truncated.
    """
    frames = []
    for code in data_codes_of(cfg):
        rows_url = SRC["rpls_rows"].format(millesime=millesime, code=code)
        try:
            total = int(json.loads(ingest._get(rows_url))["total"])
            if total < 0:
                raise ValueError("negative count")
        except (ValueError, KeyError, TypeError) as exc:
            ingest._evict_cache(rows_url)       # never replay an error body
            raise ingest.IngestUnavailable(
                "SDES RPLS", f"décompte illisible pour {code} ({type(exc).__name__})") from exc
        if total == 0:
            continue
        csv_url = SRC["rpls_csv"].format(millesime=millesime, code=code,
                                         columns=",".join(RPLS_COLS))
        body = ingest._get(csv_url, timeout=300)
        try:
            df = pd.read_csv(io.BytesIO(body), sep=";", dtype=str, keep_default_na=False,
                             encoding="utf-8")
        except (ValueError, pd.errors.ParserError) as exc:
            ingest._evict_cache(csv_url)
            raise ingest.IngestUnavailable("SDES RPLS", f"CSV illisible pour {code}") from exc
        problem = None
        if list(df.columns) != RPLS_COLS:
            problem = f"colonnes inattendues pour {code}"
        elif len(df) != total or not df["DEPCOM"].eq(code).all():
            problem = f"{len(df)} lignes pour {code}, {total} annoncées"
        if problem:
            ingest._evict_cache(csv_url)
            ingest._evict_cache(rows_url)
            raise ingest.IngestUnavailable("SDES RPLS", problem)
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=RPLS_COLS)
    return pd.concat(frames, ignore_index=True)


def dwelling_status(r: pd.DataFrame, year: int = TAX_YEAR) -> pd.DataFrame:
    """Each RPLS dwelling's TFPB status in `year`: 'exempt' (factor 0),
    'qpv' (abated, 0.7) or 'taxable' (1). Decision table: legal_report §7.

    The exemption clock starts the year after completion (new builds, VEFA)
    or acquisition (acquisitions entering the social stock). An acquisition
    from another landlord carries no new exemption: its clock is the
    original one. DATCONV, the convention date, follows the dwelling: a
    convention older than the entry into this landlord's stock (by more than
    TRANSFER_CONV_GAP years) marks a transfer, whose clock is then the later
    of completion and convention. Without DATCONV, a first letting before
    the entry marks one (LOCAT is reported inconsistently: some landlords give
    the building's first letting ever, so it is only the fallback). DATCONV
    also stands in for the financing decision date that sets 15 or 25 years.
    """
    def num(c):
        return pd.to_numeric(r[c], errors="coerce")

    construct, locat, patr = num("CONSTRUCT"), num("LOCAT"), num("PATRIMOINE")
    origine = r["ORIGINE"].fillna("").str.strip()
    fin = r["FINAN_CODE"].fillna("").str.strip()
    datconv = pd.to_datetime(r["DATCONV"].where(r["DATCONV"].str.strip() != ""),
                             format="%Y-%m-%d", errors="coerce")
    conv_year = datconv.dt.year
    acq = origine.isin(["2", "3"])
    by_conv = conv_year.notna()
    transfer = acq & ((by_conv & (conv_year < patr - TRANSFER_CONV_GAP))
                      | (~by_conv & (locat < patr - 1)))
    original = np.fmax(construct, conv_year.where(by_conv, locat - 1))
    start = construct.where(~acq, patr)
    start = start.where(~transfer, original)
    start = start.fillna(locat - 1)
    long_ = (datconv >= LONG_WINDOW[0]) & (datconv <= LONG_WINDOW[1])
    long_ &= (start >= LONG_DEFAULT_FROM) | (datconv >= AMBIGUOUS_DATCONV_FROM)
    long_ = long_.where(datconv.notna(), start >= LONG_DEFAULT_FROM)
    conv = r["CONV"].fillna("").str.strip().eq("1")
    eligible = conv & fin.isin(ELIGIBLE_FINANCING)
    in_short = start >= year - SHORT_YEARS
    in_long = long_.astype(bool) & (start >= max(FIRST_LONG_START, year - LONG_YEARS))
    exempt = eligible & (in_short | in_long) & (start < year)
    qpv = (r["PLG_QP24"].fillna("").str.strip().str.startswith("QN")
           & (conv | fin.isin(PRE_1977_FINANCING))
           & ~fin.isin(INTERMEDIATE_FINANCING) & ~exempt)
    status = np.where(exempt, "exempt", np.where(qpv, "qpv", "taxable"))
    factor = np.where(exempt, 0.0, np.where(qpv, QPV_FACTOR, 1.0))
    return pd.DataFrame({"status": status, "factor": factor}, index=r.index)


def _num(df: pd.DataFrame, c: str) -> pd.Series:
    """A numeric RPLS column (text, decimal point or comma)."""
    return pd.to_numeric(df[c].astype(str).str.strip().str.replace(",", ".", regex=False),
                         errors="coerce")


def _place(rpls: pd.DataFrame, pg, anchors: set) -> pd.Series:
    """idpar of each RPLS dwelling (NaN when it cannot be placed)."""
    import geopandas as gpd
    x, y = _num(rpls, "X"), _num(rpls, "Y")
    ok = x.notna() & y.notna() & rpls["EPSG"].astype(str).str.strip().eq(str(ingest.CRS_METRIC))
    out = pd.Series(np.nan, index=rpls.index, dtype=object)
    if not ok.any():
        return out
    xy = pd.DataFrame({"x": x[ok], "y": y[ok]})
    uniq = xy.drop_duplicates().reset_index(drop=True)
    pts = gpd.GeoDataFrame(uniq, geometry=gpd.points_from_xy(uniq["x"], uniq["y"]),
                           crs=ingest.CRS_METRIC)
    got = pd.Series(np.nan, index=pts.index, dtype=object)
    soc = pg[pg["idpar"].isin(anchors)][["idpar", "geometry"]]
    if len(soc):
        nn = gpd.sjoin_nearest(pts[["geometry"]], soc, how="left",
                               max_distance=JOIN_SOCIAL_M)
        nn = nn[~nn.index.duplicated()]
        got = nn["idpar"].reindex(pts.index)
    miss = got.isna()
    if miss.any():
        nn = gpd.sjoin_nearest(pts.loc[miss, ["geometry"]], pg[["idpar", "geometry"]],
                               how="left", max_distance=JOIN_ANY_M)
        nn = nn[~nn.index.duplicated()]
        got[miss] = nn["idpar"].reindex(pts.index[miss]).values
    key = pd.MultiIndex.from_frame(uniq[["x", "y"]])
    lookup = pd.Series(got.values, index=key)
    out[ok] = lookup.reindex(pd.MultiIndex.from_frame(xy)).values
    return out


def _clusters(pg, ids: set, keys: pd.Series) -> tuple:
    """Estates: parcels in `ids` within CLUSTER_GAP_M of each other and held
    by the same landlord (keys: landlord_key per idpar, NaN when unknown).
    Neighbouring estates of different landlords stay apart (their dwellings'
    ages differ); a parcel of unknown landlord joins a touching estate but
    never bridges two landlords. Returns (estate id per idpar, landlord key
    per estate)."""
    import geopandas as gpd
    sub = pg[pg["idpar"].isin(ids)][["idpar", "geometry"]].reset_index(drop=True)
    if sub.empty:
        return pd.Series(dtype=object), pd.Series(dtype=object)
    key = keys.reindex(sub["idpar"]).to_numpy(dtype=object)
    known = pd.notna(key)
    buf = gpd.GeoDataFrame(sub[["idpar"]], geometry=sub.geometry.buffer(CLUSTER_GAP_M / 2),
                           crs=pg.crs)
    pairs = gpd.sjoin(buf, buf, how="inner", predicate="intersects")
    pairs = pairs[pairs.index != pairs["index_right"]]
    parent = list(range(len(sub)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    left, right = pairs.index.to_numpy(), pairs["index_right"].to_numpy(dtype=int)
    same = np.array([(known[a] and known[b] and key[a] == key[b]) or not (known[a] or known[b])
                     for a, b in zip(left, right)], dtype=bool)
    for a, b in zip(left[same], right[same]):          # same landlord, or both unknown
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    est_key = {}
    for i in np.flatnonzero(known):
        est_key[find(i)] = key[i]
    for a, b in zip(left, right):                       # attach unknown to a known estate
        if known[a] and not known[b]:
            ra, rb = find(a), find(b)
            if rb not in est_key and ra != rb:
                parent[rb] = ra
    roots = [find(i) for i in range(len(sub))]
    est = pd.Series([sub["idpar"].iat[r] for r in roots], index=sub["idpar"].values)
    owner = pd.Series({sub["idpar"].iat[r]: k for r, k in est_key.items() if find(r) == r},
                      dtype=object)
    return est, owner


def parcel_social(pg, floor_housing: pd.Series, social: pd.DataFrame,
                  rpls: pd.DataFrame, year: int = TAX_YEAR) -> tuple:
    """Per-parcel social share and today's TFPB factor on housing floor.

    pg: parcels GeoDataFrame (idpar, geometry) in Lambert-93.
    floor_housing: gross housing floor per idpar (estimate.baseline_floor).
    social: social_parcels rows for the commune's parcels.
    rpls: fetch_rpls rows.

    social_share s: 1 on an estate (the landlord holds the land and units; an
    SEM's only if RPLS dwellings sit in its estate), otherwise the parcel's
    RPLS habitable area over its housing floor (HAB_TO_GROSS), capped at 1.
    The dwellings' factor (dwelling_status) is averaged per estate, weighted
    by habitable area, or over the parcel's own dwellings off estates.
    hlm_tax_factor = 1 − s × (1 − factor): the weight of the parcel's housing
    floor in today's tax.

    Returns (frame with PARCEL_COLS, summary dict of commune-level counts).
    """
    if len(rpls):
        st = dwelling_status(rpls, year)
        d = pd.DataFrame({"idpar": _place(rpls, pg, set(social["idpar"])),
                          "hab": _num(rpls, "SURFHAB").fillna(0.0)})
        d["taxed"] = d["hab"] * st["factor"]
        d = d.dropna(subset=["idpar"])
    else:
        st = pd.DataFrame({"status": pd.Series(dtype=str)})
        d = pd.DataFrame({"idpar": pd.Series(dtype=str), "hab": pd.Series(dtype=float),
                          "taxed": pd.Series(dtype=float)})
    summary = {
        "tax_year": int(year),
        "rpls_dwellings": int(len(rpls)),
        "placed_dwellings": int(len(d)),
        "exempt_dwellings": int((st["status"] == "exempt").sum()),
        "qpv_abated_dwellings": int((st["status"] == "qpv").sum()),
        "estates": 0,
        "social_parcels": 0,
    }
    per = d.groupby("idpar").agg(n=("hab", "size"), hab=("hab", "sum"), taxed=("taxed", "sum"))
    members = (set(social.loc[(social["units"] > 0) | social["land"], "idpar"])
               | set(per.index)) & set(pg["idpar"])
    if not members:
        return pd.DataFrame(columns=PARCEL_COLS), summary
    soc = social.set_index("idpar").reindex(sorted(members))
    est, est_owner = _clusters(pg, members, soc["landlord_key"])
    has_rpls = per["n"].reindex(est.index).fillna(0) > 0
    rpls_est = has_rpls.groupby(est).any()
    c_hab = per["hab"].reindex(est.index).fillna(0.0).groupby(est).sum()
    c_tax = per["taxed"].reindex(est.index).fillna(0.0).groupby(est).sum()
    c_factor = (c_tax / c_hab.where(c_hab > 0)).fillna(1.0)

    ids = pd.Index(sorted(members))
    estate_of = est.reindex(ids)
    units = soc["units"].fillna(0).reindex(ids)
    land = soc["land"].eq(True).reindex(ids)
    landlord = soc["landlord"].reindex(ids)
    on_estate = (units > 0) & land & (landlord.eq("hlm") | estate_of.map(rpls_est).eq(True))
    fh = floor_housing.reindex(ids).fillna(0.0)
    own_hab = per["hab"].reindex(ids).fillna(0.0)
    own = (own_hab / (HAB_TO_GROSS * fh.where(fh > 0))).clip(upper=1.0)
    own = own.where(fh > 0, (own_hab > 0).astype(float)).fillna(0.0)
    share = own.where(~on_estate, 1.0)
    own_factor = (per["taxed"] / per["hab"].where(per["hab"] > 0)).reindex(ids).fillna(1.0)
    factor = own_factor.where(~on_estate, estate_of.map(c_factor).fillna(1.0))
    out = pd.DataFrame({
        "idpar": ids,
        "social_share": share.round(4).values,
        "hlm_tax_factor": (1.0 - share * (1.0 - factor)).round(4).values,
        "rpls_dwellings": per["n"].reindex(ids).fillna(0).astype(int).values,
        # a parcel of unknown landlord takes its estate's, for counting landlords
        "landlord_key": soc["landlord_key"].reindex(ids)
                        .fillna(estate_of.map(est_owner)).values,
    })
    out = out[(out["social_share"] > 0) | out["landlord_key"].notna()]
    summary["estates"] = int(est.nunique())
    summary["social_parcels"] = int((out["social_share"] >= SOCIAL_CATEGORY_SHARE).sum())
    return out.reset_index(drop=True)[PARCEL_COLS], summary


def social_for_commune(cfg, parcels: pd.DataFrame, buildings: pd.DataFrame,
                       year: int = TAX_YEAR) -> tuple:
    """parcel_social for one commune, from live (or cached) sources."""
    import estimate
    pg = ingest.parcels_to_gdf(parcels[["idpar", "geometry"]])
    social = social_parcels_for_departement(cfg.departement)
    social = social[social["idpar"].isin(set(parcels["idpar"]))]
    floor = estimate.baseline_floor(buildings).set_index("idpar")["floor_housing"] \
        if len(buildings) else pd.Series(dtype=float)
    return parcel_social(pg, floor, social, fetch_rpls(cfg), year)
