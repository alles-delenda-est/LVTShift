import { describe, expect, it } from "vitest";
import { socialNote } from "./socialHousing";
import type { Commune } from "./types";

const c = (social?: NonNullable<Commune["provenance"]["social_housing"]>) =>
  ({ provenance: { social_housing: social } }) as Pick<Commune, "provenance">;

describe("socialNote", () => {
  it("says nothing for runs without social housing, or communes with none", () => {
    expect(socialNote(c())).toBeNull();
    expect(socialNote(c({ modelled: false }))).toBeNull();
    expect(socialNote(c({ modelled: true, category: "none" }))).toBeNull();
  });

  it("quotes the commune's exempt and abated shares where the category is shown", () => {
    const n = socialNote(c({ modelled: true, category: "shown", tax_year: 2025,
      rpls_dwellings: 18755, exempt_dwellings_pct: 23.7, qpv_abated_dwellings_pct: 41.8 }));
    expect(n?.kind).toBe("category");
    expect(n?.counts).toBe(
      "Ici, 23,7 % des 18 755 logements sociaux sont exonérés de taxe foncière en 2025 " +
      "et 41,8 % bénéficient de l'abattement de 30 % en quartier prioritaire.");
    const noQpv = socialNote(c({ modelled: true, category: "shown", tax_year: 2025,
      rpls_dwellings: 1000, exempt_dwellings_pct: 30, qpv_abated_dwellings_pct: 0 }));
    expect(noQpv?.counts?.endsWith("en 2025.")).toBe(true);
  });

  it("gives no figures where the category is folded into Other", () => {
    expect(socialNote(c({ modelled: true, category: "folded", rpls_dwellings: 900,
      exempt_dwellings_pct: 30 }))).toEqual({ kind: "folded", counts: null });
  });
});
