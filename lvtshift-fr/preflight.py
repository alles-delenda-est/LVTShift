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
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import export_web as ew
from config import DATA_SOURCES as SRC

OK, WARN, FAIL = "OK", "WARN", "FAIL"

# Departments with no open DVF (sales recorded in the Livre Foncier).
ALSACE_MOSELLE = {"57", "67", "68"}

# Land-share sanity band for the validation check (national anchor ~45–50 %,
# widened for dense cores). Outside the band is a WARN to investigate, never a
# target to hit.
LAND_SHARE_BAND = (40.0, 65.0)
# Minimum distinct IRIS incomes for a genuine 5-bin income-quintile chart.
MIN_DISTINCT_INCOMES = 5


def _chk(name, category, severity, message, adaptation=None, detail=None) -> dict:
    return {
        "check": name, "category": category, "severity": severity,
        "message": message, "adaptation": adaptation, "detail": detail or {},
    }


def _probe(url: str, timeout: int = 30):
    """Final HTTP status for `url` following redirects, or None on error.

    Uses a 1-byte ranged GET so it never downloads a whole file: 200/206 =
    present, 404 = absent. Network failures return None (treated as 'unknown').
    """
    req = urllib.request.Request(
        url, headers={"User-Agent": "lvtshift-fr-preflight/1.0", "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


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
    avail = [y for y in years
             if _available(probe(SRC["dvf"].format(
                 year=y, dep=cfg.departement, insee=cfg.insee_code)))]
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
    p = probe(SRC["cadastre_parcelles"].format(dep=cfg.departement, insee=cfg.insee_code))
    if _available(p):
        out.append(_chk("cadastre_parcelles", "source", OK, "Parcellaire cadastral disponible."))
    else:
        out.append(_chk(
            "cadastre_parcelles", "source", FAIL,
            f"Parcellaire cadastral introuvable (HTTP {p}).",
            adaptation="Sans parcellaire, aucune modélisation possible.",
            detail={"http": p}))
    b_url = SRC["cadastre_parcelles"].format(
        dep=cfg.departement, insee=cfg.insee_code).replace("parcelles", "batiments")
    b = probe(b_url)
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


def analyze_run(cfg, out_dir: str = "output") -> list:
    """Post-run validations read from the standard export, if it exists."""
    slug = cfg.name.lower().replace(" ", "")
    path = Path(out_dir) / f"{slug}.csv"
    if not path.exists():
        return [_chk("model_ran", "run", WARN,
                     "Modèle non exécuté (pas de sortie standard).")]
    df = pd.read_csv(path)
    checks = [_chk("model_ran", "run", OK, f"Exécuté : {len(df):,} parcelles.")]

    cur = float(df["current_tax"].sum())
    new = float(df["new_tax"].sum())
    dev = abs(new - cur) / cur if cur else None
    checks.append(_chk(
        "revenue_neutrality", "validation",
        OK if (dev is not None and dev < 0.01) else WARN,
        (f"Neutralité des recettes : écart {dev * 100:.2f} %."
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
        (f"Quintiles de revenu : 5/5 bins produits ({ninc} revenus IRIS distincts)."
         if nq == 5 else
         f"Quintiles de revenu : {nq}/5 bins — revenu IRIS trop peu varié "
         f"({ninc} valeurs distinctes)."),
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
        (f"Part foncière {ls:.1f} % (bande {lo:.0f}–{hi:.0f} %)."
         if ls is not None else "Base imposable nulle."),
        adaptation=(None if inband else
                    "Hors bande : cœur très dense ou imputation à confronter au "
                    "méthodo — signalé, jamais une cible à atteindre."),
        detail={"land_share_pct": round(ls, 1) if ls is not None else None}))
    return checks


def diagnose_commune(commune_key: str, cfg, out_dir: str = "output", probe=_probe) -> dict:
    """Full diagnostic for one commune: source probes + post-run validations."""
    checks = [check_dvf(cfg, probe)] + check_cadastre(cfg, probe) + analyze_run(cfg, out_dir)
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


def diagnose_all(out_dir: str = "output", probe=_probe,
                 md_path: str = "docs/INGESTION_REGISTER.md",
                 json_path: str = "site/public/data/ingestion_register.json") -> dict:
    """Diagnose every configured commune and write the register (MD + JSON)."""
    from config import COMMUNES
    reports = [diagnose_commune(k, cfg, out_dir, probe) for k, cfg in COMMUNES.items()]
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)
    Path(md_path).write_text(_register_markdown(reports), encoding="utf-8")
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(json_path).write_text(
        json.dumps({"communes": reports}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return {
        "communes": len(reports),
        "not_modellable": [r["commune_key"] for r in reports if not r["modellable"]],
        "with_warnings": [r["commune_key"] for r in reports if r["n_warn"]],
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
    if a.commune:
        from config import COMMUNES
        print(json.dumps(diagnose_commune(a.commune, COMMUNES[a.commune], a.out_dir, probe_fn),
                         ensure_ascii=False, indent=2))
    else:
        print(diagnose_all(a.out_dir, probe_fn))
