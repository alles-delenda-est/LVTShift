import { describe, expect, it } from "vitest";
import { bandSpan, byKey } from "./band";

describe("bandSpan", () => {
  it("spans the central value and both legs", () => {
    expect(bandSpan(2, -1, 5)).toEqual({ err: [3, 3], lo: -1, hi: 5 });
  });
  it("keeps the central value inside the span when legs fall on one side", () => {
    expect(bandSpan(2, 3, 4)).toEqual({ err: [0, 2], lo: 2, hi: 4 });
  });
  it("returns null when any value is missing", () => {
    expect(bandSpan(null, 1, 2)).toBeNull();
    expect(bandSpan(1, undefined, 2)).toBeNull();
    expect(bandSpan(1, 2, Number.NaN)).toBeNull();
  });
});

describe("byKey", () => {
  it("indexes rows and tolerates a missing list", () => {
    expect(byKey([{ q: 1, v: 2 }], "q").get(1)).toEqual({ q: 1, v: 2 });
    expect(byKey(null as { q: number }[] | null, "q").size).toBe(0);
  });
});
