import { describe, it, expect } from "vitest";
import { euros, pct, signedPct, signedPctAxis } from "@/lib/format";

const NBSP = " "; // espace insécable
describe("french formatters", () => {
  it("scales euros with insécable spacing", () => {
    expect(euros(1234)).toBe(`1${NBSP}234${NBSP}€`);
    expect(euros(101_800_000)).toBe(`101,8${NBSP}M€`);
    expect(euros(30_480_000_000)).toBe(`30,5${NBSP}Md€`);
  });
  it("formats percentages with a comma and insécable space, null -> n. d.", () => {
    expect(pct(12.5)).toBe(`12,5${NBSP}%`);
    expect(pct(null)).toBe("n. d.");
  });
  it("signs percentages with a true minus sign", () => {
    expect(signedPct(6.3)).toBe(`+6,3${NBSP}%`);
    expect(signedPct(-10.1)).toBe(`−10,1${NBSP}%`);
  });
});

describe("signedPctAxis", () => {
  it("drops the decimal on round ticks and keeps the true minus", () => {
    expect(signedPctAxis(20)).toBe("+20 %");
    expect(signedPctAxis(-40)).toBe("−40 %");
    expect(signedPctAxis(0)).toBe("0 %");
    expect(signedPctAxis(2.5)).toBe("+2,5 %");
  });
});
