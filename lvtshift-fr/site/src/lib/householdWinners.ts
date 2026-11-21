import type { CategoryRow } from "@/lib/types";

export interface HouseholdWinnersSummary {
  totalDwellings: number;
  /** Share of private dwellings in parcels paying less or the same (%). */
  pctPayingLess: number;
  /** Share of private dwellings in parcels paying strictly more (%). */
  pctPayingMore: number;
}

const PRIVATE_RESIDENTIAL_CATEGORIES = new Set([
  "Single Family Residential",
  "Condominium",
  "Large Multi-Family (5+ units)",
]);

/**
 * Share of private residential dwellings whose modelled tax falls (or stays
 * unchanged), weighted by dwelling counts across houses, small buildings
 * (2–4 units) and collective housing (5+ units). Social housing stays out:
 * its tax falls on the landlord, not on tenants.
 *
 * Returns null if no private dwellings are present or if any present private
 * category had its dwelling figures withheld (disclosure control / older run),
 * so the site never publishes a partial figure pretending to be the whole.
 */
export function computePrivateHouseholdWinners(
  byCategory: CategoryRow[],
): HouseholdWinnersSummary | null {
  let totalDwellings = 0;
  let dwellingsPayingMore = 0;

  for (const row of byCategory) {
    if (!PRIVATE_RESIDENTIAL_CATEGORIES.has(row.category)) continue;
    const count = row.dwellings ?? 0;
    const pctMore = row.share_dwellings_paying_more_pct;
    if (count > 0 && typeof pctMore === "number" && Number.isFinite(pctMore)) {
      totalDwellings += count;
      dwellingsPayingMore += count * (pctMore / 100);
    } else if (row.parcels > 0) {
      return null;
    }
  }

  if (totalDwellings <= 0) return null;

  const rawMore = (dwellingsPayingMore / totalDwellings) * 100;
  const pctPayingMore = Math.round(rawMore * 10) / 10;
  const pctPayingLess = Math.round((100 - pctPayingMore) * 10) / 10;
  return { totalDwellings, pctPayingLess, pctPayingMore };
}
