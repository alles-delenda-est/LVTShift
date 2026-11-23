import type { BandCategoryRow, CategoryRow } from "@/lib/types";

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

function summarize(
  pairs: { dwellings: number; shareMore: number }[],
): HouseholdWinnersSummary | null {
  let totalDwellings = 0;
  let dwellingsPayingMore = 0;
  for (const { dwellings, shareMore } of pairs) {
    totalDwellings += dwellings;
    dwellingsPayingMore += dwellings * (shareMore / 100);
  }
  if (totalDwellings <= 0) return null;

  const rawMore = (dwellingsPayingMore / totalDwellings) * 100;
  const pctPayingMore = Math.round(rawMore * 10) / 10;
  const pctPayingLess = Math.round((100 - pctPayingMore) * 10) / 10;
  return { totalDwellings, pctPayingLess, pctPayingMore };
}

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
  const pairs: { dwellings: number; shareMore: number }[] = [];

  for (const row of byCategory) {
    if (!PRIVATE_RESIDENTIAL_CATEGORIES.has(row.category)) continue;
    const count = row.dwellings ?? 0;
    const pctMore = row.share_dwellings_paying_more_pct;
    if (count > 0 && typeof pctMore === "number" && Number.isFinite(pctMore)) {
      pairs.push({ dwellings: count, shareMore: pctMore });
    } else if (row.parcels > 0) {
      return null;
    }
  }

  return summarize(pairs);
}

/**
 * Same private-dwelling share evaluated on a sensitivity / alternative-baseline
 * leg (`baseline_sensitivity.low.by_category` or `headline_sensitivity.{low,high}`),
 * using the central rows' dwelling counts (legs omit `dwellings` to keep payloads
 * compact). Returns null if the leg is missing or omits any present private category.
 */
export function computePrivateHouseholdWinnersForLeg(
  byCategory: CategoryRow[],
  legByCategory?: BandCategoryRow[] | null,
): HouseholdWinnersSummary | null {
  if (!legByCategory?.length) return null;
  const legByKey = new Map(legByCategory.map((r) => [r.category, r]));
  const pairs: { dwellings: number; shareMore: number }[] = [];

  for (const row of byCategory) {
    if (!PRIVATE_RESIDENTIAL_CATEGORIES.has(row.category)) continue;
    const count = row.dwellings ?? 0;
    const pctMore = legByKey.get(row.category)?.share_dwellings_paying_more_pct;
    if (count > 0 && typeof pctMore === "number" && Number.isFinite(pctMore)) {
      pairs.push({ dwellings: count, shareMore: pctMore });
    } else if (row.parcels > 0) {
      return null;
    }
  }

  return summarize(pairs);
}
