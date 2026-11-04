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
import { pct } from "./format";

export interface SocialNote {
  /** "category": the category is shown; "folded": counted in « Autre bâtiment ». */
  kind: "category" | "folded";
  /** The commune's share of social dwellings exempt / abated today, or null. */
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
      `Ici, ${pct(s.exempt_dwellings_pct)} des ${n} logements sociaux sont ` +
      `exonérés de taxe foncière en ${s.tax_year ?? 2025}` +
      (s.qpv_abated_dwellings_pct != null && s.qpv_abated_dwellings_pct > 0
        ? ` et ${pct(s.qpv_abated_dwellings_pct)} bénéficient de l'abattement de 30 % ` +
          `en quartier prioritaire.`
        : ".");
  }
  return { kind: "category", counts };
}
