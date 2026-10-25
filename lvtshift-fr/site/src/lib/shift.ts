/**
 * Share of the levy that changes payer: the sum of the increases, as % of
 * the levy.
 *
 * The site used to show the "gross" figure (increases + decreases), which
 * counts every euro twice: under revenue neutrality the increases and the
 * decreases are equal, so gross is exactly twice net (Rungis showed 113,9 %).
 * Older member rows carry only the gross figure; each member commune is
 * revenue-neutral on its own levy, so halving it gives the net exactly.
 */
export function shiftedPct(
  net: number | null | undefined,
  gross: number | null | undefined,
): number | null {
  if (net != null) return net;
  if (gross != null) return Math.round((gross / 2) * 10) / 10;
  return null;
}
