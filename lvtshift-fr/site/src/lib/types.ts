export interface Headline {
  parcels_modeled: number; tax_base_eur: number; land_base_eur: number;
  improvement_base_eur: number; land_share_pct: number | null; neutral_levy_eur: number;
  gross_shifted_eur: number; net_shifted_eur: number; gross_pct_of_levy: number | null;
  net_pct_of_levy: number | null; gross_bps_of_base: number | null; currency: "EUR";
}
export interface SensitivityLeg {
  land_share_pct: number; gross_pct_of_levy: number | null; net_pct_of_levy: number | null;
  median_change_pct_residential: number | null; share_paying_more_pct: number | null;
}
export interface Sensitivity { delta_pt: number; base: SensitivityLeg; low: SensitivityLeg; high: SensitivityLeg; }
export interface CategoryRow {
  category: string; label_fr: string; parcels: number; share_of_parcels_pct: number | null;
  median_change_pct: number | null; median_change_eur: number; count_paying_more: number;
  share_paying_more_pct: number | null;
}
export interface QuintileRow {
  quintile: number; median_income_eur: number; median_change_pct: number | null;
  median_change_pct_residential: number | null; parcels: number;
}
export interface BucketRow {
  bucket: string; label: string; parcels: number; value_eur: number;
  value_pct_of_base: number | null; share_of_gross_change_pct: number | null;
}
export interface Commune {
  commune_key: string; insee: string; name: string; departement: string;
  reference_year: number | null; model_type: string; headline: Headline;
  headline_sensitivity: Sensitivity; by_category: CategoryRow[];
  by_income_quintile: QuintileRow[] | null; by_improvement_ratio: BucketRow[];
  provenance: { construction_cost_eur_m2: number; land_share_bounds: number[]; note: string };
  currency: "EUR";
}
export interface IndexCommune {
  commune_key: string; name: string; insee: string; departement: string;
  parcels_modeled: number; land_share_pct: number | null; gross_pct_of_levy: number | null;
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
