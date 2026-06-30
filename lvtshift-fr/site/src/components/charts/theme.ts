// Shared design tokens for all chart components.
// Values are byte-identical to the site palette declared in globals.css.

export const ROUGE     = "#b5281e";
export const MARINE    = "#1a2744";
export const CREME     = "#f6f4f0";
export const ENCRE     = "#1c1917";
export const GRIS      = "#6b6560";
export const LISERE    = "#d6d1ca";
export const GRIS_PALE = "#b0a89f";
export const GREEN     = "#2a6244"; // institutional green — "pays less" diverging bars

export const TICK = {
  fontFamily: "var(--font-body)",
  fontSize: 11,
  fill: GRIS,
} as const;
