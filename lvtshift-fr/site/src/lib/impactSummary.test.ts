import { describe, expect, it } from "vitest";
import { impactSummary } from "./impactSummary";
import { loadCommune, loadIndex } from "./data";

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
    expect(s.houseMedianMin).toBe(-19.7);
    expect(s.houseMedianMax).toBe(41.4);
    expect(s.shiftMin).toBe(9.8); // Paris
    expect(s.shiftMax).toBe(25.9); // Grenoble
  });
});
