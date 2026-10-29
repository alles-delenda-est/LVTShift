"""Ingestion preflight diagnostics + comprehensive per-commune register.

For each commune this module (1) **detects** whether each open-data source is
available, (2) **signals** the result as OK/WARN/FAIL with a plain-language
message, (3) **analyses** the cause (e.g. the Alsace-Moselle DVF exclusion vs a
transient miss vs thin data), and (4) notes the **adaptation** taken or possible.
It then runs the key post-run validations from the model output. `diagnose_all`
writes a complete register — Markdown (human) + JSON (machine, ships to the site)
— so every commune has an honest, auditable analysis, including the ones that
cannot be modelled and exactly why.

A *check*, not a calibration step: nothing here tunes the model. Live probes are
injectable (`probe=`) so the logic is unit-testable offline.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import export_web as ew
from config import DATA_SOURCES as SRC, data_codes_of, slug_of

OK, WARN, FAIL = "OK", "WARN", "FAIL"

# Departments with no open DVF (sales recorded in the Livre Foncier).
ALSACE_MOSELLE = {"57", "67", "68"}

# Land-share sanity band for the validation check (national anchor ~45–50 %,
# widened for dense cores). Outside the band is a WARN to investigate, never a
# target to hit.
LAND_SHARE_BAND = (40.0, 65.0)
# Minimum distinct IRIS incomes for a genuine 5-bin income-quintile chart.
MIN_DISTINCT_INCOMES = 5
# Share of built parcels pinned at a land-share bound above which the split is
# considered set by the clip rather than measured.
CLIP_WARN_PCT = 50.0


def _fr(x: float, digits: int = 0) -> str:
    """French number typography for register messages shown on the site:
    decimal comma, no-break space between thousands (matches site/src/lib/format.ts)."""
    return f"{x:,.{digits}f}".translate(str.maketrans({",": "\u00a0", ".": ","}))


def _chk(name, category, severity, message, adaptation=None, detail=None) -> dict:
    return {
        "check": name, "category": category, "severity": severity,
        "message": message, "adaptation": adaptation, "detail": detail or {},
    }


def _probe(url: str, timeout: int = 30, attempts: int = 3):
    """Final HTTP status for `url` following redirects, or None on error.

    Uses a 1-byte ranged GET so it never downloads a whole file: 200/206 =
    present, 404 = absent. Transient failures (dropped connection, timeout,
    429, 5xx) are retried with a short backoff, so one flaky request among
    many parallel probes does not turn into a spurious WARN; if every attempt
    fails the result is None (treated as 'unknown').
    """
    req = urllib.request.Request(
        url, headers={"User-Agent": "lvtshift-fr-preflight/1.0", "Range": "bytes=0-0"})
    status = None
    for attempt in range(max(1, attempts)):
        if attempt:
            time.sleep(2 ** attempt)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            status = e.code
            if e.code != 429 and e.code < 500:
                return e.code
        except Exception:
            status = None
    return status


def _available(status) -> bool:
    return status in (200, 206)


def check_dvf(cfg, probe=_probe) -> dict:
    """DVF (sales) availability — the load-bearing source for land valuation."""
    if cfg.departement in ALSACE_MOSELLE:
        return _chk(
            "dvf_coverage", "source", FAIL,
            f"Dépt {cfg.departement} (Alsace-Moselle) : ventes au Livre Foncier, "
            "absentes du DVF ouvert.",
            adaptation="Non modélisable par la méthode hédonique DVF. Pistes : "
                       "source Livre Foncier (DGFiP/ANCT) ou retrait du panel.",
            detail={"dept": cfg.departement, "years_available": 0,
                    "structural": "alsace_moselle_dvf_exclusion"})
    years = list(cfg.dvf_years)
    codes = data_codes_of(cfg)
    # a year counts only if EVERY data code (arrondissement) has its file —
    # a Paris year missing one arrondissement would bias that arrondissement
    avail = [y for y in years
             if all(_available(probe(SRC["dvf"].format(
                 year=y, dep=cfg.departement, insee=c))) for c in codes)]
    n = len(avail)
    if n == 0:
        return _chk(
            "dvf_coverage", "source", FAIL,
            f"Aucun fichier DVF pour {cfg.insee_code} ({years[0]}–{years[-1]}).",
            adaptation="Vérifier l'INSEE / le chemin ; sans DVF la méthode hédonique "
                       "ne peut pas tourner.",
            detail={"years_available": 0, "years_tested": years})
    if n < len(years):
        return _chk(
            "dvf_coverage", "source", WARN,
            f"DVF partiel : {n}/{len(years)} années disponibles {avail}.",
            adaptation="Années manquantes ignorées ; repli médiane communale / "
                       "EPTB national si comparables trop rares (déjà en place).",
            detail={"years_available": n, "years": avail})
    return _chk("dvf_coverage", "source", OK,
                f"DVF complet : {n}/{len(years)} années.",
                detail={"years_available": n})


def check_cadastre(cfg, probe=_probe) -> list:
    """Cadastre parcelles (required) + batiments (validation only)."""
    out = []
    codes = data_codes_of(cfg)
    statuses = {c: probe(SRC["cadastre_parcelles"].format(dep=cfg.departement, insee=c))
                for c in codes}
    bad = {c: st for c, st in statuses.items() if not _available(st)}
    p = next(iter(bad.values())) if bad else 200
    if bad and len(bad) < len(codes):
        out.append(_chk(
            "cadastre_parcelles", "source", FAIL,
            f"Parcellaire manquant pour {len(bad)}/{len(codes)} arrondissements "
            f"({', '.join(sorted(bad))}).",
            adaptation="Un arrondissement sans parcelles fausserait la répartition "
                       "du produit communal : ne pas modéliser en l'état.",
            detail={"missing_codes": sorted(bad)}))
        return out
    if _available(p):
        out.append(_chk("cadastre_parcelles", "source", OK, "Parcellaire cadastral disponible."))
    else:
        out.append(_chk(
            "cadastre_parcelles", "source", FAIL,
            f"Parcellaire cadastral introuvable (HTTP {p}).",
            adaptation="Sans parcellaire, aucune modélisation possible.",
            detail={"http": p}))
    b_status = {c: probe(SRC["cadastre_parcelles"].format(
                    dep=cfg.departement, insee=c).replace("parcelles", "batiments"))
                for c in codes}
    b_bad = [st for st in b_status.values() if not _available(st)]
    b = b_bad[0] if b_bad else 200
    if _available(b):
        out.append(_chk("cadastre_batiments", "source", OK,
                        "Bâti cadastral (DGFiP) disponible pour le contrôle croisé."))
    else:
        out.append(_chk(
            "cadastre_batiments", "validation", WARN,
            f"Bâti cadastral indisponible (HTTP {b}) : contrôle croisé bâti impossible.",
            adaptation="Le contrôle qualité cadastre-vs-BD TOPO sera 'non disponible'.",
            detail={"http": b}))
    return out


# Share of the commune's total FB "montant réel" that the modelled layers may
# leave out (syndicats, TSE, GEMAPI…) before we flag it. Above this, the
# revenue-neutral envelope materially understates the real foncier-bâti bill.
REI_EXCLUDED_WARN = 0.05


def _rei_fb_by_layer(cfg) -> dict:
    """{year: {destinataire: montant réel}} for FB, from OFGL REI (live)."""
    import urllib.parse
    from ingest import _get
    where = (f'idcom="{cfg.insee_code}" and dispositif_fiscal="FB" '
             f'and varlib like "MONTANT"')
    rows = []
    # paginate: a single page would silently drop rows past 100. Opendatasoft
    # refuses offset + limit > 10 000, so stop there with a clear error.
    for offset in range(0, 10_000, 100):
        q = urllib.parse.urlencode({
            "where": where, "limit": 100, "offset": offset,
            "order_by": "annee,destinataire,varlib",
            "select": "annee,destinataire,varlib,valeur"})
        page = json.loads(_get(f"{SRC['ofgl_rei']}?{q}")).get("results", [])
        rows.extend(page)
        if len(page) < 100:
            break
    else:
        raise RuntimeError(f"REI query for {cfg.insee_code} exceeds 10 000 rows")
    out = {}
    for r in rows:
        if r.get("valeur") is None or "MONTANT R" not in (r.get("varlib") or "").upper():
            continue
        out.setdefault(r["annee"], {})
        out[r["annee"]][r["destinataire"]] = (
            out[r["annee"]].get(r["destinataire"], 0.0) + float(r["valeur"]))
    return out


def check_rei_layers(cfg, layers=("Commune", "GFP"), fetch=_rei_fb_by_layer) -> dict:
    """Which FB beneficiary layers exist, and how much the modelled ones omit.

    Answers 'are we holding the whole foncier-bâti bill neutral?' with data
    rather than assumption (e.g. whether EPTs in the petite couronne levy FB).
    """
    try:
        by_year = fetch(cfg)
    except Exception as exc:   # network etc.: unknown, not a failure of the commune
        return _chk("rei_layers", "source", WARN,
                    f"REI non interrogeable ({type(exc).__name__}).",
                    detail={"error": type(exc).__name__})   # no local paths in public JSON
    if not by_year:
        return _chk("rei_layers", "source", FAIL,
                    f"Aucun produit FB 'montant réel' au REI pour {cfg.insee_code}.",
                    adaptation="Sans produit fiscal, pas de cible de neutralité : "
                               "vérifier le code INSEE fiscal (arrondissements : "
                               "utiliser le code de la commune).")
    year = max(by_year)
    lay = by_year[year]
    total = sum(lay.values())
    kept = sum(v for k, v in lay.items() if k in layers)
    excluded = {k: round(v) for k, v in lay.items() if k not in layers}
    share = (total - kept) / total if total else 0.0
    sev = OK if kept and share <= REI_EXCLUDED_WARN else WARN
    return _chk(
        "rei_layers", "source", sev,
        (f"REI FB {year} : couches {', '.join(sorted(lay))} ; modélisé "
         f"{'+'.join(layers)} = {_fr(kept)}\u00a0€ ; hors périmètre "
         f"{_fr(share * 100, 1)}\u00a0% du produit FB total."),
        adaptation=(None if sev == OK else
                    "Part non modélisée significative : choix de périmètre à "
                    "documenter (syndicats/TSE/GEMAPI) ou à élargir."),
        detail={"year": year, "layers": {k: round(v) for k, v in lay.items()},
                "modelled_eur": round(kept), "excluded": excluded,
                "excluded_share_pct": round(share * 100, 2)})


def analyze_run(cfg, out_dir: str = "output") -> list:
    """Post-run validations read from the standard export, if it exists."""
    slug = slug_of(cfg)
    path = Path(out_dir) / f"{slug}.csv"
    if not path.exists():
        return [_chk("model_ran", "run", WARN,
                     "Modèle non exécuté (pas de sortie standard).")]
    df = pd.read_csv(path)
    checks = [_chk("model_ran", "run", OK, f"Exécuté : {_fr(len(df))} parcelles.")]

    cur = float(df["current_tax"].sum())
    new = float(df["new_tax"].sum())
    dev = abs(new - cur) / cur if cur else None
    checks.append(_chk(
        "revenue_neutrality", "validation",
        OK if (dev is not None and dev < 0.01) else WARN,
        (f"Neutralité des recettes : écart {_fr(dev * 100, 2)}\u00a0%."
         if dev is not None else "Recettes courantes nulles — à investiguer."),
        detail={"deviation_pct": round(dev * 100, 3) if dev is not None else None}))

    # Authoritative: ask the real exporter whether 5 quintile bins actually form
    # (≥5 distinct incomes is necessary but not sufficient — quantile boundaries
    # can collapse on tied IRIS values, as for Cahors).
    ninc = int(df["median_income"].nunique()) if "median_income" in df.columns else 0
    try:
        q = ew.build_by_income_quintile(df)
    except Exception:
        q = None
    nq = len(q) if q else 0
    checks.append(_chk(
        "income_quintiles", "validation",
        OK if nq == 5 else WARN,
        (f"Quintiles de revenu : 5/5 groupes produits ({ninc} revenus IRIS distincts)."
         if nq == 5 else
         f"Quintiles de revenu : {nq}/5 groupes — revenu IRIS trop peu varié "
         f"({ninc} valeurs distinctes, minimum {ew.MIN_IRIS_INCOMES})."),
        adaptation=(None if nq == 5 else
                    "Structurel (petite commune / peu d'IRIS) : agrégat quintile "
                    "mis à null, aucun graphique publié."),
        detail={"quintile_bins": nq, "distinct_incomes": ninc}))

    land = float(df["taxable_land_value"].sum())
    base = land + float(df["taxable_improvement_value"].sum())
    ls = 100.0 * land / base if base else None
    lo, hi = LAND_SHARE_BAND
    inband = ls is not None and lo <= ls <= hi
    checks.append(_chk(
        "land_share_band", "validation", OK if inband else WARN,
        (f"Part foncière {_fr(ls, 1)}\u00a0% (bande {lo:.0f}–{hi:.0f}\u00a0%)."
         if ls is not None else "Base imposable nulle."),
        adaptation=(None if inband else
                    "Hors bande : cœur très dense ou imputation à confronter au "
                    "méthodo — signalé, jamais une cible à atteindre."),
        detail={"land_share_pct": round(ls, 1) if ls is not None else None}))

    # Is the land/building split measured, or set by the clip? When most built
    # parcels sit at the upper land-share bound, every parcel has the same
    # split, so the land tax collapses into a tax proportional to market value:
    # the result then measures a revaluation, not land-vs-building (Paris).
    lo_b, hi_b = getattr(cfg, "land_share_bounds", (0.15, 0.85))
    imp = df["taxable_improvement_value"]
    tot = df["taxable_land_value"] + imp
    built = imp > 0
    share_b = (df.loc[built, "taxable_land_value"] / tot[built])
    at_cap = float((share_b >= hi_b - 1e-3).mean() * 100) if built.any() else 0.0
    at_floor = float((share_b <= lo_b + 1e-3).mean() * 100) if built.any() else 0.0
    bound = max(at_cap, at_floor)
    checks.append(_chk(
        "land_share_clip", "validation", OK if bound <= CLIP_WARN_PCT else WARN,
        (f"Parcelles bâties à la borne de part foncière : {_fr(at_cap, 1)}\u00a0% au plafond "
         f"({hi_b * 100:.0f}\u00a0%), {_fr(at_floor, 1)}\u00a0% au plancher ({lo_b * 100:.0f}\u00a0%)."),
        adaptation=(None if bound <= CLIP_WARN_PCT else
                    "La répartition terrain/bâti est fixée par la borne, pas "
                    "mesurée : l'impôt foncier y devient proportionnel à la valeur "
                    "vénale (effet de revalorisation). Résultats à présenter comme "
                    "tels ; lever la borne ou caler coûts/dépréciation."),
        detail={"at_cap_pct": round(at_cap, 1), "at_floor_pct": round(at_floor, 1)}))
    return checks


def diagnose_commune(commune_key: str, cfg, out_dir: str = "output", probe=_probe,
                     rei_fetch=_rei_fb_by_layer) -> dict:
    """Full diagnostic for one commune: source probes + post-run validations.

    rei_fetch=None skips the live REI layer check (offline / --no-probe)."""
    checks = [check_dvf(cfg, probe)] + check_cadastre(cfg, probe)
    if rei_fetch is not None:
        checks.append(check_rei_layers(cfg, fetch=rei_fetch))
    checks += analyze_run(cfg, out_dir)
    n_fail = sum(c["severity"] == FAIL for c in checks)
    n_warn = sum(c["severity"] == WARN for c in checks)
    source_fail = any(c["severity"] == FAIL and c["category"] == "source" for c in checks)
    return {
        "commune_key": commune_key,
        "insee": cfg.insee_code,
        "name": cfg.name,
        "departement": cfg.departement,
        "modellable": not source_fail,
        "verdict": FAIL if n_fail else (WARN if n_warn else OK),
        "n_fail": n_fail,
        "n_warn": n_warn,
        "checks": checks,
    }


def _register_markdown(reports: list) -> str:
    lines = [
        "# Registre d'ingestion & validations par commune",
        "",
        "*Généré par `preflight.py`. Pour chaque commune : disponibilité des "
        "sources ouvertes, cause analysée de tout échec, adaptation, et les "
        "validations clés du modèle. C'est un contrôle, jamais une cible de "
        "calibration.*",
        "",
        "## Synthèse",
        "",
        "| Commune | INSEE | Dépt | Modélisable | Verdict | FAIL | WARN |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in reports:
        lines.append(
            f"| {r['name']} | {r['insee']} | {r['departement']} | "
            f"{'oui' if r['modellable'] else '**non**'} | {r['verdict']} | "
            f"{r['n_fail']} | {r['n_warn']} |")
    lines += ["", "## Détail par commune", ""]
    for r in reports:
        lines.append(f"### {r['name']} ({r['insee']}, dépt {r['departement']}) — {r['verdict']}")
        if not r["modellable"]:
            lines.append("")
            lines.append("> **Non modélisable** par la méthode actuelle (voir ci-dessous).")
        lines.append("")
        for c in r["checks"]:
            line = f"- **[{c['severity']}] {c['check']}** ({c['category']}) — {c['message']}"
            if c.get("adaptation"):
                line += f"  \n  *Adaptation :* {c['adaptation']}"
            lines.append(line)
        lines.append("")
    return "\n".join(lines)


def diagnose_all(out_dir: str = "output", probe=_probe, rei_fetch=_rei_fb_by_layer,
                 md_path: str = "docs/INGESTION_REGISTER.md",
                 json_path: str = "site/public/data/ingestion_register.json",
                 workers: int = 8) -> dict:
    """Diagnose every configured commune and write the register (MD + JSON)."""
    from config import COMMUNES, SITE_COMMUNES, TERRITORIES
    from concurrent.futures import ThreadPoolExecutor

    def run(keys):
        # probes are I/O-bound HEAD-style requests: a small thread pool keeps
        # the ~190-commune register to minutes without hammering the servers
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return list(ex.map(
                lambda k: diagnose_commune(k, COMMUNES[k], out_dir, probe, rei_fetch), keys))

    reports = run(list(SITE_COMMUNES))
    members = {t: run([k for k in spec["members"] if k not in SITE_COMMUNES])
               for t, spec in TERRITORIES.items()}
    md = _register_markdown(reports)
    for t, reps in members.items():
        md += "\n\n" + _register_markdown(reps).replace(
            "# Registre d'ingestion & validations par commune",
            f"# Territoire {TERRITORIES[t]['name']} — communes membres", 1)
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(md_path).write_text(md, encoding="utf-8")
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(
        json.dumps({"communes": reports, "territory_members": members},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    everything = reports + [r for reps in members.values() for r in reps]
    return {
        "communes": len(everything),
        "not_modellable": [r["commune_key"] for r in everything if not r["modellable"]],
        "with_warnings": [r["commune_key"] for r in everything if r["n_warn"]],
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Ingestion preflight + commune register.")
    ap.add_argument("commune", nargs="?", help="commune key; omit to register all")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--no-probe", action="store_true",
                    help="skip live source probes (static rules + post-run checks only)")
    a = ap.parse_args()
    probe_fn = (lambda url, timeout=30: None) if a.no_probe else _probe
    rei_fn = None if a.no_probe else _rei_fb_by_layer
    if a.commune:
        from config import COMMUNES
        print(json.dumps(diagnose_commune(a.commune, COMMUNES[a.commune], a.out_dir,
                                          probe_fn, rei_fn),
                         ensure_ascii=False, indent=2))
    else:
        print(diagnose_all(a.out_dir, probe_fn, rei_fn))
