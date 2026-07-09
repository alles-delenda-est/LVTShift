# Implementation specs — LVTShift-FR

Detailed specs for the high-priority "do first" items from the 2026-07 external
review (weekend-review `findings/LVTShift/`). One file per task. Drafts for the
maintainer, not committed roadmap. Scope: `lvtshift-fr/` (Patrick's surface).

| # | Spec | Priority | Depends on | Status |
|---|---|---|---|---|
| 0001 | [Wire the Notaires-INSEE deflator](0001-notaires-insee-deflator.md) | P0 (HIGH, ~1h) | — | Draft |
| 0002 | [Wire the ±10 pt sensitivity band into the pipeline](0002-wire-sensitivity-band.md) | P0 (HIGH) | F9 (on main via #14) | Draft |
| 0003 | [Flag TFPB-exempt stock](0003-flag-tfpb-exempt-stock.md) | P1 (HIGH) | — | Draft |
| 0004 | [Add CI](0004-add-ci.md) | P1 | — | Draft |

**Design & strategic decisions** (the non-code choices around these specs) live
in [STRATEGY.md](STRATEGY.md): the Fichiers Fonciers access campaign, upstream
contribution strategy (U2–U4), the Filosofi 2/2023 vintage decision, the
SHON→habitable factor, reproducibility (caching + manifest), and publication/
localisation choices.

**Why these.** 0001–0003 are the review's "cheap, high-value model fixes that
don't need Fichiers Fonciers access" plus the standing published promise (the
band). 0004 turns "tests exist" into "tests run". Each closes a live gap between
what the docs claim and what the pipeline does.

**Not specced here** (deferred per the review): applying for CEREMA/DGFiP
Fichiers Fonciers access (strategic, no code — needs an owner and a demand
dossier), the SHON→habitable surface factor (F4, changes published levels —
needs Patrick's factor choice), evaluating Filosofi 2 / 2023 (A4, a dated
decision point), localising the published charts fully into French, raw-data
caching + manifest, a feedback route, and sending the upstream U2–U4 fixes to
`gregmiller00/LVTShift` (different repo). See
`findings/LVTShift/PENDING_NEXT_STEPS.md` and `PROPOSED_NEXT_STEPS.md`.
