/**
 * Sensitivity-band helpers: turn the low / high legs of headline_sensitivity
 * into a [below, above] whisker around a central value, for Recharts ErrorBar.
 */

import type { BandCategoryRow, BandQuintileRow } from "./types";

export interface BandSpan {
  /** distance below and above the central value (both ≥ 0) */
  err: [number, number];
  lo: number;
  hi: number;
}

/** Range spanned by the central value and the two band legs, or null when any
 *  of them is missing (no whisker is drawn then). */
export function bandSpan(
  central: number | null | undefined,
  a: number | null | undefined,
  b: number | null | undefined,
): BandSpan | null {
  if (central == null || a == null || b == null) return null;
  if (![central, a, b].every(Number.isFinite)) return null;
  const lo = Math.min(central, a, b);
  const hi = Math.max(central, a, b);
  return { err: [central - lo, hi - central], lo, hi };
}

/** Index rows by a key, ignoring a null/undefined list. */
export function byKey<T, K extends keyof T>(
  rows: T[] | null | undefined,
  key: K,
): Map<T[K], T> {
  return new Map((rows ?? []).map((r) => [r[key], r]));
}

/** Extract a category sensitivity leg's % change for the exact metric plotted
 *  on the central bar — never silently mixing a dwelling-weighted central value
 *  with a parcel-weighted sensitivity leg (returns undefined/null instead). */
export function categoryBandValue(
  row: Pick<BandCategoryRow, "median_change_pct" | "household_median_change_pct"> | undefined,
  metric: "household" | "median",
): number | null | undefined {
  if (!row) return undefined;
  return metric === "household" ? row.household_median_change_pct : row.median_change_pct;
}

/** Extract a quintile sensitivity leg's % change for the exact metric plotted
 *  on the central bar — never silently substituting a parcel median when the
 *  active metric is household-weighted or group-total. */
export function quintileBandValue(
  row: Pick<
    BandQuintileRow,
    "total_change_pct" | "household_median_change_pct" | "median_change_pct_residential"
  > | undefined,
  metric: "total" | "household" | "residential",
): number | null | undefined {
  if (!row) return undefined;
  if (metric === "household") return row.household_median_change_pct;
  if (metric === "total") return row.total_change_pct;
  return row.median_change_pct_residential;
}
