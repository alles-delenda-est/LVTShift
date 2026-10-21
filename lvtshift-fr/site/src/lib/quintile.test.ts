import { describe, expect, it } from "vitest";
import { quintileBars } from "./quintile";
import type { QuintileRow } from "./types";

const row = (q: number, extra: Partial<QuintileRow> = {}): QuintileRow => ({
  quintile: q, median_income_eur: 20000 + q, median_change_pct: 5,
  median_change_pct_residential: 6, parcels: 100, ...extra,
});

describe("quintileBars", () => {
  it("draws the group total as the bar and the household median as the marker", () => {
    const out = quintileBars(
      [row(2, { total_change_pct: 1 }),
       row(1, { total_change_pct: -8.4, household_median_change_pct: -3 })],
      [{ quintile: 1, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: -10 }],
      [{ quintile: 1, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: -7 }],
    );
    expect(out.isTotal).toBe(true);
    expect(out.hasHousehold).toBe(true);
    expect(out.rows.map((r) => r.quintile)).toEqual([1, 2]);
    expect(out.rows[0].bar).toBe(-8.4);
    expect(out.rows[0].household).toBe(-3);
    expect(out.rows[0].bandLo).toBe(-10);
    expect(out.rows[0].bandHi).toBe(-7);
    expect(out.rows[1].household).toBeNull();
    expect(out.rows[1].err).toBeNull();          // no band legs for Q2
  });

  it("falls back to the residential parcel median on older payloads", () => {
    const out = quintileBars([row(1)]);
    expect(out.isTotal).toBe(false);
    expect(out.hasHousehold).toBe(false);
    expect(out.rows[0].bar).toBe(6);
  });
});
