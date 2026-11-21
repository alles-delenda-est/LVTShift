/**
 * The reading notes under the category chart, built from the commune's own
 * published rows so that no figure is hard-coded and no note appears for a
 * category the commune does not publish (withheld under 11 parcels, or absent).
 */

import type { PublishedCategoryRow } from "./types";
import { pct, signedChange } from "./format";

export interface CategoryNotes {
  /** Collective housing (5+ dwellings): label to show, or null if absent. */
  collective: { label: string } | null;
  /** Social landlords: label and the sentence on the category's total change
   *  (null when the total is withheld). */
  social: { label: string; totalSentence: string | null } | null;
  /** Industrial premises: label and the commune's parcel median (null if undefined). */
  industrial: { label: string; median: string | null } | null;
}

export function socialTotalSentence(totalPct: number | null | undefined): string | null {
  if (totalPct == null || !Number.isFinite(totalPct)) return null;
  // decide on the figure as printed (one decimal), so +0.04 reads « stable »
  const shown = Math.round(totalPct * 10) / 10;
  if (shown === 0) {
    return "Dans ce territoire, l'impôt total des bailleurs sociaux reste stable.";
  }
  const sens = shown > 0 ? "hausse" : "baisse";
  return `Dans ce territoire, l'impôt total des bailleurs sociaux est en ${sens} de ${pct(Math.abs(shown))}.`;
}

export function categoryNotes(rows: PublishedCategoryRow[]): CategoryNotes {
  const find = (key: string) => rows.find((r) => r.category === key);
  const collective = find("Large Multi-Family (5+ units)");
  const social = find("Social Housing");
  const industrial = find("Industrial");
  return {
    collective: collective ? { label: collective.label_fr } : null,
    social: social
      ? { label: social.label_fr, totalSentence: socialTotalSentence(social.total_change_pct) }
      : null,
    industrial: industrial
      ? {
          label: industrial.label_fr,
          median:
            industrial.median_change_pct == null ? null : signedChange(industrial.median_change_pct),
        }
      : null,
  };
}

/** true when at least one note applies. */
export function hasCategoryNotes(n: CategoryNotes): boolean {
  return n.collective !== null || n.social !== null || n.industrial !== null;
}
