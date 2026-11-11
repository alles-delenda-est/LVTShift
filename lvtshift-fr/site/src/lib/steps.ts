/**
 * Decomposition table data: the reform's change for each group split into
 * three steps that add up to its total (export_web._steps):
 *   1. today's tax with housing brought to market values (no other change);
 *   2. the land tax (TFVN), today's social housing exemptions kept;
 *   3. the end of those exemptions.
 * Each step is in % of the group's tax today. Rows without steps (withheld,
 * older payloads) are left out; the exemptions column is shown only where
 * some group has a non-zero value.
 */

import type { CategoryRow, QuintileRow } from "./types";

export interface StepRow {
  key: string;
  label: string;
  sublabel?: string;
  revaluation: number;
  land: number;
  exemptions: number;
  total: number;
}

export interface StepTable {
  categories: StepRow[];
  quintiles: StepRow[];
  showExemptions: boolean;
}

type WithSteps = Pick<
  CategoryRow,
  "total_change_pct" | "step_revaluation_pct" | "step_land_pct" | "step_exemptions_pct"
>;

function steps(r: WithSteps) {
  const { step_revaluation_pct: a, step_land_pct: b, step_exemptions_pct: c, total_change_pct: t } = r;
  if (a == null || b == null || c == null || t == null) return null;
  if (![a, b, c, t].every(Number.isFinite)) return null;
  return { revaluation: a, land: b, exemptions: c, total: t };
}

const QUINTILE_LABEL = ["", "Revenus les plus modestes", "Revenus modestes", "Revenus médians",
  "Revenus aisés", "Revenus les plus aisés"];

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
        label: `Quintile ${r.quintile}`,
        sublabel: QUINTILE_LABEL[r.quintile],
        ...s,
      });
  }
  const showExemptions = [...categories, ...quintiles].some((r) => r.exemptions !== 0);
  return { categories, quintiles, showExemptions };
}
