/**
 * Decomposition table data: the reform's change for each group split into
 * two steps that add up to its total (export_web._steps):
 *   1. today's tax with housing brought to market values (no other change);
 *   2. the move to the land tax (TVTN), end of the social housing
 *      exemptions included.
 * Each step is in % of the group's tax today. Rows without steps (withheld,
 * older payloads) are left out.
 */

import type { CategoryRow, QuintileRow } from "./types";
import { QUINTILE_LABELS } from "./baselineRange";

export interface StepRow {
  key: string;
  label: string;
  sublabel?: string;
  revaluation: number;
  land: number;
  total: number;
}

export interface StepTable {
  categories: StepRow[];
  quintiles: StepRow[];
}

type WithSteps = Pick<CategoryRow, "total_change_pct" | "step_revaluation_pct" | "step_land_pct">;

function steps(r: WithSteps) {
  const { step_revaluation_pct: a, step_land_pct: b, total_change_pct: t } = r;
  if (a == null || b == null || t == null) return null;
  if (![a, b, t].every(Number.isFinite)) return null;
  return { revaluation: a, land: b, total: t };
}

export function stepTable(
  byCategory: CategoryRow[],
  byQuintile: QuintileRow[] | null | undefined,
): StepTable {
  const categories: StepRow[] = [];
  for (const r of byCategory) {
    const s = steps(r);
    if (s) categories.push({ key: r.category, label: r.label_fr, ...s });
  }
  const quintiles: StepRow[] = [];
  for (const r of [...(byQuintile ?? [])].sort((x, y) => x.quintile - y.quintile)) {
    const s = steps(r);
    if (s)
      quintiles.push({
        key: `q${r.quintile}`,
        label: QUINTILE_LABELS[r.quintile] ?? `Quintile ${r.quintile}`,
        ...s,
      });
  }
  return { categories, quintiles };
}
