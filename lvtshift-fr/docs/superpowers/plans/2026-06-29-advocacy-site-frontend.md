# Advocacy Site — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax. Use superpowers:frontend-design for visual polish during the UI tasks.

**Goal:** A French-language Next.js advocacy site for « Pour une terre productive » that renders the model's aggregate results interactively (commune explorer), presents the methodology + validation register honestly, and hosts the comms pagers — deployed to a Vercel preview.

**Architecture:** Next.js (App Router) reading the **already-built static JSON** in `lvtshift-fr/site/public/data/` at build time via the filesystem (no backend, no runtime API). Pure logic (types, data adapters, French formatter) is unit-tested with Vitest; visual components are verified with `next build` + typecheck + a Playwright smoke. Charts use Recharts.

**Tech Stack:** Next.js 15 (App Router, React 19, TypeScript), Tailwind CSS v4, Recharts 2, `@next/mdx` for pagers, Vitest 2 for unit tests. Node 20+. Vercel root directory = `lvtshift-fr/site`.

## Global Constraints

- **Site root is `lvtshift-fr/site/`** — the Vercel project's root directory; all frontend files live under it.
- **Read, never recompute.** The site only *displays* the JSON in `public/data/`; it performs no modelling and emits no per-parcel data. Aggregates only.
- **French UI only** (v1). All copy, number and currency formatting in French: `1 234 €`, `Md€`/`M€`/`k€`, `12,5 %`, espace insécable before `%` and `€`.
- **Currency is euros.** JSON values are plain numbers + `"currency": "EUR"`; never render a `$`.
- **Honest headlines** (spec §8): lead with the typical owner-occupier *including the share who pay more*; show the ±10 pt sensitivity band on headline claims; label commune/scope on every figure; never headline only favourable extremes.
- **Graceful nulls.** `by_income_quintile` is `null` for small communes (Cahors, Figeac) — the income chart must omit cleanly with an explanatory note, never error or fake bins.
- **9-commune panel.** Mulhouse is **not** in the data (Alsace-Moselle DVF exclusion); the méthodologie page documents the gap. The explorer is driven by `index.json`, so it shows exactly whichever communes have data.
- **Campaign identity:** « Pour une terre productive » / « Récompenser le travail, décourager la rente ».

---

## Data contract (the JSON the site consumes, verified 2026-06-29)

All files in `lvtshift-fr/site/public/data/`:
- `index.json`: `{ communes: IndexCommune[], currency: "EUR" }` where `IndexCommune = { commune_key, name, insee, departement, parcels_modeled, land_share_pct, gross_pct_of_levy }`.
- `<commune_key>.json`: `{ commune_key, insee, name, departement, reference_year, model_type, headline, headline_sensitivity, by_category, by_income_quintile, by_improvement_ratio, provenance, currency }` (full key tree in the TS types below).
- `<commune_key>.validation.json`: `{ commune_key, insee, name, departement, checks: ValidationCheck[] }`.
- `ingestion_register.json`: `{ communes: RegisterCommune[] }`.

---

## File Structure

```
lvtshift-fr/site/
  package.json, tsconfig.json, next.config.mjs, vitest.config.ts, tailwind/globals.css
  vercel.json                         (optional; Vercel root set in dashboard)
  public/data/*.json                  (ALREADY BUILT — do not regenerate here)
  src/
    lib/
      types.ts                        Task 2 — TS types mirroring the JSON
      data.ts                         Task 2 — build-time loaders (fs reads)
      data.test.ts                    Task 2 — Vitest
      format.ts                       Task 3 — French number/currency formatters
      format.test.ts                  Task 3 — Vitest
    components/
      Identity.tsx, Nav.tsx, Footer.tsx        Task 4 — shell
      charts/HeadlineCards.tsx                 Task 5
      charts/WinLoseSplit.tsx                  Task 5
      charts/CategoryImpactBars.tsx            Task 5
      charts/IncomeQuintileChart.tsx           Task 5 (null-safe)
      charts/SensitivityBand.tsx               Task 5
      CommunePicker.tsx                        Task 6 (client)
    app/
      layout.tsx, page.tsx                     Task 7 (landing) / Task 4 (layout)
      resultats/page.tsx                       Task 6 (explorer)
      methodologie/page.tsx                    Task 8
      sources/page.tsx                         Task 8
      (pagers)/[various]/page.tsx              Task 9 (MDX)
    content/pagers/*.mdx                        Task 9
```

Run unit tests: `cd lvtshift-fr/site && npm run test`. Build: `npm run build`. Typecheck: `npm run typecheck`.

---

### Task 1: Scaffold the Next.js app + toolchain

**Files:** Create `lvtshift-fr/site/{package.json, tsconfig.json, next.config.mjs, vitest.config.ts, .gitignore, src/app/layout.tsx, src/app/page.tsx, src/app/globals.css}`

**Interfaces:**
- Produces: a building Next.js app at `lvtshift-fr/site/`; npm scripts `dev`, `build`, `start`, `lint`, `typecheck`, `test`.

- [ ] **Step 1: Scaffold** — from `lvtshift-fr/site/` create `package.json`:

```json
{
  "name": "terre-productive-site",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "^15.1.0", "react": "^19.0.0", "react-dom": "^19.0.0", "recharts": "^2.13.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0", "@types/react": "^19.0.0", "@types/node": "^22.0.0",
    "tailwindcss": "^4.0.0", "@tailwindcss/postcss": "^4.0.0", "postcss": "^8.4.0",
    "vitest": "^2.1.0", "eslint": "^9.0.0", "eslint-config-next": "^15.1.0"
  }
}
```

- [ ] **Step 2: Config files** — `tsconfig.json` (strict, `"paths": {"@/*": ["./src/*"]}`), `next.config.mjs` (`export default {}`), `vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";
import path from "node:path";
export default defineConfig({
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
});
```

`.gitignore`: `node_modules/`, `.next/`, `out/` (but NOT `public/data/` — those JSON ship). Minimal `src/app/globals.css` with `@import "tailwindcss";`, `src/app/layout.tsx` (html/body, French `lang="fr"`), placeholder `src/app/page.tsx`.

- [ ] **Step 3: Install + verify build**

Run: `cd lvtshift-fr/site && npm install && npm run build && npm run test`
Expected: `npm install` succeeds; `next build` completes (placeholder page); `vitest run` reports "no test files" (exit 0).

- [ ] **Step 4: Commit**

```bash
git add lvtshift-fr/site/package.json lvtshift-fr/site/package-lock.json lvtshift-fr/site/tsconfig.json lvtshift-fr/site/next.config.mjs lvtshift-fr/site/vitest.config.ts lvtshift-fr/site/.gitignore lvtshift-fr/site/src
git commit -m "Frontend: scaffold Next.js app (App Router, TS, Tailwind, Vitest)"
```

---

### Task 2: Data types + build-time loaders

**Files:** Create `src/lib/types.ts`, `src/lib/data.ts`, `src/lib/data.test.ts`

**Interfaces:**
- Produces: `Commune`, `IndexCommune`, `Headline`, `SensitivityLeg`, `CategoryRow`, `QuintileRow`, `BucketRow`, `ValidationCheck`, `RegisterCommune` types; loaders `loadIndex(): {communes: IndexCommune[]}`, `loadCommune(key: string): Commune`, `loadValidation(key: string): {checks: ValidationCheck[]} | null`, `loadRegister(): {communes: RegisterCommune[]}`, `communeKeys(): string[]`.

- [ ] **Step 1: Write the failing test** — `src/lib/data.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { loadIndex, loadCommune, communeKeys, loadRegister } from "@/lib/data";

describe("data loaders", () => {
  it("loads the index with the 9 modelled communes", () => {
    const idx = loadIndex();
    expect(idx.communes.length).toBeGreaterThanOrEqual(9);
    expect(idx.communes.find((c) => c.commune_key === "mulhouse")).toBeUndefined();
    expect(idx.communes[0]).toHaveProperty("land_share_pct");
  });
  it("loads a commune payload with headline + sensitivity legs", () => {
    const c = loadCommune("montreuil");
    expect(c.headline.currency).toBe("EUR");
    expect(c.headline_sensitivity.base.land_share_pct).toBeTypeOf("number");
    expect(["object"]).toContain(typeof c.by_category);
  });
  it("tolerates a null income quintile (small communes)", () => {
    const cahors = loadCommune("cahors");
    expect(cahors.by_income_quintile === null || Array.isArray(cahors.by_income_quintile)).toBe(true);
  });
  it("register marks mulhouse not modellable", () => {
    const reg = loadRegister();
    const m = reg.communes.find((c) => c.commune_key === "mulhouse");
    expect(m?.modellable).toBe(false);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd lvtshift-fr/site && npm run test`
Expected: FAIL — cannot resolve `@/lib/data`.

- [ ] **Step 3: Write types + loaders** — `src/lib/types.ts` (mirror the verified contract exactly):

```ts
export interface Headline {
  parcels_modeled: number; tax_base_eur: number; land_base_eur: number;
  improvement_base_eur: number; land_share_pct: number | null; neutral_levy_eur: number;
  gross_shifted_eur: number; net_shifted_eur: number; gross_pct_of_levy: number | null;
  net_pct_of_levy: number | null; gross_bps_of_base: number | null; currency: "EUR";
}
export interface SensitivityLeg {
  land_share_pct: number; gross_pct_of_levy: number | null; net_pct_of_levy: number | null;
  median_change_pct_residential: number | null; share_paying_more_pct: number | null;
}
export interface Sensitivity { delta_pt: number; base: SensitivityLeg; low: SensitivityLeg; high: SensitivityLeg; }
export interface CategoryRow {
  category: string; label_fr: string; parcels: number; share_of_parcels_pct: number | null;
  median_change_pct: number | null; median_change_eur: number; count_paying_more: number;
  share_paying_more_pct: number | null;
}
export interface QuintileRow {
  quintile: number; median_income_eur: number; median_change_pct: number | null;
  median_change_pct_residential: number | null; parcels: number;
}
export interface BucketRow {
  bucket: string; label: string; parcels: number; value_eur: number;
  value_pct_of_base: number | null; share_of_gross_change_pct: number | null;
}
export interface Commune {
  commune_key: string; insee: string; name: string; departement: string;
  reference_year: number | null; model_type: string; headline: Headline;
  headline_sensitivity: Sensitivity; by_category: CategoryRow[];
  by_income_quintile: QuintileRow[] | null; by_improvement_ratio: BucketRow[];
  provenance: { construction_cost_eur_m2: number; land_share_bounds: number[]; note: string };
  currency: "EUR";
}
export interface IndexCommune {
  commune_key: string; name: string; insee: string; departement: string;
  parcels_modeled: number; land_share_pct: number | null; gross_pct_of_levy: number | null;
}
export interface ValidationCheck {
  benchmark: string; independence: string; status: string; note: string;
  external_value_pct?: number | null; model_comparable_pct?: number | null;
  model_comparable_label?: string; [k: string]: unknown;
}
export interface RegisterCheck {
  check: string; category: string; severity: "OK" | "WARN" | "FAIL";
  message: string; adaptation: string | null; detail: Record<string, unknown>;
}
export interface RegisterCommune {
  commune_key: string; name: string; insee: string; departement: string;
  modellable: boolean; verdict: "OK" | "WARN" | "FAIL"; n_fail: number; n_warn: number;
  checks: RegisterCheck[];
}
```

`src/lib/data.ts` (build-time fs reads — runs in Server Components only):

```ts
import fs from "node:fs";
import path from "node:path";
import type { Commune, IndexCommune, ValidationCheck, RegisterCommune } from "@/lib/types";

const DATA = path.join(process.cwd(), "public", "data");
function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(path.join(DATA, file), "utf-8")) as T;
}
export function loadIndex(): { communes: IndexCommune[]; currency: string } {
  return readJson("index.json");
}
export function communeKeys(): string[] {
  return loadIndex().communes.map((c) => c.commune_key);
}
export function loadCommune(key: string): Commune {
  return readJson<Commune>(`${key}.json`);
}
export function loadValidation(key: string): { checks: ValidationCheck[] } | null {
  try { return readJson(`${key}.validation.json`); } catch { return null; }
}
export function loadRegister(): { communes: RegisterCommune[] } {
  return readJson("ingestion_register.json");
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd lvtshift-fr/site && npm run test`
Expected: PASS (4 tests). If a test path can't find JSON, confirm `process.cwd()` is the site dir during vitest (it is, since vitest runs from `lvtshift-fr/site`).

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/site/src/lib
git commit -m "Frontend: data types + build-time JSON loaders (Vitest-tested)"
```

---

### Task 3: French number/currency formatters

**Files:** Create `src/lib/format.ts`, `src/lib/format.test.ts`

**Interfaces:**
- Produces: `euros(n: number): string` (→ `1 234 €`, scaling to `k€`/`M€`/`Md€`), `pct(n: number | null): string` (→ `12,5 %` / `n. d.` for null), `eurosExact(n: number): string` (full euros, spaced thousands), `signedPct(n: number | null): string` (→ `+6,3 %` / `−10,1 %`).

- [ ] **Step 1: Write the failing test** — `src/lib/format.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { euros, pct, signedPct } from "@/lib/format";

const NBSP = " "; // espace insécable
describe("french formatters", () => {
  it("scales euros with insécable spacing", () => {
    expect(euros(1234)).toBe(`1${NBSP}234${NBSP}€`);
    expect(euros(101_800_000)).toBe(`101,8${NBSP}M€`);
    expect(euros(30_480_000_000)).toBe(`30,5${NBSP}Md€`);
  });
  it("formats percentages with a comma and insécable space, null -> n. d.", () => {
    expect(pct(12.5)).toBe(`12,5${NBSP}%`);
    expect(pct(null)).toBe("n. d.");
  });
  it("signs percentages with a true minus sign", () => {
    expect(signedPct(6.3)).toBe(`+6,3${NBSP}%`);
    expect(signedPct(-10.1)).toBe(`−10,1${NBSP}%`);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd lvtshift-fr/site && npm run test -- format`
Expected: FAIL — cannot resolve `@/lib/format`.

- [ ] **Step 3: Write the implementation** — `src/lib/format.ts`:

```ts
const NBSP = " ";
function frNum(n: number, digits = 0): string {
  return n.toLocaleString("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits })
    .replace(/ /g, NBSP); // normalise narrow nbsp to nbsp
}
export function euros(n: number): string {
  const a = Math.abs(n);
  if (a >= 1e9) return `${frNum(n / 1e9, 1)}${NBSP}Md€`;
  if (a >= 1e6) return `${frNum(n / 1e6, 1)}${NBSP}M€`;
  if (a >= 1e4) return `${frNum(n / 1e3, 0)}${NBSP}k€`;
  return `${frNum(n, 0)}${NBSP}€`;
}
export function eurosExact(n: number): string { return `${frNum(n, 0)}${NBSP}€`; }
export function pct(n: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "n. d.";
  return `${frNum(n, 1)}${NBSP}%`;
}
export function signedPct(n: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "n. d.";
  const sign = n > 0 ? "+" : n < 0 ? "−" : "";
  return `${sign}${frNum(Math.abs(n), 1)}${NBSP}%`;
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd lvtshift-fr/site && npm run test -- format`
Expected: PASS. (If `toLocaleString` produces a narrow nbsp ` `, the `.replace` normalises it; the assertions use ` `.)

- [ ] **Step 5: Commit**

```bash
git add lvtshift-fr/site/src/lib/format.ts lvtshift-fr/site/src/lib/format.test.ts
git commit -m "Frontend: French euro/percent formatters (Vitest-tested)"
```

---

### Task 4: App shell — layout, identity, nav, footer

**Files:** Modify `src/app/layout.tsx`, `src/app/globals.css`; Create `src/components/{Identity.tsx, Nav.tsx, Footer.tsx}`

**Interfaces:**
- Produces: a shared layout wrapping all routes with the campaign identity header, a nav linking the IA routes (§6), and a footer. Server components.

- [ ] **Step 1: Build the shell** — `Identity.tsx` renders the title « Pour une terre productive » and tagline « Récompenser le travail, décourager la rente ». `Nav.tsx` links: Accueil `/`, Résultats `/resultats`, Justice `/justice`, Voie juridique `/voie-juridique`, Logement abordable `/logement-abordable`, Exonérations & protections `/exonerations-protections`, Sceptiques `/sceptiques`, Outils existants `/outils-existants`, Méthodologie `/methodologie`, Sources `/sources`. `Footer.tsx`: a short note that figures are model imputations from open data, aggregate-only. Wire all three into `layout.tsx` with `lang="fr"` and a basic Tailwind container. Use the frontend-design skill for visual treatment (serious, civic, legible; restrained palette).

- [ ] **Step 2: Verify build + typecheck**

Run: `cd lvtshift-fr/site && npm run build && npm run typecheck`
Expected: build + typecheck pass; nav renders on the placeholder pages.

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/app/layout.tsx lvtshift-fr/site/src/app/globals.css lvtshift-fr/site/src/components/Identity.tsx lvtshift-fr/site/src/components/Nav.tsx lvtshift-fr/site/src/components/Footer.tsx
git commit -m "Frontend: app shell — campaign identity, nav, footer"
```

---

### Task 5: Result components (Recharts cards + charts)

**Files:** Create `src/components/charts/{HeadlineCards.tsx, WinLoseSplit.tsx, CategoryImpactBars.tsx, IncomeQuintileChart.tsx, SensitivityBand.tsx}`

**Interfaces:**
- Consumes: `Commune` (Task 2 types), `euros`/`pct`/`signedPct` (Task 3).
- Produces: components each taking a typed prop (`{ commune: Commune }` or the relevant slice). `HeadlineCards({headline})`, `WinLoseSplit({byCategory})`, `CategoryImpactBars({byCategory})`, `IncomeQuintileChart({quintiles})` (renders an explanatory note when `quintiles === null`), `SensitivityBand({sensitivity})`. Recharts components are client components (`"use client"`).

- [ ] **Step 1: Build the components.** Concrete requirements:
  - `HeadlineCards`: stat cards — parcels modelled, neutral levy (`euros`), land share (`pct`), and **% who pay more** (from `byCategory` aggregate or a passed figure) shown plainly, not buried (honesty rule).
  - `WinLoseSplit`: a stacked/diverging bar per category showing `count_paying_more` vs the rest, using `share_paying_more_pct`; caption names the typical owner-occupier category and its share who pay more.
  - `CategoryImpactBars`: horizontal bars of `median_change_pct` (or `median_change_eur`) by `label_fr`, sorted; `signedPct` labels; diverging colour at 0.
  - `IncomeQuintileChart`: line/bar of `median_change_pct_residential` across quintiles 1→5; **if `quintiles === null`, render a short note** ("Revenu IRIS trop peu varié dans cette commune pour un découpage en quintiles") instead of a chart.
  - `SensitivityBand`: a caption/strip rendering the ±`delta_pt` band — `low`/`base`/`high` `gross_pct_of_levy` and residential median change — so every headline carries the band.

- [ ] **Step 2: Verify build + typecheck + a render smoke** — temporarily mount the components on `/resultats` (Task 6) or a scratch route, then:

Run: `cd lvtshift-fr/site && npm run build && npm run typecheck`
Expected: pass; no Recharts SSR errors (ensure `"use client"` on chart files).

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/components/charts
git commit -m "Frontend: headline cards + win/lose, category, quintile, sensitivity charts"
```

---

### Task 6: Results explorer `/resultats` + commune picker

**Files:** Create `src/app/resultats/page.tsx`, `src/components/CommunePicker.tsx`

**Interfaces:**
- Consumes: `loadIndex`, `loadCommune` (Task 2); the Task 5 components.
- Produces: a server page that loads all communes' data at build time and a **client** `CommunePicker` that switches the displayed commune without a round-trip (data passed as props from the server page).

- [ ] **Step 1: Build the page.** `resultats/page.tsx` (server): `const index = loadIndex(); const communes = index.communes.map(c => loadCommune(c.commune_key));` pass to `<CommunePicker communes={communes} />`. `CommunePicker.tsx` (`"use client"`): a `<select>`/segmented control over commune names; holds selected key in state; renders `HeadlineCards`, `SensitivityBand`, `WinLoseSplit`, `CategoryImpactBars`, `IncomeQuintileChart` for the selected commune. Every figure labelled with the commune name + reference year (honesty rule). Default to a commune with a full quintile chart (e.g. Montreuil).

- [ ] **Step 2: Verify build + Playwright smoke**

Run: `cd lvtshift-fr/site && npm run build && npm start &` then drive Playwright (MCP) to `http://localhost:3000/resultats`: assert the page renders, the picker lists ≥9 communes, switching to "Cahors" shows the quintile *note* (not a chart), switching to "Montreuil" shows the quintile chart. Stop the server.
Expected: all assertions pass.

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/app/resultats lvtshift-fr/site/src/components/CommunePicker.tsx
git commit -m "Frontend: interactive results explorer with commune picker"
```

---

### Task 7: Landing page `/`

**Files:** Modify `src/app/page.tsx`

**Interfaces:**
- Consumes: `loadIndex` (Task 2), `euros`/`pct` (Task 3).

- [ ] **Step 1: Build the landing.** The campaign essential (one paragraph from `Comms docs/FR-pager-1-quick-takeaway.md`): the problem (idle well-located land), the reform (shift tax off buildings onto land, revenue-neutral, using the *existing* TFPB/TFPNB levers), and the "recettes constantes" framing. A few headline figures aggregated across the panel (e.g. number of communes modelled, typical land share range) pulled from `index.json`. A clear CTA into `/resultats`. Keep claims honest (no cherry-picked extremes).

- [ ] **Step 2: Verify build**

Run: `cd lvtshift-fr/site && npm run build && npm run typecheck`
Expected: pass.

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/app/page.tsx
git commit -m "Frontend: landing page (essential + headline teaser + CTA)"
```

---

### Task 8: Méthodologie + Sources pages

**Files:** Create `src/app/methodologie/page.tsx`, `src/app/sources/page.tsx`

**Interfaces:**
- Consumes: `loadRegister`, `loadValidation`, `loadIndex` (Task 2).

- [ ] **Step 1: Build méthodologie.** Sections: (a) how land value is imputed (classify-then-price; ±10 pt sensitivity), in plain French; (b) **« Confronter le modèle au réel »** — a table from each commune's `*.validation.json` (benchmark, independence label, model comparable, status); (c) the **ingestion register** from `ingestion_register.json` — a per-commune coverage table (modellable, verdict, FAIL/WARN counts) with the structural notes; (d) honest limitations: **Paris absent** (single giant commune, infeasible whole-commune ingest) and **Mulhouse non-modélisable** (Alsace-Moselle / Livre Foncier), the construction-cost calibration caveat, and the small-commune income-quintile gap. `sources/page.tsx`: CPO (déc. 2023), Trannoy & Wasmer (2022), and the open-data lineage (DVF, cadastre Etalab, BD TOPO, GPU, DPE ADEME, REI/OFGL, Filosofi/IRIS).

- [ ] **Step 2: Verify build + typecheck**

Run: `cd lvtshift-fr/site && npm run build && npm run typecheck`
Expected: pass; the validation + register tables render for the 9 communes and Mulhouse appears as a documented gap.

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/app/methodologie lvtshift-fr/site/src/app/sources
git commit -m "Frontend: méthodologie (validation + register + limits) and sources"
```

---

### Task 9: Pager pages (MDX)

**Files:** Create `src/content/pagers/{justice,voie-juridique,logement-abordable,exonerations-protections,sceptiques,outils-existants}.mdx`, the route pages under `src/app/`, a shared `src/components/PagerLayout.tsx`; modify `next.config.mjs` for MDX.

**Interfaces:**
- Consumes: the `Comms docs/FR-pager-*.md` drafts as content sources; `loadCommune` for any inline model figures.

- [ ] **Step 1: Wire MDX + author pagers.** Add `@next/mdx` + `@mdx-js/react` to deps; configure `next.config.mjs` with `createMDX`. `PagerLayout.tsx`: a shared readable article wrapper. Author the six pagers in MDX, adapting the `Comms docs/` drafts. **Honesty rules baked in (spec §8):** where a pager states owner-occupier impact, use the real model figures (e.g. residential median change + share paying more from the explorer data) and *name the share who pay more*; label commune/scope on every number; show the sensitivity band on headline claims; do not headline only favourable extremes. Justice pager placed prominently per the comms feedback.

- [ ] **Step 2: Verify build + Playwright smoke across routes**

Run: `cd lvtshift-fr/site && npm run build && npm start &` then Playwright-visit `/`, `/resultats`, `/justice`, `/methodologie`, `/sources` and assert each returns 200 and renders its `<h1>`. Stop server.
Expected: all routes render.

- [ ] **Step 3: Commit**

```bash
git add lvtshift-fr/site/src/content lvtshift-fr/site/src/app lvtshift-fr/site/src/components/PagerLayout.tsx lvtshift-fr/site/next.config.mjs lvtshift-fr/site/package.json
git commit -m "Frontend: comms pagers as MDX with honest model figures"
```

---

### Task 10: Final verification + Vercel preview

**Files:** none new (config/verify)

- [ ] **Step 1: Full green** — `cd lvtshift-fr/site && npm run lint && npm run typecheck && npm run test && npm run build`. Expected: all pass; no `$` or English in the rendered output (grep the built HTML in `.next` or via Playwright text).
- [ ] **Step 2: Playwright cross-route smoke** — visit every IA route; assert each renders and that `/resultats` switches communes and handles the null-quintile commune.
- [ ] **Step 3: Deploy a Vercel preview** — connect the Vercel project with **root directory `lvtshift-fr/site`**; push the branch to trigger a preview (or `vercel` CLI). Confirm the preview URL renders with the real data. Report the URL.
- [ ] **Step 4: Commit any config** (e.g. `vercel.json` if used) and record the preview URL in the PR description.

---

## Self-Review

**1. Spec coverage (design spec §6/§7/§8):**
- §6 IA — Accueil (Task 7), /resultats (Task 6), pagers (Task 9), /methodologie (Task 8), /sources (Task 8). ✔
- §7 explorer — picker + headline cards + income quintile + category bars + win/lose + ±10pt caption (Tasks 5–6). ✔
- §8 pager honesty — baked into Task 9 (and Task 6 labelling). ✔
- Mulhouse/Paris honesty notes — Task 8. ✔
- Currency cleanliness / French formatting — Task 3 + global constraint. ✔

**2. Placeholder scan:** UI tasks specify component contracts + concrete requirements rather than every Tailwind class — deliberate (visual polish via the frontend-design skill, per the header). Pure-logic tasks (2, 3) carry full code + tests. No "TBD"/"add error handling".

**3. Type consistency:** `Commune`/`IndexCommune`/`Headline`/`Sensitivity`/`CategoryRow`/`QuintileRow`/`BucketRow` defined once in Task 2 and consumed by Tasks 5/6/7/8 with the same names/shapes (verified against the live JSON keys). `by_income_quintile: QuintileRow[] | null` handled in Task 5 (IncomeQuintileChart null-branch) and exercised in the Task 6 smoke (Cahors).

**Known scope notes:** Component-level unit tests are intentionally replaced by typecheck + `next build` + Playwright smoke (no JS unit-test infra exists and adding it for visual components is out of scope); pure logic IS unit-tested (Vitest). Pager number-filling depends on the explorer data already shipped.

## Execution Handoff

(Filled by the skill after save.)
