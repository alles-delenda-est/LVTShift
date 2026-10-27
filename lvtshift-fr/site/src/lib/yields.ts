/**
 * Yields to replace in the three nested scenarios (spec 0005).
 *
 * The figures come from lvtshift-fr/yields.py via public/data/yields.json;
 * this module only groups them for display. Nothing here recomputes a yield.
 */

export type ScenarioKey = "S1" | "S2" | "S3";
export type Tier = "local" | "departmental" | "national";
export type Status = "verified" | "derived" | "reported";

export interface YieldTax {
  key: string;
  label_fr: string;
  scenario: "S1" | "S2" | "S2_IFI" | "S3";
  tier: Tier;
  budget: string;
  basis: "average" | "latest";
  status: Status;
  values_meur: Record<string, number>;
  reference_years: number[];
  reference_meur: number;
  source: string;
  url: string;
  scope: string;
  note: string;
}

export interface YieldVariant {
  scenario: ScenarioKey;
  include_ifi: boolean;
  total_meur: number;
  tiers_meur: Record<Tier, number>;
  rate_pct: number;
  lines: string[];
}

export interface YieldsData {
  as_of: string;
  average_years: number;
  taxes: YieldTax[];
  land_base: {
    taxable_meur: number;
    total_meur: number;
    public_meur: number;
    year: number;
    source: string;
    url: string;
    note: string;
    farmland: {
      value_meur: number;
      low_meur: number;
      high_meur: number;
      area_ha: number;
      vine_area_ha: number;
      price_free_eur_ha: number;
      price_let_eur_ha: number;
      vine_price_eur_ha: number;
      year: number;
      source: string;
      url: string;
      insee_meur: number;
      forest_upper_meur: number;
    };
  };
  variants: YieldVariant[];
}

/** Display families: the stacked segments of the chart, in fixed order. */
export const FAMILIES = [
  { key: "tf", label: "Taxe foncière", taxes: ["tfpb", "tfpnb", "tf_annexes", "tf_etat"] },
  { key: "thrs", label: "Taxe d'habitation (résidences secondaires)", taxes: ["thrs", "thrs_etat"] },
  { key: "dmto", label: "Droits de mutation", taxes: ["dmto_communes", "dmto_departements", "dmto_etat"] },
  { key: "gains", label: "Impôts sur les plus-values immobilières", taxes: ["gains_ir", "gains_ps"] },
  { key: "ifi", label: "IFI", taxes: ["ifi"] },
  { key: "rents", label: "Impôts sur les revenus locatifs", taxes: ["rents_ir", "rents_ps", "rents_csg"] },
] as const;

export type FamilyKey = (typeof FAMILIES)[number]["key"];

/**
 * Family colours, fixed order. Checked with the dataviz palette validator on
 * the crème surface: all checks pass; the light blue and ochre are under 3:1
 * contrast, so each family is also named in the legend and the table.
 */
export const FAMILY_COLORS: Record<FamilyKey, string> = {
  tf: "#2b4c9b",
  thrs: "#8e5bb5",
  dmto: "#7a9fe0",
  gains: "#b5281e",
  ifi: "#c98a1e",
  rents: "#2e7d4f",
};

export function familyOf(taxKey: string): FamilyKey | null {
  const f = FAMILIES.find((x) => (x.taxes as readonly string[]).includes(taxKey));
  return f ? f.key : null;
}

export const SCENARIO_LABELS: Record<ScenarioKey, { short: string; long: string }> = {
  S1: { short: "Scénario 1", long: "Taxe foncière, taxe d'habitation des résidences secondaires et droits de mutation" },
  S2: { short: "Scénario 2", long: "+ impôts sur les plus-values immobilières" },
  S3: { short: "Scénario 3", long: "+ impôts sur les revenus locatifs" },
};

export const TIER_LABELS: Record<Tier, string> = {
  local: "Communal",
  departmental: "Départemental",
  national: "National",
};

export const STATUS_LABELS: Record<Status, string> = {
  verified: "Vérifié",
  derived: "Calculé",
  reported: "À confirmer",
};

export function variant(data: YieldsData, scenario: ScenarioKey, includeIfi: boolean): YieldVariant {
  const ifi = scenario === "S1" ? false : includeIfi;
  const v = data.variants.find((x) => x.scenario === scenario && x.include_ifi === ifi);
  if (!v) throw new Error(`missing variant ${scenario}${ifi ? " + IFI" : ""}`);
  return v;
}

/** One chart row: a scenario split into families, M€. */
export interface StackRow {
  scenario: ScenarioKey;
  total: number;
  rate: number;
  segments: Record<FamilyKey, number>;
}

export function stackRows(data: YieldsData, includeIfi: boolean): StackRow[] {
  const byKey = new Map(data.taxes.map((t) => [t.key, t]));
  return (["S1", "S2", "S3"] as ScenarioKey[]).map((sc) => {
    const v = variant(data, sc, includeIfi);
    const included = new Set(v.lines);
    const segments = {} as Record<FamilyKey, number>;
    for (const f of FAMILIES) {
      segments[f.key] = f.taxes
        .filter((k) => included.has(k))
        .reduce((s, k) => s + (byKey.get(k)?.reference_meur ?? 0), 0);
    }
    return { scenario: sc, total: v.total_meur, rate: v.rate_pct, segments };
  });
}

/** "2021–2025" or "2025" for the years behind a reference value. */
export function yearsLabel(years: number[]): string {
  if (years.length === 0) return "";
  const lo = Math.min(...years);
  const hi = Math.max(...years);
  return lo === hi ? String(lo) : `${lo}–${hi}`;
}

/** Billions of euros with one decimal and a comma: 61 964 → "62,0". */
export function mdEur(meur: number): string {
  return (meur / 1000).toLocaleString("fr-FR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}
