/**
 * Rows for the "today's tax" uncertainty table: the same figures under the
 * central and the lower-bound share of professional premises in today's tax.
 */
import type { BaselineSensitivity, BandQuintileRow } from "@/lib/types";

export type RangeFormat = "pct" | "signed";

export interface RangeRow {
  label: string;
  sublabel?: string;
  central: number | null;
  low: number | null;
  format: RangeFormat;
}

const QUINTILE_LABELS: Record<number, string> = {
  1: "20 % les plus modestes",
  2: "2ᵉ quintile",
  3: "3ᵉ quintile",
  4: "4ᵉ quintile",
  5: "20 % les plus aisés",
};

function totals(rows: BandQuintileRow[] | null | undefined): Map<number, number | null> {
  return new Map((rows ?? []).map((r) => [r.quintile, r.total_change_pct ?? null]));
}

/** Headline rows, then one row per income quintile (group total change).
 *  Territories use the within-commune ranking, where each levy applies. */
export function baselineRangeRows(
  b: BaselineSensitivity,
  withinCommune = false,
): RangeRow[] {
  const rows: RangeRow[] = [
    {
      label: "Transfert brut",
      sublabel: "% du prélèvement total",
      central: b.central.gross_pct_of_levy,
      low: b.low.gross_pct_of_levy,
      format: "pct",
    },
    {
      label: "Proportion qui paie davantage",
      sublabel: "parcelles",
      central: b.central.share_paying_more_pct,
      low: b.low.share_paying_more_pct,
      format: "pct",
    },
    {
      label: "Variation médiane résidentielle",
      sublabel: "logements",
      central: b.central.median_change_pct_residential,
      low: b.low.median_change_pct_residential,
      format: "signed",
    },
  ];
  const key = withinCommune ? "by_income_quintile_within" : "by_income_quintile";
  const c = totals(b.central[key]);
  const l = totals(b.low[key]);
  for (const q of [1, 2, 3, 4, 5]) {
    if (!c.has(q) && !l.has(q)) continue;
    rows.push({
      label: QUINTILE_LABELS[q],
      sublabel: "variation totale du groupe",
      central: c.get(q) ?? null,
      low: l.get(q) ?? null,
      format: "signed",
    });
  }
  return rows;
}
