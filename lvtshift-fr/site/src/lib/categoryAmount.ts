import type { CategoryRow } from "@/lib/types";

/**
 * The euro amount to show for a property category, and what it is per.
 *
 * The parcel median in euros compares a whole block of flats with a single
 * house: in Lyon, +800 € per block against +267 € per house, read as "flats
 * pay three times more" when each flat pays a few tens of euros. Residential
 * categories therefore show the typical household's change (per dwelling)
 * when the payload carries it; a building category from an older payload says
 * "par immeuble"; every other category is per parcel.
 */
export type AmountBasis = "dwelling" | "building" | "parcel";

const BUILDINGS = new Set(["Large Multi-Family (5+ units)", "Condominium"]);

export const BASIS_LABEL: Record<AmountBasis, string> = {
  dwelling: "par logement",
  building: "par immeuble",
  parcel: "par parcelle",
};

export function categoryAmount(row: CategoryRow): { basis: AmountBasis; eur: number | null } {
  if (row.median_change_eur_per_dwelling != null) {
    return { basis: "dwelling", eur: row.median_change_eur_per_dwelling };
  }
  return {
    basis: BUILDINGS.has(row.category) ? "building" : "parcel",
    eur: row.median_change_eur,
  };
}
