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

  // November 2026 payloads: social landlords' parcels left the household
  // figures, and the reform replaces the tax on non-agricultural unbuilt land
  it("matches the central-case figures in the November 2026 payloads", () => {
    expect(s.housesPayMore).toBe(10); // all but Roubaix, Figeac and La Rochelle
    expect(s.smallBuildingsPayLess).toBe(6);
    expect(s.blocksPayLess).toBe(13);
    expect(s.poorestAnalysable).toBe(11); // Cahors and Figeac: no quintiles
    expect(s.poorestPayLess).toBe(11);
    expect(s.poorestBelowRichest).toBe(11); // Villeurbanne at parity: −1.5 % vs −1.3 %
    expect(s.houseMedianMin).toBe(-22.5); // Roubaix
    expect(s.houseMedianMax).toBe(106.2); // Paris
    expect(s.shiftMin).toBe(20.6); // Paris
    expect(s.shiftMax).toBe(35.9); // Grenoble
  });

  it("matches the local-variant figures in the November 2026 payloads", () => {
    expect(s.alt).toEqual({
      housesPayMore: 10,
      smallBuildingsPayLess: 5,
      blocksPayLess: 13,
      poorestAnalysable: 11,
      poorestPayLess: 8,
      poorestBelowRichest: 10, // Villeurbanne: +11.0 % vs +9.9 %
    });
    expect(s.poorestBelowRichestBoth).toBe(10);
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
    expect(countRange(9, 6, 13)).toBe("6 à 9 sur 13");
    expect(countRange(11, 12, 13)).toBe("11 à 12 sur 13");
  });
});
