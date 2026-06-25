# Design — « Pour une terre productive » advocacy site

*Date: 2026-06-24 · Branch target: new feature branch off `main` · Scope: `lvtshift-fr/`*

## 1. Problem & goal

The LVTShift-FR pipeline can model a revenue-neutral shift of the taxe foncière
onto land value for any configured French commune, producing per-parcel outputs,
matplotlib report charts, and a cross-commune infographic. The comms workstream
has produced a campaign identity (**« Pour une terre productive »** /
*« Récompenser le travail, décourager la rente »*) and eight French "pager"
drafts under `Comms docs/`, but with number placeholders (`[à chiffrer]`,
`[+ X %]`) awaiting real model figures.

**Goal:** a public-facing, French-language **advocacy website** that pairs the
persuasion content (the pagers) with the model evidence (interactive results
across a representative set of communes), deployable to Vercel. Audience:
parliamentarians, journalists, élus, and the expert circuit.

## 2. Decisions locked (from brainstorming, 2026-06-24)

- **Site type:** public advocacy site (not an internal dashboard).
- **Results presentation:** interactive, data-driven charts rendered in-browser
  (not static PNGs).
- **Aggregation discipline (no false precision):** the site publishes aggregates
  only — by property category and income quintile — never per-parcel figures.
  This is **not** a data-privacy measure (there is no confidential data: the
  per-parcel figures are *imputations* from open data, not real bills). The
  reason is **epistemic**: the imputation is honest where errors average out
  (category/quintile), but a per-parcel number would imply a precision the method
  does not have. Aggregate-only is the credibility rule from `THEORY.md`.
- **External validation:** the site's credibility rests on independent checks,
  not on revenue-neutrality (which is circular — the tax target is a model
  *input*). A validation layer correlates model aggregates against independent
  open benchmarks (INSEE vacancy, market €/m², national land-share band).
- **Stack:** Next.js, deployed on Vercel (matches existing GitHub→Vercel flow).
- **Pager numbers:** filled from the model **honestly** (lead with the typical
  owner-occupier *including* the share who pay more; reconcile and label every
  figure; show the sensitivity band; never headline only favourable extremes —
  per `Comms docs/260622 LVT comms docs claude feedback.txt`).
- **Commune slate:** the ten below. Paris deliberately omitted (single giant
  commune, infeasible whole-commune ingest; noted honestly on the methodology
  page). Figeac kept over Montpellier (deep-rural point; Sète already covers the
  Méditerranée slot).

## 3. Commune slate (10)

| # | Commune | INSEE | Dépt | Represents | Run status |
|---|---------|-------|------|-----------|-----------|
| 1 | Roubaix | 59512 | 59 | Nord post-industrial, poor, high vacancy | already modeled |
| 2 | Montreuil | 93048 | 93 | Île-de-France dense inner suburb, gentrifying | already modeled |
| 3 | Villeurbanne | 69266 | 69 | Lyon core (autonomous proxy for Lyon) | configured |
| 4 | Grenoble | 38185 | 38 | Prosperous Alpine metro | already modeled |
| 5 | Annemasse | 74012 | 74 | Geneva-border boomtown, extreme land pressure | configured |
| 6 | Cahors | 46042 | 46 | Small rural préfecture, modest incomes | already modeled |
| 7 | Figeac | 46102 | 46 | Deep-rural bourg (~9.7k), micro-scale rural LVT | configured |
| 8 | Sète | 34301 | 34 | Méditerranée — coastal/port/tourist, second homes | new |
| 9 | La Rochelle | 17300 | 17 | Atlantique — prosperous tourist port | new |
| 10 | Mulhouse | 68224 | 68 | Est/Rhin — Alsatian post-industrial, poor + vacant | new (heaviest ingest) |

All ten are ≥5,000 inhabitants, so every commune retains the Filosofi
income-quintile chart. Sète, La Rochelle, Mulhouse need adding to
`config.py::COMMUNES` with construction-cost bands (~1,800–1,850, ~1,800–1,850,
~1,800–1,850 €/m² respectively; refine on the FFB/BT01 gradient).

## 4. Architecture — monorepo, build-time static data

```
lvtshift-fr/
  export_web.py          NEW: per-commune model output -> aggregate JSON
  site/                  NEW: Next.js app (Vercel root directory)
    public/data/
      index.json         list of communes + headline teaser per commune
      <commune>.json     aggregate-only payload for one commune
    content/pagers/       MDX pagers (adapted from Comms docs drafts)
    app/ or pages/        routes (see §6)
    components/charts/    Recharts components
```

The Python pipeline writes static JSON into `site/public/data/`; the site reads
those files at build time. **No backend, no database, no runtime API** — the
data is small, aggregate, and infrequently updated. It also keeps the
aggregation discipline simple: the only thing the browser can receive is what
`export_web.py` chooses to emit, and it emits aggregates only.

*Rejected alternatives:* a runtime API / DB (pointless for static aggregate
data); a separate site repo (splits the workflow; the data producer and consumer
belong together).

## 5. Data contract — `export_web.py`

Reads, per commune, the model output (`output/<commune>.csv` per-parcel frame +
`output/reports/<commune>/metrics_<commune>.csv`) and writes
`site/public/data/<commune>.json` containing **only aggregates**:

- **headline**: parcels modeled; full tax base; land/improvement split (€ and %);
  neutral levy; gross & net € shifted; gross/net as % of levy; bps of base.
- **headline_sensitivity**: the same headline impact figures recomputed at land
  share ±10 pt (the band that every published headline must carry per
  `THEORY.md`). If the pipeline does not already compute this, producing it is in
  scope (re-solve at the two bracketing land shares).
- **by_category**: per `property_category` — count; median `tax_change_pct`;
  median `tax_change` (€/parcel); **count and share paying more** (honest
  win/lose). Mirrors upstream `calculate_category_tax_summary`.
- **by_income_quintile**: Q1→Q5 (binned on `median_income`) — median
  `tax_change_pct`, residential and non-vacant variants (as the existing report
  charts do). Emit a `null`/flag if income data is unavailable.
- **by_improvement_ratio**: the vacant / under-developed / developed buckets
  (already in the metrics CSV).
- **provenance**: `imp_quality` distribution, data-coverage notes, model type
  (`split_rate:4.0`), reference year, and any commune-specific caveats.

`index.json` lists communes with a one-line teaser headline each (for the
explorer's picker and the landing page).

**Currency:** the upstream metrics label columns `_usd` and abbreviate `$…B/M/K`
though the values are euros (known label bug). `export_web.py` emits clean
numeric values plus a `currency: "EUR"` marker; **all** French formatting
(`1 234 €`, `Md€`/`M€`/`k€`) happens in the site's formatter. No `$`/`usd` string
ever reaches a JSON value.

**Aggregation guard (test):** a light shape test asserts each emitted JSON
contains only the aggregate keys above and no row-level array of parcels — so a
future refactor can't accidentally start shipping per-parcel imputations (false
precision), and the leftover US census columns (`minority_pct`, `black_pct`) and
any geoid are dropped. This is a shape check, not a privacy scan.

## 5b. External validation layer — `validate_external.py`

The model's only built-in "check" — revenue-neutrality — is circular: the tax
target (REI produit) is an *input*, so hitting it proves the arithmetic, not the
imputation. Real robustness needs **independent** ground truth. This component
fetches a small set of open external benchmarks per commune (verified reachable
2026-06-25), compares them to model aggregates with explicit tolerance bands, and
writes `site/public/data/<commune>.validation.json`. Each benchmark is labelled
**independent** or **partially circular** so the méthodologie page can present it
honestly.

| Benchmark | Source | Independence | Checks |
|-----------|--------|--------------|--------|
| **Housing vacancy %** | INSEE commune dossier (`insee.fr/fr/statistiques/2011101?geo=COM-<insee>`) | Independent (INSEE census, not used by the model) | The "idle/under-used land" story — does the model put more under-developed/vacant land where INSEE vacancy is high (Roubaix, Mulhouse) and less where it's low (Annemasse)? Directional correlation across the 10, not a per-commune equality. |
| **Market €/m²** | Price portals (JDN / MeilleursAgents / PAP) | **Partially circular** (several are DVF-derived; DVF is the hedonic's input) — flagged | Level-check: the model's implied total value ÷ floor area should sit in the same order of magnitude as the published €/m². Catches gross hedonic errors, not fine calibration. |
| **Land share of value** | National anchor ~45–50% (INSEE comptes de patrimoine, static) | Independent (national aggregate) | Sanity band on the land/improvement split. No per-commune ground truth exists, so this is a *band* (dense cores higher, periphery lower), not a point target. |

**Cross-source building-map check (data quality, *not* economic validation).**
The current-tax baseline hinges on *which parcels carry a building* — the model
derives that from IGN **BD TOPO** footprints (`ingest.py:153`), and already
ingests the cadastre *parcelles* layer (`config.py::cadastre_parcelles`) for
parcel geometry and `contenance`. So neither parcel area nor footprint coverage
can validate the model — they are already **inputs** (checking them would be
circular). The one cadastre layer the model does **not** use is **`batiments`**
(DGFiP-sourced) — an *independent building map of the same parcels from a
different agency* than BD TOPO (IGN). Overlaying it yields a per-commune
agreement rate: where the two disagree on whether a parcel is built (or grossly
on footprint), that flags an ingest/coverage error in the model's most
load-bearing input. Verified reachable per commune via the same Etalab path
(`…/cadastre-{insee}-batiments.json.gz`; Roubaix 59512 = 33,917 parcels /
37,619 cadastre buildings, 2026-06-25). It is reported **alongside** the three
economic benchmarks but labelled distinctly: it corroborates the *physical
building map*, never the land **valuation** or the tax-shift result. Note BD TOPO
carries height/storeys (→ floor area) which the 2-D cadastre footprint does not,
so disagreement is investigated as a possible BD TOPO gap, not assumed to favour
either source.

Design rules:
- **Verify every source live before coding** (the fork's hard rule) — done for
  INSEE + price portals on 2026-06-25; re-verify at implementation.
- **Fetch politely and cache** — one fetch per commune per source, cached to
  `output/validation_cache/`; portals may rate-limit or block bots, so the layer
  must degrade gracefully (a missing benchmark is reported as "non disponible",
  never fabricated).
- **Never tune the model to the benchmark.** This is a *check*, not a calibration
  target — correlation is reported as-is, including where it's poor. A poor
  correlation is a finding to surface, not to hide.
- **Output** per commune: each benchmark's external value, the model's
  comparable, the deviation, the independence label, and a pass/flag against the
  tolerance band. Surfaced on `/methodologie` as a "Confronter le modèle au réel"
  table.

## 6. Site information architecture (French)

- **Accueil** `/` — campaign identity, the one-paragraph essential, headline
  figures, CTA into results.
- **Qui gagne, qui perd** `/resultats` — the interactive results explorer (§7).
- **Pagers** (MDX, adapted from drafts; Justice promoted near the top per the
  feedback note):
  - `/justice`, `/voie-juridique`, `/logement-abordable`,
    `/exonerations-protections`, `/sceptiques`, `/outils-existants`.
- **Méthodologie & limites** `/methodologie` — transparency: how land value is
  imputed, the known limitations, the **"Confronter le modèle au réel"**
  external-validation table (§5b), *and the honest feasibility note on why Paris
  is absent*. Directly answers the "black-box valuation" and "is this doable on
  the 1970 base" risks from the adaptation plan.
- **Sources** `/sources` — CPO (Dec 2023), Trannoy & Wasmer (2022), open-data
  lineage.

Pagers become canonical as MDX in the site; the `Comms docs/` markdown remains
the working drafts (kept in sync when figures change).

## 7. Interactive results explorer

A commune picker drives charts rendered with **Recharts** (sufficient for our
3–4 chart types; React-native; low overhead):

- **Headline stat cards** — parcels, neutral levy, land share, **% who pay more**
  (shown honestly, not buried).
- **Income-quintile** chart — the progressivity gradient Q1→Q5.
- **Category-impact** bars — median €/parcel change by category (vacant /
  under-used land vs built stock).
- **Win/lose split** — shows the majority honestly, including modest losers among
  owner-occupiers.
- Headline figures carry a visible **±10 pt sensitivity-band** caption.

Charts read only from `public/data/<commune>.json`. The picker is populated from
`index.json`, so the explorer automatically covers whichever communes have run.

## 8. Pager content — honesty rules (baked in)

When filling placeholders from the model:
1. Lead with the **typical owner-occupier**, explicitly stating the share who pay
   more.
2. **Reconcile and label** geography/scope on every figure (no two-different-
   numbers-for-the-same-thing slips).
3. Show the **sensitivity band** on headline claims.
4. Never headline only the prettiest extremes.

## 9. Phasing

1. **Exporter** (`export_web.py`) + JSON for the **4 already-modeled communes** —
   unblocks the site with real sample data.
2. **Site shell** — Next.js scaffold, layout, identity, results explorer working
   on those 4.
3. **Commune runs** — add Sète/La Rochelle/Mulhouse to config; run the 6
   not-yet-run communes (Villeurbanne, Annemasse, Figeac, Sète, La Rochelle,
   Mulhouse). Run Mulhouse first (heaviest) so failures surface early. Ship
   whatever runs; flag any that fail rather than block.
4. **External validation** — run `validate_external.py` across the modeled
   communes; review the correlations *before* writing any pager numbers (a poor
   correlation may change what we can honestly claim).
5. **Fill pagers** honestly from completed runs, informed by phase 4.
6. **Deploy** to a Vercel preview.

## 10. Testing & verification

Three layers, strongest emphasis on the external one (the user's request to
"test more robustly"):

- **Software tests (exporter):** aggregation-shape guard (§5, no per-parcel
  arrays); JSON-schema validation of every emitted file; a **golden snapshot** of
  one known commune's aggregate JSON (e.g. Grenoble) so regressions in the
  numbers are caught; a test that headline figures equal the source metrics CSV.
- **External validation (the robustness check):** `validate_external.py` produces
  the model-vs-benchmark table per commune with tolerance bands; the test asserts
  the *independent* benchmarks (INSEE vacancy directional correlation; land-share
  band) fall within tolerance, and **records** the partially-circular €/m² check
  without gating on it. Separately, the **cross-source building-map check**
  (cadastre `batiments` vs BD TOPO) reports a per-commune agreement rate and
  flags any commune below a coverage threshold for manual review — a data-quality
  guard on the building input, not an economic gate. Failures are reported, not
  silenced.
- **Site:** `next build` and typecheck green; the explorer renders for every
  commune in `index.json`; spot-check that displayed figures equal the JSON
  values; French currency formatting verified (no `$`).

## 11. Risks & non-goals

- **The 10 runs are the long pole.** Live open-data ingest can be slow or fail
  (Mulhouse heaviest). The site must degrade gracefully — it presents whichever
  communes have valid JSON. We do **not** promise all ten; we ship what runs.
- **Pager figures depend on completed runs** — number-filling (phase 4) is gated
  on phase 3.
- **Non-goals:** no per-parcel maps or bills (false precision, not privacy); no
  user accounts; no CMS; no live re-running of the model from the browser;
  English UI (French only for v1, though pager English drafts exist).
- **Validation is a check, never a calibration target** — if a benchmark
  correlates poorly, we surface it on the méthodologie page, not tune the model
  to it. Some external sources may rate-limit/block; the layer degrades to "non
  disponible" rather than fabricating.

## 12. Open questions

- Does `run_pipeline.py` already compute the ±10 pt land-share sensitivity, or
  must `export_web.py` re-solve to produce it? (Resolve during planning; if not
  present, it is in scope for the exporter.)
- Exact Recharts vs. a lighter alternative (e.g. Observable Plot) — defaulting to
  Recharts unless the plan surfaces a reason to switch.
- Vercel project: new project rooted at `lvtshift-fr/site`; confirm build command
  and that the JSON data is committed (not gitignored — the per-parcel CSVs are
  gitignored, but the aggregate JSON must ship).
- Which market-€/m² source is the least DVF-circular and most bot-tolerant
  (MeilleursAgents vs PAP vs JDN)? Pick during implementation after a live probe;
  if all are too circular/blocked, drop the €/m² check and lean on the two
  independent benchmarks (vacancy, land-share band).
