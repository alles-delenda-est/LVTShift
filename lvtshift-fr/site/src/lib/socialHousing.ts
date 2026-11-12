/**
 * The note on social housing under the category chart.
 *
 * Runs that model social housing (provenance.social_housing.modelled) give
 * today's exemptions their effect and put parcels held mainly by social
 * landlords in a "Social Housing" category, outside every household figure.
 * Where showing it apart would describe a landlord or a property (too few
 * landlords, one dominant, too few parcels), the exporter folds it into
 * "Other" and leaves the commune's counts out: the note then says so without
 * figures. A commune with no such parcel gets no note.
 */

import type { Commune } from "./types";
import { pct, signedPct } from "./format";

export interface SocialNote {
  /** "category": the category is shown; "folded": counted in « Autre bâtiment ». */
  kind: "category" | "folded";
  /** The commune's share of social dwellings exempt / abated today, as a
   *  clause for a parenthesis ("ici, … sont exonérés en 2025"), or null. */
  counts: string | null;
}

export function socialNote(commune: Pick<Commune, "provenance">): SocialNote | null {
  const s = commune.provenance?.social_housing;
  if (!s?.modelled || (s.category !== "shown" && s.category !== "folded")) return null;
  if (s.category === "folded") return { kind: "folded", counts: null };
  let counts: string | null = null;
  if (s.rpls_dwellings != null && s.exempt_dwellings_pct != null) {
    const n = s.rpls_dwellings.toLocaleString("fr-FR").replace(/\s/g, " ");
    counts =
      `ici, ${pct(s.exempt_dwellings_pct)} des ${n} logements sociaux sont ` +
      `exonérés en ${s.tax_year ?? 2025}` +
      (s.qpv_abated_dwellings_pct != null && s.qpv_abated_dwellings_pct > 0
        ? ` et ${pct(s.qpv_abated_dwellings_pct)} bénéficient de l'abattement de 30 % ` +
          `en quartier prioritaire`
        : "");
  }
  return { kind: "category", counts };
}

export interface SocialSummary {
  /** Territories publishing the social landlords' total change. */
  published: number;
  /** Of those, territories where that total falls. */
  payLess: number;
  /** Lowest and highest total change, % (null when none is published). */
  min: number | null;
  max: number | null;
}

/** Social landlords' total change across the published territories (central
 *  case): exemptions ended, but dense estates gain from a tax on land. */
export function socialSummary(communes: Pick<Commune, "by_category">[]): SocialSummary {
  const totals = communes
    .map((c) => c.by_category.find((r) => r.category === "Social Housing")?.total_change_pct)
    .filter((v): v is number => v != null);
  return {
    published: totals.length,
    payLess: totals.filter((v) => v < 0).length,
    min: totals.length ? Math.min(...totals) : null,
    max: totals.length ? Math.max(...totals) : null,
  };
}

/** The sentence the protections page shows, or "" when no total is published. */
export function socialSummarySentence(s: SocialSummary): string {
  if (!s.published || s.min == null || s.max == null) return "";
  return (
    `Dans les ${s.published} territoires où le total de cette catégorie est publié, ` +
    `l'impôt des bailleurs sociaux, exonérations supprimées, varie de ` +
    `${signedPct(s.min)} à ${signedPct(s.max)} (cas central) : il baisse dans ` +
    `${s.payLess} d'entre eux et augmente dans ${s.published - s.payLess}.`
  );
}
