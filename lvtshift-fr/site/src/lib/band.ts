/**
 * Sensitivity-band helpers: turn the low / high legs of headline_sensitivity
 * into a [below, above] whisker around a central value, for Recharts ErrorBar.
 */

export interface BandSpan {
  /** distance below and above the central value (both ≥ 0) */
  err: [number, number];
  lo: number;
  hi: number;
}

/** Range spanned by the central value and the two band legs, or null when any
 *  of them is missing (no whisker is drawn then). */
export function bandSpan(
  central: number | null | undefined,
  a: number | null | undefined,
  b: number | null | undefined,
): BandSpan | null {
  if (central == null || a == null || b == null) return null;
  if (![central, a, b].every(Number.isFinite)) return null;
  const lo = Math.min(central, a, b);
  const hi = Math.max(central, a, b);
  return { err: [central - lo, hi - central], lo, hi };
}

/** Index rows by a key, ignoring a null/undefined list. */
export function byKey<T, K extends keyof T>(
  rows: T[] | null | undefined,
  key: K,
): Map<T[K], T> {
  return new Map((rows ?? []).map((r) => [r[key], r]));
}
