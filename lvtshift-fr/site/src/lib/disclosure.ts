import type { CategoryRow, PublishedCategoryRow } from "@/lib/types";

/**
 * The exporter blanks every figure of a category with fewer than 11 parcels
 * (export_web.MIN_GROUP_PARCELS) and keeps its count. Charts show only the
 * categories with figures; the page says how many were held back.
 */
export function publishedCategories(rows: CategoryRow[]): PublishedCategoryRow[] {
  return rows.filter(
    (r): r is PublishedCategoryRow =>
      r.median_change_eur !== null && r.count_paying_more !== null,
  );
}

export function withheldCategories(rows: CategoryRow[]): number {
  return rows.length - publishedCategories(rows).length;
}
