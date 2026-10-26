import type { Commune, IndexCommune } from "@/lib/types";

/**
 * Land share of every modelled commune in the panel, de-duplicated by key.
 *
 * The home page used to take its min–max over the selector entries only
 * (11 communes + 2 territory aggregates), which hid the member communes'
 * spread: the true maximum is a member (Neuilly-sur-Seine, 78,1 %), not
 * Paris. Territory members come from each territory's own payload.
 */
export function panelLandShares(
  index: IndexCommune[],
  load: (key: string) => Pick<Commune, "members">,
): Map<string, number> {
  const out = new Map<string, number>();
  for (const c of index) {
    if (c.kind === "territory") {
      for (const m of load(c.commune_key).members ?? []) {
        if (m.land_share_pct != null) out.set(m.commune_key, m.land_share_pct);
      }
    } else if (c.land_share_pct != null) {
      out.set(c.commune_key, c.land_share_pct);
    }
  }
  return out;
}
