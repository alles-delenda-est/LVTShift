import { describe, expect, it } from "vitest";
import { bandSpan, byKey, categoryBandValue, quintileBandValue } from "./band";

describe("bandSpan", () => {
  it("spans the central value and both legs", () => {
    expect(bandSpan(2, -1, 5)).toEqual({ err: [3, 3], lo: -1, hi: 5 });
  });
  it("keeps the central value inside the span when legs fall on one side", () => {
    expect(bandSpan(2, 3, 4)).toEqual({ err: [0, 2], lo: 2, hi: 4 });
  });
  it("returns null when any value is missing", () => {
    expect(bandSpan(null, 1, 2)).toBeNull();
    expect(bandSpan(1, undefined, 2)).toBeNull();
    expect(bandSpan(1, 2, Number.NaN)).toBeNull();
  });
});

describe("byKey", () => {
  it("indexes rows and tolerates a missing list", () => {
    expect(byKey([{ q: 1, v: 2 }], "q").get(1)).toEqual({ q: 1, v: 2 });
    expect(byKey(null as { q: number }[] | null, "q").size).toBe(0);
  });
});

describe("categoryBandValue", () => {
  it("extracts the exact metric requested without cross-metric fallback", () => {
    const row = { median_change_pct: -14.2, household_median_change_pct: -18.6 };
    expect(categoryBandValue(row, "household")).toBe(-18.6);
    expect(categoryBandValue(row, "median")).toBe(-14.2);
  });
  it("returns null/undefined when household_median_change_pct is absent in household metric", () => {
    expect(
      categoryBandValue({ median_change_pct: 68.2, household_median_change_pct: null }, "household"),
    ).toBeNull();
    expect(categoryBandValue({ median_change_pct: 68.2 }, "household")).toBeUndefined();
    expect(categoryBandValue({ median_change_pct: 68.2 }, "median")).toBe(68.2);
    expect(categoryBandValue(undefined, "household")).toBeUndefined();
  });
});

describe("quintileBandValue", () => {
  it("extracts the exact quintile metric without cross-metric fallback", () => {
    const row = {
      total_change_pct: -24.9,
      household_median_change_pct: -37.9,
      median_change_pct_residential: -25.9,
    };
    expect(quintileBandValue(row, "household")).toBe(-37.9);
    expect(quintileBandValue(row, "total")).toBe(-24.9);
    expect(quintileBandValue(row, "residential")).toBe(-25.9);
    expect(
      quintileBandValue({ median_change_pct_residential: -10.0 }, "household"),
    ).toBeUndefined();
    expect(
      quintileBandValue({ median_change_pct_residential: -10.0 }, "total"),
    ).toBeUndefined();
    expect(
      quintileBandValue({ median_change_pct_residential: -10.0 }, "residential"),
    ).toBe(-10.0);
  });
});
