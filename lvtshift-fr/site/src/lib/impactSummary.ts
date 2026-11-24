import type { BandCategoryRow, BandQuintileRow, Commune, SensitivityLeg } from "@/lib/types";
import { shiftedPct } from "@/lib/shift";
import { signedPct } from "@/lib/format";

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
  /** Small buildings of 2–4 dwellings ("Condominium") paying less. */
  smallBuildingsPayLess: number;
  /** Large blocks of 5+ dwellings, where most flats are, paying less. */
  blocksPayLess: number;
  poorestAnalysable: number;
  poorestPayLess: number;
  /** Territories where the poorest fifth's total change is below the richest fifth's. */
  poorestBelowRichest: number;
}

/** Poorest and richest fifths' total change under one hypothesis, %. */
export interface FifthsPair {
  poorest: number;
  richest: number;
}

/** A territory where the poorest fifth does NOT do better than the richest
 *  under both hypotheses (so it is missing from `poorestBelowRichestBoth`). */
export interface PoorestException {
  name: string;
  central: FifthsPair;
  /** Null when no comparable local variant is published. */
  local: FifthsPair | null;
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
  /** The territories behind the gap between `poorestAnalysable` and
   *  `poorestBelowRichestBoth`. */
  poorestExceptions: PoorestException[];
}

interface Inputs {
  house: number | null;
  small: number | null;
  block: number | null;
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
    small: median(c.by_category, "Condominium"),
    block: median(c.by_category, "Large Multi-Family (5+ units)"),
    q1: total(rows, 1),
    q5: total(rows, 5),
  };
}

function legInputs(c: Commune, leg: SensitivityLeg): Inputs {
  const rows = c.kind === "territory" ? leg.by_income_quintile_within : leg.by_income_quintile;
  return {
    house: median(leg.by_category, "Single Family Residential"),
    small: median(leg.by_category, "Condominium"),
    block: median(leg.by_category, "Large Multi-Family (5+ units)"),
    q1: total(rows, 1),
    q5: total(rows, 5),
  };
}

function count(inputs: Inputs[]): LegCounts {
  const analysable = inputs.filter((i) => i.q1 != null && i.q5 != null);
  return {
    housesPayMore: inputs.filter((i) => i.house != null && i.house > 0).length,
    smallBuildingsPayLess: inputs.filter((i) => i.small != null && i.small < 0).length,
    blocksPayLess: inputs.filter((i) => i.block != null && i.block < 0).length,
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

  const pair = (i: Inputs): FifthsPair => ({ poorest: i.q1!, richest: i.q5! });
  const exceptions: PoorestException[] = [];
  central.forEach((i, k) => {
    if (i.q1 == null || i.q5 == null) return;
    const a = comparable ? alt![k] : null;
    if (below(i) && (a == null || below(a))) return;
    exceptions.push({ name: communes[k].name, central: pair(i), local: a ? pair(a) : null });
  });

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
    poorestExceptions: exceptions,
  };
}

const fifths = (p: FifthsPair) =>
  `les plus modestes ${signedPct(p.poorest)}, les plus aisés ${signedPct(p.richest)}`;
const doesWorse = (p: FifthsPair) => !(p.poorest < p.richest);

/**
 * Plain-French note for the exception(s) to the « X sur Y » headline, two
 * short lines, or null when there is none. With a single exception it gives
 * the hypothesis where the poorest fifth does not do better, and the gap in
 * the other; several exceptions are only named.
 */
export function exceptionNote(exceptions: PoorestException[]): string[] | null {
  if (exceptions.length === 0) return null;
  if (exceptions.length > 1) {
    return [
      `Exceptions : ${exceptions.map((e) => e.name).join(", ")}.`,
      "Dans ces territoires, les plus modestes ne s’en sortent pas mieux que les plus aisés dans au moins une hypothèse.",
    ];
  }
  const e = exceptions[0];
  const worseCentral = doesWorse(e.central);
  if (worseCentral && (e.local == null || doesWorse(e.local))) {
    return [
      `Exception : ${e.name}, dans le cas central : ${fifths(e.central)}.`,
      ...(e.local ? [`Dans la variante locale : ${fifths(e.local)}.`] : []),
    ];
  }
  const [failing, ok, failLabel, okLabel] = worseCentral
    ? [e.central, e.local!, "dans le cas central", "Dans la variante locale"]
    : [e.local!, e.central, "dans la variante locale", "Dans le cas central"];
  const gap = (ok.richest - ok.poorest).toLocaleString("fr-FR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  return [
    `Exception : ${e.name}, ${failLabel} : ${fifths(failing)}.`,
    `${okLabel}, l’écart y est de ${gap} point${Number(gap.replace(",", ".")) >= 2 ? "s" : ""} en faveur des plus modestes.`,
  ];
}

/** One territory's poorest-fifth and richest-fifth total change (central case). */
export interface QuintileGap {
  commune_key: string;
  name: string;
  /** Total change in today's tax for the poorest fifth of households, %. */
  poorest: number;
  /** Same for the richest fifth, %. */
  richest: number;
}

/**
 * The poorest and richest fifths side by side, one row per territory that
 * can be split by income (the same ones `poorestAnalysable` counts, chosen by
 * the same rule), ordered from the widest advantage for the poorest to the
 * narrowest. Feeds the home page's chart so it cannot drift from the counts.
 */
export function quintileGaps(communes: Commune[]): QuintileGap[] {
  const rows: QuintileGap[] = [];
  for (const c of communes) {
    const { q1, q5 } = centralInputs(c);
    if (q1 != null && q5 != null) {
      rows.push({ commune_key: c.commune_key, name: c.name, poorest: q1, richest: q5 });
    }
  }
  return rows.sort((a, b) => a.poorest - a.richest - (b.poorest - b.richest));
}

/** "9 sur 13" when both hypotheses agree, "6 à 9 sur 13" otherwise (no-break spaces). */
export function countRange(central: number, alt: number | undefined, of: number): string {
  if (alt == null || alt === central) return `${central} sur ${of}`;
  return `${Math.min(central, alt)} à ${Math.max(central, alt)} sur ${of}`;
}


/** Where both income groups pay less, who pays more: one sentence for the
 *  income chart, or null when every territory has a group paying more. The
 *  levy is unchanged, so the rise falls on parcels outside the household
 *  figures; vacant land's multiple and the categories whose median rises are
 *  read from the payloads (category totals in euros are withheld, so no
 *  ranking of who pays most is claimed). */
export function bothPayLessNote(communes: Commune[], gaps: QuintileGap[]): string | null {
  const both = gaps.filter((g) => g.poorest < 0 && g.richest < 0);
  if (both.length === 0) return null;
  const byKey = new Map(communes.map((c) => [c.commune_key, c]));
  const median = (c: Commune | undefined, cat: string) =>
    c?.by_category.find((r) => r.category === cat)?.median_change_pct ?? null;
  const place = (name: string) =>
    /extra-muros/.test(name) ? (/^Lyon/.test(name) ? "dans la couronne lyonnaise" : "dans la petite couronne")
      : `à ${name}`;
  const multiples = both
    .map((g) => ({ g, m: median(byKey.get(g.commune_key), "Vacant Land") }))
    .filter((x) => x.m != null && x.m > 0)
    .map(({ g, m }) => `×${Math.round(1 + (m as number) / 100)} ${place(g.name)}`);
  const others = [
    ["Single Family Residential", "les maisons"],
    ["Commercial", "les commerces"],
    ["Industrial", "l'industrie"],
  ].filter(([cat]) => both.some((g) => (median(byKey.get(g.commune_key), cat) ?? 0) > 0))
    .map(([, label]) => label);
  const list = (xs: string[], conj: string) =>
    xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} ${conj} ${xs[xs.length - 1]}`;
  const where = list(both.map((g) => place(g.name)), "et");
  return (
    `${where.charAt(0).toUpperCase()}${where.slice(1)}, les ménages modestes comme aisés ` +
    `paient moins. À recettes égales, ` +
    `d'autres paient donc davantage : le terrain constructible laissé vide` +
    (multiples.length ? ` (impôt ${multiples.join(", ")})` : "") +
    (others.length ? ` et, selon le territoire, ${list(others, "ou")}` : "") +
    "."
  );
}
