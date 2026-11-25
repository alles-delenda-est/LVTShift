import { describe, expect, it } from "vitest";
import { wrapLabel } from "./labelWrap";

describe("wrapLabel", () => {
  it("keeps short labels on one line", () => {
    expect(wrapLabel("Commerce", 18)).toEqual(["Commerce"]);
    expect(wrapLabel("Autre bâtiment‡", 18)).toEqual(["Autre bâtiment‡"]);
  });

  it("wraps long French property-category labels cleanly to at most two lines", () => {
    const cases: [string, string[]][] = [
      ["Maison individuelle", ["Maison", "individuelle"]],
      ["Petit immeuble (2–4 logements)", ["Petit immeuble", "(2–4 logements)"]],
      ["Immeuble collectif (5+ logements)", ["Immeuble collectif", "(5+ logements)"]],
      ["Logement social (bailleurs)‡", ["Logement social", "(bailleurs)‡"]],
      ["Terrain nu / non bâti‡", ["Terrain nu / non", "bâti‡"]],
    ];
    for (const [label, expected] of cases) {
      const lines = wrapLabel(label, 18);
      expect(lines).toEqual(expected);
      expect(lines.length).toBeLessThanOrEqual(2);
      for (const line of lines) {
        expect(line.length).toBeLessThanOrEqual(18);
      }
    }
  });
});
