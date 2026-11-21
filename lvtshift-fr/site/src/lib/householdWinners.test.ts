import { describe, expect, it } from "vitest";
import { computePrivateHouseholdWinners } from "./householdWinners";
import type { CategoryRow } from "./types";

function makeRow(
  category: string,
  dwellings: number | null,
  shareMore: number | null,
  parcels = 100,
): CategoryRow {
  return {
    category,
    label_fr: category,
    parcels,
    share_of_parcels_pct: 10,
    median_change_pct: 0,
    median_change_eur: 0,
    count_paying_more: 50,
    share_paying_more_pct: 50,
    dwellings,
    share_dwellings_paying_more_pct: shareMore,
  };
}

describe("computePrivateHouseholdWinners", () => {
  it("computes Paris private household winner share across residential categories", () => {
    const rows: CategoryRow[] = [
      makeRow("Single Family Residential", 4382, 92.1),
      makeRow("Condominium", 11360, 71.7),
      makeRow("Large Multi-Family (5+ units)", 1010883, 27.8),
      // Non-private categories must be ignored
      makeRow("Social Housing", null, null, 4656),
      makeRow("Commercial", null, null, 7507),
    ];
    const res = computePrivateHouseholdWinners(rows);
    expect(res).toEqual({
      totalDwellings: 1026625,
      pctPayingLess: 71.4,
      pctPayingMore: 28.6,
    });
  });

  it("returns null if a present private residential category has withheld dwelling figures", () => {
    const rows: CategoryRow[] = [
      makeRow("Single Family Residential", 500, 80.0),
      makeRow("Large Multi-Family (5+ units)", null, null, 15),
    ];
    expect(computePrivateHouseholdWinners(rows)).toBeNull();
  });

  it("returns null when no private residential categories are present", () => {
    expect(computePrivateHouseholdWinners([makeRow("Commercial", null, null)])).toBeNull();
  });

  it("keeps pctPayingLess + pctPayingMore equal to 100 on .x5 rounding ties", () => {
    const rows: CategoryRow[] = [
      makeRow("Single Family Residential", 1000, 28.5),
      makeRow("Condominium", 1000, 28.6),
    ];
    const res = computePrivateHouseholdWinners(rows);
    expect(res).toEqual({
      totalDwellings: 2000,
      pctPayingLess: 71.4,
      pctPayingMore: 28.6,
    });
  });
});
