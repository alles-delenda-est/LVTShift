# REVIEW.md — guidance for the AI code reviewer

> Owner: Patrick. Loaded by every automated review of this repo, alongside CLAUDE.md.
> Tune this for a few weeks: whenever a human repeats the same review comment, move it here.

## Scope (this is a fork)

This repo is a fork of Center-for-Land-Economics/LVTShift. The owner's own work is the French adaptation in `lvtshift-fr/`, plus `vercel.json` and `THEORY.MD`. Review focus: `lvtshift-fr/` and the files the owner changed in the PR. Code inherited from upstream is `Pre-existing`: flag real issues, but do not refactor it (this keeps upstream merges painless).

## What failure looks like in this repo
- **Silently wrong totals:** the TFPB shift stops being revenue-neutral against the REI réel (1 % tolerance), or the commune's homes / business-premises split (WC75, CFE base) is calibrated to the wrong year or commune.
- **Plausible but wrong bills:** a land-value imputation in `lvtshift-fr/` uses the wrong construction cost (per m² brut vs habitable), depreciation floor, terrain benchmark (terrain à bâtir, SAFER, ×0.45 / ×0.35 activity factor) or DVF index year, so a parcel's modelled tax looks reasonable but is not.
- **Publication leak:** per-parcel bills or land values reach `lvtshift-fr/site/public/data/` or an export, against the aggregate-only rule in `lvtshift-fr/CLAUDE.md`.
- **Mis-joined data:** BD TOPO buildings, DPE years or parcels attached by centroid instead of area-weighted intersection, or matched to the wrong commune, IRIS zone or millésime.
- Upstream US-property code inherited from LVTShift is out of scope; flag real issues there only as `Pre-existing`.

## What to check first
1. Correctness of any calculation or economic parameter (units, indexation year, currency, nominal vs real).
2. Security: input validation, secrets in code or logs, injection, unsafe deserialisation, dependency risk (OWASP Top 10).
3. Error handling at system boundaries (user input, external APIs, files).
4. Whether the change matches CLAUDE.md conventions — and whether CLAUDE.md now has stale lines.

## Rules for the reviewer
- **Evidence required.** Every finding cites a file and line and says what input breaks it. No guesses from a name.
- **Label every comment** `Important` (a bug / security issue), `Nit` (style), or `Pre-existing` (not introduced by this PR — never blame the author).
- **Cap nits at 3** per review. Drop style-only findings if there is a real bug to report.
- **Start the summary with a count** ("2 Important, 1 Nit, 0 Pre-existing") and say plainly "Nothing to fix" when clean.
- **Do not repeat** a finding already posted on this PR.
- **After 3 rounds**, stop line-by-line review and ask the author to reconsider the approach.
- **After the first few passes, review only the new diff.**
- When you find a bug, **name the bug class** so the author fixes every instance, not just the one quoted.

## Skip these paths
- `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`
- `dist/`, `build/`, `.next/`, `node_modules/`
- `lvtshift-fr/site/public/data/`: generated aggregate JSON shipped to the site (built by the pipeline; review the method, not the numbers)

## Always needs a human (never auto-approve)
- Anything under `.github/workflows/`
- Authentication, payments/billing, secrets handling
- Changes to economic assumptions or parameters (rates, mortality tables, inflation) — a person must confirm the source
- Deployment / release configuration
