import { describe, expect, it } from "vitest";
import { poorestNote } from "./poorestNote";
import { loadCommune } from "./data";
import type { Commune } from "./types";

describe("poorestNote", () => {
  it("reads Villeurbanne's published figures", () => {
    const n = poorestNote(loadCommune("villeurbanne"));
    expect(n).not.toBeNull();
    expect(n!.q1Total).toBe(3.4);
    expect(n!.q5Total).toBe(-2.2);
    expect(n!.q1Household).toBeLessThan(0);
    expect(n!.housesTotal).toBeGreaterThan(100);
    expect(n!.q1Income).toBeLessThan(n!.q5Income);
  });

  it("stays silent elsewhere, or once the poorest no longer fare worse", () => {
    expect(poorestNote(loadCommune("paris"))).toBeNull();
    const v = loadCommune("villeurbanne");
    const better: Commune = {
      ...v,
      by_income_quintile: (v.by_income_quintile ?? []).map((r) =>
        r.quintile === 1 ? { ...r, total_change_pct: -5 } : r,
      ),
    };
    expect(poorestNote(better)).toBeNull();
    expect(poorestNote({ ...v, by_income_quintile: null })).toBeNull();
  });
});
