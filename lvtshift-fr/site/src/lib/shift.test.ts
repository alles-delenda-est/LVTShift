import { describe, expect, it } from "vitest";
import { shiftedPct } from "./shift";

describe("shiftedPct", () => {
  it("prefers the published net figure", () => {
    expect(shiftedPct(12.5, 25.1)).toBe(12.5);
  });
  it("halves the gross figure when net is absent (revenue neutrality)", () => {
    expect(shiftedPct(undefined, 113.9)).toBe(57);
    expect(shiftedPct(null, 25.1)).toBe(12.6);
  });
  it("returns null when neither is known", () => {
    expect(shiftedPct(null, null)).toBeNull();
  });
});
