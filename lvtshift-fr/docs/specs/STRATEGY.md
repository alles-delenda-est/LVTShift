# Design & strategic steps — LVTShift-FR

Companion to the implementation specs (0001–0004). These are the **decisions**,
not the builds. Each carries: **Why**, **Interaction with the specs**,
**Pros / Cons**, **Next best alternative**. Ordered roughly by leverage.

---

## S1 — Run the Fichiers Fonciers access campaign (the pilot's raison d'être)

**Why.** The project's stated top-level goal is not a number — it is to *make the
case for* CEREMA/DGFiP Fichiers Fonciers access, mapping each open-data compromise
to the administrative field that would resolve it (true per-parcel VLC baseline,
real construction years, exemption flags, declared per-local surfaces, native
MAJIC building↔parcel links). The README table is the best piece of forward
planning in any of the three repos. But **the step has no owner, no trigger, and
no dossier**: nothing says who applies, when, or what the demand requires.

**Interaction with the specs.** The specs are the *evidence* for this campaign,
not a substitute for it. 0001 (deflator), 0002 (band), 0003 (exemptions) each
close a limitation *without* the data grail — which strengthens the dossier ("we
went this far on open data; here is precisely what access unlocks") and removes
the risk that the access table becomes an excuse to defer one-line fixes. Do the
specs first; they are the demo, and "the demo is the argument for access".

**Pros / Cons.** Pro: it's the whole point — access converts every proxy row into
exact administrative data at zero marginal cost to the partner. Con: it's a
relationship/bureaucratic process with an uncertain timeline, outside the repo's
control; over-indexing on it can stall the codeable improvements.

**Next best alternative.** If access is slow or blocked: keep shipping the
open-data fixes (0001–0003 + SHON factor S4) and publish the pilot results as-is
with the limitations register honest — a credible open-data pilot is valuable on
its own and is itself the strongest possible access request.

---

## S2 — Set an upstream contribution strategy (send U2–U4 + roster fixes home)

**Why.** The fork inherits real upstream bugs on every merge and currently
contributes nothing back. The highest-value one is **U2** (`calculate_category_tax
_summary` silently reuses a stale `tax_change` column — provably dropping 38
parcels from st_paul's committed summaries), plus **U3** (zero-base parcels
reported as "0 %", which *does* leak into the FR pilot's category chart), **U4**
(cross-city outputs silently cover 19/22 cities), and the README roster staleness.

**Interaction with the specs.** Partly overlaps Spec 0003 (exemptions) and the FR
charts: U3's "Vacant Land 0 %" bar is the same object the FR infographic already
works around with euro framing. Sending U3 upstream would let the FR side drop its
workaround. Independent of 0001/0002/0004. Best done as small upstream PRs/issues
to `gregmiller00/LVTShift` after the FR specs land (so the fork is demonstrably a
good-faith contributor, not just a taker).

**Pros / Cons.** Pro: fixes bugs Patrick inherits anyway, builds goodwill with an
active research group, U2 is a genuine correctness bug in a tool they publish
with. Con: upstream review latency is outside our control; a fix sent upstream
may sit unmerged, so the fork may still need a local patch in the interim.

**Next best alternative.** If upstream is unresponsive: carry a **thin local
override** for U2/U3 in `lvtshift-fr/` (re-summarise with a coerced `tax_change`,
suppress/annotate the zero-base bar) rather than modifying upstream files — keeps
the "zero upstream modification" rule while protecting the published FR outputs.

---

## S3 — Decide the Filosofi vintage (2021 vs the new 2023 "Filosofi 2")

**Why.** The 2021 pin was a deliberate, documented choice whose justification
("2022 not published") **expired** in May 2026 when INSEE shipped a Filosofi 2 /
2023 IRIS vintage (a methodological break, not directly comparable). The income
quintile charts — a headline output — currently run on data two vintages old while
the disclosure (now corrected in PR #14) says "pending evaluation". This is a
genuine, dated decision point the repo created for itself.

**Interaction with the specs.** Touches the same distributional-output path Spec
0002 (band) renders, and Spec 0004 (CI) would guard against a broken switch.
Independent of 0001/0003. Should be resolved before the band goes public, so the
quintile bands aren't built on knowingly-superseded income data.

**Pros / Cons.** Pro (adopt 2023): freshest income data, removes a standing stale
-data caveat. Con: the methodological break means 2023 is not comparable with the
prior series, and re-basing the IRIS join + re-validating the quintiles is real
work; the DISP_MED field/key names may have changed.

**Next best alternative.** Keep 2021 but **re-document the decision explicitly**
("2023 exists; retained 2021 because <comparability/effort reason>, revisit at
next publication") — the honest hold — rather than letting the "last vintage"
framing quietly rot again.

---

## S4 — Choose the SHON→habitable surface factor (calibration decision)

**Why.** `floor_area = footprint × storeys` is a gross, walls-included (SHOB-like)
surface, but it multiplies both a construction cost stated in €/m² SHON and a
hedonic €/m² estimated on DVF `surface_reelle_bati` (habitable). Both value levels
are overstated (order 10–25 % by building type) and the residual inherits it. This
is now in the limitations register (PR #14), but *fixing* it requires a judgement
call on the conversion factor — it changes every published euro level, so it's a
decision, not a mechanical patch.

**Interaction with the specs.** Deliberately **not** in the implementation specs
because it needs your factor choice. Once chosen, it's a small code change on both
the market and improvement sides of `estimate.py`. It should land *with or before*
Spec 0002 (band), because the band publishes euro levels that this bias currently
inflates.

**Pros / Cons.** Pro (apply a factor, e.g. ×0.8 for collective housing): corrects
a systematic level bias in every published euro figure. Con: the "right" factor
varies by building type and tenure; a single flat factor trades one documented
approximation for another — and the top-down §5 validation partly absorbs the
current bias (both numerator and denominator inflated), so the *land-share* result
is less affected than the euro levels.

**Next best alternative.** Keep the register disclosure and **do not** apply a
factor yet — publish euro levels with the ±band and an explicit "levels overstated
~10–25 %, land shares less so" caveat — if a defensible per-type factor can't be
sourced. Honest disclosure beats a wrong correction.

---

## S5 — Decide the reproducibility architecture (raw-data caching + manifest)

**Why.** Every real run re-downloads every source from live endpoints that
"occasionally move" (config.py's own warning); no doc discloses this, and it makes
runs reproducible as *commands* but not as *data*. A cache + a small manifest
(source, URL, fetch date, row count, hash) per export turns §8 "Reproducibility"
from a description of commands into something closer to real reproducibility, and
makes vintage drift (S3) visible instead of silent.

**Interaction with the specs.** Enables Spec 0004 (CI) to stay honest — CI runs
offline on synthetic data by design, but a cached real-run manifest is what makes
a *published* result reproducible. Orthogonal to 0001–0003 but complements the
deflator (0001) by pinning which vintage of each source produced a given figure.

**Pros / Cons.** Pro: real reproducibility, drift becomes visible, published
figures become traceable to exact source snapshots. Con: caching adds storage +
cache-invalidation logic; the manifest must be maintained or it becomes another
stale artifact.

**Next best alternative.** The minimal version: write a **manifest only** (no
cache) — each `run_commune` emits a `{commune}_sources.json` recording each URL,
fetch timestamp, row count and hash — which delivers the traceability/drift
-visibility benefit without the caching machinery.

---

## S6 — Publication & presentation choices (full French localisation + split "terrain sous-utilisé")

**Why.** The published charts non-technical readers will actually circulate are
half-localised (upstream titles/axes remain English; only currency is swapped),
and the "Terrain sous-utilisé" category lumps constructible vacant land with
agricultural/natural land — in Cahors ~42 % of parcels are A/N, so the headline
"X % paient PLUS" band is structurally inflated by mostly-farmland.

**Interaction with the specs.** Directly shapes how Spec 0002's band is presented
and interacts with Spec 0003 (exemptions change the category bars). The category
split should be decided *before* wiring the band's category-level rendering, so
the band is drawn over the right categories.

**Pros / Cons.** Pro: the images that circulate become accurate and fully French;
splitting the land category removes a structural inflation of the headline card.
Con: full localisation means either forking upstream's chart text (violates the
zero-upstream-modification rule) or extending the `charts_fr` intercept to
titles/axes — more interception surface to maintain.

**Next best alternative.** Split the land category (high value, low cost) but keep
the `charts_fr` currency-only localisation, adding French titles only to the
FR-authored `make_infographic` charts (which we fully control) rather than
re-localising the intercepted upstream report — if extending the intercept is more
than wanted.

---

### Explicitly parked (upstream-owned or process housekeeping)
The three US city export stubs (Scranton/Denver/Morgantown — upstream's, and the
real fix is U4's one-line roster diff, folded into S2). Archiving the stale April
`run_report.md`. Opening GitHub issues for the register items to give the repo a
work queue + feedback surface (pairs with S2). See
`findings/LVTShift/PENDING_NEXT_STEPS.md` / `PROPOSED_NEXT_STEPS.md`.
