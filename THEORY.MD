# Theory: LVTShift-FR Civic Website

## Problem

France's taxe foncière taxes land and buildings at the same rate, which penalises
construction while rewarding land hoarding. A revenue-neutral shift of the full levy
onto land value alone would encourage building and dampen land speculation — but the
political case requires credible, commune-specific evidence presented honestly to
citizens, journalists, and policymakers.

The problem is not modelling (the upstream lvt/ solver handles that). The problem is
translation: turning per-commune JSON outputs into a trustworthy public-facing website
that communicates both the promise (productivity gains, progressive incidence) and the
honest costs (some owner-occupiers pay more) without distortion.

## Operating Theory

The site is built as a Next.js 15 App Router project with static generation at build
time. All commune data lives in `public/data/` as JSON files produced by the Python
pipeline. Server components load this data at build time; client components receive it
as plain-object props and handle interactivity without network round-trips.

The central design constraint is the "honesty rule": the share of property owners who
pay more under reform must never be buried. HeadlineCards gives it a rouge accent tile
at equal weight to the positive figures. WinLoseSplit sorts categories by share-paying-
more descending. Reference years are displayed only when known — never fabricated.

A corollary: every headline claim in prose is computed from the payloads at build time
(`lib/impactSummary`), and a vitest pins the counts, so a pipeline re-run that changes
a claim fails a test instead of silently making the prose false.

The chart layer (HeadlineCards, SensitivityBand, WinLoseSplit, CategoryImpactBars,
IncomeQuintileChart) is shared across the site via `src/components/charts/`. All use
the shared palette from `theme.ts` (MARINE, ROUGE, CREME, GRIS, LISERE) which mirrors
the Tailwind `@theme` tokens in `globals.css`.

## Strategy

The build follows a subagent-driven development plan (SDD) with sequential tasks:
1. Data layer (types, loaders, format utilities)
2. Per-chart components
3. The `/resultats` results explorer
4. Remaining editorial pages

The `/resultats` page uses a server/client split that is intentional and load-bearing:
the server page calls `loadIndex()` and `loadCommune()` for every commune at build time,
passes the full array to the client `CommunePicker` as props, and the client switches
communes via `useState` with zero latency. This means all commune data is bundled into
the page JS. Now 14 entries (12 communes + 2 ring aggregates, whose member tables add
~180 rows); the 177 ring members are deliberately not individual picker entries.

Claims are graded by robustness. The biggest uncertainty is not the land share but
today's tax: no public data splits a commune's taxe foncière between homes and
business premises. The site therefore publishes two baselines (central case and a
local variant from the 2017 taxe d'habitation) and prose leads with what holds under
both, giving ranges where they differ.

## Key Discoveries

- The `h1` is owned by `Identity.tsx` (the persistent site banner). Every page must
  use `h2` as its top-level heading — enforced in the resultats page.
- Section IDs inside `CommunePicker` (e.g. `section-indicateurs`) are static strings.
  This is safe for a single-instance use but would cause ARIA collisions if the
  component were mounted twice on one page.
- The Recharts bundle (~46 kB) is already shared across the site. The marginal cost
  of adding a new chart page is small.
- `reference_year` can be null in the Commune type. The honesty rule requires
  omitting the year rather than inventing one when it is null.
- Territories (inner rings) reuse the commune payload shape with `kind:
  "territory"`, `insee: null`, a per-member table and coverage. The picker groups
  them separately; landing totals sum de-duplicated counts because Montreuil and
  Villeurbanne appear both alone and inside their ring. Ring-wide income
  quintiles can mislead (they mix the reform with commune-to-commune differences),
  so territories also show quintiles ranked within each commune.
- The alternative baseline flipped direction (Nov 2026). The old one (raw CFE) gave
  business a smaller share of today's tax, so it was kinder to households; the 2017
  taxe d'habitation variant gives business a larger share almost everywhere (Figeac
  aside), so it is harsher. Prose written for the old alternative ("si elle est plus
  faible, la réforme est plus favorable aux ménages") became the reverse of the truth
  without any test failing, because tests pinned counts, not sentences.
- Under both baselines the poorest fifth fares better than the richest in 11 of 11
  territories: progressivity is robust. Absolute claims are not, and they also
  depend on how built land is valued.
- Site value moved the category story (Nov 2026). Valuing built land as if vacant
  at its zone's density moves tax within each neighbourhood from dense blocks to
  low-rise plots: blocks of 5+ pay less in 13 of 13 territories (10 in the
  variant), houses more in 10 of 13, small 2–4 buildings less in only 4. The
  home page's old « appartement type » was the 2–4 category, so it now names the
  collective block. The richest fifth's total falls in Grenoble and Annemasse, so
  "the richest fifth pays more" is no longer a panel-wide claim. Income-fifth
  totals barely move, as IRIS land totals are kept.

## Open Questions

- Which baseline is closer to the truth? Only the Fichiers fonciers (per-premises
  rental values) would settle it; the 2017 check leans towards the variant in cities.
- Site value cannot be checked against sales of built property; only rare vacant
  and teardown sales measure it. The density elasticity moves the typical house
  by ±15–17 points in Lyon and Villeurbanne: house figures are the least robust
  on the site.
- Draft #58 (flats vs houses across both building categories) predates site
  value and needs rebasing on it.
- Will the departement field reliably distinguish communes with the same name?
  Currently displayed in the select option as "(93)" etc. — but may need INSEE code
  as the authoritative disambiguator if multiple communes share a name across departments.
- Bundle size at scale: at what commune count does the static prerender become too slow
  or the client bundle too large? Likely fine to 50 communes; beyond that, consider
  dynamic loading per commune key.
- The remaining editorial pages (justice, voie-juridique, logement-abordable, etc.)
  are stubs. The theory for those pages will develop as they are built.
