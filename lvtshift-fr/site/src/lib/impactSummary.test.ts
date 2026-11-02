import { describe, expect, it } from "vitest";
import { countRange, impactSummary } from "./impactSummary";
import { loadCommune, loadIndex } from "./data";
import type { Commune } from "./types";

describe("impactSummary on the published data", () => {
  // Reads site/public/data, like the build does: if a pipeline rerun changes
  // these counts, the home page text changes with them and this test says so.
  const communes = loadIndex().communes.map((c) => loadCommune(c.commune_key));
  const s = impactSummary(communes);

  it("counts every published territory", () => {
    expect(s.territories).toBe(13);
  });

  it("matches the central-case figures in the October 2026 payloads", () => {
    expect(s.housesPayMore).toBe(11); // all but Roubaix and La Rochelle
    expect(s.flatsPayLess).toBe(9);
    expect(s.poorestAnalysable).toBe(11); // Cahors and Figeac: no quintiles
    expect(s.poorestPayLess).toBe(11);
    expect(s.poorestBelowRichest).toBe(11);
    expect(s.houseMedianMin).toBe(-19.7);
    expect(s.houseMedianMax).toBe(41.4);
    expect(s.shiftMin).toBe(9.8); // Paris
    expect(s.shiftMax).toBe(25.9); // Grenoble
  });

  it("matches the local-variant figures in the 31 October 2026 payloads", () => {
    expect(s.alt).toEqual({
      housesPayMore: 12, // all but La Rochelle
      flatsPayLess: 6, // Villeurbanne, Montreuil, Paris and Lyon turn positive
      poorestAnalysable: 11,
      poorestPayLess: 8, // Villeurbanne, Montreuil and Paris extra-muros turn positive
      poorestBelowRichest: 11,
    });
    expect(s.poorestBelowRichestBoth).toBe(11);
  });
});

describe("impactSummary without a comparable variant", () => {
  const base = loadCommune("paris");

  it("drops the variant counts when a territory lacks one", () => {
    const without: Commune = { ...base, baseline_sensitivity: null };
    const s = impactSummary([base, without]);
    expect(s.alt).toBeNull();
    expect(s.poorestBelowRichestBoth).toBe(s.poorestBelowRichest);
  });

  it("drops them when the variant lacks quintiles the central case has", () => {
    const b = base.baseline_sensitivity!;
    const noQuintiles: Commune = {
      ...base,
      baseline_sensitivity: { ...b, low: { ...b.low, by_income_quintile: null } },
    };
    expect(impactSummary([noQuintiles]).alt).toBeNull();
  });
});

describe("countRange", () => {
  it("gives one number when both hypotheses agree", () => {
    expect(countRange(11, 11, 13)).toBe("11 sur 13");
    expect(countRange(11, undefined, 13)).toBe("11 sur 13");
  });

  it("gives the lower count first", () => {
    expect(countRange(9, 6, 13)).toBe("6 à 9 sur 13");
    expect(countRange(11, 12, 13)).toBe("11 à 12 sur 13");
  });
});
