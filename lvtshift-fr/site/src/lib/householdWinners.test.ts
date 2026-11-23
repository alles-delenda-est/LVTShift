import { describe, expect, it } from "vitest";
import {
  computePrivateHouseholdWinners,
  computePrivateHouseholdWinnersForLeg,
} from "./householdWinners";
import type { BandCategoryRow, CategoryRow } from "./types";

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

describe("computePrivateHouseholdWinnersForLeg", () => {
  it("computes the alternative-baseline share using central dwelling counts", () => {
    const central: CategoryRow[] = [
      makeRow("Single Family Residential", 4382, 92.1),
      makeRow("Condominium", 11360, 71.7),
      makeRow("Large Multi-Family (5+ units)", 1010883, 27.8),
    ];
    const leg: BandCategoryRow[] = [
      { category: "Single Family Residential", median_change_pct: 120, median_change_eur: 1000, share_paying_more_pct: 95, share_dwellings_paying_more_pct: 95.0 },
      { category: "Condominium", median_change_pct: 40, median_change_eur: 400, share_paying_more_pct: 80, share_dwellings_paying_more_pct: 80.0 },
      { category: "Large Multi-Family (5+ units)", median_change_pct: -4, median_change_eur: -100, share_paying_more_pct: 45, share_dwellings_paying_more_pct: 40.0 },
    ];
    const res = computePrivateHouseholdWinnersForLeg(central, leg);
    expect(res).toEqual({
      totalDwellings: 1026625,
      pctPayingMore: 40.7,
      pctPayingLess: 59.3,
    });
  });

  it("returns null when the leg is absent or omits a present private category", () => {
    const central: CategoryRow[] = [
      makeRow("Single Family Residential", 500, 80.0),
      makeRow("Condominium", 500, 60.0),
    ];
    expect(computePrivateHouseholdWinnersForLeg(central, null)).toBeNull();
    expect(
      computePrivateHouseholdWinnersForLeg(central, [
        { category: "Single Family Residential", median_change_pct: 10, median_change_eur: 100, share_paying_more_pct: 80, share_dwellings_paying_more_pct: 80 },
      ]),
    ).toBeNull();
  });
});
