# Spec 0001 — Wire the Notaires-INSEE price deflator

**Status:** Draft · **Priority:** P0 (HIGH, ~1 hour) ·
**Source:** external review BUGS.md F3, PROPOSED_NEXT_STEPS #2, PR #1 item 4 ·
**Est. effort:** ~1 hour

---

## 1. Problem

DVF 2021–2025 sales enter the hedonic (`estimate.fit_hedonic`) and the
terrain-à-bâtir price base (`ingest.tab_comparables`) at **nominal** prices.
The Notaires-INSEE house-price index moved materially inside the pooled window
(~+7–8 % 2021, ~+5–6 % 2022, ~−2 % 2023, ~−1 % 2024, ~flat 2025) — an ~8–10-point
peak-to-trough swing. Cells whose sales cluster early get systematically
different price levels than cells clustering late, so the error is **spatially
structured**, not noise. This was flagged in the pilot's own founding review
(PR #1) and is now disclosed in the limitations register (PR #14) but not fixed.

The hook already exists: `fit_hedonic(dvf, deflator=None)`. Nothing calls it
with a deflator (`run_pipeline.run:~93` calls `fit_hedonic(dvf)`).

## 2. Goal

Deflate all pooled DVF sale prices to a common reference year using a cited
Notaires-INSEE annual index, in both the hedonic and the TAB land-comparable
path, so pooled-window price drift no longer biases cell-level values.

## 3. Design

### 3.1 Add the index to config

`config.py` — a small dict of the Notaires-INSEE annual index (national, or
France-métropole ex-IdF vs IdF if a split is warranted), normalised to the
reference year (`reference_year = 2025`):

```python
# Notaires-INSEE indice des prix des logements anciens, base = reference_year.
# Multiplicative factor to bring a sale of year Y to reference_year € .
# Source: INSEE série ..., valeurs annuelles moyennes (cite table id + access date).
NOTAIRES_INSEE_DEFLATOR = {
    2021: 1.0XX,   # 2021 prices × factor → 2025 €
    2022: 1.0XX,
    2023: 1.0XX,
    2024: 1.0XX,
    2025: 1.000,
}
```

> The six numbers must be transcribed from the published INSEE/Notaires index
> with the table id and access date in the comment (the repo's sourcing
> discipline). If an IdF vs province split is used, key by département group and
> document the mapping.

### 3.2 Thread it through the pipeline

- `run_pipeline.run` — pass `estimate.fit_hedonic(dvf,
  deflator=cfg_deflator)` where `cfg_deflator` is `NOTAIRES_INSEE_DEFLATOR`
  (module constant or a `CommuneConfig` field defaulting to it).
- `estimate.fit_hedonic` already applies `deflator.get(year, 1.0)` per row — no
  change needed there beyond confirming the `year` column is the sale year.
- `ingest.tab_comparables` — apply the **same** deflator to the terrain-à-bâtir
  `valeur_fonciere` before computing `eur_m2_land`, so constructible-land prices
  are on the same real basis. Add a `deflator` parameter mirroring `fit_hedonic`.

### 3.3 Reference year consistency

Everything is deflated to `cfg.reference_year` (2025), which is also the
construction-cost and improvement-value basis — so market and improvement sides
share one price year and the residual is internally consistent.

## 4. Files

| File | Change |
|---|---|
| `config.py` | `NOTAIRES_INSEE_DEFLATOR` dict (6 cited numbers) |
| `run_pipeline.py` | pass the deflator into `fit_hedonic` (and to `tab_comparables` via `run_commune`) |
| `ingest.py` | `tab_comparables(cfg, tab, deflator=None)` applies the factor to TAB prices |
| `run_commune.py` | pass `NOTAIRES_INSEE_DEFLATOR` into `classify_and_price_land` → `tab_comparables` |
| `METHODOLOGY.md` / `METHODOLOGIE.md` §3.3 + §6 item 10 | change "nominal pooling" caveat to "deflated with Notaires-INSEE (base 2025)"; keep the residual-method caveats |
| `test_units.py` | new deflator test (see §5) |

## 5. Tests & acceptance

1. **Deflator applied** — `fit_hedonic` with a known deflator shifts the implied
   €/m² by exactly the factor for a single-year, single-cell synthetic frame
   (e.g. a 2021 sale at nominal X, deflator 1.10 → surface reflects 1.10·X).
2. **TAB parity** — `tab_comparables` output €/m²_land scales with the deflator
   identically.
3. **No-op with `deflator=None`** — existing behaviour unchanged (keeps the
   synthetic end-to-end test green).
4. **Revenue neutrality preserved** — `test_synthetic.py` still passes (the
   solver is scale-free in land level; neutrality holds regardless).
5. Numbers in config transcribed and cited; reviewer can trace each to INSEE.

## 6. Risks

- **Which index** — the headline Notaires-INSEE "logements anciens" is national;
  a commune in a diverging local market still carries basis risk. Document that
  the deflator corrects *temporal* drift within the pool, not cross-sectional
  local-market differences (those are the hedonic's job).
- **Annual vs quarterly** — annual averages are adequate for a 5-year pool;
  quarterly would be marginally better and is a documented v2.
