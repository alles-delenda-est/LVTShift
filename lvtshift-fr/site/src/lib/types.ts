export interface Headline {
  parcels_modeled: number; tax_base_eur: number; land_base_eur: number;
  improvement_base_eur: number; land_share_pct: number | null; neutral_levy_eur: number;
  /** % of built parcels whose land share sits at the 85 % clip (absent in older payloads) */
  built_at_cap_pct?: number | null;
  gross_shifted_eur: number; net_shifted_eur: number; gross_pct_of_levy: number | null;
  net_pct_of_levy: number | null; gross_bps_of_base: number | null; currency: "EUR";
}
/** One category's figures in a sensitivity leg (subset of CategoryRow). */
export interface BandCategoryRow {
  category: string; median_change_pct: number | null; median_change_eur: number | null;
  share_paying_more_pct: number | null;
}
/** One income quintile's figures in a sensitivity leg (subset of QuintileRow). */
export interface BandQuintileRow {
  quintile: number; median_change_pct: number | null;
  median_change_pct_residential: number | null;
  /** Absent in older payloads. */
  total_change_pct?: number | null; household_median_change_pct?: number | null;
}
export interface SensitivityLeg {
  land_share_pct: number; gross_pct_of_levy: number | null; net_pct_of_levy: number | null;
  median_change_pct_residential: number | null; share_paying_more_pct: number | null;
  /** Per-group figures under this leg (absent in older payloads). */
  by_category?: BandCategoryRow[] | null;
  by_income_quintile?: BandQuintileRow[] | null;
  by_income_quintile_within?: BandQuintileRow[] | null;
}
export interface Sensitivity { delta_pt: number; base: SensitivityLeg; low: SensitivityLeg; high: SensitivityLeg; }
/** Central vs lower-bound share of professional premises in today's tax: the
 *  LVT bills are identical, only today's tax (and so every change) differs. */
export interface BaselineSensitivity {
  pro_scale_central: number; pro_scale_low: number;
  central: SensitivityLeg; low: SensitivityLeg;
}
export interface CategoryRow {
  category: string; label_fr: string; parcels: number; share_of_parcels_pct: number | null;
  /** Null for a category below the disclosure minimum (count only). */
  median_change_pct: number | null; median_change_eur: number | null;
  count_paying_more: number | null; share_paying_more_pct: number | null;
}
/** A category whose figures are published (see lib/disclosure). */
export type PublishedCategoryRow = CategoryRow & {
  median_change_eur: number; count_paying_more: number;
};
export interface QuintileRow {
  quintile: number; median_income_eur: number; median_change_pct: number | null;
  median_change_pct_residential: number | null; parcels: number;
  /** Group total change on residential parcels (absent in older payloads). */
  total_change_pct?: number | null;
  /** Typical household's change: parcel change weighted by dwellings. */
  household_median_change_pct?: number | null;
  dwellings?: number | null;
}
export interface BucketRow {
  bucket: string; label: string; parcels: number; value_eur: number | null;
  value_pct_of_base: number | null; share_of_gross_change_pct: number | null;
}
/** One member commune of a territory (per-commune aggregates, never per-parcel). */
export interface MemberRow {
  commune_key: string; name: string; insee: string; parcels_modeled: number;
  neutral_levy_eur: number; land_share_pct: number | null;
  gross_pct_of_levy: number | null; share_paying_more_pct: number | null;
  /** Sum of increases as % of the levy (absent in older payloads). */
  net_pct_of_levy?: number | null;
}
export interface Coverage {
  members_total: number; members_modeled: number; members_missing: string[];
}
/** A commune, or a territory (inner ring) aggregating per-commune runs: a
 *  territory has kind "territory", insee null, and carries members + coverage. */
export interface Commune {
  commune_key: string; kind?: "commune" | "territory"; insee: string | null;
  name: string; departement: string;
  reference_year: number | null; model_type: string; headline: Headline;
  headline_sensitivity: Sensitivity; by_category: CategoryRow[];
  /** Absent in older payloads and in runs without a calibrated baseline. */
  baseline_sensitivity?: BaselineSensitivity | null;
  by_income_quintile: QuintileRow[] | null; by_improvement_ratio: BucketRow[];
  provenance: {
    construction_cost_eur_m2: number | null; land_share_bounds: number[]; note: string;
    /** cost applied to houses, same basis (absent in older payloads; null = commune cost) */
    house_cost_eur_m2?: number | null;
    /** business land as a share of the local building-plot price (absent in older payloads) */
    activity_land_ratio?: number | null;
    /** how today's tax was shared: calibrated to the REI split by tax group, or plain floor area */
    current_tax_baseline?: {
      method: string; members_calibrated?: number;
      target_industrial_share?: number | null; achieved_industrial_share?: number | null;
      target_professional_share?: number | null; achieved_professional_share?: number | null;
      /** industrial and professional treated as one group (warehouses taxed as professional premises) */
      industrial_merged_into_professional?: boolean;
    };
    /** parcels treated as exempt public property (count only; absent in older payloads) */
    exempt_public_parcels?: number;
    farmland_excluded_parcels?: number;
  };
  members?: MemberRow[]; coverage?: Coverage;
  /** Territory only: quintiles ranked inside each member commune, then pooled. */
  by_income_quintile_within?: QuintileRow[] | null;
  by_income_quintile_within_coverage_pct?: number;
  currency: "EUR";
}
export interface IndexCommune {
  commune_key: string; kind?: "commune" | "territory"; name: string;
  insee: string | null; departement: string;
  parcels_modeled: number; land_share_pct: number | null; gross_pct_of_levy: number | null;
  /** Communes / parcels this entry adds to the panel totals without double
   *  counting communes also published on their own (e.g. Montreuil). */
  n_communes_unique?: number; parcels_unique?: number;
}
export interface ValidationCheck {
  benchmark: string; independence: string; status: string; note: string;
  external_value_pct?: number | null; model_comparable_pct?: number | null;
  model_comparable_label?: string; [k: string]: unknown;
}
export interface RegisterCheck {
  check: string; category: string; severity: "OK" | "WARN" | "FAIL";
  message: string; adaptation: string | null; detail: Record<string, unknown>;
}
export interface RegisterCommune {
  commune_key: string; name: string; insee: string; departement: string;
  modellable: boolean; verdict: "OK" | "WARN" | "FAIL"; n_fail: number; n_warn: number;
  checks: RegisterCheck[];
}
