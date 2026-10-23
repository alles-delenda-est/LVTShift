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

The chart layer (HeadlineCards, SensitivityBand, WinLoseSplit, CategoryImpactBars,
IncomeQuintileChart) is shared across the site via `src/components/charts/`. All use
the shared palette from `theme.ts` (MARINE, ROUGE, CREME, GRIS, LISERE) which mirrors
the Tailwind `@theme` tokens in `globals.css`.

## Strategy

The build follows a subagent-driven development plan (SDD) with sequential tasks:
1. Data layer (types, loaders, format utilities)
2. Per-chart components
3. The `/resultats` results explorer (Task 6 — now complete)
4. Remaining editorial pages

The `/resultats` page uses a server/client split that is intentional and load-bearing:
the server page calls `loadIndex()` and `loadCommune()` for every commune at build time,
passes the full array to the client `CommunePicker` as props, and the client switches
communes via `useState` with zero latency. This means all commune data is bundled into
the page JS. Now 14 entries (12 communes + 2 ring aggregates, whose member tables add
~180 rows); the 177 ring members are deliberately not individual picker entries.

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

## Open Questions

- Will the departement field reliably distinguish communes with the same name?
  Currently displayed in the select option as "(93)" etc. — but may need INSEE code
  as the authoritative disambiguator if multiple communes share a name across departments.
- Bundle size at scale: at what commune count does the static prerender become too slow
  or the client bundle too large? Likely fine to 50 communes; beyond that, consider
  dynamic loading per commune key.
- The remaining editorial pages (justice, voie-juridique, logement-abordable, etc.)
  are stubs. The theory for those pages will develop as they are built.
