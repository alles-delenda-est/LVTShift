import { describe, expect, it } from "vitest";
import { bothPayLessNote, countRange, exceptionNote, impactSummary, quintileGaps } from "./impactSummary";
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

  // November 2026 payloads: the land-only tax at permitted use (the reform
  // also replaces the tax on non-agricultural unbuilt land; social
  // landlords' parcels are outside the household figures; building-less
  // urban land at site value, open space as natural land, 2026-11-24)
  it("matches the central-case figures in the November 2026 payloads", () => {
    expect(s.housesPayMore).toBe(10); // all but Roubaix, Figeac and La Rochelle
    expect(s.smallBuildingsPayLess).toBe(4); // the Lyon ring's 2–4 now +2.1 %
    expect(s.blocksPayLess).toBe(13);
    expect(s.poorestAnalysable).toBe(11); // Cahors and Figeac: no quintiles
    expect(s.poorestPayLess).toBe(10); // Villeurbanne: +0.9 %
    expect(s.poorestBelowRichest).toBe(10); // Villeurbanne: +0.9 % vs −4.6 %
    expect(s.houseMedianMin).toBe(-23); // Roubaix
    expect(s.houseMedianMax).toBe(116.7); // Paris
    expect(s.shiftMin).toBe(23.2); // Paris
    expect(s.shiftMax).toBe(40.1); // Grenoble
  });

  it("matches the local-variant figures in the November 2026 payloads", () => {
    expect(s.alt).toEqual({
      housesPayMore: 11, // La Rochelle's houses +3.2 % in the local variant
      smallBuildingsPayLess: 4,
      blocksPayLess: 13,
      poorestAnalysable: 11,
      poorestPayLess: 8,
      poorestBelowRichest: 10, // Villeurbanne: +13.7 % vs +6.5 %
    });
    expect(s.poorestBelowRichestBoth).toBe(10);
  });
});

describe("the exception to the « sur 11 » headline", () => {
  const communes = loadIndex().communes.map((c) => loadCommune(c.commune_key));
  const s = impactSummary(communes);

  it("is Villeurbanne alone, in both hypotheses, which explains 10 sur 11", () => {
    expect(s.poorestExceptions).toEqual([
      {
        name: "Villeurbanne",
        central: { poorest: 0.9, richest: -4.6 },
        local: { poorest: 13.7, richest: 6.5 },
      },
    ]);
    expect(s.poorestAnalysable - s.poorestExceptions.length).toBe(s.poorestBelowRichestBoth);
  });

  it("is written in two lines from the figures", () => {
    const nb = (t: string) => t.replace(/ /g, " ");
    expect(exceptionNote(s.poorestExceptions)!.map(nb)).toEqual([
      nb("Exception : Villeurbanne, dans le cas central : les plus modestes +0,9 %, les plus aisés −4,6 %."),
      nb("Dans la variante locale : les plus modestes +13,7 %, les plus aisés +6,5 %."),
    ]);
  });

  it("has no note when there is no exception", () => {
    expect(exceptionNote([])).toBeNull();
    const clean = impactSummary([loadCommune("grenoble"), loadCommune("paris")]);
    expect(clean.poorestExceptions).toEqual([]);
  });

  it("covers a failure in the central case and in both", () => {
    const e = { name: "X", central: { poorest: 2, richest: 1 }, local: { poorest: -5, richest: -1 } };
    expect(exceptionNote([e])![0]).toContain("dans le cas central");
    expect(exceptionNote([e])![1]).toContain("4,0 points");
    const both = exceptionNote([{ ...e, local: { poorest: 3, richest: 1 } }]);
    expect(both).toHaveLength(2); // one line per hypothesis
    expect(exceptionNote([{ ...e, local: null }])).toHaveLength(1);
    expect(exceptionNote([e, { ...e, name: "Y" }])![0]).toBe("Exceptions : X, Y.");
  });
});

describe("quintileGaps on the published data", () => {
  const communes = loadIndex().communes.map((c) => loadCommune(c.commune_key));
  const s = impactSummary(communes);
  const gaps = quintileGaps(communes);

  it("has one row per territory the counts analyse, and agrees with them", () => {
    expect(gaps).toHaveLength(s.poorestAnalysable);
    expect(gaps.filter((g) => g.poorest < 0)).toHaveLength(s.poorestPayLess);
    expect(gaps.filter((g) => g.poorest < g.richest)).toHaveLength(s.poorestBelowRichest);
  });

  it("orders the widest advantage for the poorest first", () => {
    expect(gaps[0].commune_key).toBe("roubaix"); // −32,7 % vs +49,0 %
    expect(gaps[0]).toMatchObject({ poorest: -32.7, richest: 49.0 });
    expect(gaps.at(-1)!.commune_key).toBe("villeurbanne"); // +0,9 % vs −4,6 %: the poorest fifth does worse
    const diffs = gaps.map((g) => g.poorest - g.richest);
    expect(diffs).toEqual([...diffs].sort((a, b) => a - b));
  });

  it("leaves out territories without an income split", () => {
    const keys = gaps.map((g) => g.commune_key);
    expect(keys).not.toContain("cahors");
    expect(keys).not.toContain("figeac");
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

describe("bothPayLessNote", () => {
  const communes = loadIndex().communes.map((c) => loadCommune(c.commune_key));
  const gaps = quintileGaps(communes);
  it("names the territories where both groups pay less and who pays more in total", () => {
    const note = bothPayLessNote(communes, gaps)!;
    // November 2026 (PR #85): Grenoble, La Rochelle, Annemasse and the Lyon ring
    expect(note).toMatch(/^À Grenoble, à La Rochelle, à Annemasse et dans la couronne lyonnaise, les ménages/);
    expect(note).toContain("×5 à Grenoble");
    expect(note).toContain("×20 à La Rochelle");
    expect(note).toContain("dans la couronne lyonnaise");
    // Commercial pays more in total in La Rochelle only (+0,6 %), though its median falls
    expect(note).toContain("les commerces");
    expect(note).toContain("les bailleurs sociaux");
    expect(note).toContain("les autres bâtiments");
    expect(note).toContain("au sein même des ménages, sur les maisons individuelles");
  });
  it("says nothing when a group pays more everywhere", () => {
    expect(bothPayLessNote(communes, gaps.filter((g) => g.richest > 0))).toBeNull();
  });
});
