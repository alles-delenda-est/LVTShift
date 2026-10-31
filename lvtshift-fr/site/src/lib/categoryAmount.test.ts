import { describe, expect, it } from "vitest";
import { categoryAmount } from "@/lib/categoryAmount";
import type { CategoryRow } from "@/lib/types";

const row = (category: string, extra: Partial<CategoryRow> = {}): CategoryRow => ({
  category, label_fr: category, parcels: 100, share_of_parcels_pct: 10,
  median_change_pct: 9.6, median_change_eur: 800, count_paying_more: 70,
  share_paying_more_pct: 70, ...extra,
});

describe("category euro amount", () => {
  it("is per dwelling when the payload has it", () => {
    expect(categoryAmount(row("Large Multi-Family (5+ units)", { median_change_eur_per_dwelling: 42 })))
      .toEqual({ basis: "dwelling", eur: 42 });
  });

  it("names a building figure as one when per-dwelling is missing", () => {
    expect(categoryAmount(row("Large Multi-Family (5+ units)")).basis).toBe("building");
    expect(categoryAmount(row("Condominium", { median_change_eur_per_dwelling: null })).basis).toBe("building");
  });

  it("is per parcel for houses without counts and non-residential land", () => {
    expect(categoryAmount(row("Commercial"))).toEqual({ basis: "parcel", eur: 800 });
    expect(categoryAmount(row("Single Family Residential")).basis).toBe("parcel");
  });
});
