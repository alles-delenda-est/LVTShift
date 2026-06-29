import { describe, it, expect } from "vitest";
import { loadIndex, loadCommune, communeKeys, loadRegister } from "@/lib/data";

describe("data loaders", () => {
  it("loads the index with the 9 modelled communes", () => {
    const idx = loadIndex();
    expect(idx.communes.length).toBeGreaterThanOrEqual(9);
    expect(idx.communes.find((c) => c.commune_key === "mulhouse")).toBeUndefined();
    expect(idx.communes[0]).toHaveProperty("land_share_pct");
  });
  it("loads a commune payload with headline + sensitivity legs", () => {
    const c = loadCommune("montreuil");
    expect(c.headline.currency).toBe("EUR");
    expect(c.headline_sensitivity.base.land_share_pct).toBeTypeOf("number");
    expect(["object"]).toContain(typeof c.by_category);
  });
  it("tolerates a null income quintile (small communes)", () => {
    const cahors = loadCommune("cahors");
    expect(cahors.by_income_quintile === null || Array.isArray(cahors.by_income_quintile)).toBe(true);
  });
  it("register marks mulhouse not modellable", () => {
    const reg = loadRegister();
    const m = reg.communes.find((c) => c.commune_key === "mulhouse");
    expect(m?.modellable).toBe(false);
  });
});
