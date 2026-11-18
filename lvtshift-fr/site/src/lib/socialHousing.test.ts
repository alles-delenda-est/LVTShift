import { describe, expect, it } from "vitest";
import { socialNote, socialSummary, socialSummarySentence } from "./socialHousing";
import { loadCommune, loadIndex } from "./data";
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
      "ici, 23,7 % des 18 755 logements sociaux sont exonérés en 2025 " +
      "et 41,8 % bénéficient de l'abattement de 30 % en quartier prioritaire");
    const noQpv = socialNote(c({ modelled: true, category: "shown", tax_year: 2025,
      rpls_dwellings: 1000, exempt_dwellings_pct: 30, qpv_abated_dwellings_pct: 0 }));
    expect(noQpv?.counts?.endsWith("en 2025")).toBe(true);
  });

  it("gives no figures where the category is folded into Other", () => {
    expect(socialNote(c({ modelled: true, category: "folded", rpls_dwellings: 900,
      exempt_dwellings_pct: 30 }))).toEqual({ kind: "folded", counts: null });
  });
});

describe("socialSummary", () => {
  const row = (total: number | null | undefined) =>
    ({ by_category: [{ category: "Social Housing", total_change_pct: total }] }) as Pick<
      Commune,
      "by_category"
    >;

  it("counts only territories that publish the social landlords' total", () => {
    const s = socialSummary([row(-26), row(21.7), row(null), { by_category: [] }]);
    expect(s).toEqual({ published: 2, payLess: 1, min: -26, max: 21.7 });
    expect(socialSummarySentence(s)).toBe(
      "Dans les 2 territoires où le total de cette catégorie est publié, l'impôt des " +
        "bailleurs sociaux, exonérations supprimées, varie de −26,0\u00a0% à +21,7\u00a0% " +
        "(cas central) : il baisse dans 1 d'entre eux et augmente dans 1.",
    );
  });

  it("says nothing when no total is published", () => {
    expect(socialSummarySentence(socialSummary([row(null)]))).toBe("");
  });

  // Reads site/public/data, like the build: a re-run that changes the
  // protections page's sentence fails here first.
  it("matches the November 2026 payloads", () => {
    const communes = loadIndex().communes.map((c) => loadCommune(c.commune_key));
    // land-only tax: La Rochelle −33.7 %, Annemasse +10.3 %
    expect(socialSummary(communes)).toEqual({ published: 10, payLess: 6, min: -33.7, max: 10.3 });
  });
});
