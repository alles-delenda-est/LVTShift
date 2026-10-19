"""Flag obviously TFPB-exempt public property (spec 0003).

Source: DGFiP « Fichiers des locaux et des parcelles des personnes morales »
(data.economie.gouv.fr, Licence Ouverte 2.0, annual, situation au 1er janvier).
It lists every right held by a legal person on each parcel (`NB` file) and on
each local, i.e. building unit (`B` file), with the holder's INSEE legal form.

CGI art. 1382-1° exempts the property of the State, regions, départements,
communes, their groupings and public scientific / teaching / assistance bodies
when it is affected to a public or general-interest service and yields no
income (BOFIP BOI-IF-TFB-10-50-10-10). The file has no exemption code and no
use field, so ownership is a proxy. The rule is deliberately conservative: it
errs towards under-flagging (see METHODOLOGY §3.5).

A parcel is flagged when every holder of a right on its land and on every
building unit is a qualifying public body holding full ownership (droit P, or Z
for State-managed property), on its own territory, with no condominium syndic,
no lease (emphytéose, bail à construction, AOT…), no dismemberment, and no
private or housing manager. Network-utility units (ENEDIS, GRDF…) are ignored.

Tiers:
  A1  building units recorded and all public               -> exempt
  A2  public land, no building unit recorded                -> exempt only if
      the model also sees no building (parks, woods, cemeteries); a building on
      such a parcel (e.g. a concession) stays taxable until corroborated.

Privacy: owner names are read only to recognise utilities and housing managers
and are never stored or exported; the cache keeps idpar, tier and owner type.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import unicodedata
import urllib.parse
import zipfile
from pathlib import Path

import pandas as pd

import ingest
from config import DATA_SOURCES as SRC

PM_YEAR = 2025          # situation au 1er janvier; bump when DGFiP publishes N+1

# INSEE legal forms of qualifying public owners (CGI 1382-1°, BOFIP §30, §370-435)
STATE = {"7111", "7112", "7113", "7120", "7150", "7160", "7171", "7172", "7179", "7190"}
COLLECTIVITES = {"7210", "7220", "7225", "7229", "7230", "7312", "7313"}
EPCI = {"7340", "7341", "7342", "7343", "7344", "7345", "7346", "7347", "7348", "7349",
        "7351", "7352", "7353", "7354", "7355", "7356", "7357"}
EP_SEA = {"7331", "7361", "7362", "7364", "7365", "7366", "7367", "7372", "7383", "7384"}
PUBLIC_FORMS = STATE | COLLECTIVITES | EPCI | EP_SEA
OWNER_TYPE = {**{f: "etat" for f in STATE}, **{f: "collectivite" for f in COLLECTIVITES},
              **{f: "epci" for f in EPCI}, **{f: "etablissement_public" for f in EP_SEA}}

# Network operators whose small units (substations, gas stations, heating
# plant rooms) sit inside public buildings. Matched only on a unit held in full
# ownership (droit P): a lessee whose name happens to contain one of these words
# must still block the flag. Generic brands (« Orange ») are not listed.
UTILITY_RE = re.compile(r"\b(?:ENEDIS|ELECTRICITE RESEAU DISTRIBUTION FRANCE|GRDF|"
                        r"GAZ RESEAU DISTRIBUTION FRANCE|RTE RESEAU DE TRANSPORT|"
                        r"CLIMESPACE|CPCU)\b")
HOUSING_RE = re.compile(r"LOGEMENT|HABITAT|HLM|IMMOBILI|GERANCE|FONCIA|REGIE|CABINET|"
                        r"SYNDIC|ADMINISTRATEUR")
MANAGER_RIGHTS = {"G", "S", "Q"}
FULL_OWNER_RIGHTS = {"P", "Z"}

PM_HOST = "data.economie.gouv.fr"
MAX_MEMBER_BYTES = 1_000_000_000      # largest real member (Paris locaux) ≈ 161 MB
FLAG_COLS = ["idpar", "tier", "owner_type"]

VILLE_DE_PARIS_SIREN = "217500016"
METROPOLE_LYON_SIREN = "200046977"
# PLM arrondissements belong to their city for the territory test
_PLM = {"751": "75056", "693": "69123", "132": "13055"}

B_COLS = ["dep", "dir", "com", "nom_com", "prefixe", "section", "plan", "bat",
          "ent", "niv", "porte", "num_voirie", "indice_rep", "code_voie_majic",
          "rivoli", "nature_voie", "nom_voie", "code_droit", "num_majic", "siren",
          "groupe", "forme", "forme_abr", "denomination"]
NB_COLS = ["dep", "dir", "com", "nom_com", "prefixe", "section", "plan",
           "num_voirie", "indice_rep", "code_voie_majic", "rivoli", "nature_voie",
           "nom_voie", "contenance_par", "suf", "nature_culture", "contenance_suf",
           "code_droit", "num_majic", "siren", "groupe", "forme", "forme_abr",
           "denomination"]
KEEP = ["dep", "com", "prefixe", "section", "plan", "code_droit", "siren", "forme",
        "denomination"]


# Fingerprint of the rule: part of the flag-cache file name.
RULE_VERSION = hashlib.sha256(repr((
    sorted(PUBLIC_FORMS), UTILITY_RE.pattern, HOUSING_RE.pattern,
    sorted(MANAGER_RIGHTS), sorted(FULL_OWNER_RIGHTS), VILLE_DE_PARIS_SIREN,
    METROPOLE_LYON_SIREN, sorted(_PLM.items()), 2)).encode()).hexdigest()[:10]


def _dep_number(dep: str) -> int:
    return 20 if dep.upper() in ("2A", "2B") else int(dep)


def _attachments(year: int) -> dict:
    """{'B': url, 'NB': [(lo, hi, url), ...]} for one vintage, from the catalog
    (attachment ids change every year, so they are matched by pattern)."""
    try:
        items = json.loads(ingest._get(SRC["pm_catalog"]))["attachments"]
        listed = [((a.get("metas") or {}).get("id", ""), a["href"]) for a in items]
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ingest.IngestUnavailable(
            "DGFiP personnes morales", f"catalogue illisible ({type(exc).__name__})") from exc
    out = {"B": None, "NB": []}
    for aid, href in listed:
        if f"situation_{year}" not in aid or not aid.endswith("_zip"):
            continue
        # downloads must stay on the publisher's host (no file://, no redirection
        # of the fetch to an arbitrary server by a tampered catalog)
        u = urllib.parse.urlparse(str(href))
        if u.scheme != "https" or u.hostname != PM_HOST:
            raise ingest.IngestUnavailable(
                "DGFiP personnes morales", f"lien de téléchargement inattendu pour {aid}")
        if "locaux" in aid:
            out["B"] = href
        elif "parcelles" in aid:
            m = re.search(r"dpts_(\d+)_a_(\d+)", aid)
            if m:
                out["NB"].append((int(m.group(1)), int(m.group(2)), href))
    if not out["B"] or not out["NB"]:
        raise ingest.IngestUnavailable(
            "DGFiP personnes morales", f"pas de fichiers 'situation {year}' au catalogue")
    return out


def idpar_of(df: pd.DataFrame) -> pd.Series:
    """14-char cadastral id: dep(2) + com(3) + préfixe(3, blank -> 000)
    + section(2, ' E' -> '0E') + plan(4)."""
    pre = df["prefixe"].fillna("").str.strip().replace("", "000").str.zfill(3)
    sec = df["section"].fillna("").str.strip().str.upper().str.zfill(2)
    return (df["dep"].str.strip().str.upper().str.zfill(2)
            + df["com"].str.strip().str.zfill(3)
            + pre + sec + df["plan"].fillna("").str.strip().str.zfill(4))


def _norm(label: str) -> str:
    """Header label without accents/case/punctuation, for drift checks."""
    s = unicodedata.normalize("NFKD", str(label)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


# Expected header fragments at key positions (schema-drift guard): a reordered
# or renamed column must fail loudly rather than misread rights or owners.
_HEADER_CHECK = {"dep": "departement", "code_droit": "droit", "siren": "siren",
                 "forme": "forme", "denomination": "denomination"}


def _read_member(z: zipfile.ZipFile, name: str, cols: list) -> pd.DataFrame:
    info = z.getinfo(name)
    if info.file_size > MAX_MEMBER_BYTES:          # decompression-bomb guard
        raise ingest.IngestUnavailable(
            "DGFiP personnes morales", f"{name}: fichier anormalement volumineux")
    header = pd.read_csv(z.open(name), sep=";", dtype=str, nrows=0,
                         encoding="utf-8").columns
    if len(header) != len(cols):       # schema drift between vintages
        raise ingest.IngestUnavailable(
            "DGFiP personnes morales", f"{name}: {len(header)} colonnes inattendues")
    for col, frag in _HEADER_CHECK.items():
        if frag not in _norm(header[cols.index(col)]):
            raise ingest.IngestUnavailable(
                "DGFiP personnes morales", f"{name}: colonne {col!r} inattendue")
    idx = [cols.index(c) for c in KEEP]
    df = pd.read_csv(z.open(name), sep=";", dtype=str, keep_default_na=False,
                     encoding="utf-8", header=0, usecols=idx)
    df.columns = [cols[i] for i in sorted(idx)]
    return df[KEEP]


def fetch_rows(dep: str, year: int = PM_YEAR) -> pd.DataFrame:
    """All rights rows (NB and B) for one département, with `src` and `idpar`."""
    dep = str(dep).strip().upper()
    att = _attachments(year)
    n = _dep_number(dep)
    nb_urls = [u for lo, hi, u in att["NB"] if lo <= n <= hi]
    if not nb_urls:
        raise ingest.IngestUnavailable("DGFiP personnes morales",
                                       f"aucun fichier parcelles pour le département {dep}")
    pat = re.compile(rf"_(B|NB)[_-]{re.escape(dep)}0\b")
    frames = []
    for kind, url, cols in [("B", att["B"], B_COLS)] + [("NB", u, NB_COLS) for u in nb_urls]:
        with zipfile.ZipFile(io.BytesIO(ingest._get(url, timeout=900))) as z:
            for name in z.namelist():
                m = pat.search(name.rsplit("/", 1)[-1])
                if m and m.group(1) == kind:
                    frames.append(_read_member(z, name, cols).assign(src=kind))
    if not any((f["src"] == "B").any() for f in frames) or \
            not any((f["src"] == "NB").any() for f in frames):
        raise ingest.IngestUnavailable("DGFiP personnes morales",
                                       f"département {dep} absent des fichiers {year}")
    rows = pd.concat(frames, ignore_index=True)
    rows["idpar"] = idpar_of(rows)
    return rows


def _in_territory(rows: pd.DataFrame, lyon_metropole: set) -> pd.Series:
    """Public owner on its own territory? Out-of-territory holdings of communes
    and départements are only partly exempt (BOFIP §90, §250): not flagged."""
    code5 = rows["idpar"].str[:5]
    city = code5.str[:3].map(_PLM).fillna(code5)              # PLM -> city code
    absorbed = rows["idpar"].str[:2] + rows["idpar"].str[5:8]   # merged commune
    siren = rows["siren"].fillna("").str.strip()
    commune_of_siren = siren.str[2:4] + siren.str[5:8]
    ok = pd.Series(True, index=rows.index)
    f = rows["forme"]
    commune = f == "7210"
    ok[commune] = (commune_of_siren[commune] == city[commune]) | \
                  (commune_of_siren[commune] == absorbed[commune])   # merged commune
    dept = f == "7220"
    ok[dept] = siren[dept].str[2:4] == rows.loc[dept, "dep"].str.zfill(2)
    other = f == "7229"           # « autre collectivité »: Ville de Paris, Métropole de Lyon
    ok[other] = ((siren[other] == VILLE_DE_PARIS_SIREN) & (code5[other].str[:2] == "75")) | \
                ((siren[other] == METROPOLE_LYON_SIREN) & city[other].isin(lyon_metropole))
    return ok


def classify(rows: pd.DataFrame, lyon_metropole: set = frozenset()) -> pd.DataFrame:
    """Per-parcel flag table: idpar, tier ('A1' | 'A2'), owner_type.

    Only flagged parcels are returned. Owner names are used here only and are
    not part of the result.
    """
    r = rows.copy()
    r["droit"] = r["code_droit"].fillna("").str.strip().str[:1]
    den = r["denomination"].fillna("").str.upper()
    util = den.str.contains(UTILITY_RE) & (r["src"] == "B") & (r["droit"] == "P")
    pub = r["forme"].isin(PUBLIC_FORMS) & _in_territory(r, set(lyon_metropole))
    mgr = r["droit"].isin(MANAGER_RIGHTS)
    owner = ~mgr & ~util
    bad_owner = owner & ~(pub & r["droit"].isin(FULL_OWNER_RIGHTS))
    bad_mgr = (r["droit"] == "S") | (mgr & ~util & (~r["forme"].isin(PUBLIC_FORMS)
                                                    | den.str.contains(HOUSING_RE)))
    bad = set(r.loc[bad_owner | bad_mgr, "idpar"])
    land_owned = r[(r["src"] == "NB") & owner]
    cand = land_owned[~land_owned["idpar"].isin(bad)]
    if cand.empty:
        return pd.DataFrame(columns=FLAG_COLS)
    with_units = set(r.loc[(r["src"] == "B") & owner, "idpar"])
    first = cand.drop_duplicates("idpar")
    return pd.DataFrame({
        "idpar": first["idpar"].values,
        "tier": ["A1" if i in with_units else "A2" for i in first["idpar"]],
        "owner_type": first["forme"].map(OWNER_TYPE).values,
    })


def flags_for_departement(dep: str, year: int = PM_YEAR) -> pd.DataFrame:
    """Classified flags for a whole département, cached (no names) when
    ingest.CACHE_DIR is set, so a batch of communes classifies it once."""
    from config import LYON_METROPOLE_INSEE
    dep = str(dep).strip().upper()
    cache = None
    if ingest.CACHE_DIR:
        # the rule version is part of the name: changing the rule never reuses
        # flags computed under the old one
        cache = Path(ingest.CACHE_DIR) / f"pm_flags_{year}_{dep}_{RULE_VERSION}.csv"
        if cache.exists():
            cached = pd.read_csv(cache, dtype=str)
            if list(cached.columns) == FLAG_COLS and len(cached):
                return cached
            cache.unlink(missing_ok=True)          # unusable: recompute
    flags = classify(fetch_rows(dep, year), LYON_METROPOLE_INSEE)
    if cache is not None:
        tmp = cache.with_suffix(f".{os.getpid()}.part")
        flags.to_csv(tmp, index=False)
        try:
            tmp.replace(cache)
        except OSError:          # another worker wrote it first
            tmp.unlink(missing_ok=True)
    return flags


def exempt_public(cfg, parcels: pd.DataFrame, has_building: pd.Series,
                  year: int = PM_YEAR) -> pd.DataFrame:
    """idpar, is_exempt_public, exempt_tier for the commune's parcels.

    has_building: boolean Series aligned on `parcels` (the model's own view).
    """
    flags = flags_for_departement(cfg.departement, year)
    out = parcels[["idpar"]].merge(flags, on="idpar", how="left")
    built = pd.Series(has_building.reindex(parcels.index).fillna(False).values,
                      index=out.index).astype(bool)
    exempt = (out["tier"] == "A1") | ((out["tier"] == "A2") & ~built)
    out["is_exempt_public"] = exempt.fillna(False).astype(bool)
    out["exempt_tier"] = out["tier"].where(out["is_exempt_public"])
    return out[["idpar", "is_exempt_public", "exempt_tier"]]
