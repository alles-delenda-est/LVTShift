import { describe, expect, it } from "vitest";
import { panelLandShares } from "./panel";
import type { IndexCommune, MemberRow } from "./types";

const ic = (k: string, share: number | null, kind?: "territory"): IndexCommune => ({
  commune_key: k, kind, name: k, insee: null, departement: "", parcels_modeled: 1,
  land_share_pct: share, gross_pct_of_levy: null,
});
const m = (k: string, share: number | null): MemberRow => ({
  commune_key: k, name: k, insee: "", parcels_modeled: 1, neutral_levy_eur: 1,
  land_share_pct: share, gross_pct_of_levy: null, share_paying_more_pct: null,
});

describe("panelLandShares", () => {
  it("includes territory members and counts a commune listed twice once", () => {
    const shares = panelLandShares(
      [ic("paris", 75.8), ic("montreuil", 66.6), ic("ring", 65.3, "territory")],
      () => ({ members: [m("montreuil", 66.6), m("neuilly", 78.1), m("x", null)] }),
    );
    expect(shares.size).toBe(3);
    expect(Math.max(...shares.values())).toBe(78.1);
    expect(shares.has("ring")).toBe(false);
  });
});
