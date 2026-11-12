/**
 * Villeurbanne's note under the income chart: why its poorest fifth pays
 * more in total while its typical household pays less. Every figure comes
 * from the published payload, so a rerun cannot leave a stale number; the
 * note disappears if the poorest fifth no longer fares worse than the
 * richest. The breakdown of the fifth by housing type that motivates the
 * text is not published (no disclosure check covers that cross-table), so
 * the text uses it only in words.
 */

import type { Commune } from "./types";

export interface PoorestNote {
  q1Total: number;
  q5Total: number;
  q1Household: number | null;
  q1Income: number;
  q5Income: number;
  housesTotal: number | null;
}

/** Communes whose note has been written and checked against the data. */
const NOTED = new Set(["villeurbanne"]);

export function poorestNote(
  c: Pick<Commune, "commune_key" | "by_income_quintile" | "by_category">,
): PoorestNote | null {
  if (!NOTED.has(c.commune_key)) return null;
  const q = new Map((c.by_income_quintile ?? []).map((r) => [r.quintile, r]));
  const q1 = q.get(1);
  const q5 = q.get(5);
  const t1 = q1?.total_change_pct;
  const t5 = q5?.total_change_pct;
  if (q1 == null || q5 == null || t1 == null || t5 == null) return null;
  // the note explains a poorest fifth that pays more and fares worse
  if (!(t1 > 0 && t1 > t5)) return null;
  const houses = c.by_category.find((r) => r.category === "Single Family Residential");
  return {
    q1Total: t1,
    q5Total: t5,
    q1Household: q1.household_median_change_pct ?? null,
    q1Income: q1.median_income_eur,
    q5Income: q5.median_income_eur,
    housesTotal: houses?.total_change_pct ?? null,
  };
}
