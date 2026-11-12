import { describe, expect, it } from "vitest";
import { stepTable } from "./steps";
import type { CategoryRow, QuintileRow } from "./types";

const cat = (category: string, extra: Partial<CategoryRow> = {}): CategoryRow => ({
  category, label_fr: category, parcels: 100, share_of_parcels_pct: 10,
  median_change_pct: 1, median_change_eur: 1, count_paying_more: 1,
  share_paying_more_pct: 1, ...extra,
});
const q = (quintile: number, extra: Partial<QuintileRow> = {}): QuintileRow => ({
  quintile, median_income_eur: 20000, median_change_pct: 1,
  median_change_pct_residential: 1, parcels: 100, ...extra,
});
const s = (a: number, b: number) => ({
  step_revaluation_pct: a, step_land_pct: b, total_change_pct: Math.round((a + b) * 10) / 10,
});

describe("stepTable", () => {
  it("keeps rows with both steps, quintiles in order", () => {
    const t = stepTable([cat("Maisons", s(4, 7.5)), cat("Autres")], [q(5, s(6, 1.8)), q(1, s(-9, -3.4))]);
    expect(t.categories.map((r) => r.key)).toEqual(["Maisons"]);
    expect(t.categories[0]).toMatchObject({ revaluation: 4, land: 7.5, total: 11.5 });
    expect(t.quintiles.map((r) => r.key)).toEqual(["q1", "q5"]);
    expect(t.quintiles[0].label).toBe("20 % les plus modestes");
  });

  it("leaves out older payloads and partial rows", () => {
    expect(stepTable([cat("Maisons")], [q(1)])).toEqual({ categories: [], quintiles: [] });
    expect(stepTable([cat("X", { ...s(1, 2), step_land_pct: null })], null).categories).toEqual([]);
    expect(stepTable([cat("X", { ...s(1, 2), total_change_pct: Number.NaN })], null).categories).toEqual([]);
  });
});
