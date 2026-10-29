import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { FAMILIES, stackRows, variant, yearsLabel, mdEur, type YieldsData } from "@/lib/yields";

const data = JSON.parse(
  fs.readFileSync(path.join(process.cwd(), "public", "data", "yields.json"), "utf-8"),
) as YieldsData;

describe("yields", () => {
  it("every tax belongs to exactly one display family", () => {
    const inFamilies = FAMILIES.flatMap((f) => f.taxes as readonly string[]);
    expect(new Set(inFamilies).size).toBe(inFamilies.length);
    expect([...inFamilies].sort()).toEqual(data.taxes.map((t) => t.key).sort());
  });

  it("stack segments add up to the exported totals (±1 M€ rounding per line)", () => {
    for (const ifi of [false, true]) {
      for (const row of stackRows(data, ifi)) {
        const sum = Object.values(row.segments).reduce((a, b) => a + b, 0);
        expect(Math.abs(sum - row.total)).toBeLessThanOrEqual(data.taxes.length);
      }
    }
  });

  it("scenarios are nested and the IFI toggle leaves S1 alone", () => {
    const [s1, s2, s3] = stackRows(data, false);
    expect(s1.total).toBeLessThan(s2.total);
    expect(s2.total).toBeLessThan(s3.total);
    expect(s1.segments.gains).toBe(0);
    expect(s2.segments.rents).toBe(0);
    expect(variant(data, "S1", true)).toEqual(variant(data, "S1", false));
    expect(stackRows(data, true)[1].segments.ifi).toBeGreaterThan(0);
    expect(stackRows(data, false)[1].segments.ifi).toBe(0);
  });

  it("puts no transfer on companies in S1 and a growing one in S2–S3", () => {
    expect(variant(data, "S1", false).company_land_meur).toBe(0);
    const s2 = variant(data, "S2", false).company_land_meur;
    const s3 = variant(data, "S3", false).company_land_meur;
    const s3i = variant(data, "S3", true).company_land_meur;
    expect(s2).toBeGreaterThan(0);
    expect(s3).toBeGreaterThan(s2);
    expect(s3i).toBeGreaterThan(s3);
    expect(data.price_basis.year).toBe(2025);
  });

  it("formats years and billions", () => {
    expect(yearsLabel([2021, 2022, 2023, 2024, 2025])).toBe("2021–2025");
    expect(yearsLabel([2025])).toBe("2025");
    expect(mdEur(61964)).toBe("62,0");
  });
});
