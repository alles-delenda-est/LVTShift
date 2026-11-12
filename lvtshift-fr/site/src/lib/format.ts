// French number/currency typography for every stat and chart label.
// Decimals use a comma; thousands are grouped with an espace insécable (U+00A0).
// ICU (fr-FR) emits a NARROW no-break space (U+202F) as the group separator and
// before "%"; we normalise that (and any plain space) to U+00A0 so output is
// stable across Node/ICU versions and matches the assertions in format.test.ts.
const NBSP = " ";

function frNum(n: number, digits = 0): string {
  return n
    .toLocaleString("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits })
    .replace(/[\s  ]/g, NBSP);
}

export function euros(n: number): string {
  const a = Math.abs(n);
  if (a >= 1e9) return `${frNum(n / 1e9, 1)}${NBSP}Md€`;
  if (a >= 1e6) return `${frNum(n / 1e6, 1)}${NBSP}M€`;
  if (a >= 1e4) return `${frNum(n / 1e3, 0)}${NBSP}k€`;
  return `${frNum(n, 0)}${NBSP}€`;
}

export function eurosExact(n: number): string {
  return `${frNum(n, 0)}${NBSP}€`;
}

export function pct(n: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "n. d.";
  return `${frNum(n, 1)}${NBSP}%`;
}

export function signedPct(n: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "n. d.";
  const sign = n > 0 ? "+" : n < 0 ? "−" : ""; // U+2212 true minus
  return `${sign}${frNum(Math.abs(n), 1)}${NBSP}%`;
}

/** From this rise (%), a change reads better as a multiple than as a percentage. */
export const MULTIPLE_FROM_PCT = 200;

/** A signed % change, or a multiple once the rise reaches MULTIPLE_FROM_PCT
 *  ("+85,0 %", "×3,5", "×47"): vacant land's tax today is tiny, so its rise in
 *  % runs to thousands and reads like an error. */
export function signedChange(n: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "n. d.";
  if (n < MULTIPLE_FROM_PCT) return signedPct(n);
  const m = n / 100 + 1;
  return `×${frNum(m, m < 10 ? 1 : 0)}`;
}

/** Axis ticks: round values without a trailing ",0" ("+20 %", "−40 %"). */
export function signedPctAxis(n: number): string {
  if (!Number.isInteger(n)) return signedPct(n);
  const sign = n > 0 ? "+" : n < 0 ? "−" : "";
  return `${sign}${frNum(Math.abs(n), 0)}${NBSP}%`;
}
