# CLAUDE.md — LVTShift-FR

Guidance for agents working in `lvtshift-fr/`. The repo-root `CLAUDE.md` is the
upstream (US) project's; this file maps the French fork that lives here.

## What this is

A French adaptation of LVTShift: it imputes per-parcel land value from French
**open data** and feeds the *unmodified* upstream solver to model a revenue-neutral
shift of the taxe foncière onto land value. Read `THEORY.md` first to orient.

## Module map

```
config.py        communes, construction costs, land benchmarks, data endpoints
ingest.py        all fetchers: cadastre, DVF, BD TOPO buildings, DPE year,
                 GPU zoning, terrain-à-bâtir comparables, REI (OFGL), IRIS, Filosofi
estimate.py      improvement value, hedonic market value, classify-then-price
                 land value, current-tax baseline
run_pipeline.py  orchestration; calls upstream model_split_rate_tax + export
run_commune.py   live-data driver for one commune (python run_commune.py <key>)
charts_fr.py     euro-localised wrapper over the upstream report
test_synthetic.py  end-to-end test through the real solver (offline)
test_units.py    offline unit tests of the pure logic
```

## Hard rules

- **Zero upstream modification.** Import `lvt` (at the repo root); never edit it.
  Improvements pulled from upstream must keep flowing through.
- **Verify every data source live before coding against it** (endpoint, schema,
  coverage) — every source here was confirmed this way.
- **Aggregate-only results.** Publish by property category / income quintile,
  never per-parcel bills. The imputations are honest at aggregate level only.
- **Flag, don't hide, weak steps** in-band (`lv_flag`, `imp_quality`).

## Workflow conventions (per the user's global CLAUDE.md)

- Economic/parameter choices: research + Gemini (`GEMINI_API_KEY`) review at
  checkpoints; explain trade-offs in plain language (the user is a non-coder
  domain expert).
- One feature per PR; branch off `main`. On Windows, run with `PYTHONUTF8=1`.

## Docs

`METHODOLOGY.md` (full methods reference, EN) · `METHODOLOGIE.md` (parallel FR)
· `THEORY.md` (operating theory, open questions) · `README.md` (French summary) ·
`GUIDE.md` / `GUIDE.fr.md` (plain-English how-to, EN + FR). Keep both methodology
files (and both guides) in sync when things change; the code is canonical.
