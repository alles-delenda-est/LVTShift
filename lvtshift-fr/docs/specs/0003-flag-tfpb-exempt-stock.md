# Spec 0003 — Flag obviously-TFPB-exempt stock

**Status:** Draft · **Priority:** P1 (HIGH) ·
**Source:** external review BUGS.md F2, PROPOSED_NEXT_STEPS #3 ·
**Est. effort:** ~half a day

---

## 1. Problem

Public buildings (mairies, écoles, hôpitaux), religious buildings, and
permanently-exempt agricultural buildings (bâtiments ruraux, CGI art. 1382) are
**TFPB-exempt in reality**. In the model they (a) absorb a share of today's
produit — `estimate.current_tax` distributes the produit across *all* built
parcels by floor area — and (b) pay LVT in the solve, deflating everyone else's
modelled bill. This hits the two things the pilot actually publishes: the
category-level impact bars (the `Autre`/`Commerce` bars include exempt stock)
and the baseline every percentage change is computed from.

Upstream already supports it: `model_split_rate_tax(..., exemption_flag_col=...)`
zeroes flagged parcels correctly (`lvt/lvt_utils.py`). The FR pipeline passes no
flag column today.

## 2. Goal

Identify obviously-exempt built parcels from open attributes, exclude them from
**both** sides of the ledger (baseline produit distribution and the LVT solve),
and disclose the residual (non-obvious exemptions we still can't see) as a
numbered register item.

## 3. Design

### 3.1 Derive an exemption flag from BD TOPO

`run_commune.derive_parcel_category` already reads BD TOPO `usage_1`/`nature`.
Add a parallel `derive_exemption_flag(buildings) -> Series[bool]` keyed per
parcel, true when the dominant building is obviously exempt:

- `usage_1` (or `nature`) in {Religieux} → exempt (culte).
- Public-service attributes: `nature`/`usage` matching
  Mairie / Enseignement / Hôpital / Établissement public-type values → exempt.
- `usage_1 == 'Agricole'` (bâtiments ruraux, art. 1382-6°) → exempt.

Encode the matched value set in one documented dict (like `USAGE_MAP`), so the
"obviously exempt" rule is auditable and easily extended.

### 3.2 Exclude from the baseline `current_tax`

`estimate.current_tax` — add an `exempt_col` parameter; parcels flagged exempt
get weight 0 in the VLC-proxy distribution (they bear no current TFPB, which is
correct). The produit is then shared only over genuinely-taxable built stock.

### 3.3 Exclude from the LVT solve

`run_pipeline.run` — pass `exemption_flag_col='is_exempt'` into
`model_split_rate_tax`. Upstream zeroes those parcels' new tax and holds them out
of the revenue-neutral solve, so the levy falls only on taxable parcels.

### 3.4 Disclose the residual

Exempt detection from open data is necessarily incomplete (partial exemptions,
ZFU/ZRR temporary exemptions, social-housing abatements are invisible). Add a
numbered limitations-register item: "obvious institutional/religious/agricultural
exemptions are flagged from BD TOPO usage; partial and time-limited exemptions
remain unmodelled."

## 4. Files

| File | Change |
|---|---|
| `run_commune.py` | `derive_exemption_flag`; attach `is_exempt` to parcels; pass through |
| `estimate.py` | `current_tax(..., exempt_col=None)` — zero-weight exempt parcels |
| `run_pipeline.py` | `model_split_rate_tax(..., exemption_flag_col='is_exempt')` |
| `config.py` | documented set of exempt `usage_1`/`nature` values |
| `METHODOLOGY.md` / `METHODOLOGIE.md` §6 | new register item (residual exemptions); update §3.5 baseline description |
| `test_units.py` | exemption tests (see §5) |

## 5. Tests & acceptance

1. **Baseline excludes exempt** — a synthetic commune with one large `Religieux`
   parcel: it bears €0 current tax and the produit is fully distributed over the
   remaining taxable parcels (conservation holds). (Reproduces experiment E6
   from the review, now with the fix.)
2. **Solve excludes exempt** — the flagged parcel's `new_tax` is 0; revenue
   neutrality holds over the taxable set.
3. **Flag derivation** — `derive_exemption_flag` returns true for
   Religieux/Mairie/Enseignement/Agricole dominant buildings, false for
   Résidentiel/Commerce.
4. `test_synthetic.py` still green (default synthetic frame has no exempt flag →
   behaviour unchanged when `exempt_col=None`).

## 6. Risks

- **Over-flagging** — matching too broadly (e.g. all `Annexe`) would wrongly
  exempt taxable dependances. Keep the set tight and documented; err toward
  under-flagging with the residual disclosed.
- **Category bars** — once exempt stock is removed, the `Autre`/`Commerce` bars
  shift; note this in the changelog so the movement isn't mistaken for a bug.
- Depends on BD TOPO attribute coverage per commune; where `usage_1` is null,
  no parcel is flagged (fail-open to taxable — conservative for revenue, and
  disclosed).
