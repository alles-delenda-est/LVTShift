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
const s = (a: number, b: number, c: number) => ({
  step_revaluation_pct: a, step_land_pct: b, step_exemptions_pct: c,
  total_change_pct: Math.round((a + b + c) * 10) / 10,
});

describe("stepTable", () => {
  it("keeps rows with all three steps, quintiles in order", () => {
    const t = stepTable(
      [cat("Maisons", s(4, 8, -0.5)), cat("Autres")],
      [q(5, s(6, 2, -0.2)), q(1, s(-9, -3, -0.4))],
    );
    expect(t.categories.map((r) => r.key)).toEqual(["Maisons"]);
    expect(t.categories[0]).toMatchObject({ revaluation: 4, land: 8, exemptions: -0.5, total: 11.5 });
    expect(t.quintiles.map((r) => r.key)).toEqual(["q1", "q5"]);
    expect(t.quintiles[0].sublabel).toBe("Revenus les plus modestes");
    expect(t.showExemptions).toBe(true);
  });

  it("hides the exemptions column where no group has social housing, and old payloads", () => {
    const t = stepTable([cat("Maisons", s(4, 8, 0))], null);
    expect(t.showExemptions).toBe(false);
    expect(t.quintiles).toEqual([]);
    expect(stepTable([cat("Maisons")], [q(1)])).toEqual({
      categories: [], quintiles: [], showExemptions: false,
    });
    // a partial row (one step missing) is never shown
    expect(stepTable([cat("X", { ...s(1, 2, 0), step_land_pct: null })], null).categories).toEqual([]);
  });
});
