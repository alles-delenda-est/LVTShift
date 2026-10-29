import { describe, expect, it } from "vitest";
import { publishedCategories, withheldCategories } from "@/lib/disclosure";
import type { CategoryRow } from "@/lib/types";

const row = (category: string, parcels: number, blank: boolean): CategoryRow => ({
  category, label_fr: category, parcels, share_of_parcels_pct: null,
  median_change_pct: blank ? null : 1, median_change_eur: blank ? null : 10,
  count_paying_more: blank ? null : 3, share_paying_more_pct: blank ? null : 50,
});

describe("small categories", () => {
  it("are left out of the charts and counted", () => {
    const rows = [row("A", 500, false), row("B", 4, true)];
    expect(publishedCategories(rows).map((r) => r.category)).toEqual(["A"]);
    expect(withheldCategories(rows)).toBe(1);
  });
});
