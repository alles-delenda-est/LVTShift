import type { BandCategoryRow, BandQuintileRow, Commune, SensitivityLeg } from "@/lib/types";
import { shiftedPct } from "@/lib/shift";

/**
 * Counts behind the home page's "who pays" card, computed from the published
 * payloads so the prose cannot drift from the model (the card used to promise
 * owner-occupiers "une baisse ou une quasi-neutralité", which the model
 * contradicts for houses almost everywhere).
 *
 * Counts come under the central case and, in `alt`, under the published local
 * variant of today's tax (baseline_sensitivity.low), which gives business
 * premises a larger share of today's tax in most cities, so the reform shifts
 * more onto homes. Territories use the within-commune income ranking,
 * which is where each levy applies.
 */
export interface LegCounts {
  housesPayMore: number;
  flatsPayLess: number;
  poorestAnalysable: number;
  poorestPayLess: number;
  /** Territories where the poorest fifth's total change is below the richest fifth's. */
  poorestBelowRichest: number;
}

export interface ImpactSummary extends LegCounts {
  territories: number;
  houseMedianMin: number | null;
  houseMedianMax: number | null;
  /** Share of the levy that changes payer, % (lowest and highest territory). */
  shiftMin: number | null;
  shiftMax: number | null;
  /** Same counts under the local variant; null unless every territory
   *  publishes one with the same quintile coverage, so both sets of counts
   *  share a denominator. */
  alt: LegCounts | null;
  /** Territories where the poorest fifth does better than the richest under
   *  both hypotheses (equals poorestBelowRichest when alt is null). */
  poorestBelowRichestBoth: number;
}

interface Inputs {
  house: number | null;
  flat: number | null;
  q1: number | null;
  q5: number | null;
}

function median(rows: BandCategoryRow[] | null | undefined, category: string): number | null {
  return rows?.find((r) => r.category === category)?.median_change_pct ?? null;
}

function total(rows: BandQuintileRow[] | null | undefined, quintile: number): number | null {
  return rows?.find((r) => r.quintile === quintile)?.total_change_pct ?? null;
}

function centralInputs(c: Commune): Inputs {
  const rows = c.kind === "territory" ? c.by_income_quintile_within : c.by_income_quintile;
  return {
    house: median(c.by_category, "Single Family Residential"),
    flat: median(c.by_category, "Condominium"),
    q1: total(rows, 1),
    q5: total(rows, 5),
  };
}

function legInputs(c: Commune, leg: SensitivityLeg): Inputs {
  const rows = c.kind === "territory" ? leg.by_income_quintile_within : leg.by_income_quintile;
  return {
    house: median(leg.by_category, "Single Family Residential"),
    flat: median(leg.by_category, "Condominium"),
    q1: total(rows, 1),
    q5: total(rows, 5),
  };
}

function count(inputs: Inputs[]): LegCounts {
  const analysable = inputs.filter((i) => i.q1 != null && i.q5 != null);
  return {
    housesPayMore: inputs.filter((i) => i.house != null && i.house > 0).length,
    flatsPayLess: inputs.filter((i) => i.flat != null && i.flat < 0).length,
    poorestAnalysable: analysable.length,
    poorestPayLess: analysable.filter((i) => i.q1! < 0).length,
    poorestBelowRichest: analysable.filter((i) => i.q1! < i.q5!).length,
  };
}

const below = (i: Inputs) => i.q1 != null && i.q5 != null && i.q1 < i.q5;

export function impactSummary(communes: Commune[]): ImpactSummary {
  const shifts: number[] = [];
  for (const c of communes) {
    const s = shiftedPct(c.headline.net_pct_of_levy, c.headline.gross_pct_of_levy);
    if (s != null) shifts.push(s);
  }
  const central = communes.map(centralInputs);
  const houses = central.map((i) => i.house).filter((v): v is number => v != null);

  // A territory without the variant, or whose variant lacks quintiles the
  // central case has, would give the two counts different denominators.
  const legs = communes.map((c) => c.baseline_sensitivity?.low ?? null);
  const alt = legs.every((l) => l != null)
    ? communes.map((c, k) => legInputs(c, legs[k]!))
    : null;
  const comparable =
    alt != null &&
    alt.every(
      (a, k) => (a.q1 == null) === (central[k].q1 == null) && (a.q5 == null) === (central[k].q5 == null),
    );

  return {
    territories: communes.length,
    ...count(central),
    houseMedianMin: houses.length ? Math.min(...houses) : null,
    houseMedianMax: houses.length ? Math.max(...houses) : null,
    shiftMin: shifts.length ? Math.min(...shifts) : null,
    shiftMax: shifts.length ? Math.max(...shifts) : null,
    alt: comparable ? count(alt!) : null,
    poorestBelowRichestBoth: comparable
      ? central.filter((i, k) => below(i) && below(alt![k])).length
      : central.filter(below).length,
  };
}

/** "9 sur 13" when both hypotheses agree, "6 à 9 sur 13" otherwise (no-break spaces). */
export function countRange(central: number, alt: number | undefined, of: number): string {
  if (alt == null || alt === central) return `${central} sur ${of}`;
  return `${Math.min(central, alt)} à ${Math.max(central, alt)} sur ${of}`;
}
