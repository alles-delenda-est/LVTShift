import type { Commune, QuintileRow } from "@/lib/types";
import { shiftedPct } from "@/lib/shift";

/**
 * Counts behind the home page's "who pays" card, computed from the published
 * payloads so the prose cannot drift from the model (the card used to promise
 * owner-occupiers "une baisse ou une quasi-neutralité", which the model
 * contradicts for houses almost everywhere).
 *
 * Central case only. Territories use the within-commune income ranking, which
 * is where each levy applies.
 */
export interface ImpactSummary {
  territories: number;
  housesPayMore: number;
  houseMedianMin: number | null;
  houseMedianMax: number | null;
  flatsPayLess: number;
  poorestAnalysable: number;
  poorestPayLess: number;
  /** Share of the levy that changes payer, % (lowest and highest territory). */
  shiftMin: number | null;
  shiftMax: number | null;
}

function poorestTotal(c: Commune): number | null {
  const rows: QuintileRow[] | null | undefined =
    c.kind === "territory" ? c.by_income_quintile_within : c.by_income_quintile;
  const q1 = rows?.find((r) => r.quintile === 1);
  return q1?.total_change_pct ?? null;
}

export function impactSummary(communes: Commune[]): ImpactSummary {
  const houses: number[] = [];
  let flatsPayLess = 0;
  let poorestAnalysable = 0;
  let poorestPayLess = 0;
  const shifts: number[] = [];
  for (const c of communes) {
    const s = shiftedPct(c.headline.net_pct_of_levy, c.headline.gross_pct_of_levy);
    if (s != null) shifts.push(s);
    const house = c.by_category.find((r) => r.category === "Single Family Residential");
    const flat = c.by_category.find((r) => r.category === "Condominium");
    if (house?.median_change_pct != null) houses.push(house.median_change_pct);
    if (flat?.median_change_pct != null && flat.median_change_pct < 0) flatsPayLess++;
    const q1 = poorestTotal(c);
    if (q1 != null) {
      poorestAnalysable++;
      if (q1 < 0) poorestPayLess++;
    }
  }
  return {
    territories: communes.length,
    housesPayMore: houses.filter((v) => v > 0).length,
    houseMedianMin: houses.length ? Math.min(...houses) : null,
    houseMedianMax: houses.length ? Math.max(...houses) : null,
    flatsPayLess,
    poorestAnalysable,
    poorestPayLess,
    shiftMin: shifts.length ? Math.min(...shifts) : null,
    shiftMax: shifts.length ? Math.max(...shifts) : null,
  };
}
