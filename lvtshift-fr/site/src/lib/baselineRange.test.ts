import { describe, it, expect } from "vitest";
import { baselineRangeRows } from "@/lib/baselineRange";
import type { BaselineSensitivity, SensitivityLeg } from "@/lib/types";

function leg(over: Partial<SensitivityLeg>): SensitivityLeg {
  return {
    land_share_pct: 60, gross_pct_of_levy: 20, net_pct_of_levy: 10,
    median_change_pct_residential: 1, share_paying_more_pct: 50, ...over,
  };
}

const b: BaselineSensitivity = {
  pro_scale_central: 2.5,
  pro_scale_low: 1,
  central: leg({
    by_income_quintile: [
      { quintile: 1, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: -17.4 },
      { quintile: 5, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: 18.9 },
    ],
  }),
  low: leg({
    gross_pct_of_levy: 30, share_paying_more_pct: 42,
    by_income_quintile: [
      { quintile: 1, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: -27.6 },
      { quintile: 5, median_change_pct: 0, median_change_pct_residential: 0, total_change_pct: 3.9 },
    ],
  }),
};

describe("baselineRangeRows", () => {
  it("pairs central and lower-bound figures, headline rows first", () => {
    const rows = baselineRangeRows(b);
    expect(rows[0]).toMatchObject({ label: "Transfert brut", central: 20, low: 30 });
    expect(rows[1]).toMatchObject({ central: 50, low: 42 });
    const q1 = rows.find((r) => r.label === "20 % les plus modestes");
    expect(q1).toMatchObject({ central: -17.4, low: -27.6, format: "signed" });
  });
  it("skips quintiles absent from both legs", () => {
    expect(baselineRangeRows(b).filter((r) => r.label.includes("quintile"))).toHaveLength(0);
  });
  it("reads the within-commune ranking for territories, tolerating its absence", () => {
    const rows = baselineRangeRows(b, true);
    expect(rows).toHaveLength(3); // headline rows only
  });
  it("keeps a null when one leg lacks a figure", () => {
    const partial = { ...b, low: leg({ by_income_quintile: null }) };
    const q1 = baselineRangeRows(partial).find((r) => r.label === "20 % les plus modestes");
    expect(q1).toMatchObject({ central: -17.4, low: null });
  });
});
