import { describe, expect, it } from "vitest";
import { symmetricAxis } from "./axis";

describe("symmetricAxis", () => {
  it("puts every tick on a round value", () => {
    // Montreuil's category chart: largest reach 63,1 % (was ±85,3 % ticks)
    const a = symmetricAxis(63.1);
    expect(a.ticks).toEqual([-80, -60, -40, -20, 0, 20, 40, 60, 80]);
    expect(a.lim).toBeGreaterThanOrEqual(63.1);
  });

  it("covers the data with the requested headroom", () => {
    for (const m of [0.4, 3, 9.9, 17.9, 23.7, 48, 104.2, 380]) {
      const a = symmetricAxis(m, { headroom: 1.25 });
      expect(a.lim).toBeGreaterThanOrEqual(m * 1.25 - 1e-9);
      expect(a.ticks.length).toBeLessThanOrEqual(9);
      expect(a.ticks[0]).toBe(-a.lim);
      expect(a.ticks.at(-1)).toBe(a.lim);
    }
  });

  it("never goes below the minimum limit", () => {
    const a = symmetricAxis(0);
    expect(a.lim).toBeGreaterThanOrEqual(5);
    expect(a.ticks).toEqual([-6, -4, -2, 0, 2, 4, 6]);
  });

  it("avoids half-step ticks such as 17,5", () => {
    const a = symmetricAxis(23.7, { headroom: 1.25 });
    expect(a.ticks.every((t) => Number.isInteger(t))).toBe(true);
  });
});
