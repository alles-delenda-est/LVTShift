"""External validation for the « Pour une terre productive » site.

Confronts the model's aggregates with *independent* open benchmarks (INSEE
housing vacancy, a national land-share band) and a *data-quality* cross-source
check (DGFiP cadastre `batiments` vs IGN BD TOPO — agreement on which parcels
are built). A check, NEVER a calibration target: missing sources degrade to
"non disponible", never fabricated. See spec §5b.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import export_web as ew

INSEE_DOSSIER_URL = "https://www.insee.fr/fr/statistiques/2011101?geo=COM-{insee}"
CADASTRE_BATIMENTS_URL = (
    "https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/"
    "geojson/communes/{dep}/{insee}/cadastre-{insee}-batiments.json.gz")
CADASTRE_PARCELLES_URL = (
    "https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/"
    "geojson/communes/{dep}/{insee}/cadastre-{insee}-parcelles.json.gz")


def land_share_band_check(land_share_pct: float, band=(40.0, 65.0)) -> dict:
    lo, hi = band
    return {
        "benchmark": "Part du foncier dans la valeur (ancrage national)",
        "independence": "independent",
        "model_land_share_pct": land_share_pct,
        "band": [lo, hi],
        "within_band": (land_share_pct is not None) and (lo <= land_share_pct <= hi),
        "status": "ok" if (land_share_pct is not None and lo <= land_share_pct <= hi) else "flag",
        "note": ("Ancrage INSEE comptes de patrimoine ~45–50 % national ; "
                 "bande élargie (cœurs denses plus haut). Pas de cible par commune."),
    }


def building_agreement_rate(parcels_gdf, buildings_gdf) -> dict:
    """Share of parcels intersecting at least one cadastre building footprint."""
    import geopandas as gpd
    if buildings_gdf.crs != parcels_gdf.crs:
        buildings_gdf = buildings_gdf.to_crs(parcels_gdf.crs)
    joined = gpd.sjoin(parcels_gdf, buildings_gdf, how="left", predicate="intersects")
    built = joined.index_right.notna().groupby(level=0).any()
    n_parcels = len(parcels_gdf)
    return {
        "cadastre_built_share_pct": round(100.0 * float(built.sum()) / n_parcels, 1) if n_parcels else None,
        "n_parcels": int(n_parcels),
        "n_buildings": int(len(buildings_gdf)),
    }


def _read_geojson_gz(url: str):
    """Fetch a gzipped GeoJSON into a GeoDataFrame, or None on any failure."""
    import io, gzip, urllib.request
    import geopandas as gpd
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            raw = gzip.decompress(resp.read())
        return gpd.read_file(io.BytesIO(raw))
    except Exception as exc:  # network / parse / empty — degrade
        print(f"  [validate] cadastre fetch failed for {url}: {exc}")
        return None


def fetch_cadastre_agreement(cfg, cache_dir="output/validation_cache"):
    """Live cadastre batiments-vs-parcelles agreement; None if unavailable."""
    p = _read_geojson_gz(CADASTRE_PARCELLES_URL.format(dep=cfg.departement, insee=cfg.insee_code))
    b = _read_geojson_gz(CADASTRE_BATIMENTS_URL.format(dep=cfg.departement, insee=cfg.insee_code))
    if p is None or b is None or len(p) == 0:
        return None
    return building_agreement_rate(p.to_crs(2154), b.to_crs(2154))


def fetch_insee_vacancy(insee_code: str, cache_dir="output/validation_cache"):
    """Best-effort INSEE housing-vacancy %. None on any failure (degrade).

    NOTE: re-verify the page/selector live before trusting (sources move). The
    parser is intentionally defensive; a miss returns None, never an exception.
    """
    import re, urllib.request
    cache = Path(cache_dir) / f"insee_vacancy_{insee_code}.txt"
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        try:
            return float(cache.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
    try:
        req = urllib.request.Request(
            INSEE_DOSSIER_URL.format(insee=insee_code),
            headers={"User-Agent": "lvtshift-fr-validation/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r"[Ll]ogements?\s+vacants?.{0,200}?(\d{1,2}[.,]\d)\s*%", html, re.S)
        if not m:
            return None
        val = float(m.group(1).replace(",", "."))
        cache.write_text(str(val), encoding="utf-8")
        return val
    except Exception as exc:
        print(f"  [validate] INSEE vacancy fetch failed for {insee_code}: {exc}")
        return None


def validate_commune(commune_key, df, cfg, cache_dir="output/validation_cache",
                     data_dir="site/public/data", insee_vacancy="__FETCH__",
                     cadastre="__FETCH__") -> dict:
    """Assemble + write <commune>.validation.json. Pass insee_vacancy/cadastre
    explicitly (incl. None) to stay offline in tests; default fetches live."""
    headline = ew.build_headline(df)
    buckets = ew.build_buckets(df)
    underused = sum(b["value_pct_of_base"] or 0 for b in buckets
                    if b["bucket"] in ("vacant", "lt10", "r10_25", "r25_50"))

    if insee_vacancy == "__FETCH__":
        insee_vacancy = fetch_insee_vacancy(cfg.insee_code, cache_dir)
    if cadastre == "__FETCH__":
        cadastre = fetch_cadastre_agreement(cfg, cache_dir)

    checks = []

    # 1) INSEE housing vacancy (independent, directional across communes)
    checks.append({
        "benchmark": "Vacance des logements (INSEE)",
        "independence": "independent",
        "external_value_pct": insee_vacancy,
        "model_comparable_pct": round(underused, 1),
        "model_comparable_label": "part sous-bâtie/vacante de la base (valeur)",
        "status": "non disponible" if insee_vacancy is None else "recorded",
        "note": ("Corrélation directionnelle entre communes (vacance INSEE vs "
                 "foncier sous-utilisé), pas une égalité par commune."),
    })

    # 2) National land-share band (independent)
    checks.append(land_share_band_check(headline["land_share_pct"]))

    # 3) Cadastre vs BD TOPO building map (data quality, NOT economic)
    model_built_share = round(
        100.0 * float((df["property_category"] != "Vacant Land").sum()) / len(df), 1) if len(df) else None
    if cadastre is None:
        checks.append({
            "benchmark": "Carte du bâti (cadastre DGFiP vs BD TOPO)",
            "independence": "data-quality",
            "status": "non disponible",
            "note": "Couche cadastre `batiments` non récupérée.",
        })
    else:
        cad = cadastre["cadastre_built_share_pct"]
        gap = abs((cad or 0) - (model_built_share or 0))
        checks.append({
            "benchmark": "Carte du bâti (cadastre DGFiP vs BD TOPO)",
            "independence": "data-quality",
            "cadastre_built_share_pct": cad,
            "model_built_share_pct": model_built_share,
            "n_parcels_cadastre": cadastre["n_parcels"],
            "n_buildings_cadastre": cadastre["n_buildings"],
            "gap_pt": round(gap, 1),
            "status": "ok" if gap <= 10.0 else "flag",
            "note": ("Accord entre deux cartes du bâti d'agences différentes ; "
                     "contrôle qualité de l'entrée 'bâti', pas de la valorisation."),
        })

    out = {
        "commune_key": commune_key, "insee": cfg.insee_code,
        "name": cfg.name, "departement": cfg.departement, "checks": checks,
    }
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    (Path(data_dir) / f"{commune_key}.validation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def validate_all(out_dir="output", cache_dir="output/validation_cache",
                 data_dir="site/public/data") -> dict:
    from config import COMMUNES
    done = []
    for key, cfg in COMMUNES.items():
        slug = cfg.name.lower().replace(" ", "")
        if not (Path(out_dir) / f"{slug}.csv").exists():
            continue
        df = ew.load_parcels(key, out_dir)
        validate_commune(key, df, cfg, cache_dir, data_dir)
        done.append(key)
    return {"validated": done}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="External validation -> validation JSON.")
    ap.add_argument("commune", nargs="?", help="commune key; omit to validate all available")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--data-dir", default="site/public/data")
    a = ap.parse_args()
    if a.commune:
        from config import COMMUNES
        df = ew.load_parcels(a.commune, a.out_dir)
        print(validate_commune(a.commune, df, COMMUNES[a.commune], data_dir=a.data_dir))
    else:
        print(validate_all(a.out_dir, data_dir=a.data_dir))
