/**
 * Income-quintile chart data: which figure each bar and marker shows.
 *
 * The bar is the whole group's total change (Σ new tax ÷ Σ current tax − 1 on
 * its residential parcels). The marker is the typical household's change (the
 * parcel change weighted by dwellings, so a 200-flat block counts 200 times).
 * A plain parcel median counts that block once, like a house, and can show a
 * group "paying more" while the group as a whole pays less.
 *
 * Older payloads carry neither figure; the bar then falls back to the
 * residential parcel median, as before, and `isTotal` is false so the caption
 * can say so.
 */

import type { BandQuintileRow, QuintileRow } from "./types";
import { bandSpan, byKey } from "./band";

export interface QuintileBar extends QuintileRow {
  /** Value drawn as the bar. */
  bar: number | null;
  /** Value drawn as the household marker (null: no marker). */
  household: number | null;
  /** [below, above] whisker of the bar's ±10 pt band, or null. */
  err: [number, number] | null;
  bandLo: number | null;
  bandHi: number | null;
}

export interface QuintileBars {
  rows: QuintileBar[];
  /** true when the bars are group totals; false on the median fallback. */
  isTotal: boolean;
  /** true when at least one row has a household marker. */
  hasHousehold: boolean;
}

export function quintileBars(
  quintiles: QuintileRow[],
  low?: BandQuintileRow[] | null,
  high?: BandQuintileRow[] | null,
): QuintileBars {
  const isTotal = quintiles.some((r) => r.total_change_pct != null);
  const pick = (r: QuintileRow | BandQuintileRow | undefined) =>
    r == null
      ? undefined
      : isTotal
        ? r.total_change_pct
        : r.median_change_pct_residential;
  const lo = byKey(low, "quintile");
  const hi = byKey(high, "quintile");
  const rows = [...quintiles]
    .sort((a, b) => a.quintile - b.quintile)
    .map((r) => {
      const bar = pick(r) ?? null;
      const span = bandSpan(bar, pick(lo.get(r.quintile)), pick(hi.get(r.quintile)));
      return {
        ...r,
        bar,
        household: r.household_median_change_pct ?? null,
        err: span?.err ?? null,
        bandLo: span?.lo ?? null,
        bandHi: span?.hi ?? null,
      };
    });
  return { rows, isTotal, hasHousehold: rows.some((r) => r.household != null) };
}
